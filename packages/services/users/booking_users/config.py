"""Configuration module for users service."""

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Config for env file loading
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    # Application info
    APP_NAME: str = "Booking Users Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # API settings
    API_PREFIX: str = "/api/v1"

    # Database settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./../../../database.db"

    # CORS settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]


# Create settings instance
settings = Settings()
