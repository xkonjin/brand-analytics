# =============================================================================
# Authentication Module
# =============================================================================
# This module provides API key-based authentication for the Brand Analytics API.
#
# Components:
# - models.py: Pydantic models for User and APIKey
# - jwt.py: JWT token utilities for session management
# - dependencies.py: FastAPI dependencies for route protection
# - service.py: Business logic for key creation/validation
#
# Usage:
#     from app.auth.dependencies import require_api_key, get_optional_auth
#     
#     @router.post("/analyze")
#     async def analyze(api_key: APIKey = Depends(require_api_key)):
#         ...
# =============================================================================

from app.auth.models import User, APIKey, APIKeyCreate, TokenData
from app.auth.dependencies import (
    require_api_key,
    get_optional_auth,
    get_current_user,
)

__all__ = [
    "User",
    "APIKey",
    "APIKeyCreate", 
    "TokenData",
    "require_api_key",
    "get_optional_auth",
    "get_current_user",
]
