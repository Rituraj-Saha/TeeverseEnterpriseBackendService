from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Dict,List
import enum
from app.utils.validators import validate_and_format_phone_number

class RoleEnum(str, enum.Enum):
    admin = "admin"
    developer = "developer"
    user = "user"
    seller = "seller"
    logistic = "logistic"

class Address(BaseModel):
    id: int
    addressline: str
    pincode: str
    landmark: Optional[str]
    city: str
    state: str
    nation: str
    receiverPhoneNumber: str
    default: bool = False
class AddressAddRequest(BaseModel):
    addressline: str
    pincode: str
    landmark: Optional[str] = None
    city: str
    state: str
    nation: str
    receiverPhoneNumber: Optional[str] = None
    default: bool = False
class AddressUpdateRequest(Address):
    id: int
class AddressDeleteRequest(BaseModel):
    id: int
class UserCreate(BaseModel):
    phone_number: str
    email: EmailStr
    name: str
    address: Optional[List[Address]] = [] 
    role: Optional[RoleEnum] = RoleEnum.user

    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v):
        return validate_and_format_phone_number(v)

class UserOut(BaseModel):
    userid: int
    phone_number: str
    email: EmailStr
    name: str
    role: RoleEnum
    address: Optional[List[Address]] = [] 
    model_config = {
        "from_attributes": True  # ✅ replaces orm_mode=True in Pydantic v2
    }

class UserLoginViaEmail(BaseModel):
    email: EmailStr
    # password: str


class UserLoginViaPhone(BaseModel):
    phone_number: str
    # password: str

    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v):
        return validate_and_format_phone_number(v)

class TokenPayload(BaseModel):
    token: str

    class Config:
        from_attributes = True

class OTPVerifyRequest(BaseModel):
    identifier: str  # email or phone
    otp: str