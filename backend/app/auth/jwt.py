# =============================================================================
# JWT Token Utilities
# =============================================================================
# Provides utilities for creating and validating JWT tokens.
# Used for session-based authentication alongside API keys.
# =============================================================================

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from uuid import UUID
import secrets

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings


# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hash.
    
    Args:
        plain_password: The password to verify
        hashed_password: The stored bcrypt hash
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: The plain text password
        
    Returns:
        str: The bcrypt hash
    """
    return pwd_context.hash(password)


def generate_api_key() -> tuple[str, str, str]:
    """
    Generate a new API key.
    
    Returns:
        tuple: (full_key, key_prefix, hashed_key)
            - full_key: The complete API key to give to the user (shown once)
            - key_prefix: First 8 chars for identification
            - hashed_key: Hashed version to store in database
    
    The key format is: ba_xxxxxxxxxxxxxxxxxxxxxxxxxxxx (32 random chars)
    """
    # Generate 32 random characters
    random_part = secrets.token_urlsafe(24)  # ~32 chars
    full_key = f"ba_{random_part}"
    
    # Extract prefix for display
    key_prefix = full_key[:11]  # "ba_" + first 8 chars
    
    # Hash the full key for storage
    hashed_key = pwd_context.hash(full_key)
    
    return full_key, key_prefix, hashed_key


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """
    Verify an API key against its stored hash.
    
    Args:
        plain_key: The API key provided by the user
        hashed_key: The stored bcrypt hash
        
    Returns:
        bool: True if key is valid, False otherwise
    """
    return pwd_context.verify(plain_key, hashed_key)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Payload data to encode in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT access token.
    
    Args:
        token: The JWT token to decode
        
    Returns:
        Optional[Dict]: Decoded token payload, or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        return None


def create_api_key_token(api_key_id: UUID, user_id: UUID) -> str:
    """
    Create a short-lived token from an API key authentication.
    
    This allows API key auth to work with the same token-based
    middleware as JWT auth.
    
    Args:
        api_key_id: The authenticated API key's ID
        user_id: The owner's user ID
        
    Returns:
        str: Short-lived JWT token
    """
    return create_access_token(
        data={
            "sub": str(user_id),
            "api_key_id": str(api_key_id),
            "type": "api_key",
        },
        expires_delta=timedelta(minutes=5),  # Short-lived for API key auth
    )
