from fastapi import APIRouter, Depends, HTTPException,status
from app.authService.schemas.user import UserCreate, UserOut, UserLogin, TokenPayload
from app.authService.services.auth import create_user, authenticate_user, create_access_token, create_refresh_token, logout_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.databaseConfigs.database import SessionLocal
from app.authService.auth.dependencies import get_current_user, get_admin_user
from app.databaseConfigs.database import get_db
from datetime import timedelta
from app.config import settings
from jose import jwt, JWTError
from datetime import datetime
from app.databaseConfigs.models.authServiceModel.user import User 
from fastapi.responses import JSONResponse 
from app.authService.schemas.user import UserOut

router = APIRouter()

@router.post("/create-user", response_model=UserOut)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(user, db)

@router.post("/login")
async def login_user(form_data: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": user.phone_number},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(
        data={"sub": user.phone_number},
        expires_delta=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "refresh_token": refresh_token}

@router.post("/logout")
async def logout_user_route(payload: TokenPayload, db: AsyncSession = Depends(get_db)):
    try:
        token = payload.token
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        jti = payload.get("jti")
        exp = payload.get("exp")

        if not jti:
            raise HTTPException(status_code=400, detail="Token does not contain jti")

        expires_at = datetime.utcfromtimestamp(exp) if exp else datetime.utcnow()
        await logout_user(db=db, token_jti=jti, expires_at=expires_at)

        return {"msg": "Logged out successfully"}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
@router.get("/secure/user", tags=["Protected"])
async def secure_user_path(current_user: User = Depends(get_current_user)):
    if current_user.role != "user":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    return {"message": f"Hello, {current_user.email}! You have access to the user route."}

@router.get("/me", tags=["User"], status_code=status.HTTP_200_OK)
async def get_current_user_info(current_user = Depends(get_current_user)):
    user_out = UserOut.model_validate(current_user)  
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "success",
            "user": user_out.model_dump()  # if current_user is a Pydantic model
        }
    )