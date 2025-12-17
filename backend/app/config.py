# =============================================================================
# Application Configuration
# =============================================================================
# This module handles all application configuration using Pydantic Settings.
# Environment variables are loaded from .env file and validated.
# =============================================================================

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings can be overridden via environment variables or .env file.
    The .env file should be placed in the backend directory.
    """
    
    # -------------------------------------------------------------------------
    # Application Settings
    # -------------------------------------------------------------------------
    APP_NAME: str = "Brand Analytics API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # -------------------------------------------------------------------------
    # API Settings
    # -------------------------------------------------------------------------
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # -------------------------------------------------------------------------
    # Database Settings (PostgreSQL)
    # -------------------------------------------------------------------------
    # Database connection string format: postgresql+asyncpg://user:pass@host:port/db
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/brand_analytics"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    
    # -------------------------------------------------------------------------
    # Redis Settings (Cache & Celery Broker)
    # -------------------------------------------------------------------------
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  # Default cache TTL in seconds (1 hour)
    
    # -------------------------------------------------------------------------
    # Celery Settings (Task Queue)
    # -------------------------------------------------------------------------
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # -------------------------------------------------------------------------
    # External API Keys
    # -------------------------------------------------------------------------
    # OpenAI API key for GPT-4 analysis (brand archetype, content analysis)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"  # Best model for analysis
    
    # Google APIs
    GOOGLE_API_KEY: Optional[str] = None  # For PageSpeed and Custom Search
    GOOGLE_SEARCH_ENGINE_ID: Optional[str] = None  # Custom Search Engine ID
    
    # Apify for social media scraping
    APIFY_API_TOKEN: Optional[str] = None
    
    # Clearbit for company logos (free tier)
    CLEARBIT_API_KEY: Optional[str] = None
    
    # -------------------------------------------------------------------------
    # Storage Settings (S3/R2 for PDF storage)
    # -------------------------------------------------------------------------
    S3_BUCKET_NAME: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None  # For Cloudflare R2 or MinIO
    S3_REGION: str = "auto"
    
    # -------------------------------------------------------------------------
    # Analysis Settings
    # -------------------------------------------------------------------------
    # Maximum time allowed for a single analysis (in seconds)
    ANALYSIS_TIMEOUT: int = 300  # 5 minutes
    
    # Number of recent tweets to analyze
    TWITTER_POSTS_LIMIT: int = 10
    
    # Number of recent blog posts to analyze
    BLOG_POSTS_LIMIT: int = 5
    
    # -------------------------------------------------------------------------
    # Scoring Weights (configurable per deployment)
    # -------------------------------------------------------------------------
    # These weights determine how each module contributes to the overall score
    WEIGHT_SEO: float = 0.15
    WEIGHT_AI_DISCOVERABILITY: float = 0.10
    WEIGHT_SOCIAL_MEDIA: float = 0.20
    WEIGHT_BRAND_MESSAGING: float = 0.15
    WEIGHT_WEBSITE_UX: float = 0.15
    WEIGHT_CONTENT: float = 0.10
    WEIGHT_TEAM_PRESENCE: float = 0.10
    WEIGHT_CHANNEL_FIT: float = 0.05
    
    # -------------------------------------------------------------------------
    # Pydantic Settings Configuration
    # -------------------------------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    
    Uses lru_cache to ensure settings are only loaded once and reused.
    This is important for performance as reading from environment is slow.
    
    Returns:
        Settings: Application settings instance
    """
    return Settings()


# Export a default settings instance for convenience
settings = get_settings()

