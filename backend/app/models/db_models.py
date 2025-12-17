# =============================================================================
# SQLAlchemy Database Models
# =============================================================================
# This module defines the database schema using SQLAlchemy ORM.
# These models represent persistent storage for analyses and reports.
# =============================================================================

from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Integer,
    Float,
    JSON,
    Enum as SQLEnum,
    Index,
    TypeDecorator,
)
import enum

from app.database import Base
from app.config import settings


# =============================================================================
# Cross-Database UUID Type
# =============================================================================
# SQLite doesn't support UUID natively. This custom type stores UUIDs as
# strings for SQLite and uses native UUID for PostgreSQL.
# =============================================================================
class GUID(TypeDecorator):
    """
    Platform-independent GUID type.
    Uses String(36) for SQLite, stores as UUID string.
    """
    impl = String(36)
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)
        return value
    
    def process_result_value(self, value, dialect):
        if value is not None:
            return uuid.UUID(value)
        return value


class AnalysisStatusEnum(str, enum.Enum):
    """
    Enum representing the status of an analysis job.
    
    States:
        pending: Analysis request received, waiting to start
        processing: Analysis is currently running
        completed: Analysis finished successfully
        failed: Analysis failed due to an error
    """
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Analysis(Base):
    """
    Database model for brand analysis jobs.
    
    This table stores information about each analysis request,
    including the input URL, current status, progress, and results.
    
    Attributes:
        id: Unique identifier for the analysis (UUID)
        url: The website URL being analyzed
        description: Optional business description provided by user
        industry: Optional industry/category for channel fit analysis
        email: Optional email for sending the report
        status: Current status of the analysis job
        progress: JSON object tracking progress of each module
        scores: JSON object containing scores for each module
        report: JSON object containing the full report data
        error_message: Error details if analysis failed
        created_at: Timestamp when analysis was requested
        updated_at: Timestamp of last update
        completed_at: Timestamp when analysis completed
    """
    __tablename__ = "analyses"
    
    # -------------------------------------------------------------------------
    # Primary Key
    # -------------------------------------------------------------------------
    id = Column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for the analysis"
    )
    
    # -------------------------------------------------------------------------
    # Input Fields
    # -------------------------------------------------------------------------
    url = Column(
        String(2048),
        nullable=False,
        index=True,
        comment="Website URL being analyzed"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Optional business description from user"
    )
    
    industry = Column(
        String(255),
        nullable=True,
        comment="Industry category for channel fit analysis"
    )
    
    email = Column(
        String(255),
        nullable=True,
        comment="Email address for report delivery"
    )
    
    # -------------------------------------------------------------------------
    # Status & Progress
    # -------------------------------------------------------------------------
    status = Column(
        SQLEnum(AnalysisStatusEnum),
        default=AnalysisStatusEnum.PENDING,
        nullable=False,
        index=True,
        comment="Current status of the analysis"
    )
    
    progress = Column(
        JSON,
        default=dict,
        nullable=False,
        comment="Progress tracking for each analysis module"
    )
    
    # -------------------------------------------------------------------------
    # Results
    # -------------------------------------------------------------------------
    scores = Column(
        JSON,
        nullable=True,
        comment="Individual scores for each analysis module"
    )
    
    overall_score = Column(
        Float,
        nullable=True,
        comment="Weighted overall brand score (0-100)"
    )
    
    report = Column(
        JSON,
        nullable=True,
        comment="Complete analysis report data"
    )
    
    pdf_url = Column(
        String(2048),
        nullable=True,
        comment="URL to the generated PDF report"
    )
    
    error_message = Column(
        Text,
        nullable=True,
        comment="Error details if analysis failed"
    )
    
    # -------------------------------------------------------------------------
    # Timestamps
    # -------------------------------------------------------------------------
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="When the analysis was requested"
    )
    
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Last update timestamp"
    )
    
    completed_at = Column(
        DateTime,
        nullable=True,
        comment="When the analysis completed"
    )
    
    # -------------------------------------------------------------------------
    # Processing Metadata
    # -------------------------------------------------------------------------
    processing_time_seconds = Column(
        Float,
        nullable=True,
        comment="Total time taken to complete analysis"
    )
    
    # -------------------------------------------------------------------------
    # Indexes for Common Queries
    # -------------------------------------------------------------------------
    __table_args__ = (
        # Index for finding recent analyses
        Index("ix_analyses_created_at", created_at.desc()),
        # Index for finding analyses by status
        Index("ix_analyses_status_created", status, created_at.desc()),
    )
    
    def __repr__(self) -> str:
        return f"<Analysis(id={self.id}, url={self.url}, status={self.status})>"


class AnalysisCache(Base):
    """
    Cache table for storing scraped data and API responses.
    
    This helps reduce API calls and scraping requests for the same
    URL within a configurable time window.
    
    Attributes:
        id: Unique cache entry ID
        cache_key: Unique key combining URL and data type
        url: The URL that was scraped/queried
        data_type: Type of cached data (e.g., 'pagespeed', 'twitter')
        data: The cached JSON data
        expires_at: When this cache entry expires
        created_at: When the cache entry was created
    """
    __tablename__ = "analysis_cache"
    
    id = Column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    cache_key = Column(
        String(512),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique cache key (hash of URL + data type)"
    )
    
    url = Column(
        String(2048),
        nullable=False,
        comment="Source URL for the cached data"
    )
    
    data_type = Column(
        String(50),
        nullable=False,
        comment="Type of cached data"
    )
    
    data = Column(
        JSON,
        nullable=False,
        comment="Cached response data"
    )
    
    expires_at = Column(
        DateTime,
        nullable=False,
        index=True,
        comment="Cache expiration timestamp"
    )
    
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    
    __table_args__ = (
        Index("ix_cache_url_type", url, data_type),
    )
    
    def __repr__(self) -> str:
        return f"<AnalysisCache(key={self.cache_key}, type={self.data_type})>"

