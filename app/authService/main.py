from app.authService.config import settings
from fastapi import FastAPI

app = FastAPI()

print("Running in:", settings.ENVIRONMENT)
print("Using DB:", settings.DATABASE_URL)