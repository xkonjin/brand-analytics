# =============================================================================
# EXPLAINER: Application Configuration
# =============================================================================
#
# WHAT IS THIS?
# This module is the central nervous system for the application's configuration.
# It uses Pydantic Settings to load and validate environment variables.
#
# WHY DO WE NEED IT?
# 1. **Twelve-Factor App**: We store config in the environment, not code.
# 2. **Type Safety**: Pydantic ensures integers are integers, booleans are booleans.
# 3. **Centralization**: All settings (DB, Redis, API keys) are in one place.
# 4. **Validation**: We fail fast at startup if a required key is missing.
#
# KEY SECTIONS:
# - App Settings: Basic metadata (name, version, environment).
# - Database: PostgreSQL connection details.
# - Redis/Celery: Caching and background task queue configuration.
# - External APIs: OpenAI, Google, etc. keys.
# - Scoring Weights: Tunable parameters for the brand analysis algorithm.
#
# MARKETING/BUSINESS CONTEXT:
# The `SCORING WEIGHTS` section is crucial. It defines the "recipe" for a perfect brand.
# For example, we weight Social Media (20%) higher than Channel Fit (5%) because
# active engagement is a stronger predictor of growth than just being on the right platform.
# =============================================================================

from functools import lru_cache
from typing import Optional, List
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
    
    # -------------------------------------------------------------------------
    # CORS Configuration (Security Critical)
    # -------------------------------------------------------------------------
    # Allowed origins for CORS - set via CORS_ORIGINS env var as comma-separated list
    # In production, this should be restricted to your actual frontend domain(s)
    # Example: CORS_ORIGINS=https://brand-analytics.vercel.app,https://www.brand-analytics.com
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Allowed hosts for Host header validation (prevents host header attacks)
    # Set via ALLOWED_HOSTS env var as comma-separated list
    # Use "*" only for development, never in production
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # -------------------------------------------------------------------------
    # Debug & Documentation Settings
    # -------------------------------------------------------------------------
    # Enable OpenAPI documentation endpoints (/docs, /redoc, /openapi.json)
    # Should be False in production unless explicitly needed
    ENABLE_DOCS: bool = True
    
    # Enable detailed error messages in API responses
    # Should be False in production to prevent information leakage
    ENABLE_DEBUG_ERRORS: bool = True
    
    # -------------------------------------------------------------------------
    # Authentication Settings
    # -------------------------------------------------------------------------
    # JWT Configuration (for future session-based auth)
    JWT_SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-32"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # API Key Authentication
    REQUIRE_AUTH: bool = False  # Set True in production to require API keys
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_AUTHENTICATED: int = 100  # requests per minute for authenticated users
    RATE_LIMIT_UNAUTHENTICATED: int = 10  # requests per minute for unauthenticated users
    
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
    # Updated to gpt-4o for better performance and lower latency
    OPENAI_MODEL: str = "gpt-4o"  
    
    # Google APIs
    GOOGLE_API_KEY: Optional[str] = None  # For PageSpeed and Custom Search
    GOOGLE_SEARCH_ENGINE_ID: Optional[str] = None  # Custom Search Engine ID
    
    # Apify for social media scraping
    APIFY_API_TOKEN: Optional[str] = None
    
    # Twitter/X API v2 (get from developer.twitter.com)
    TWITTER_BEARER_TOKEN: Optional[str] = None
    
    # Clearbit for company logos (free tier)
    CLEARBIT_API_KEY: Optional[str] = None
    
    # Sentry for error tracking (get from sentry.io)
    SENTRY_DSN: Optional[str] = None
    
    # -------------------------------------------------------------------------
    # Logging Settings
    # -------------------------------------------------------------------------
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_JSON: bool = True    # True for production (JSON), False for dev (colored)
    
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
    # Tuned based on standard marketing audit practices.
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
