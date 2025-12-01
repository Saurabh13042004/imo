import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:password@localhost:5432/product_aggregator"
    )
    DATABASE_ECHO: bool = os.getenv("DATABASE_ECHO", "False").lower() == "true"

    # API Keys
    RAPIDAPI_KEY: str = os.getenv("RAPIDAPI_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
    REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET", "")

    # Redis (optional)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")

    # Server
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))

    # Cache settings (in seconds)
    SEARCH_CACHE_TTL: int = int(os.getenv("SEARCH_CACHE_TTL", 3600))  # 1 hour
    PRODUCT_CACHE_TTL: int = int(os.getenv("PRODUCT_CACHE_TTL", 86400))  # 24 hours
    REVIEW_CACHE_TTL: int = int(os.getenv("REVIEW_CACHE_TTL", 604800))  # 7 days

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", 100))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", 60))  # seconds

    # API Timeouts (in seconds)
    HTTP_TIMEOUT: int = int(os.getenv("HTTP_TIMEOUT", 30))
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", 60))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"


settings = Settings()
