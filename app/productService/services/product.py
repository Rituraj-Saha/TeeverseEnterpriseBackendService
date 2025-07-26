from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from typing import List, Optional

from app.databaseConfigs.models.productServiceModel.product import Product
from app.databaseConfigs.models.productServiceModel.category import Category
from app.databaseConfigs.models.productServiceModel.product_size import ProductSize
from app.productService.schemas.product import (
    ProductCreate,
    ProductUpdate
)


async def create_product(db: AsyncSession, payload: ProductCreate) -> Product:
    # Fetch categories
    stmt = select(Category).where(Category.id.in_(payload.category_ids))
    result = await db.execute(stmt)
    categories = result.scalars().all()

    if len(categories) != len(payload.category_ids):
        raise HTTPException(status_code=404, detail="One or more categories not found")

    # Create product
    product = Product(
        sku=payload.sku,
        name=payload.name,
        thumbnail=payload.thumbnail,
        images=payload.images,
        description=payload.description,
        price=payload.price,
        cost_price=payload.cost_price,
        discount=payload.discount,
        max_discount=payload.max_discount,
        gender=payload.gender,
        age_group=payload.age_group,
        max_order_count=payload.max_order_count,
        is_active=payload.is_active,
        categories=categories,
    )

    # Add sizes
    for size in payload.sizes:
        product.sizes.append(ProductSize(**size.dict()))

    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


async def get_product_by_id(db: AsyncSession, product_id: str) -> Product:
    stmt = select(Product).where(Product.id == product_id)
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


async def list_products(db: AsyncSession, skip: int = 0, limit: int = 10) -> List[Product]:
    stmt = select(Product).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def update_product(
    db: AsyncSession, product_id: str, payload: ProductUpdate
) -> Product:
    product = await get_product_by_id(db, product_id)

    for field, value in payload.dict(exclude_unset=True).items():
        if field == "category_ids":
            stmt = select(Category).where(Category.id.in_(value))
            result = await db.execute(stmt)
            product.categories = result.scalars().all()
        elif field == "sizes":
            product.sizes.clear()
            for size_data in value:
                product.sizes.append(ProductSize(**size_data.dict()))
        else:
            setattr(product, field, value)

    await db.commit()
    await db.refresh(product)
    return product


async def delete_product(db: AsyncSession, product_id: str) -> None:
    product = await get_product_by_id(db, product_id)
    await db.delete(product)
    await db.commit()
