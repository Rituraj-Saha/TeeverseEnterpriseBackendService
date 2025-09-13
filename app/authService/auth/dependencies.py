from fastapi import Depends, HTTPException, status, Request, Response, BackgroundTasks, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError
from datetime import timedelta

from app.databaseConfigs.database import get_db
from app.config import settings
from app.authService.schemas.user import UserCreate, OTPVerifyRequest, Address,AddressAddRequest,AddressDeleteRequest,AddressUpdateRequest
from app.authService.services import auth as auth_service
from app.authService.auth import jwt as jwt_utils
from app.databaseConfigs.models.authServiceModel.user import User
from app.utils.validators import validate_and_format_phone_number

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ---------------- REGISTER ----------------
async def register_user_dependency(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = None  # passed from route
):
    return await auth_service.create_user(user, db, background_tasks)


# ---------------- LOGIN (SEND OTP) ----------------
async def login_user_dependency(
    identifier: str = Query(..., description="Email or phone"),
    db: AsyncSession = Depends(get_db),
):
    formatted_identifier = identifier
    if identifier.isdigit() or identifier.startswith("+"):
        try:
            formatted_identifier = validate_and_format_phone_number(identifier)
        except Exception as e:
            print(f"Phone format error: {e}")

    user = await auth_service.get_user_by_email(db, formatted_identifier) \
        or await auth_service.get_user_by_phone(db, formatted_identifier)

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


# ---------------- VERIFY OTP ----------------
async def verify_otp_dependency(
    payload: OTPVerifyRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    user = await auth_service.get_user_by_email(db, payload.identifier) \
        or await auth_service.get_user_by_phone(db, payload.identifier)
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
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
    )

    # Send refresh token as HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    )

    return {"access_token": access_token, "token_type": "bearer"}


# ---------------- CURRENT USER ----------------
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt_utils.decode_access_token(token)
        sub = payload.get("sub")
        if not sub:
            raise credentials_exception
        jti = payload.get("jti")
        if await jwt_utils.is_token_blacklisted(jti, db):
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await auth_service.get_user_by_email(db, sub) \
        or await auth_service.get_user_by_phone(db, sub)
    if not user:
        raise credentials_exception

    return user


# ---------------- ADMIN CHECK ----------------
async def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


# ---------------- REFRESH TOKEN ----------------
async def get_refresh_token_user(request: Request):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    return await auth_service.validate_refresh_token(refresh_token)


# ---------------- DEPENDENCY FOR DB ----------------
def get_db_dependency():
    return get_db()


# ADD
async def add_address_dependency(
    payload: AddressAddRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    print("Address Payload: ",payload)
    return await auth_service.add_address(current_user, payload.dict(), db)

# UPDATE
async def update_address_dependency(
    payload: AddressUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        updated_addresses = await auth_service.update_address(current_user, payload.dict(), db)
    except ValueError as e:
        raise HTTPException(status_code=404,detail=str(e))
    if not updated_addresses:
        raise HTTPException(status_code=404, detail="Address not found")
    return updated_addresses

# DELETE
async def delete_address_dependency(
    payload: AddressDeleteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        updated_addresses = await auth_service.delete_address(current_user, payload.id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if not updated_addresses:
        raise HTTPException(status_code=404, detail="Address not found")

    return updated_addresses

# GET ALL ADDRESSES
async def get_addresses_dependency(
    current_user: User = Depends(get_current_user),
):
    return current_user.address or []