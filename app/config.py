import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get base directory of this config.py file
BASE_DIR = Path(__file__).resolve().parent

# Read ENVIRONMENT from the shared .env file
env_file_base = BASE_DIR / ".env"
if env_file_base.exists():
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_file_base)

# Determine which env file to load
env_mode = os.getenv("ENVIRONMENT", "development")
env_filename = ".env.prod" if env_mode == "production" else ".env.dev"
env_file_path = BASE_DIR / env_filename

class Settings(BaseSettings):
    ENVIRONMENT: str
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    INTERNAL_API_URL:str
    INTERNAL_SECRET_TOKEN: str
    ALGORITHM: str
    LOG_LEVEL: str = "info"

    model_config = SettingsConfigDict(
        env_file=str(env_file_path),
        env_file_encoding="utf-8",
        extra="allow"
    )

settings = Settings()
