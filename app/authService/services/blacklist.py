from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.databaseConfigs.models.authServiceModel.blacklist import BlacklistedToken
from app.authService.schemas.blacklist import BlacklistTokenCreate
from datetime import datetime


async def add_token_to_blacklist(db: AsyncSession, token_data: BlacklistTokenCreate):
    blacklist_token = BlacklistedToken(jti=token_data.jti, expires_at=token_data.expires_at)
    db.add(blacklist_token)
    await db.commit()
    await db.refresh(blacklist_token)
    return blacklist_token


async def is_token_blacklisted(db: AsyncSession, jti: str) -> bool:
    result = await db.execute(select(BlacklistedToken).where(BlacklistedToken.jti == jti))
    token = result.scalars().first()
    if token:
        # Optionally remove expired tokens here
        if token.is_expired():
            await db.delete(token)
            await db.commit()
            return False
        return True
    return False


async def cleanup_expired_tokens(db: AsyncSession):
    """Optional: Periodic task to delete expired tokens."""
    result = await db.execute(select(BlacklistedToken))
    tokens = result.scalars().all()
    for token in tokens:
        if token.is_expired():
            await db.delete(token)
    await db.commit()
