from fastapi import APIRouter, Depends, status

from app.authService.auth import dependencies as auth_dependency
from app.authService.schemas.user import UserCreate, UserOut, UserLoginViaEmail, UserLoginViaPhone, TokenPayload
from app.databaseConfigs.models.authServiceModel.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut)
async def register_user(result=Depends(auth_dependency.register_user_dependency)):
    return result


@router.post("/login")
async def login_user(result=Depends(auth_dependency.login_user_dependency)):
    return result


@router.post("/logout")
async def logout_user(payload: TokenPayload, result=Depends(auth_dependency.logout_user_dependency)):
    return result


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(auth_dependency.get_current_user)):
    return current_user


@router.get("/admin-check")
async def admin_check(current_user: User = Depends(auth_dependency.get_admin_user)):
    return {"msg": f"Hello {current_user.email}, you are an admin."}
