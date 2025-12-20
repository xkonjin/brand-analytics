# =============================================================================
# API Dependencies
# =============================================================================
# This module provides common dependencies used across API routes.
# Dependencies are injected using FastAPI's Depends() mechanism.
# =============================================================================

from typing import Annotated, Optional
import redis.asyncio as redis

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db


# =============================================================================
# Type Aliases for Common Dependencies
# =============================================================================
# Use these type aliases in route functions for cleaner code
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


# =============================================================================
# Redis Client Dependency
# =============================================================================
async def get_redis() -> redis.Redis:
    """
    Get a Redis client connection.

    Creates a new Redis connection that should be closed after use.
    The connection is used for caching and real-time progress tracking.

    Yields:
        redis.Redis: Redis client instance
    """
    client = redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )
    try:
        yield client
    finally:
        await client.close()


RedisClient = Annotated[redis.Redis, Depends(get_redis)]


# =============================================================================
# API Key Validation (Optional - for rate limiting or premium features)
# =============================================================================
async def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> Optional[str]:
    """
    Verify the API key from request headers.

    This is optional and returns None if no key is provided.
    For premium features, this would validate against stored keys.

    Args:
        x_api_key: API key from X-API-Key header

    Returns:
        Optional[str]: The API key if provided and valid

    Note:
        Currently returns the key as-is without validation.
        Implement actual validation logic for production.
    """
    # For now, just return the key if provided
    # In production, validate against a database of API keys
    return x_api_key


# =============================================================================
# Rate Limiting Dependency
# =============================================================================
async def check_rate_limit(
    redis_client: RedisClient,
    x_forwarded_for: Optional[str] = Header(None),
) -> None:
    """
    Check if the request exceeds rate limits.

    Uses Redis to track request counts per IP address.
    Raises 429 Too Many Requests if limit exceeded.

    Args:
        redis_client: Redis connection
        x_forwarded_for: Client IP from proxy header

    Raises:
        HTTPException: 429 if rate limit exceeded
    """
    # Skip rate limiting in development
    if settings.DEBUG:
        return

    # Get client IP
    client_ip = x_forwarded_for or "unknown"

    # Rate limit key
    key = f"rate_limit:{client_ip}"

    try:
        # Get current count
        count = await redis_client.get(key)

        if count is None:
            # First request, set counter with 1 minute expiry
            await redis_client.setex(key, 60, 1)
        else:
            count = int(count)

            # Check limit (100 requests per minute)
            if count >= 100:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please wait before making more requests.",
                )

            # Increment counter
            await redis_client.incr(key)
    except redis.RedisError:
        # If Redis fails, allow the request but log the error
        pass


# =============================================================================
# Common Query Parameters
# =============================================================================
async def common_parameters(
    limit: int = 20,
    offset: int = 0,
) -> dict:
    """
    Common pagination parameters for list endpoints.

    Args:
        limit: Maximum number of items to return (1-100)
        offset: Number of items to skip

    Returns:
        dict: Validated pagination parameters
    """
    # Validate and constrain limit
    if limit < 1:
        limit = 1
    elif limit > 100:
        limit = 100

    # Ensure offset is not negative
    if offset < 0:
        offset = 0

    return {"limit": limit, "offset": offset}


CommonParams = Annotated[dict, Depends(common_parameters)]
