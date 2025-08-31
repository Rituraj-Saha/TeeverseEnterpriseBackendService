# app/cartService/services.py
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.databaseConfigs.models.cartServiceModel.cart import Cart
from app.databaseConfigs.models.productServiceModel.product import Product

PRODUCT_SERVICE_URL = "http://localhost:8000/api/v1"  # adjust base URL if needed


async def add_to_cart(
    db: AsyncSession, 
    user_id: int, 
    product_id: str, 
    requested_qty: int, 
    requested_size: str
):
    # Step 1: check product exists
    print("called")
    result = await db.execute(select(Product).filter(Product.id == product_id, Product.is_active == True))
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or inactive")

    # Step 2: call ProductSize API
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{PRODUCT_SERVICE_URL}/sizes/product/{product_id}")
    if res.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to fetch product sizes")

    sizes_data = res.json()  # list of sizes with stock
    size_entry = next((s for s in sizes_data if s["size"] == requested_size), None)
    if not size_entry:
        raise HTTPException(
            status_code=400,
            detail=f"Size {requested_size} not available for product {product_id}"
        )

    # Step 3: stock validation
    available_stock = size_entry["stock"]
    if available_stock == 0:
        raise HTTPException(status_code=400, detail=f"Size {requested_size} is out of stock")
    if requested_qty > available_stock:
        raise HTTPException(
            status_code=400,
            detail=f"Only {available_stock} items available for size {requested_size}"
        )

    # Step 4: max order validation (still keep your rule)
    if product.max_order_count and requested_qty > product.max_order_count:
        raise HTTPException(
            status_code=400,
            detail=f"Max {product.max_order_count} items allowed per order"
        )

    # Step 5: add/update cart entry
    result = await db.execute(
        select(Cart).filter(
            Cart.user_id == user_id,
            Cart.product_id == product_id,
            Cart.requested_size == requested_size
        )
    )
    cart_item = result.scalars().first()

    if cart_item:
        cart_item.requested_qty = requested_qty
    else:
        cart_item = Cart(
            user_id=user_id,
            product_id=product_id,
            requested_qty=requested_qty,
            requested_size=requested_size
        )
        db.add(cart_item)

    await db.commit()
    await db.refresh(cart_item)
    return cart_item

async def get_user_cart(db: AsyncSession, user_id: int):
    result = await db.execute(select(Cart).filter(Cart.user_id == user_id))
    return result.scalars().all()


async def update_cart_item(db: AsyncSession, user_id: int, cart_id: str, requested_qty: int):
    result = await db.execute(select(Cart).filter(Cart.id == cart_id, Cart.user_id == user_id))
    cart_item = result.scalars().first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    cart_item.requested_qty = requested_qty
    await db.commit()
    await db.refresh(cart_item)
    return cart_item


async def delete_cart_item(db: AsyncSession, user_id: int, cart_id: str):
    result = await db.execute(select(Cart).filter(Cart.id == cart_id, Cart.user_id == user_id))
    cart_item = result.scalars().first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    await db.delete(cart_item)
    await db.commit()
    return {"message": "Cart item deleted"}
