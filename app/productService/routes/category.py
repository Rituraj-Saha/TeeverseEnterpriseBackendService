from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.databaseConfigs.database import get_db
from app.productService.schemas.category import CategoryCreate, CategoryResponse
from app.productService.services import category as category_service
from app.productService.schemas.product import ProductResponse
router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=CategoryResponse)
async def create_category(payload: CategoryCreate, db: AsyncSession = Depends(get_db)):
    return await category_service.create_category(db, payload)


@router.get("/", response_model=List[CategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_db)):
    return await category_service.list_categories(db)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: str, db: AsyncSession = Depends(get_db)):
    return await category_service.get_category_by_id(db, category_id)


@router.delete("/{category_id}", status_code=204)
async def delete_category(category_id: str, db: AsyncSession = Depends(get_db)):
    await category_service.delete_category(db, category_id)

@router.get("/{category_id}/products", response_model=List[ProductResponse])
async def get_products_for_category(
    category_id: str,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    return await category_service.get_products_by_category(db, category_id, skip, limit)