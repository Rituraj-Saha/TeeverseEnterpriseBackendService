from fastapi import APIRouter, Depends, Form, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from fastapi import HTTPException
from app.databaseConfigs.database import get_db
from app.productService.schemas.product import ProductUpdate, ProductResponse,ProductCreate
from app.productService.schemas.product_size import ProductSizeCreate
from app.productService.services import product as product_service
import json
router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse)
async def create_product_with_files(
    sku: int = Form(...),
    name: str = Form(...),
    price: float = Form(...),
    cost_price: float = Form(...),
    description: Optional[str] = Form(None),
    discount: int = Form(0),
    max_discount: Optional[int] = Form(None),
    gender: Optional[str] = Form(None),
    age_group: Optional[str] = Form(None),
    max_order_count: int = Form(5),
    is_active: bool = Form(True),
    category_ids: Optional[str] = Form(None),  # comma-separated string of category IDs
    sizes: str = Form(...),         # JSON string or comma-separated
    thumbnail: UploadFile = File(...),
    images: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
):
    # Parse category_ids
    category_id_list = category_ids.split(",") if category_ids else []

    # Parse sizes (expecting JSON string of array of objects)
    size_list = []
    print("RAW sizes string from Swagger:", sizes)
    if sizes:
        try:
            size_dicts = json.loads(sizes)
            size_list = [ProductSizeCreate(**s) for s in size_dicts]
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid sizes format. Should be JSON list.")

    payload = ProductCreate(
        sku=sku,
        name=name,
        price=price,
        cost_price=cost_price,
        description=description,
        discount=discount,
        max_discount=max_discount,
        gender=gender,
        age_group=age_group,
        max_order_count=max_order_count,
        is_active=is_active,
        category_ids=category_id_list,
        sizes=size_list,
    )

    return await product_service.create_product_with_files(
        db=db,
        payload=payload,
        thumbnail_file=thumbnail,
        image_files=images,
    )

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
