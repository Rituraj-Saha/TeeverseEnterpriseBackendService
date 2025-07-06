# app/authService/services/auth.py

from datetime import datetime, timedelta
from typing import Optional

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.databaseConfigs.models.authServiceModel.user import User
from app.authService.schemas.user import UserCreate
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_user_by_phone(db: AsyncSession, phone: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.phone_number == phone))
    return result.scalars().first()


async def create_user(user: UserCreate, db: AsyncSession) -> User:
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        phone_number=user.phone_number,
        email=user.email,
        name=user.name,
        password=hashed_password,
        address=user.address.dict() if user.address else None,
        role=user.role.value if user.role else "user",
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user_by_email(db: AsyncSession, email: str, password: str) -> Optional[User]:
    user = await get_user_by_email(db, email)
    if user and await verify_password(password, user.password):
        return user
    return None


async def authenticate_user_by_phone(db: AsyncSession, phone: str, password: str) -> Optional[User]:
    user = await get_user_by_phone(db, phone)
    if user and await verify_password(password, user.password):
        return user
    return None
