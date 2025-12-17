# =============================================================================
# Analysis Request/Response Models
# =============================================================================
# Pydantic models for API request validation and response serialization.
# These models define the contract between frontend and backend.
# =============================================================================

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, field_validator


class AnalysisStatus(str, Enum):
    """
    Enum representing the status of an analysis job.
    
    Statuses:
        pending: Analysis queued, waiting to start
        processing: Analysis is actively running
        completed: Analysis finished successfully
        failed: Analysis encountered an error
    """
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ModuleStatus(str, Enum):
    """
    Enum representing the status of an individual analysis module.
    
    Statuses:
        pending: Module hasn't started yet
        running: Module is currently executing
        completed: Module finished successfully
        failed: Module encountered an error
        skipped: Module was skipped (e.g., no social media found)
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class AnalysisProgress(BaseModel):
    """
    Progress tracking for each analysis module.
    
    Each field represents the status of one analysis module.
    This is used for real-time progress updates to the frontend.
    
    Attributes:
        seo: SEO Performance analysis status
        social_media: Social Media Presence analysis status
        brand_messaging: Brand Messaging & Archetype analysis status
        website_ux: Website UX & Conversion analysis status
        ai_discoverability: AI Discoverability analysis status
        content: Content & Posts analysis status
        team_presence: Team Presence analysis status
        channel_fit: Channel Fit Scoring status
        scorecard: Overall Scorecard generation status
    """
    seo: str = "pending"
    social_media: str = "pending"
    brand_messaging: str = "pending"
    website_ux: str = "pending"
    ai_discoverability: str = "pending"
    content: str = "pending"
    team_presence: str = "pending"
    channel_fit: str = "pending"
    scorecard: str = "pending"
    
    class Config:
        # Allow extra fields for flexibility
        extra = "allow"


class AnalysisRequest(BaseModel):
    """
    Request model for starting a new brand analysis.
    
    The only required field is the URL. All other fields are optional
    but can improve the accuracy of the analysis.
    
    Attributes:
        url: Website URL to analyze (required)
        description: Brief description of the business/product
        industry: Industry category (helps with channel fit scoring)
        email: Email to send the completed report to
    
    Example:
        {
            "url": "https://example.com",
            "description": "A DeFi platform for lending and borrowing",
            "industry": "crypto",
            "email": "founder@example.com"
        }
    """
    url: HttpUrl = Field(
        ...,
        description="Website URL to analyze",
        examples=["https://example.com", "https://www.company.io"]
    )
    
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Brief description of the business or product",
        examples=["A DeFi lending protocol for institutional investors"]
    )
    
    industry: Optional[str] = Field(
        None,
        max_length=100,
        description="Industry or category (e.g., 'crypto', 'fintech', 'saas')",
        examples=["crypto", "fintech", "saas", "ecommerce"]
    )
    
    email: Optional[str] = Field(
        None,
        max_length=255,
        description="Email address to send the report to",
        examples=["founder@example.com"]
    )
    
    @field_validator("url", mode="before")
    @classmethod
    def normalize_url(cls, v: str) -> str:
        """
        Normalize the URL by ensuring it has a protocol.
        
        Adds https:// if no protocol is specified.
        """
        if isinstance(v, str):
            v = v.strip()
            if not v.startswith(("http://", "https://")):
                v = f"https://{v}"
        return v
    
    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """
        Basic email validation.
        """
        if v is None:
            return v
        v = v.strip().lower()
        if "@" not in v or "." not in v:
            raise ValueError("Invalid email address")
        return v


class AnalysisResponse(BaseModel):
    """
    Response model for analysis status and results.
    
    This model is used for:
    - Initial response after starting an analysis
    - Status/progress polling responses
    - Final completed analysis response
    
    Attributes:
        id: Unique identifier for the analysis
        url: The URL being analyzed
        status: Current status of the analysis
        progress: Progress of each analysis module
        scores: Individual module scores (when completed)
        overall_score: Weighted overall score (when completed)
        created_at: When the analysis was started
        completed_at: When the analysis finished (if applicable)
        processing_time_seconds: Total processing time (if completed)
        pdf_url: URL to download the PDF report (if completed)
        message: Human-readable status message
    
    Example (in progress):
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "url": "https://example.com",
            "status": "processing",
            "progress": {
                "seo": "completed",
                "social_media": "running",
                "brand_messaging": "pending",
                ...
            },
            "created_at": "2024-01-15T10:30:00Z",
            "message": "Analysis in progress..."
        }
    
    Example (completed):
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "url": "https://example.com",
            "status": "completed",
            "overall_score": 75.5,
            "scores": {
                "seo": 80,
                "social_media": 65,
                ...
            },
            "created_at": "2024-01-15T10:30:00Z",
            "completed_at": "2024-01-15T10:32:15Z",
            "processing_time_seconds": 135.2,
            "pdf_url": "https://storage.example.com/reports/xyz.pdf",
            "message": "Analysis completed successfully"
        }
    """
    id: UUID = Field(
        ...,
        description="Unique identifier for the analysis"
    )
    
    url: str = Field(
        ...,
        description="The URL being analyzed"
    )
    
    status: AnalysisStatus = Field(
        ...,
        description="Current status of the analysis"
    )
    
    progress: Optional[AnalysisProgress] = Field(
        None,
        description="Progress of each analysis module"
    )
    
    scores: Optional[Dict[str, float]] = Field(
        None,
        description="Individual scores for each module (0-100)"
    )
    
    overall_score: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Weighted overall brand score (0-100)"
    )
    
    created_at: datetime = Field(
        ...,
        description="When the analysis was started"
    )
    
    completed_at: Optional[datetime] = Field(
        None,
        description="When the analysis finished"
    )
    
    processing_time_seconds: Optional[float] = Field(
        None,
        description="Total time taken to complete the analysis"
    )
    
    pdf_url: Optional[str] = Field(
        None,
        description="URL to download the PDF report"
    )
    
    message: Optional[str] = Field(
        None,
        description="Human-readable status message"
    )
    
    class Config:
        # Use enum values in JSON serialization
        use_enum_values = True
        # Include example in OpenAPI schema
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "url": "https://example.com",
                "status": "processing",
                "progress": {
                    "seo": "completed",
                    "social_media": "running",
                    "brand_messaging": "pending",
                    "website_ux": "pending",
                    "ai_discoverability": "pending",
                    "content": "pending",
                    "team_presence": "pending",
                    "channel_fit": "pending",
                    "scorecard": "pending"
                },
                "created_at": "2024-01-15T10:30:00Z",
                "message": "Analysis in progress..."
            }
        }


class AnalysisError(BaseModel):
    """
    Model for analysis error responses.
    
    Used when an analysis fails to provide structured error information.
    
    Attributes:
        id: Analysis ID
        status: Always 'failed'
        error_code: Machine-readable error code
        error_message: Human-readable error description
        failed_at: When the failure occurred
        failed_module: Which module failed (if applicable)
    """
    id: UUID
    status: AnalysisStatus = AnalysisStatus.FAILED
    error_code: str = Field(
        ...,
        description="Machine-readable error code"
    )
    error_message: str = Field(
        ...,
        description="Human-readable error description"
    )
    failed_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the failure occurred"
    )
    failed_module: Optional[str] = Field(
        None,
        description="Which analysis module failed"
    )

