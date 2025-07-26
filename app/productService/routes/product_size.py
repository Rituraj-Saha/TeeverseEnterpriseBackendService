from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.databaseConfigs.database import get_db
from app.productService.services import product_size as size_service
from app.productService.schemas.product_size import ProductSizeResponse

router = APIRouter(prefix="/sizes", tags=["Product Sizes"])


@router.get("/", response_model=List[ProductSizeResponse])
async def get_sizes(db: AsyncSession = Depends(get_db)):
    return await size_service.list_sizes(db)


@router.get("/{size_id}", response_model=ProductSizeResponse)
async def get_size(size_id: str, db: AsyncSession = Depends(get_db)):
    return await size_service.get_size_by_id(db, size_id)


@router.delete("/{size_id}", status_code=204)
async def delete_size(size_id: str, db: AsyncSession = Depends(get_db)):
    await size_service.delete_size(db, size_id)
    
@router.get("/product/{product_id}", response_model=List[ProductSizeResponse])
async def get_sizes_for_product(product_id: str, db: AsyncSession = Depends(get_db)):
    return await size_service.get_sizes_by_product_id(db, product_id)