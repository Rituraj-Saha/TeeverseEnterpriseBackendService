from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.databaseConfigs.database import Base


class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String, unique=True, nullable=False)  # renamed from token to jti
    expires_at = Column(DateTime, nullable=False)
    blacklisted_at = Column(DateTime, default=datetime.utcnow)

    def is_expired(self):
        return datetime.utcnow() > self.expires_at
