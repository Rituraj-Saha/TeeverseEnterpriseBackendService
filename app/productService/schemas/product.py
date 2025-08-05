from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

# You can import from their respective files if modular
from app.productService.schemas.category import CategoryResponse
from app.productService.schemas.product_size import ProductSizeCreate, ProductSizeResponse


# ----- BASE PRODUCT SCHEMA -----
class ProductBase(BaseModel):
    sku: int
    name: str
    thumbnail: str
    images: Optional[List[str]] = None
    description: Optional[str] = None

    price: Decimal
    cost_price: Decimal
    discount: Optional[int] = 0
    max_discount: Optional[int] = 0

    gender: Optional[str] = None  # Male, Female, Unisex
    age_group: Optional[str] = None  # Kids, Adults

    max_order_count: Optional[int] = 5
    is_active: Optional[bool] = True


# ----- CREATE SCHEMA -----
class ProductCreate(ProductBase):
    category_ids: List[str]  # Refer to category UUIDs
    sizes: List[ProductSizeCreate]


# ----- UPDATE SCHEMA -----
class ProductUpdate(BaseModel):
    sku: Optional[int]
    name: Optional[str]
    thumbnail: Optional[str]
    images: Optional[List[str]]
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
    sizes: Optional[List[ProductSizeCreate]]  # Allow replacing entire size list


# ----- RESPONSE SCHEMA -----
class ProductResponse(ProductBase):
    id: str
    created_at: datetime
    updated_at: datetime
    name: str
    thumbnail: str
    images: Optional[List[str]]
    categories: List[CategoryResponse]
    sizes: List[ProductSizeResponse]

    class Config:
        orm_mode = True
