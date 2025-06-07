from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
import enum

class RoleEnum(str, enum.Enum):
    admin = "admin"
    developer = "developer"
    user = "user"
    seller = "seller"
    logistic = "logistic"

class Address(BaseModel):
    addressline: str
    pincode: str
    landmark: Optional[str]
    city: str
    state: str
    nation: str

class UserCreate(BaseModel):
    phone_number: str
    email: EmailStr
    password: str
    address: Optional[Address]
    role: Optional[RoleEnum] = RoleEnum.user

class UserOut(BaseModel):
    userid: int
    phone_number: str
    email: EmailStr
    role: RoleEnum
    address: Optional[Address]
    model_config = {
        "from_attributes": True  # ✅ replaces orm_mode=True in Pydantic v2
    }

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenPayload(BaseModel):
    token: str

    class Config:
        from_attributes = True