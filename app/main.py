from app.config import settings
from fastapi import FastAPI
from app.authService.routes import user
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.adminService.admin import setup_admin
from starlette.middleware.sessions import SessionMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run before the application starts
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield  # Yield control to the app
    
    # Optionally, add any shutdown logic here

app = FastAPI(lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key="supersecretkey")

print("Running in:", settings.ENVIRONMENT)
print("Using DB:", settings.DATABASE_URL)
app.include_router(user.router, prefix="/api/v1")
setup_admin(app)