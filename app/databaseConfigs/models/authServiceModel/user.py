from sqlalchemy import Column, Integer, String, JSON, Enum,DateTime
from app.databaseConfigs.database import Base
import enum
from datetime import datetime

class RoleEnum(str, enum.Enum):
    admin = "admin"
    developer = "developer"
    user = "user"
    seller = "seller"
    logistic = "logistic"

class User(Base):
    __tablename__ = "users"

    userid = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    address = Column(JSON, nullable=True)
    role = Column(Enum(RoleEnum), default="user")
    otp_expiry = Column(DateTime, nullable=True)