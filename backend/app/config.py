from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/audit_db"
    ANTHROPIC_API_KEY: str = ""
    APIFY_API_KEY: str = ""
    SOCIAL_BLADE_API_KEY: str = ""
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    PDF_BASE_URL: str = "http://localhost:3000"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
