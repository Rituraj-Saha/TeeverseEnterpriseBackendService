# app/cartService/schemas.py
from pydantic import BaseModel
from datetime import datetime

class CartBase(BaseModel):
    product_id: str
    requested_qty: int
    requested_size: str

class CartCreate(CartBase):
    pass

class CartUpdate(BaseModel):
    requested_qty: int
    requested_size: str

class CartResponse(BaseModel):
    id: str
    user_id: int
    product_id: str
    requested_qty: int
    requested_size: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
