import asyncio
import random
from typing import TypeVar, Callable, Any, Optional
from functools import wraps
import logging

import httpx

from app.utils.circuit_breaker import (
    get_circuit,
    CircuitOpenError,
)
from app.utils.cache import CacheManager

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RetryConfig:
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_status_codes: tuple[int, ...] = (429, 500, 502, 503, 504),
        retryable_exceptions: tuple[type[Exception], ...] = (
            httpx.ConnectError,
            httpx.ConnectTimeout,
            httpx.ReadTimeout,
            asyncio.TimeoutError,
        ),
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_status_codes = retryable_status_codes
        self.retryable_exceptions = retryable_exceptions

    def get_delay(self, attempt: int) -> float:
        delay = min(self.base_delay * (self.exponential_base**attempt), self.max_delay)
        if self.jitter:
            delay *= 0.5 + random.random()
        return delay


DEFAULT_RETRY_CONFIG = RetryConfig()

CONSERVATIVE_RETRY_CONFIG = RetryConfig(
    max_retries=2,
    base_delay=2.0,
    max_delay=10.0,
)

AGGRESSIVE_RETRY_CONFIG = RetryConfig(
    max_retries=5,
    base_delay=0.5,
    max_delay=60.0,
)


def with_retry(
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable[[int, Exception], None]] = None,
):
    retry_config = config or DEFAULT_RETRY_CONFIG

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception: Optional[Exception] = None

            for attempt in range(retry_config.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except retry_config.retryable_exceptions as e:
                    last_exception = e
                    if attempt < retry_config.max_retries:
                        delay = retry_config.get_delay(attempt)
                        logger.warning(
                            f"Retry {attempt + 1}/{retry_config.max_retries} "
                            f"for {func.__name__} after {delay:.2f}s: {e}"
                        )
                        if on_retry:
                            on_retry(attempt + 1, e)
                        await asyncio.sleep(delay)
                    else:
                        raise
                except httpx.HTTPStatusError as e:
                    if e.response.status_code in retry_config.retryable_status_codes:
                        last_exception = e
                        if attempt < retry_config.max_retries:
                            delay = retry_config.get_delay(attempt)

                            if e.response.status_code == 429:
                                retry_after = e.response.headers.get("Retry-After")
                                if retry_after and retry_after.isdigit():
                                    delay = max(delay, float(retry_after))

                            logger.warning(
                                f"Retry {attempt + 1}/{retry_config.max_retries} "
                                f"for {func.__name__} (HTTP {e.response.status_code}) "
                                f"after {delay:.2f}s"
                            )
                            if on_retry:
                                on_retry(attempt + 1, e)
                            await asyncio.sleep(delay)
                        else:
                            raise
                    else:
                        raise

            if last_exception:
                raise last_exception
            raise RuntimeError("Unexpected retry loop exit")

        return wrapper

    return decorator


class ResilientHTTPClient:
    def __init__(
        self,
        service_name: str,
        base_url: str = "",
        timeout: float = 30.0,
        retry_config: Optional[RetryConfig] = None,
        cache_prefix: Optional[str] = None,
        cache_ttl: Optional[int] = None,
        circuit_failure_threshold: int = 5,
        circuit_recovery_timeout: float = 30.0,
    ):
        self.service_name = service_name
        self.base_url = base_url
        self.timeout = timeout
        self.retry_config = retry_config or DEFAULT_RETRY_CONFIG
        self.cache_prefix = cache_prefix
        self.cache_ttl = cache_ttl
        self.circuit = get_circuit(
            service_name,
            failure_threshold=circuit_failure_threshold,
            recovery_timeout=circuit_recovery_timeout,
        )
        self._cache = CacheManager()
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.timeout),
                follow_redirects=True,
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def request(
        self,
        method: str,
        url: str,
        use_cache: bool = True,
        cache_key: Optional[str] = None,
        **kwargs,
    ) -> httpx.Response:
        if not self.circuit.is_available:
            raise CircuitOpenError(self.service_name)

        if use_cache and self.cache_prefix and method.upper() == "GET":
            key = cache_key or self._cache._make_key(self.cache_prefix, url, **kwargs)
            cached = await self._cache.get(key)
            if cached is not None:
                logger.debug(f"Cache hit for {self.service_name}: {url}")
                return cached

        last_exception: Optional[Exception] = None

        for attempt in range(self.retry_config.max_retries + 1):
            try:
                client = await self._get_client()
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()

                await self.circuit.record_success()

                if use_cache and self.cache_prefix and method.upper() == "GET":
                    key = cache_key or self._cache._make_key(
                        self.cache_prefix, url, **kwargs
                    )
                    response_data = {
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                        "content": response.text,
                    }
                    await self._cache.set(
                        key,
                        response_data,
                        ttl=self.cache_ttl,
                    )

                return response

            except self.retry_config.retryable_exceptions as e:
                last_exception = e
                await self.circuit.record_failure()

                if attempt < self.retry_config.max_retries:
                    delay = self.retry_config.get_delay(attempt)
                    logger.warning(f"{self.service_name} retry {attempt + 1}: {e}")
                    await asyncio.sleep(delay)
                else:
                    raise

            except httpx.HTTPStatusError as e:
                if e.response.status_code in self.retry_config.retryable_status_codes:
                    last_exception = e
                    await self.circuit.record_failure()

                    if attempt < self.retry_config.max_retries:
                        delay = self.retry_config.get_delay(attempt)
                        if e.response.status_code == 429:
                            retry_after = e.response.headers.get("Retry-After")
                            if retry_after and retry_after.isdigit():
                                delay = max(delay, float(retry_after))

                        logger.warning(
                            f"{self.service_name} retry {attempt + 1} "
                            f"(HTTP {e.response.status_code})"
                        )
                        await asyncio.sleep(delay)
                    else:
                        raise
                else:
                    await self.circuit.record_failure()
                    raise

        if last_exception:
            raise last_exception
        raise RuntimeError("Unexpected request loop exit")

    async def get(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("POST", url, use_cache=False, **kwargs)

    async def get_json(self, url: str, **kwargs) -> Any:
        response = await self.get(url, **kwargs)
        return response.json()

    async def post_json(self, url: str, **kwargs) -> Any:
        response = await self.post(url, **kwargs)
        return response.json()


_clients: dict[str, ResilientHTTPClient] = {}


def get_http_client(
    service_name: str,
    base_url: str = "",
    **kwargs,
) -> ResilientHTTPClient:
    if service_name not in _clients:
        _clients[service_name] = ResilientHTTPClient(
            service_name=service_name,
            base_url=base_url,
            **kwargs,
        )
    return _clients[service_name]


async def close_all_clients() -> None:
    for client in _clients.values():
        await client.close()
    _clients.clear()


PAGESPEED_CLIENT_CONFIG = {
    "service_name": "google_pagespeed",
    "base_url": "https://www.googleapis.com",
    "timeout": 60.0,
    "cache_prefix": "pagespeed",
    "cache_ttl": 3600 * 6,
    "circuit_failure_threshold": 3,
    "circuit_recovery_timeout": 60.0,
}

MOZ_CLIENT_CONFIG = {
    "service_name": "moz_api",
    "base_url": "https://lsapi.seomoz.com",
    "timeout": 30.0,
    "cache_prefix": "moz",
    "cache_ttl": 3600 * 24,
    "circuit_failure_threshold": 5,
    "circuit_recovery_timeout": 30.0,
}

TWITTER_CLIENT_CONFIG = {
    "service_name": "twitter_api",
    "base_url": "https://api.twitter.com",
    "timeout": 15.0,
    "cache_prefix": "twitter",
    "cache_ttl": 3600,
    "circuit_failure_threshold": 5,
    "circuit_recovery_timeout": 60.0,
}
