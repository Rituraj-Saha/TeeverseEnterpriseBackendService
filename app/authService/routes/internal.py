from fastapi import APIRouter, Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.databaseConfigs.database import get_db
from app.authService.services.auth import verify_password
from app.authService.auth.dependencies import get_user_by_email
from app.config import settings
from pydantic import BaseModel

class UserVerifyRequest(BaseModel):
    email: str
    password: str

router = APIRouter(prefix="/internal", tags=["internal"])

@router.post("/verify-user")
async def verify_user_is_admin_internal(
    # email: str,
    # password: str,
    data: UserVerifyRequest,
    x_internal_token: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    email = data.email
    password = data.password
    if x_internal_token != settings.INTERNAL_SECRET_TOKEN:
        raise HTTPException(status_code=403, detail="Unauthorized")

    user = await get_user_by_email(db, email)
    if not user:
        return {"success": False}
    if password != "__session__" and not await verify_password(password, user.password):
        return {"success": False}
    if user.role != "admin":
        return {"success": False}

    return {"success": True, "email": user.email, "role": user.role}
