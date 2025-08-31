# app/cartService/routes.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.orderService.cartService.schema import cartSchema
from app.orderService.cartService.service import cartService
from app.databaseConfigs.database import get_db
from app.authService.auth.dependencies import get_current_user
from app.databaseConfigs.models.authServiceModel.user import User

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.post("/", response_model=cartSchema.CartResponse, status_code=status.HTTP_201_CREATED)
async def add_item(
    cart_data: cartSchema.CartCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await cartService.add_to_cart(db, current_user.userid, cart_data.product_id, cart_data.requested_qty,cart_data.requested_size)


@router.get("/", response_model=List[cartSchema.CartResponse])
async def get_cart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await cartService.get_user_cart(db, current_user.userid)


@router.put("/{cart_id}", response_model=cartSchema.CartResponse)
async def update_cart(
    cart_id: str,
    cart_update: cartSchema.CartUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await cartService.update_cart_item(db, current_user.userid, cart_id, cart_update.requested_qty)


@router.delete("/{cart_id}")
async def delete_cart(
    cart_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await cartService.delete_cart_item(db, current_user.userid, cart_id)
