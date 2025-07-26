from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.databaseConfigs.database import get_db
from app.productService.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse
)
from app.productService.services import product as product_service

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse)
async def create_product(payload: ProductCreate, db: AsyncSession = Depends(get_db)):
    return await product_service.create_product(db, payload)


@router.get("/", response_model=List[ProductResponse])
async def list_products(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await product_service.list_products(db, skip, limit)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, db: AsyncSession = Depends(get_db)):
    return await product_service.get_product_by_id(db, product_id)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str, payload: ProductUpdate, db: AsyncSession = Depends(get_db)
):
    return await product_service.update_product(db, product_id, payload)


@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: str, db: AsyncSession = Depends(get_db)):
    await product_service.delete_product(db, product_id)