# =============================================================================
# Database Configuration and Session Management
# =============================================================================
# This module sets up SQLAlchemy async engine, session factory, and base model.
# It provides utilities for database connection management.
# =============================================================================

from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.config import settings


# =============================================================================
# SQLAlchemy Base Model
# =============================================================================
class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.
    
    All database models should inherit from this class.
    It provides the foundation for table mapping and metadata.
    """
    pass


# =============================================================================
# Async Engine Configuration
# =============================================================================
# Global engine instance - initialized on startup
_engine: Optional[AsyncEngine] = None

# Session factory - initialized on startup
_async_session_factory: Optional[async_sessionmaker] = None


async def init_db() -> None:
    """
    Initialize the database engine and session factory.
    
    This function should be called once during application startup.
    It creates the async engine with connection pooling configured
    for optimal performance.
    """
    global _engine, _async_session_factory
    
    # Determine engine options based on database type
    # SQLite doesn't support connection pooling the same way PostgreSQL does
    is_sqlite = "sqlite" in settings.DATABASE_URL
    
    if is_sqlite:
        # SQLite configuration - simpler, no pooling needed
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,  # Log SQL queries in debug mode
            connect_args={"check_same_thread": False},  # Required for SQLite
        )
    else:
        # PostgreSQL configuration - with connection pooling
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,  # Log SQL queries in debug mode
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=3600,   # Recycle connections after 1 hour
        )
    
    # Create session factory for creating database sessions
    _async_session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,  # Don't expire objects after commit
        autocommit=False,
        autoflush=False,
    )
    



async def close_db() -> None:
    """
    Close the database engine and all connections.
    
    This function should be called during application shutdown
    to ensure all connections are properly closed.
    """
    global _engine, _async_session_factory
    
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _async_session_factory = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.
    
    Usage in FastAPI routes:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    
    The session is automatically closed after the request completes.
    
    Yields:
        AsyncSession: SQLAlchemy async session
    
    Raises:
        RuntimeError: If database is not initialized
    """
    if _async_session_factory is None:
        raise RuntimeError(
            "Database not initialized. Call init_db() first."
        )
    
    async with _async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_engine() -> AsyncEngine:
    """
    Get the database engine instance.
    
    Useful for raw SQL operations or bulk operations.
    
    Returns:
        AsyncEngine: SQLAlchemy async engine
    
    Raises:
        RuntimeError: If database is not initialized
    """
    if _engine is None:
        raise RuntimeError(
            "Database not initialized. Call init_db() first."
        )
    return _engine


# =============================================================================
# Test Database Configuration
# =============================================================================
async def create_test_engine() -> AsyncEngine:
    """
    Create a test database engine with NullPool.
    
    NullPool is used for testing to ensure each test gets a fresh connection.
    This prevents connection state from leaking between tests.
    
    Returns:
        AsyncEngine: Test database engine
    """
    return create_async_engine(
        settings.DATABASE_URL.replace("brand_analytics", "brand_analytics_test"),
        echo=True,
        poolclass=NullPool,
    )

