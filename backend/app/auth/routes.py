from datetime import datetime, timedelta, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.db_models import UserRecord, APIKeyRecord, UserRoleEnum
from app.auth.models import (
    User,
    UserCreate,
    APIKey,
    APIKeyCreate,
    APIKeyWithSecret,
)
from app.auth.jwt import hash_password, generate_api_key
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Register a new user account."""
    existing = await db.execute(
        select(UserRecord).where(UserRecord.email == user_data.email)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = UserRecord(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role=UserRoleEnum.USER,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return User(
        id=user.id,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        api_keys=[],
    )


@router.post(
    "/api-keys", response_model=APIKeyWithSecret, status_code=status.HTTP_201_CREATED
)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: UserRecord = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIKeyWithSecret:
    """
    Create a new API key.

    IMPORTANT: The full key is only shown once. Store it securely.
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to create API keys",
        )

    full_key, key_prefix, hashed_key = generate_api_key()

    expires_at = None
    if key_data.expires_days:
        expires_at = datetime.now(timezone.utc) + timedelta(days=key_data.expires_days)

    api_key = APIKeyRecord(
        user_id=current_user.id,
        name=key_data.name,
        key_prefix=key_prefix,
        hashed_key=hashed_key,
        expires_at=expires_at,
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)

    return APIKeyWithSecret(
        id=api_key.id,
        name=api_key.name,
        key_prefix=api_key.key_prefix,
        key=full_key,
        created_at=api_key.created_at,
        last_used_at=api_key.last_used_at,
        expires_at=api_key.expires_at,
        is_active=api_key.is_active,
    )


@router.get("/api-keys", response_model=List[APIKey])
async def list_api_keys(
    current_user: UserRecord = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[APIKey]:
    """List all API keys for the current user."""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    result = await db.execute(
        select(APIKeyRecord).where(APIKeyRecord.user_id == current_user.id)
    )
    keys = result.scalars().all()

    return [
        APIKey(
            id=k.id,
            name=k.name,
            key_prefix=k.key_prefix,
            created_at=k.created_at,
            last_used_at=k.last_used_at,
            expires_at=k.expires_at,
            is_active=k.is_active,
        )
        for k in keys
    ]


@router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: UUID,
    current_user: UserRecord = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Revoke (deactivate) an API key."""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    result = await db.execute(
        select(APIKeyRecord).where(
            APIKeyRecord.id == key_id,
            APIKeyRecord.user_id == current_user.id,
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    api_key.is_active = False
    await db.commit()


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: UserRecord = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current user information."""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    result = await db.execute(
        select(APIKeyRecord).where(APIKeyRecord.user_id == current_user.id)
    )
    keys = result.scalars().all()

    return User(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        api_keys=[
            APIKey(
                id=k.id,
                name=k.name,
                key_prefix=k.key_prefix,
                created_at=k.created_at,
                last_used_at=k.last_used_at,
                expires_at=k.expires_at,
                is_active=k.is_active,
            )
            for k in keys
        ],
    )


@router.post("/bootstrap", response_model=APIKeyWithSecret, include_in_schema=False)
async def bootstrap_admin(
    db: AsyncSession = Depends(get_db),
) -> APIKeyWithSecret:
    """
    Bootstrap first admin user and API key. Only works if no users exist.
    This endpoint is hidden from OpenAPI docs for security.
    """
    existing = await db.execute(select(UserRecord).limit(1))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bootstrap only available when no users exist",
        )

    admin = UserRecord(
        email="admin@brandanalytics.local",
        hashed_password=hash_password("change-me-immediately"),
        role=UserRoleEnum.ADMIN,
    )
    db.add(admin)
    await db.flush()

    full_key, key_prefix, hashed_key = generate_api_key()
    api_key = APIKeyRecord(
        user_id=admin.id,
        name="Bootstrap Admin Key",
        key_prefix=key_prefix,
        hashed_key=hashed_key,
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)

    return APIKeyWithSecret(
        id=api_key.id,
        name=api_key.name,
        key_prefix=api_key.key_prefix,
        key=full_key,
        created_at=api_key.created_at,
        last_used_at=None,
        expires_at=None,
        is_active=True,
    )
