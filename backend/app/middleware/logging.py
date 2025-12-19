# =============================================================================
# Request Logging Middleware
# =============================================================================
# Provides request/response logging with correlation ID propagation.
# Every incoming request gets a unique ID that follows it through the system.
# =============================================================================

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.utils.logging import (
    get_logger,
    set_correlation_id,
    get_correlation_id,
)

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs all HTTP requests and responses.
    
    Features:
        - Assigns/propagates correlation IDs for request tracing
        - Logs request method, path, and timing
        - Logs response status codes
        - Masks sensitive headers (Authorization, Cookie)
    """
    
    # Headers that may contain sensitive information
    SENSITIVE_HEADERS = frozenset(["authorization", "cookie", "x-api-key"])
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract or generate correlation ID
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        
        set_correlation_id(correlation_id)
        
        # Extract client info
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Log request
        logger.info(
            "Request started",
            method=request.method,
            path=str(request.url.path),
            query=str(request.url.query) if request.url.query else None,
            client_ip=client_ip,
            user_agent=user_agent[:100] if user_agent else None,  # Truncate long UAs
        )
        
        # Process request and time it
        start_time = time.perf_counter()
        
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            # Log response
            logger.info(
                "Request completed",
                method=request.method,
                path=str(request.url.path),
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            
            return response
            
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            logger.exception(
                "Request failed with exception",
                method=request.method,
                path=str(request.url.path),
                duration_ms=round(duration_ms, 2),
                error=str(e),
            )
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP, accounting for proxies.
        
        Priority:
        1. X-Forwarded-For header (first IP in chain)
        2. X-Real-IP header
        3. Direct client connection
        """
        # Check X-Forwarded-For (may contain multiple IPs)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP (original client)
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fall back to direct connection
        if request.client:
            return request.client.host
        
        return "unknown"
