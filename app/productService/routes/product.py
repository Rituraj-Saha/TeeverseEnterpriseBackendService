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
            print(f"error: ${e}")
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
async def update_product_with_files(
    product_id: str,
    sku: Optional[int] = Form(None),
    name: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    cost_price: Optional[float] = Form(None),
    description: Optional[str] = Form(None),
    discount: Optional[int] = Form(None),
    max_discount: Optional[int] = Form(None),
    gender: Optional[str] = Form(None),
    age_group: Optional[str] = Form(None),
    max_order_count: Optional[int] = Form(None),
    is_active: Optional[bool] = Form(None),
    category_ids: Optional[str] = Form(None),  # comma-separated
    sizes: Optional[str] = Form(None),  # JSON string
    existing_thumbnail: Optional[str] = Form(None),  # keep current thumbnail URL if provided
    existing_images: Optional[str] = Form(None),  # JSON list of URLs
    new_thumbnail: Optional[UploadFile] = File(None),
    new_images: Optional[List[UploadFile]] = File(None),
    db: AsyncSession = Depends(get_db),
):
    # Parse category IDs
    category_id_list = category_ids.split(",") if category_ids else None

    # Parse sizes
    size_list = None
    if sizes is not None and sizes.strip() != "":
        try:
            size_dicts = json.loads(sizes)
            if not isinstance(size_dicts, list):
                raise ValueError("Sizes must be a JSON list")
            size_list = [ProductSizeCreate(**s) for s in size_dicts]
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid sizes format. Should be JSON list.")

    # Parse existing images
    existing_image_list = []
    if existing_images:
        try:
            existing_image_list = json.loads(existing_images)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid existing_images format. Should be JSON list.")

    payload = ProductUpdate(
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
        thumbnail=existing_thumbnail,
        images=existing_image_list,
    )

    return await product_service.update_product(
        db=db,
        product_id=product_id,
        payload=payload,
        new_thumbnail_file=new_thumbnail,
        new_image_files=new_images,
    )



@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: str, db: AsyncSession = Depends(get_db)):
    await product_service.delete_product(db, product_id)
