from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.config import settings
from app.models.blacklist import BlacklistedToken
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM)


async def is_token_blacklisted(token: str, db: AsyncSession) -> bool:
    result = await db.execute(
        select(BlacklistedToken).where(BlacklistedToken.jti == token)
    )
    token_entry = result.scalar_one_or_none()
    return token_entry is not None and token_entry.expires_at > datetime.utcnow()


async def blacklist_token(token: str, db: AsyncSession, expires_in_minutes: int):
    expiry_time = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
    db.add(BlacklistedToken(jti=token, expires_at=expiry_time))  # ✅ use jti
    await db.commit()