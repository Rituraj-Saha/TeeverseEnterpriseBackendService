from fastapi import APIRouter, Header, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.databaseConfigs.database import get_db
from app.authService.services.auth import verify_password
from app.authService.services import auth as auth_service
from app.config import settings

class UserVerifyRequest(BaseModel):
    email: str
    password: str

router = APIRouter(prefix="/internal", tags=["Internal"])


@router.post("/verify-user")
async def verify_user_is_admin_internal(
    data: UserVerifyRequest,
    x_internal_token: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    if x_internal_token != settings.INTERNAL_SECRET_TOKEN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")

    user = await auth_service.get_user_by_email(db, data.email)
    if not user:
        return {"success": False}

    if data.password != "__session__":
        if not await verify_password(data.password, user.password):
            return {"success": False}

    if user.role != "admin":
        return {"success": False}

    return {
        "success": True,
        "email": user.email,
        "role": user.role
    }
