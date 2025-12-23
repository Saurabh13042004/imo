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
    SERPAPI_KEY: str = os.getenv("SERPAPI_KEY", "")
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
    SEARCH_TIMEOUT: int = int(os.getenv("SEARCH_TIMEOUT", 5))  # Per-API timeout for parallel searches
    SEARCH_TOTAL_TIMEOUT: int = int(os.getenv("SEARCH_TOTAL_TIMEOUT", 8))  # Total timeout for all searches

    # Location (zipcode)
    DEFAULT_ZIPCODE: str = os.getenv("DEFAULT_ZIPCODE", "60607")  # Chicago
    DEFAULT_LOCATION: str = os.getenv("DEFAULT_LOCATION", "Chicago, Illinois")

    # JWT Authentication
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", 24))
    JWT_REFRESH_EXPIRATION_DAYS: int = int(os.getenv("JWT_REFRESH_EXPIRATION_DAYS", 7))

    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", os.getenv("GOOGLE_REDIRECT_URL", ""))

    # Password hashing
    PASSWORD_MIN_LENGTH: int = 8

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra environment variables not defined in Settings


settings = Settings()
