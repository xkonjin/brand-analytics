# =============================================================================
# Models Package
# =============================================================================
# This package contains all data models for the Brand Analytics Tool:
# - Pydantic models for API request/response validation
# - SQLAlchemy models for database persistence
# =============================================================================

from app.models.analysis import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisStatus,
    AnalysisProgress,
)
from app.models.report import (
    FullReport,
    SEOReport,
    SocialMediaReport,
    BrandMessagingReport,
    UXReport,
    AIDiscoverabilityReport,
    ContentReport,
    TeamPresenceReport,
    ChannelFitReport,
    ScoreCard,
    Recommendation,
)

__all__ = [
    # Analysis models
    "AnalysisRequest",
    "AnalysisResponse",
    "AnalysisStatus",
    "AnalysisProgress",
    # Report models
    "FullReport",
    "SEOReport",
    "SocialMediaReport",
    "BrandMessagingReport",
    "UXReport",
    "AIDiscoverabilityReport",
    "ContentReport",
    "TeamPresenceReport",
    "ChannelFitReport",
    "ScoreCard",
    "Recommendation",
]

