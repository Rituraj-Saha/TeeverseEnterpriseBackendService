from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, BackgroundTasks,status
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.databaseConfigs.models.authServiceModel.user import User
from app.authService.schemas.user import UserCreate
from app.authService.auth import jwt as jwt_utils
from app.config import settings
import random
import asyncio
from app.databaseConfigs.database import SessionLocal

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------- USER FETCH ----------------
async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_user_by_phone(db: AsyncSession, phone: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.phone_number == phone))
    return result.scalars().first()


# ---------------- OTP ----------------
def generate_otp() -> str:
    return f"{random.randint(100000, 999999)}"


async def set_otp_for_user(user: User, db: AsyncSession):
    """
    Generate OTP, save hashed OTP to user.password, schedule auto-reset after expiry.
    """
    otp = generate_otp()
    hashed_otp = pwd_context.hash(otp)
    user.password = hashed_otp
    user.otp_expiry = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_TIME)
    await db.commit()
    await db.refresh(user)
    print(f"OTP for {user.email or user.phone_number}: {otp}")  # Replace with actual email/SMS sending

    # Schedule OTP reset in background
    # BackgroundTasks.add_task(reset_otp_after_expiry, user.id, db)

    return otp


async def create_user(
    user_data: UserCreate,
    db: AsyncSession,
    background_tasks: BackgroundTasks
) -> User:
    """
    Create a new user and send OTP. Raises 409 if email or phone exists.
    """

    # ---------------- Check existing user ----------------
    existing_email = await db.execute(select(User).where(User.email == user_data.email))
    if existing_email.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already registered with this email"
        )

    existing_phone = await db.execute(select(User).where(User.phone_number == user_data.phone_number))
    if existing_phone.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already registered with this phone number"
        )

    # ---------------- Generate OTP and create user ----------------
    otp = generate_otp()
    hashed_otp = pwd_context.hash(otp)

    db_user = User(
        phone_number=user_data.phone_number,
        email=user_data.email,
        name=user_data.name,
        password=hashed_otp,
        otp_expiry=datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_TIME),
        address=user_data.address.dict() if user_data.address else None,
        role=user_data.role.value if user_data.role else "user",
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    print(f"OTP for {db_user.email or db_user.phone_number}: {otp}")

    # ---------------- Schedule OTP reset in background ----------------
    background_tasks.add_task(reset_otp_after_expiry, db_user.userid)

    return db_user

async def verify_otp(user: User, otp: str, db: AsyncSession) -> bool:
    """
    Verify OTP and invalidate it immediately after use.
    """
    if user.otp_expiry and user.otp_expiry < datetime.utcnow():
        return False
    if not pwd_context.verify(otp, user.password):
        return False
    # Invalidate OTP immediately
    user.password = pwd_context.hash(generate_otp())
    user.otp_expiry = None
    await db.commit()
    await db.refresh(user)
    return True


# ---------------- PASSWORD ----------------
async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ---------------- REFRESH TOKEN ----------------
async def validate_refresh_token(refresh_token: str) -> str:
    """
    Validate refresh token from cookie and return user identifier (email/phone).
    """
    try:
        payload = jwt_utils.decode_refresh_token(refresh_token)
        user_identifier = payload.get("sub")
        if not user_identifier:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        return user_identifier
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")


# ---------------- LOGOUT ----------------
async def logout_user(access_token: str, db: AsyncSession):
    """
    Blacklist the access token to prevent reuse.
    """
    try:
        payload = jwt_utils.decode_access_token(access_token)
        jti = payload.get("jti")
        exp = datetime.utcfromtimestamp(payload.get("exp"))
        await jwt_utils.blacklist_token(jti, db, exp)
        return True
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


# ---------------- OTP RESET AFTER EXPIRY ----------------
# ---------------- OTP RESET AFTER EXPIRY ----------------
# ---------------- OTP RESET AFTER EXPIRY ----------------
async def reset_otp_after_expiry(user_id: int):
    """
    Resets the user's OTP after expiry time (auto-expire).
    """
    await asyncio.sleep(settings.OTP_EXPIRE_TIME * 60)

    async with SessionLocal() as db:   # create a fresh session
        user = await db.get(User, user_id)
        if user and user.password:
            user.password = None
            user.otp_expiry = None
            await db.commit()
            print(f"OTP expired for user {user.email or user.phone_number}")

