# =============================================================================
# Redis Cache Utility
# =============================================================================
# Provides caching functionality for API responses to reduce costs and
# handle rate limiting. Uses Redis for distributed caching.
# =============================================================================

from typing import Any, Optional, Callable, TypeVar
from functools import wraps
import json
import hashlib
import logging
import asyncio

import redis.asyncio as aioredis

from app.config import settings

logger = logging.getLogger(__name__)

# Type variable for generic cache functions
T = TypeVar("T")


class CacheManager:
    """
    Redis-based cache manager for API responses.

    Features:
    - Async Redis connection pooling
    - JSON serialization for complex objects
    - Configurable TTL per cache key type
    - Cache invalidation support
    - Graceful fallback when Redis is unavailable

    Usage:
        cache = CacheManager()

        # Store a value
        await cache.set("key", {"data": "value"}, ttl=3600)

        # Retrieve a value
        value = await cache.get("key")

        # Use as decorator
        @cache.cached("pagespeed", ttl=3600)
        async def fetch_pagespeed(url: str):
            ...
    """

    # Default TTLs for different cache types (in seconds)
    DEFAULT_TTLS = {
        "pagespeed": 3600 * 6,  # 6 hours - PageSpeed doesn't change often
        "serp": 3600 * 24,  # 24 hours - Search results are relatively stable
        "twitter": 3600,  # 1 hour - Social data changes frequently
        "wikipedia": 3600 * 24 * 7,  # 1 week - Wikipedia rarely changes
        "openai": 3600 * 24,  # 24 hours - AI analysis results
        "default": 3600,  # 1 hour
    }

    _instance: Optional["CacheManager"] = None
    _redis: Optional[aioredis.Redis] = None

    def __new__(cls):
        """Singleton pattern for connection pooling."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def get_redis(self) -> Optional[aioredis.Redis]:
        """Get or create Redis connection."""
        if self._redis is None:
            try:
                self._redis = await aioredis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_timeout=5,
                )
                # Test connection
                await self._redis.ping()
                logger.info("Redis cache connected")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Caching disabled.")
                self._redis = None

        return self._redis

    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate a cache key from prefix and arguments.

        Uses MD5 hash for consistent, short keys.
        """
        # Serialize arguments to a stable string
        key_data = json.dumps(
            {
                "args": args,
                "kwargs": kwargs,
            },
            sort_keys=True,
        )

        # Hash for shorter, consistent keys (not used for security, just key shortening)
        key_hash = hashlib.md5(key_data.encode(), usedforsecurity=False).hexdigest()[
            :12
        ]

        return f"brand_analytics:{prefix}:{key_hash}"

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        redis = await self.get_redis()
        if not redis:
            return None

        try:
            value = await redis.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")

        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Set a value in cache.

        Args:
            key: Cache key
            value: Value to cache (must be JSON-serializable)
            ttl: Time-to-live in seconds

        Returns:
            True if cached successfully
        """
        redis = await self.get_redis()
        if not redis:
            return False

        try:
            serialized = json.dumps(value, default=str)
            await redis.set(key, serialized, ex=ttl or self.DEFAULT_TTLS["default"])
            return True
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        redis = await self.get_redis()
        if not redis:
            return False

        try:
            await redis.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete failed: {e}")
            return False

    async def clear_prefix(self, prefix: str) -> int:
        """
        Clear all keys with a given prefix.

        Args:
            prefix: Key prefix to match

        Returns:
            Number of keys deleted
        """
        redis = await self.get_redis()
        if not redis:
            return 0

        try:
            pattern = f"brand_analytics:{prefix}:*"
            keys = []
            async for key in redis.scan_iter(pattern):
                keys.append(key)

            if keys:
                await redis.delete(*keys)

            return len(keys)
        except Exception as e:
            logger.warning(f"Cache clear failed: {e}")
            return 0

    def cached(
        self,
        prefix: str,
        ttl: Optional[int] = None,
    ):
        """
        Decorator to cache async function results.

        Args:
            prefix: Cache key prefix (e.g., "pagespeed", "twitter")
            ttl: Time-to-live in seconds (uses default if not specified)

        Usage:
            @cache.cached("pagespeed", ttl=3600)
            async def analyze_pagespeed(url: str) -> dict:
                ...
        """
        cache_ttl = ttl or self.DEFAULT_TTLS.get(prefix, self.DEFAULT_TTLS["default"])

        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._make_key(prefix, *args, **kwargs)

                # Try to get from cache
                cached_value = await self.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return cached_value

                # Call the function
                result = await func(*args, **kwargs)

                # Cache the result
                if result is not None:
                    await self.set(cache_key, result, ttl=cache_ttl)
                    logger.debug(f"Cache set: {cache_key}")

                return result

            return wrapper

        return decorator


# Global cache instance
cache = CacheManager()


# Convenience decorator
def cached(prefix: str, ttl: Optional[int] = None):
    """
    Convenience decorator for caching.

    Usage:
        @cached("pagespeed", ttl=3600)
        async def fetch_data(url: str):
            ...
    """
    return cache.cached(prefix, ttl)


# Rate limiter helper
class RateLimiter:
    """
    Simple rate limiter using Redis.

    Implements a sliding window rate limit.

    Usage:
        limiter = RateLimiter("google_api", max_requests=100, window=60)
        if await limiter.is_allowed():
            # Make API call
        else:
            # Wait or fallback
    """

    def __init__(
        self,
        name: str,
        max_requests: int,
        window: int = 60,  # seconds
    ):
        """
        Initialize rate limiter.

        Args:
            name: Limiter name (e.g., "google_api")
            max_requests: Maximum requests per window
            window: Window size in seconds
        """
        self.name = name
        self.max_requests = max_requests
        self.window = window
        self.cache = CacheManager()

    @property
    def key(self) -> str:
        return f"brand_analytics:ratelimit:{self.name}"

    async def is_allowed(self) -> bool:
        """
        Check if a request is allowed under the rate limit.

        Returns:
            True if allowed, False if rate limited
        """
        redis = await self.cache.get_redis()
        if not redis:
            return True  # Allow if Redis unavailable

        try:
            import time

            now = time.time()
            window_start = now - self.window

            # Add current request timestamp
            pipe = redis.pipeline()
            pipe.zremrangebyscore(self.key, 0, window_start)  # Remove old entries
            pipe.zadd(self.key, {str(now): now})  # Add current request
            pipe.zcard(self.key)  # Count requests in window
            pipe.expire(self.key, self.window + 1)  # Set key expiry

            results = await pipe.execute()
            current_count = results[2]

            return current_count <= self.max_requests

        except Exception as e:
            logger.warning(f"Rate limit check failed: {e}")
            return True  # Allow if error

    async def wait_if_needed(self) -> None:
        """Wait if rate limited, then allow."""
        while not await self.is_allowed():
            await asyncio.sleep(1)


# Pre-configured rate limiters for common APIs
rate_limiters = {
    "google_pagespeed": RateLimiter("google_pagespeed", max_requests=25, window=60),
    "google_search": RateLimiter("google_search", max_requests=10, window=60),
    "openai": RateLimiter("openai", max_requests=50, window=60),
    "twitter": RateLimiter("twitter", max_requests=100, window=60),
}
