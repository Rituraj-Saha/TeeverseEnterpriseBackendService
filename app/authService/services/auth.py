# app/authService/services/auth.py

from datetime import datetime, timedelta
from typing import Optional

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.databaseConfigs.models.authServiceModel.user import User
from app.authService.schemas.user import UserCreate
from app.config import settings
import random
import asyncio

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()

async def get_user_by_phone(db: AsyncSession, phone: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.phone_number == phone))
    return result.scalars().first()

def generate_otp() -> str:
    return f"{random.randint(100000, 999999)}"

async def set_otp_for_user(user: User, db: AsyncSession):
    otp = generate_otp()
    hashed_otp = pwd_context.hash(otp)
    user.password = hashed_otp
    user.otp_expiry = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_TIME)
    await db.commit()
    await db.refresh(user)
    print(f"OTP for {user.email or user.phone_number}: {otp}")  # Replace with SMTP/SMS
    return otp

async def create_user(user_data: UserCreate, db: AsyncSession) -> User:
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
    print(f"OTP for {db_user.email or db_user.phone_number}: {otp}")  # Replace with SMTP/SMS
    return db_user

async def verify_otp(user: User, otp: str, db: AsyncSession) -> bool:
    if user.otp_expiry and user.otp_expiry < datetime.utcnow():
        return False
    if not pwd_context.verify(otp, user.password):
        return False
    # Invalidate OTP immediately after use
    user.password = pwd_context.hash(generate_otp()) if user.role != "admin" else pwd_context.hash("admin") # replace OTP with random hash
    user.otp_expiry = None
    await db.commit()
    await db.refresh(user)
    return True

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def reset_otp_after_expiry(user_id: int, db: AsyncSession):
    await asyncio.sleep(settings.OTP_EXPIRE_TIME * 60)
    user = await db.get(User, user_id)
    if user and user.password:  # ensure user exists
        user.password = None  # or a random invalid hash
        await db.commit()