# =============================================================================
# Authentication Dependencies
# =============================================================================
# FastAPI dependencies for authenticating and authorizing requests.
# These are injected into route handlers using Depends().
# =============================================================================

from datetime import datetime, timezone
from typing import Optional, Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status, Request
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.auth.jwt import verify_api_key, decode_access_token
from app.auth.models import TokenData


# =============================================================================
# API Key Authentication
# =============================================================================

async def get_api_key_from_header(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None),
) -> Optional[str]:
    """
    Extract API key from request headers.
    
    Supports two methods:
    1. X-API-Key header (preferred)
    2. Authorization: Bearer <key> header
    
    Args:
        x_api_key: Value from X-API-Key header
        authorization: Value from Authorization header
        
    Returns:
        Optional[str]: The API key if found, None otherwise
    """
    if x_api_key:
        return x_api_key
    
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:]  # Remove "Bearer " prefix
    
    return None


async def require_api_key(
    api_key: Optional[str] = Depends(get_api_key_from_header),
    db: AsyncSession = Depends(get_db),
) -> "APIKeyRecord":
    """
    Require a valid API key for the request.
    
    This dependency:
    1. Extracts the API key from headers
    2. Validates it against the database
    3. Updates the last_used_at timestamp
    4. Returns the API key record
    
    Args:
        api_key: API key from headers
        db: Database session
        
    Returns:
        APIKeyRecord: The validated API key database record
        
    Raises:
        HTTPException: 401 if key is missing or invalid
        HTTPException: 403 if key is expired or inactive
    """
    # Import here to avoid circular imports
    from app.models.db_models import APIKeyRecord, UserRecord
    
    # Check if auth is required
    if not settings.REQUIRE_AUTH:
        # Return a mock key for development
        return None
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Include X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    # Look up all active API keys and check against hash
    # We need to iterate because we can't query by the hashed value directly
    stmt = select(APIKeyRecord).where(
        APIKeyRecord.is_active == True
    ).join(UserRecord).where(
        UserRecord.is_active == True
    )
    
    result = await db.execute(stmt)
    api_keys = result.scalars().all()
    
    matched_key = None
    for key_record in api_keys:
        if verify_api_key(api_key, key_record.hashed_key):
            matched_key = key_record
            break
    
    if not matched_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    # Check expiration
    if matched_key.expires_at and matched_key.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key has expired",
        )
    
    # Update last_used_at
    await db.execute(
        update(APIKeyRecord)
        .where(APIKeyRecord.id == matched_key.id)
        .values(last_used_at=datetime.now(timezone.utc))
    )
    await db.commit()
    
    return matched_key


async def get_optional_auth(
    api_key: Optional[str] = Depends(get_api_key_from_header),
    db: AsyncSession = Depends(get_db),
) -> Optional["APIKeyRecord"]:
    """
    Optional authentication - returns None if no key provided.
    
    Use this for endpoints that work with or without authentication,
    but may provide different behavior (e.g., higher rate limits) for
    authenticated requests.
    
    Args:
        api_key: API key from headers
        db: Database session
        
    Returns:
        Optional[APIKeyRecord]: The API key record if authenticated, None otherwise
    """
    from app.models.db_models import APIKeyRecord, UserRecord
    
    if not api_key:
        return None
    
    try:
        return await require_api_key(api_key, db)
    except HTTPException:
        return None


async def get_current_user(
    api_key_record: "APIKeyRecord" = Depends(require_api_key),
    db: AsyncSession = Depends(get_db),
) -> "UserRecord":
    """
    Get the current authenticated user from their API key.
    
    Args:
        api_key_record: The validated API key
        db: Database session
        
    Returns:
        UserRecord: The user who owns the API key
        
    Raises:
        HTTPException: 401 if user not found or inactive
    """
    from app.models.db_models import UserRecord
    
    if api_key_record is None:
        # Auth not required, return None
        return None
    
    stmt = select(UserRecord).where(UserRecord.id == api_key_record.user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    return user


async def require_admin(
    user: "UserRecord" = Depends(get_current_user),
) -> "UserRecord":
    """
    Require the current user to be an admin.
    
    Args:
        user: The current authenticated user
        
    Returns:
        UserRecord: The admin user
        
    Raises:
        HTTPException: 403 if user is not an admin
    """
    from app.auth.models import UserRole
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    
    return user


# =============================================================================
# Rate Limiting
# =============================================================================

async def check_rate_limit(
    request: Request,
    api_key_record: Optional["APIKeyRecord"] = Depends(get_optional_auth),
) -> None:
    """
    Check and enforce rate limits.
    
    Rate limits:
    - Authenticated: 100 requests/minute
    - Unauthenticated: 10 requests/minute
    
    Args:
        request: The incoming request
        api_key_record: Optional authenticated API key
        
    Raises:
        HTTPException: 429 if rate limit exceeded
    """
    import redis.asyncio as aioredis
    
    # Skip rate limiting if disabled
    if not settings.RATE_LIMIT_ENABLED:
        return
    
    # Determine rate limit based on auth status
    if api_key_record:
        limit = settings.RATE_LIMIT_AUTHENTICATED
        identifier = f"api_key:{api_key_record.id}"
    else:
        limit = settings.RATE_LIMIT_UNAUTHENTICATED
        # Use IP address for unauthenticated requests
        client_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")
        identifier = f"ip:{client_ip.split(',')[0].strip()}"
    
    # Check rate limit in Redis
    try:
        redis = aioredis.from_url(settings.REDIS_URL)
        key = f"rate_limit:{identifier}"
        
        # Get current count
        count = await redis.get(key)
        
        if count is None:
            # First request in window
            await redis.setex(key, 60, 1)
        else:
            count = int(count)
            if count >= limit:
                # Get TTL for reset time
                ttl = await redis.ttl(key)
                await redis.close()
                
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Try again in {ttl} seconds.",
                    headers={
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(ttl),
                        "Retry-After": str(ttl),
                    },
                )
            
            # Increment counter
            await redis.incr(key)
        
        await redis.close()
        
    except HTTPException:
        raise
    except Exception:
        # If Redis is unavailable, allow the request
        pass


# =============================================================================
# Type Aliases for Cleaner Code
# =============================================================================

# Use these in route function signatures for cleaner dependency injection
RequiredAuth = Annotated["APIKeyRecord", Depends(require_api_key)]
OptionalAuth = Annotated[Optional["APIKeyRecord"], Depends(get_optional_auth)]
CurrentUser = Annotated["UserRecord", Depends(get_current_user)]
AdminUser = Annotated["UserRecord", Depends(require_admin)]
RateLimited = Annotated[None, Depends(check_rate_limit)]
