from functools import lru_cache
from typing import Any, Dict, Optional, List

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Core
    APP_NAME: str = "ShipGen API (FastAPI)"
    ENV: str = "development"
    DEBUG: bool = True

    # Database (mirror Laravel .env style where possible)
    DB_CONNECTION: str = "sqlite"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_DATABASE: str = "shipgen.db"
    DB_USERNAME: str = "techliv"
    DB_PASSWORD: str = "techliv"

    # Security / JWT (will be aligned to Laravel Sanctum behaviour where feasible)
    JWT_SECRET_KEY: str = "CHANGE_ME_SECRET"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # CORS / API
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:4201",
        "http://localhost:4200",
        "http://127.0.0.1:4201",
        "http://127.0.0.1:4200",
    ]
    PORT: int = 9001

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


@lru_cache()
def _get_settings() -> Settings:
    return Settings()


settings: Settings = _get_settings()



