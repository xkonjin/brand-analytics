# =============================================================================
# Authentication Pydantic Models
# =============================================================================
# Defines the data structures for authentication entities.
# These models are used for API request/response validation.
# =============================================================================

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, field_validator
import re


class UserRole(str, Enum):
    """User role enumeration for access control."""

    USER = "user"
    ADMIN = "admin"


class APIKeyBase(BaseModel):
    """Base model for API key data."""

    name: str = Field(
        ..., min_length=1, max_length=100, description="Friendly name for the API key"
    )


class APIKeyCreate(APIKeyBase):
    """Model for creating a new API key."""

    expires_days: Optional[int] = Field(
        None,
        ge=1,
        le=365,
        description="Number of days until expiration (null = never expires)",
    )


class APIKey(APIKeyBase):
    """
    API Key model returned to users.

    Note: The full key is only shown once at creation time.
    After that, only the prefix is available for identification.
    """

    id: UUID
    key_prefix: str = Field(
        ..., description="First 8 characters of the key for identification"
    )
    created_at: datetime
    last_used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class APIKeyWithSecret(APIKey):
    """
    API Key with the full secret key.

    IMPORTANT: This is only returned once when the key is created.
    The full key should be stored securely by the user.
    """

    key: str = Field(..., description="The full API key (only shown once)")


class UserBase(BaseModel):
    """Base model for user data."""

    email: str = Field(..., min_length=5, max_length=255)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v.lower().strip()


class UserCreate(UserBase):
    """Model for creating a new user."""

    password: str = Field(..., min_length=8, max_length=100)


class User(UserBase):
    """
    User model returned in API responses.

    Attributes:
        id: Unique identifier
        email: User's email address
        role: User's role (user/admin)
        is_active: Whether the user account is active
        created_at: Account creation timestamp
        api_keys: List of user's API keys (without secrets)
    """

    id: UUID
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime
    api_keys: List[APIKey] = Field(default_factory=list)

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    """
    Data extracted from a JWT token.

    Used internally for token validation.
    """

    user_id: Optional[UUID] = None
    api_key_id: Optional[UUID] = None
    scopes: List[str] = Field(default_factory=list)


class AuthResponse(BaseModel):
    """Response model for authentication endpoints."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Token expiration time in seconds")


class RateLimitInfo(BaseModel):
    """Information about rate limit status."""

    limit: int = Field(..., description="Maximum requests per window")
    remaining: int = Field(..., description="Remaining requests in current window")
    reset_at: datetime = Field(..., description="When the rate limit window resets")
