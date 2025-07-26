from pydantic import BaseModel
from typing import Optional

class ProductSizeBase(BaseModel):
    size: str  # e.g., "M", "L"
    stock: int
    additional_price: Optional[float] = 0.0

class ProductSizeCreate(ProductSizeBase):
    pass

class ProductSizeResponse(ProductSizeBase):
    id: str

    class Config:
        orm_mode = True
