# app/authService/auth/dependency.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from datetime import datetime, timedelta

from app.databaseConfigs.database import get_db
from app.config import settings
from app.authService.schemas.user import UserCreate, UserLoginViaEmail, UserLoginViaPhone, TokenPayload
from app.authService.services import auth as auth_service
from app.authService.auth import jwt as jwt_utils

from app.databaseConfigs.models.authServiceModel.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/login")


async def register_user_dependency(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await auth_service.create_user(user, db)


async def login_user_dependency(form_data: UserLoginViaEmail | UserLoginViaPhone, db: AsyncSession = Depends(get_db)):
    if isinstance(form_data, UserLoginViaEmail):
        user = await auth_service.authenticate_user_by_email(db, form_data.email, form_data.password)
    elif isinstance(form_data, UserLoginViaPhone):
        user = await auth_service.authenticate_user_by_phone(db, form_data.phone_number, form_data.password)
    else:
        raise HTTPException(status_code=400, detail="Invalid login payload")

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = jwt_utils.create_access_token(
        data={"sub": user.email or user.phone_number},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = jwt_utils.create_refresh_token(
        data={"sub": user.email or user.phone_number},
        expires_delta=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
    )

    return {"access_token": access_token, "refresh_token": refresh_token}


async def logout_user_dependency(payload: TokenPayload, db: AsyncSession = Depends(get_db)):
    try:
        decoded_payload = jwt.decode(payload.token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        jti = decoded_payload.get("jti")
        exp = decoded_payload.get("exp")
        if not jti or not exp:
            raise HTTPException(status_code=400, detail="Invalid token payload")

        expires_at = datetime.utcfromtimestamp(exp)
        await jwt_utils.blacklist_token(jti, db, expires_at)

        return {"msg": "Logged out successfully"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        sub = payload.get("sub")
        jti = payload.get("jti")
        exp = payload.get("exp")

        if not sub or not jti:
            raise credentials_exception

        if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Token expired")

        if await jwt_utils.is_token_blacklisted(jti, db):
            raise HTTPException(status_code=401, detail="Token has been revoked")

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
