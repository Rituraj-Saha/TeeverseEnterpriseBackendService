from pydantic import BaseModel
from typing import List, Optional, Union
from decimal import Decimal
from datetime import datetime

from app.productService.schemas.category import CategoryResponse
from app.productService.schemas.product_size import ProductSizeCreate, ProductSizeResponse


# ----- BASE PRODUCT SCHEMA -----
class ProductBase(BaseModel):
    sku: int
    name: str
    # thumbnail: str
    # images: Optional[List[str]] = None
    description: Optional[str] = None

    price: Decimal
    
    discount: Optional[int] = 0
    max_discount: Optional[int] = 0

    gender: Optional[str] = None
    age_group: Optional[str] = None

    max_order_count: Optional[int] = 5
    is_active: Optional[bool] = True


# ----- CREATE SCHEMA -----
class ProductCreate(ProductBase):
    category_ids: List[str]
    sizes: List[ProductSizeCreate]
    cost_price: Decimal


# ----- UPDATE SCHEMA (JSON only) -----
class ProductUpdate(BaseModel):
    sku: Optional[int]
    name: Optional[str]
    description: Optional[str]

    price: Optional[Decimal]
    cost_price: Optional[Decimal]
    discount: Optional[int]
    max_discount: Optional[int]

    gender: Optional[str]
    age_group: Optional[str]

    max_order_count: Optional[int]
    is_active: Optional[bool]

    category_ids: Optional[List[str]]
    sizes: Optional[List[ProductSizeCreate]]

    # These are strings (URLs), not files
    thumbnail: Optional[str]  # This should point to new URL if updated
    images: Optional[List[str]]  # Append or replace from service layer


# ----- RESPONSE SCHEMA -----
class ProductResponse(ProductBase):
    id: str
    created_at: datetime
    updated_at: datetime
    categories: List[CategoryResponse]
    sizes: List[ProductSizeResponse]
    thumbnail: str
    images: Optional[List[str]]
    class Config:
        orm_mode = True
