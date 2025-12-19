"""
Module: middleware
Purpose: Security and utility middleware for the FastAPI application.

This module provides middleware components for:
- Security headers (XSS protection, clickjacking prevention, content sniffing)
- Request/response logging (future)
- Rate limiting coordination (future)

Author: Claude Code Assistant
Date Created: 2025-01-19
"""

from app.middleware.security import SecurityHeadersMiddleware

__all__ = ["SecurityHeadersMiddleware"]
