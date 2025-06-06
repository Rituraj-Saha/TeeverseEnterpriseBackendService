import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load common env
load_dotenv(".env")

env_file = ".env.prod" if os.getenv("ENVIRONMENT") == "production" else ".env.dev"
load_dotenv(dotenv_path=env_file, override=True)


class Settings(BaseSettings):
    ENVIRONMENT: str
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str
    LOG_LEVEL: str = "info"

    model_config = SettingsConfigDict(env_file=env_file, extra="allow")


settings = Settings()