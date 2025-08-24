from datetime import datetime, timedelta
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.databaseConfigs.models.authServiceModel.blacklist import BlacklistedToken
from app.config import settings
import secrets

ALGORITHM = settings.ALGORITHM


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    jti = data.get("jti") or secrets.token_urlsafe(32)
    to_encode.update({"exp": expire, "jti": jti})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    jti = data.get("jti") or secrets.token_urlsafe(32)
    to_encode.update({"exp": expire, "jti": jti})
    return jwt.encode(to_encode, settings.JWT_REFRESH_SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])


def decode_refresh_token(token: str):
    return jwt.decode(token, settings.JWT_REFRESH_SECRET_KEY, algorithms=[ALGORITHM])


async def is_token_blacklisted(jti: str, db: AsyncSession) -> bool:
    result = await db.execute(select(BlacklistedToken).where(BlacklistedToken.jti == jti))
    token_entry = result.scalar_one_or_none()
    return token_entry is not None and token_entry.expires_at > datetime.utcnow()


async def blacklist_token(jti: str, db: AsyncSession, expires_at: datetime):
    db.add(BlacklistedToken(jti=jti, expires_at=expires_at))
    await db.commit()
