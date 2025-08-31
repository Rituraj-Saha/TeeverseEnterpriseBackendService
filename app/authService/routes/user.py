from fastapi import APIRouter, Depends, Response, Header,BackgroundTasks
from app.authService.auth import dependencies as auth_dependency
from app.authService.services import auth as auth_service
from app.authService.schemas.user import UserCreate, UserOut, OTPVerifyRequest
from app.databaseConfigs.models.authServiceModel.user import User
from app.authService.auth import jwt as jwt_utils
from datetime import timedelta
from app.config import settings
from app.databaseConfigs.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
async def register_user(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    return await auth_service.create_user(user, db, background_tasks)


@router.post("/login")
async def login_user(result=Depends(auth_dependency.login_user_dependency)):
    return result


@router.post("/verify-otp")
async def verify_otp(payload: OTPVerifyRequest, result=Depends(auth_dependency.verify_otp_dependency)):
    return result


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(auth_dependency.get_current_user)):
    return current_user


@router.get("/admin-check")
async def admin_check(current_user: User = Depends(auth_dependency.get_admin_user)):
    return {"msg": f"Hello {current_user.email}, you are an admin."}


@router.post("/refresh-token")
async def refresh_access_token(user_identifier: str = Depends(auth_dependency.get_refresh_token_user)):
    access_token = jwt_utils.create_access_token(
        data={"sub": user_identifier},
        expires_delta=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(
    response: Response,
    authorization: str = Header(...),
    db=Depends(auth_dependency.get_db_dependency),
):
    token = authorization.replace("Bearer ", "")
    await auth_service.logout_user(token, db)
    response.delete_cookie("refresh_token")
    return {"msg": "Logged out successfully"}
