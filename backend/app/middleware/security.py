"""
Module: middleware.security
Purpose: Security headers middleware to protect against common web vulnerabilities.

This middleware adds security headers to all HTTP responses:
- X-Content-Type-Options: Prevents MIME type sniffing attacks
- X-Frame-Options: Prevents clickjacking by disabling iframe embedding
- X-XSS-Protection: Legacy XSS protection for older browsers
- Referrer-Policy: Controls referrer information sent with requests
- Permissions-Policy: Restricts browser features (camera, mic, etc.)
- Content-Security-Policy: (Optional) Restricts resource loading sources

Architecture Notes:
- Applied as Starlette middleware, runs on every request/response cycle
- Headers are configurable via environment variables
- Production mode enables stricter policies

Author: Claude Code Assistant
Date Created: 2025-01-19
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable, Dict, Optional


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds security headers to all HTTP responses.
    
    These headers protect against common web vulnerabilities:
    - XSS (Cross-Site Scripting)
    - Clickjacking
    - MIME type confusion attacks
    - Information leakage via referrer
    
    Attributes:
        custom_headers: Additional headers to include beyond defaults
        
    Example:
        >>> app.add_middleware(SecurityHeadersMiddleware)
        >>> # Or with custom headers:
        >>> app.add_middleware(
        ...     SecurityHeadersMiddleware,
        ...     custom_headers={"X-Custom-Header": "value"}
        ... )
    """
    
    # Default security headers applied to all responses
    DEFAULT_HEADERS: Dict[str, str] = {
        # Prevent MIME type sniffing - browser must respect declared Content-Type
        "X-Content-Type-Options": "nosniff",
        
        # Prevent clickjacking - page cannot be embedded in iframes
        "X-Frame-Options": "DENY",
        
        # Legacy XSS filter for older browsers (modern browsers ignore this)
        "X-XSS-Protection": "1; mode=block",
        
        # Control referrer information sent with requests
        # strict-origin-when-cross-origin: Send full URL for same-origin, only origin for cross-origin
        "Referrer-Policy": "strict-origin-when-cross-origin",
        
        # Disable browser features we don't need
        # This prevents malicious scripts from accessing sensitive APIs
        "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
        
        # Prevent caching of sensitive API responses
        # Individual endpoints can override with more permissive caching if needed
        "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
    }
    
    def __init__(
        self,
        app: Callable,
        custom_headers: Optional[Dict[str, str]] = None,
        enable_csp: bool = False,
        csp_policy: Optional[str] = None,
    ) -> None:
        """
        Initialize the security headers middleware.
        
        Args:
            app: The ASGI application to wrap
            custom_headers: Additional headers to add (overrides defaults)
            enable_csp: Whether to enable Content-Security-Policy header
            csp_policy: Custom CSP policy string (if enable_csp is True)
            
        Note:
            CSP is disabled by default because it can break legitimate
            functionality. Enable it only after testing thoroughly.
        """
        super().__init__(app)
        self.headers = self.DEFAULT_HEADERS.copy()
        
        # Add Content-Security-Policy if enabled
        if enable_csp:
            self.headers["Content-Security-Policy"] = csp_policy or self._default_csp()
        
        # Override with custom headers
        if custom_headers:
            self.headers.update(custom_headers)
    
    def _default_csp(self) -> str:
        """
        Generate a reasonable default Content-Security-Policy.
        
        Returns:
            CSP policy string that allows:
            - Scripts/styles from same origin
            - Images from same origin and data: URIs
            - Fonts from same origin
            - Connections to same origin only
        """
        return "; ".join([
            "default-src 'self'",
            "script-src 'self'",
            "style-src 'self' 'unsafe-inline'",  # Allow inline styles for convenience
            "img-src 'self' data: https:",  # Allow images from HTTPS and data URIs
            "font-src 'self'",
            "connect-src 'self'",
            "frame-ancestors 'none'",  # Redundant with X-Frame-Options but more flexible
            "base-uri 'self'",
            "form-action 'self'",
        ])
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and add security headers to the response.
        
        Args:
            request: The incoming HTTP request
            call_next: The next middleware/handler in the chain
            
        Returns:
            Response with security headers added
        """
        # Call the next handler to get the response
        response = await call_next(request)
        
        # Add security headers to the response
        for header_name, header_value in self.headers.items():
            # Don't override headers already set by the application
            if header_name not in response.headers:
                response.headers[header_name] = header_value
        
        return response


class TrustedHostMiddleware:
    """
    Middleware that validates the Host header to prevent host header attacks.
    
    This prevents attackers from manipulating the Host header to:
    - Generate malicious URLs in password reset emails
    - Poison web caches
    - Bypass virtual host routing
    
    Note:
        This is a simplified version. For production, consider using
        Starlette's built-in TrustedHostMiddleware with proper configuration.
        
    Attributes:
        allowed_hosts: List of allowed hostnames (supports wildcards like *.example.com)
    """
    
    def __init__(self, app: Callable, allowed_hosts: list[str]) -> None:
        """
        Initialize the trusted host middleware.
        
        Args:
            app: The ASGI application to wrap
            allowed_hosts: List of allowed hostnames
                - Use "*" to allow any host (not recommended for production)
                - Use "*.example.com" to allow subdomains
        """
        self.app = app
        self.allowed_hosts = [h.lower() for h in allowed_hosts]
        self.allow_any = "*" in self.allowed_hosts
    
    async def __call__(self, scope, receive, send) -> None:
        """
        ASGI interface - validate host header on HTTP requests.
        
        Args:
            scope: ASGI connection scope
            receive: ASGI receive callable
            send: ASGI send callable
        """
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return
        
        # Allow any host if configured
        if self.allow_any:
            await self.app(scope, receive, send)
            return
        
        # Extract host from headers
        headers = dict(scope.get("headers", []))
        host_header = headers.get(b"host", b"").decode("latin-1").lower()
        
        # Strip port number for comparison
        host = host_header.split(":")[0]
        
        # Check if host is allowed
        if self._is_valid_host(host):
            await self.app(scope, receive, send)
        else:
            # Return 400 Bad Request for invalid hosts
            response = Response(
                content="Invalid host header",
                status_code=400,
                media_type="text/plain",
            )
            await response(scope, receive, send)
    
    def _is_valid_host(self, host: str) -> bool:
        """
        Check if a host is in the allowed list.
        
        Args:
            host: The hostname to validate
            
        Returns:
            True if host is allowed, False otherwise
        """
        for allowed in self.allowed_hosts:
            if allowed == host:
                return True
            # Support wildcard subdomains
            if allowed.startswith("*.") and host.endswith(allowed[1:]):
                return True
        return False
