from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

from app.databaseConfigs.models.productServiceModel.product_size import ProductSize
from app.productService.schemas.product_size import ProductSizeCreate


async def get_size_by_id(db: AsyncSession, size_id: str) -> ProductSize:
    stmt = select(ProductSize).where(ProductSize.id == size_id)
    result = await db.execute(stmt)
    size = result.scalar_one_or_none()
    if not size:
        raise HTTPException(status_code=404, detail="Product size not found")
    return size


async def list_sizes(db: AsyncSession):
    result = await db.execute(select(ProductSize))
    return result.scalars().all()


async def delete_size(db: AsyncSession, size_id: str):
    size = await get_size_by_id(db, size_id)
    await db.delete(size)
    await db.commit()
    
async def get_sizes_by_product_id(db: AsyncSession, product_id: str):
    stmt = select(ProductSize).where(ProductSize.product_id == product_id)
    result = await db.execute(stmt)
    return result.scalars().all()