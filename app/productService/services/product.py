# from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
# from fastapi import HTTPException, status
# from typing import List, Optional
import os
import uuid
from fastapi import UploadFile, Form
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List,Optional

from app.databaseConfigs.models.productServiceModel.product import Product
from app.databaseConfigs.models.productServiceModel.category import Category
from app.databaseConfigs.models.productServiceModel.product_size import ProductSize
from app.productService.schemas.product import (
    ProductCreate,
    ProductUpdate
)
from sqlalchemy import select

# async def create_product(db: AsyncSession, payload: ProductCreate) -> Product:
#     # Fetch categories
#     stmt = select(Category).where(Category.id.in_(payload.category_ids))
#     result = await db.execute(stmt)
#     categories = result.scalars().all()

#     if len(categories) != len(payload.category_ids):
#         raise HTTPException(status_code=404, detail="One or more categories not found")

#     # Create product
#     product = Product(
#         sku=payload.sku,
#         name=payload.name,
#         thumbnail=payload.thumbnail,
#         images=payload.images,
#         description=payload.description,
#         price=payload.price,
#         cost_price=payload.cost_price,
#         discount=payload.discount,
#         max_discount=payload.max_discount,
#         gender=payload.gender,
#         age_group=payload.age_group,
#         max_order_count=payload.max_order_count,
#         is_active=payload.is_active,
#         categories=categories,
#     )

#     # Add sizes
#     for size in payload.sizes:
#         product.sizes.append(ProductSize(**size.dict()))

#     db.add(product)
#     await db.commit()

#     stmt = (
#         select(Product)
#         .options(
#             selectinload(Product.categories),
#             selectinload(Product.sizes)
#         )
#         .where(Product.id == product.id)
#     )
#     result = await db.execute(stmt)
#     product = result.scalar_one()
#     return product

UPLOAD_DIRECTORY = "static/uploads"  # Adjust based on your project

async def save_file(file: UploadFile, subdir: str) -> str:
    os.makedirs(os.path.join(UPLOAD_DIRECTORY, subdir), exist_ok=True)
    file_extension = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, subdir, unique_name)
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    return file_path


async def create_product_with_files(
    db: AsyncSession,
    payload: ProductCreate,
    thumbnail_file: UploadFile,
    image_files: List[UploadFile]
) -> Product:

    if not thumbnail_file:
        raise HTTPException(status_code=400, detail="Thumbnail is required")

    if not image_files or len(image_files) == 0:
        raise HTTPException(status_code=400, detail="At least one image is required")

    # Save thumbnail
    thumbnail_path = await save_file(thumbnail_file, "thumbnails")

    # Save images
    image_paths = []
    for file in image_files:
        path = await save_file(file, "images")
        image_paths.append(path)

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
        thumbnail=thumbnail_path,
        images=image_paths,
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

    for size in payload.sizes:
        product.sizes.append(ProductSize(**size.dict()))

    db.add(product)
    await db.commit()

    # Fetch with relationships
    stmt = (
        select(Product)
        .options(
            selectinload(Product.categories),
            selectinload(Product.sizes)
        )
        .where(Product.id == product.id)
    )
    result = await db.execute(stmt)
    product = result.scalar_one()
    return product


async def get_product_by_id(db: AsyncSession, product_id: str) -> Product:
    stmt = (
        select(Product)
        .options(
            selectinload(Product.categories),
            selectinload(Product.sizes),
        )
        .where(Product.id == product_id)
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


async def list_products(db: AsyncSession, skip: int = 0, limit: int = 10) -> List[Product]:
    stmt = (
        select(Product)
        .options(
            selectinload(Product.categories),
            selectinload(Product.sizes),
        )
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


# async def update_product(
#     db: AsyncSession, product_id: str, payload: ProductUpdate
# ) -> Product:
#     product = await get_product_by_id(db, product_id)

#     for field, value in payload.dict(exclude_unset=True).items():
#         if field == "category_ids":
#             stmt = select(Category).where(Category.id.in_(value))
#             result = await db.execute(stmt)
#             product.categories = result.scalars().all()
#         elif field == "sizes":
#             product.sizes.clear()
#             for size_data in value:
#                 product.sizes.append(ProductSize(**size_data.dict()))
#         else:
#             setattr(product, field, value)

#     await db.commit()
#     stmt = (
#         select(Product)
#         .options(
#             selectinload(Product.categories),
#             selectinload(Product.sizes)
#         )
#         .where(Product.id == product.id)
#     )
#     result = await db.execute(stmt)
#     product = result.scalar_one()
#     return product

async def update_product(
    db: AsyncSession,
    product_id: str,
    payload: ProductUpdate,
    thumbnail_file: Optional[UploadFile] = None,
    image_files: Optional[List[UploadFile]] = None
) -> Product:
    product = await get_product_by_id(db, product_id)

    # Update fields from payload
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

    # If a new thumbnail is uploaded
    if thumbnail_file:
        product.thumbnail = await save_file(thumbnail_file, "thumbnails")

    # If new images are uploaded (replace old list)
    if image_files and len(image_files) > 0:
        image_paths = []
        for file in image_files:
            path = await save_file(file, "images")
            image_paths.append(path)
        product.images = image_paths

    await db.commit()

    # Reload the updated product with relationships
    stmt = (
        select(Product)
        .options(
            selectinload(Product.categories),
            selectinload(Product.sizes)
        )
        .where(Product.id == product.id)
    )
    result = await db.execute(stmt)
    product = result.scalar_one()
    return product


async def delete_product(db: AsyncSession, product_id: str) -> None:
    product = await get_product_by_id(db, product_id)
    await db.delete(product)
    await db.commit()
