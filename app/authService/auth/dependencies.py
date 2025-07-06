# app/authService/auth/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from datetime import datetime, timedelta

from app.databaseConfigs.database import get_db
from app.config import settings
from app.authService.schemas.user import UserCreate, OTPVerifyRequest
from app.authService.services import auth as auth_service
from app.authService.auth import jwt as jwt_utils
from app.databaseConfigs.models.authServiceModel.user import User
from fastapi import Query
from app.utils.validators import validate_and_format_phone_number

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def register_user_dependency(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await auth_service.create_user(user, db)

async def login_user_dependency(
    identifier: str = Query(..., description="Email or phone"),
    db: AsyncSession = Depends(get_db)
):
    formatted_identifier = identifier
    if identifier.isdigit() or identifier.startswith("+"):
        try:
            formatted_identifier = validate_and_format_phone_number(identifier)
        except Exception as e:
            print(f"Phone format error: {e}")
            # Optionally handle invalid phone format here

    user = await auth_service.get_user_by_email(db, formatted_identifier) or await auth_service.get_user_by_phone(db, formatted_identifier)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "User not found",
                "_links": {
                    "signup": {"href": "/api/v1/auth/register"},
                    "prev": {"href": "/api/v1/auth/login"}
                }
            }
        )

    await auth_service.set_otp_for_user(user, db)

    return {
        "message": "OTP sent to your registered email/phone",
        "_links": {
            "verify_otp": {"href": "/api/v1/auth/verify-otp"},
            "resend_otp": {"href": "/api/v1/auth/login"}
        }
    }


async def verify_otp_dependency(payload: OTPVerifyRequest, db: AsyncSession = Depends(get_db)):
    user = await auth_service.get_user_by_email(db, payload.identifier) or await auth_service.get_user_by_phone(db, payload.identifier)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    if not await auth_service.verify_otp(user, payload.otp, db):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    
    access_token = jwt_utils.create_access_token(
        data={"sub": user.email or user.phone_number},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = jwt_utils.create_refresh_token(
        data={"sub": user.email or user.phone_number},
        expires_delta=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
    )

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        sub = payload.get("sub")
        if not sub:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await auth_service.get_user_by_email(db, sub) or await auth_service.get_user_by_phone(db, sub)
    if not user:
        raise credentials_exception

    return user

async def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user
