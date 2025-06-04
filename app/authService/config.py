# app/config.py
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# # Load .env based on an ENVIRONMENT variable or default to .env.dev
# env_file = ".env.prod" if os.getenv("ENVIRONMENT") == "production" else ".env.dev"
# load_dotenv(dotenv_path=env_file)


# Always load the common env first
load_dotenv(dotenv_path=".env")  # shared across all environments

# Then override with specific one
env_file = ".env.prod" if os.getenv("ENVIRONMENT") == "production" else ".env.dev"
load_dotenv(dotenv_path=env_file)


class Settings(BaseSettings):
    ENVIRONMENT: str
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY:str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
     

    class Config:
        case_sensitive = True

settings = Settings()
