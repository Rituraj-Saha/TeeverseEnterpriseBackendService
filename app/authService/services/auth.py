from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.databaseConfigs.models.authServiceModel.user import User
from app.authService.schemas.user import UserCreate
from app.authService.schemas.blacklist import BlacklistTokenCreate
from app.authService.services.blacklist import add_token_to_blacklist, is_token_blacklisted
from app.config import settings
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = settings.ALGORITHM


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()

async def get_user_by_phone(db: AsyncSession, phn: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.phone_number == phn))
    return result.scalars().first()


async def create_user(user: UserCreate, db: AsyncSession) -> User:
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        phone_number=user.phone_number,
        email=user.email,
        password=hashed_password,
        address=user.address.dict() if user.address else None,
        role=user.role.value if user.role else "user",
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    # jti = data.get("jti") or str(jwt.utils.base64url_encode(jwt.utils.get_random_bytes(32)), "utf-8")
    jti = data.get("jti") or secrets.token_urlsafe(32)
    to_encode.update({"exp": expire, "jti": jti})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES))
    # jti = data.get("jti") or str(jwt.utils.base64url_encode(jwt.utils.get_random_bytes(32)), "utf-8")
    jti = data.get("jti") or secrets.token_urlsafe(32)
    to_encode.update({"exp": expire, "jti": jti})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not await verify_password(password, user.password):
        return None
    return user


async def logout_user(db: AsyncSession, token_jti: str, expires_at: datetime):
    """
    Add token's jti to blacklist with expiry.
    """
    blacklist_data = BlacklistTokenCreate(jti=token_jti, expires_at=expires_at)
    await add_token_to_blacklist(db, blacklist_data)


async def is_token_valid(db: AsyncSession, token: str, token_type: str = "access") -> bool:
    """
    Check if token is valid and not blacklisted.
    """
    try:
        secret_key = settings.JWT_SECRET_KEY if token_type == "access" else settings.JWT_REFRESH_SECRET_KEY
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        if not jti:
            return False
        if await is_token_blacklisted(db, jti):
            return False
        return True
    except JWTError:
        return False
