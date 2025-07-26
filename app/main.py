from app.config import settings
from fastapi import FastAPI
from app.authService.routes import user
from app.productService.routes import product
from app.productService.routes import category
from app.productService.routes import product_size
from contextlib import asynccontextmanager
from app.databaseConfigs.database import engine, Base
from app.adminService.admin import setup_admin
from starlette.middleware.sessions import SessionMiddleware
from app.authService.routes import internal


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
app.include_router(product.router, prefix="/api/v1")
app.include_router(category.router, prefix="/api/v1")
app.include_router(product_size.router, prefix="/api/v1")
app.include_router(internal.router)
setup_admin(app)