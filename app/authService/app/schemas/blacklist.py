from pydantic import BaseModel
from datetime import datetime

class BlacklistTokenCreate(BaseModel):
    jti: str  # Unique JWT ID to blacklist
    expires_at: datetime  # Token expiry time

class BlacklistTokenOut(BaseModel):
    id: int
    jti: str
    expires_at: datetime

    class Config:
        from_attributes = True
