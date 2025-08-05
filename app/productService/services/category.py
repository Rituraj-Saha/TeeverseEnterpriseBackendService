from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.databaseConfigs.models.productServiceModel.category import Category
from app.databaseConfigs.models.productServiceModel.product import Product
from app.productService.schemas.category import CategoryCreate


async def create_category(db: AsyncSession, payload: CategoryCreate) -> Category:
    category = Category(**payload.dict())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def get_category_by_id(db: AsyncSession, category_id: str) -> Category:
    stmt = select(Category).where(Category.id == category_id)
    result = await db.execute(stmt)
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return category


async def list_categories(db: AsyncSession) -> list[Category]:
    stmt = select(Category)
    result = await db.execute(stmt)
    return result.scalars().all()


async def delete_category(db: AsyncSession, category_id: str) -> None:
    category = await get_category_by_id(db, category_id)
    await db.delete(category)
    await db.commit()


async def get_products_by_category(
    db: AsyncSession, category_id: str, skip: int = 0, limit: int = 10
) -> list[Product]:
    # Ensure category exists
    await get_category_by_id(db, category_id)

    stmt = (
        select(Product)
        .join(Product.categories)
        .where(Category.id == category_id)
        .options(
            selectinload(Product.categories),
            selectinload(Product.sizes)
        )
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
