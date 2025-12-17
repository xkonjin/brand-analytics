# =============================================================================
# Report Data Models
# =============================================================================
# Pydantic models for the complete brand analysis report structure.
# These models define the format of analysis results and recommendations.
# =============================================================================

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field


# =============================================================================
# Common Types
# =============================================================================

class SeverityLevel(str, Enum):
    """Severity level for issues and recommendations."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Recommendation(BaseModel):
    """
    A single actionable recommendation from the analysis.
    
    Attributes:
        title: Short title for the recommendation
        description: Detailed explanation of what to do and why
        priority: How urgent/important this recommendation is
        category: Which analysis module this relates to
        impact: Expected impact if implemented (high/medium/low)
        effort: Estimated effort to implement (high/medium/low)
    """
    title: str = Field(..., max_length=200)
    description: str
    priority: SeverityLevel = SeverityLevel.MEDIUM
    category: str = Field(..., description="Module category (seo, social, etc.)")
    impact: str = Field("medium", pattern="^(high|medium|low)$")
    effort: str = Field("medium", pattern="^(high|medium|low)$")


class Finding(BaseModel):
    """
    A single finding/observation from the analysis.
    
    Attributes:
        title: Short description of the finding
        detail: Detailed explanation
        severity: How significant this finding is
        data: Optional associated data (metrics, values, etc.)
    """
    title: str
    detail: str
    severity: SeverityLevel = SeverityLevel.INFO
    data: Optional[Dict[str, Any]] = None


# =============================================================================
# SEO Report
# =============================================================================

class CoreWebVitals(BaseModel):
    """Core Web Vitals metrics from PageSpeed Insights."""
    lcp: Optional[float] = Field(None, description="Largest Contentful Paint (seconds)")
    fid: Optional[float] = Field(None, description="First Input Delay (milliseconds)")
    cls: Optional[float] = Field(None, description="Cumulative Layout Shift (score)")
    fcp: Optional[float] = Field(None, description="First Contentful Paint (seconds)")
    ttfb: Optional[float] = Field(None, description="Time to First Byte (seconds)")


class MetaTagAnalysis(BaseModel):
    """Analysis of page meta tags."""
    title: Optional[str] = None
    title_length: Optional[int] = None
    title_quality: Optional[str] = None  # good, too_short, too_long, missing
    description: Optional[str] = None
    description_length: Optional[int] = None
    description_quality: Optional[str] = None
    has_og_tags: bool = False
    has_twitter_cards: bool = False
    has_canonical: bool = False


class SEOReport(BaseModel):
    """
    Complete SEO Performance Analysis report section.
    
    Analyzes technical SEO health including page speed, meta tags,
    indexing status, and search visibility.
    """
    score: float = Field(..., ge=0, le=100)
    
    # Performance Metrics
    performance_score: Optional[float] = Field(None, ge=0, le=100)
    accessibility_score: Optional[float] = Field(None, ge=0, le=100)
    best_practices_score: Optional[float] = Field(None, ge=0, le=100)
    seo_score: Optional[float] = Field(None, ge=0, le=100)
    
    # Core Web Vitals
    core_web_vitals: Optional[CoreWebVitals] = None
    
    # Page Load Time
    page_load_time: Optional[float] = Field(None, description="Page load time in seconds")
    mobile_friendly: Optional[bool] = None
    
    # Meta Tag Analysis
    meta_tags: Optional[MetaTagAnalysis] = None
    
    # Indexing Status
    pages_indexed: Optional[int] = Field(None, description="Number of pages indexed by Google")
    ranks_for_brand_name: Optional[bool] = None
    has_knowledge_panel: Optional[bool] = None
    
    # Schema.org
    has_schema_markup: bool = False
    schema_types_found: List[str] = Field(default_factory=list)
    
    # Findings and Recommendations
    findings: List[Finding] = Field(default_factory=list)
    recommendations: List[Recommendation] = Field(default_factory=list)


# =============================================================================
# Social Media Report
# =============================================================================

class SocialPlatformMetrics(BaseModel):
    """Metrics for a single social media platform."""
    platform: str  # twitter, linkedin, instagram, tiktok, etc.
    url: Optional[str] = None
    followers: Optional[int] = None
    following: Optional[int] = None
    posts_count: Optional[int] = None
    posts_last_30_days: Optional[int] = None
    engagement_rate: Optional[float] = Field(None, description="Engagement rate as percentage")
    avg_likes: Optional[float] = None
    avg_comments: Optional[float] = None
    avg_shares: Optional[float] = None
    last_post_date: Optional[datetime] = None
    is_verified: bool = False
    profile_bio: Optional[str] = None


class SocialMediaReport(BaseModel):
    """
    Complete Social Media Presence & Engagement Analysis report section.
    
    Analyzes presence across major platforms, engagement metrics,
    and consistency of activity.
    """
    score: float = Field(..., ge=0, le=100)
    
    # Platform-specific metrics
    platforms: List[SocialPlatformMetrics] = Field(default_factory=list)
    
    # Summary metrics
    total_followers: int = 0
    platforms_active: int = 0
    platforms_dormant: int = 0  # No posts in 30+ days
    platforms_missing: List[str] = Field(default_factory=list)
    
    # Engagement Analysis
    overall_engagement_rate: Optional[float] = None
    engagement_trend: Optional[str] = None  # improving, stable, declining
    
    # Posting Consistency
    average_posts_per_week: Optional[float] = None
    posting_consistency: Optional[str] = None  # consistent, irregular, dormant
    
    # Community Channels
    has_discord: bool = False
    discord_members: Optional[int] = None
    discord_url: Optional[str] = None
    has_telegram: bool = False
    telegram_members: Optional[int] = None
    telegram_url: Optional[str] = None
    
    findings: List[Finding] = Field(default_factory=list)
    recommendations: List[Recommendation] = Field(default_factory=list)


# =============================================================================
# Brand Messaging Report
# =============================================================================

class BrandArchetype(BaseModel):
    """Brand archetype identification result."""
    primary: str = Field(..., description="Primary brand archetype")
    secondary: Optional[str] = Field(None, description="Secondary archetype if applicable")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    description: str = Field(..., description="Description of the archetype")
    example_brands: List[str] = Field(default_factory=list)


class BrandMessagingReport(BaseModel):
    """
    Complete Brand Messaging & Archetype Analysis report section.
    
    Analyzes brand voice, messaging clarity, archetype identification,
    and copy quality.
    """
    score: float = Field(..., ge=0, le=100)
    
    # Brand Archetype
    archetype: Optional[BrandArchetype] = None
    
    # Value Proposition
    value_proposition: Optional[str] = None
    value_proposition_clarity: Optional[float] = Field(None, ge=0, le=10)
    tagline: Optional[str] = None
    
    # Tone & Voice
    tone_keywords: List[str] = Field(default_factory=list)
    tone_description: Optional[str] = None
    tone_consistency: Optional[float] = Field(None, ge=0, le=10)
    
    # Readability
    readability_score: Optional[float] = None  # Flesch Reading Ease
    reading_grade_level: Optional[float] = None  # Flesch-Kincaid Grade
    is_jargon_heavy: bool = False
    jargon_examples: List[str] = Field(default_factory=list)
    
    # Key Messages
    key_themes: List[str] = Field(default_factory=list)
    emotional_hooks: List[str] = Field(default_factory=list)
    
    findings: List[Finding] = Field(default_factory=list)
    recommendations: List[Recommendation] = Field(default_factory=list)


# =============================================================================
# Website UX Report
# =============================================================================

class CTAAnalysis(BaseModel):
    """Call-to-action analysis."""
    cta_text: Optional[str] = None
    is_visible_above_fold: bool = False
    has_contrast: bool = False
    cta_count: int = 0
    primary_cta_present: bool = False


class UXReport(BaseModel):
    """
    Complete Website UX & Conversion Optimization Assessment.
    
    Analyzes user experience elements, CTAs, navigation,
    trust signals, and conversion readiness.
    """
    score: float = Field(..., ge=0, le=100)
    
    # First Impression
    first_impression_clarity: Optional[float] = Field(None, ge=0, le=10)
    answers_what: bool = False  # Does it say what the product is?
    answers_who: bool = False   # Does it say who it's for?
    answers_why: bool = False   # Does it say why to choose them?
    
    # CTA Analysis
    cta_analysis: Optional[CTAAnalysis] = None
    
    # Navigation
    menu_items_count: Optional[int] = None
    has_clear_navigation: bool = False
    has_search: bool = False
    clicks_to_pricing: Optional[int] = None
    clicks_to_contact: Optional[int] = None
    
    # Trust Signals
    has_testimonials: bool = False
    has_client_logos: bool = False
    has_case_studies: bool = False
    has_security_badges: bool = False
    has_social_proof_numbers: bool = False  # e.g., "10,000+ users"
    trust_signals_count: int = 0
    
    # Mobile & Accessibility
    mobile_responsive: bool = False
    accessibility_issues: List[str] = Field(default_factory=list)
    
    # Legal/Compliance
    has_privacy_policy: bool = False
    has_terms_of_service: bool = False
    
    findings: List[Finding] = Field(default_factory=list)
    recommendations: List[Recommendation] = Field(default_factory=list)


# =============================================================================
# AI Discoverability Report
# =============================================================================

class AIDiscoverabilityReport(BaseModel):
    """
    Complete AI Discoverability Analysis report section.
    
    Evaluates how well the brand can be discovered by AI assistants
    like ChatGPT, Bing Chat, and Perplexity.
    """
    score: float = Field(..., ge=0, le=100)
    
    # Wikipedia & Knowledge Graph
    has_wikipedia_page: bool = False
    wikipedia_url: Optional[str] = None
    wikipedia_quality: Optional[str] = None  # stub, good, comprehensive
    has_knowledge_panel: bool = False
    
    # Search Presence
    appears_in_top_10: bool = False
    brand_search_position: Optional[int] = None
    
    # Authoritative Mentions
    mentioned_in_major_publications: bool = False
    publication_mentions: List[str] = Field(default_factory=list)
    
    # Structured Data
    has_faq_schema: bool = False
    has_organization_schema: bool = False
    has_product_schema: bool = False
    schema_types: List[str] = Field(default_factory=list)
    
    # Content Depth
    blog_post_count: Optional[int] = None
    has_documentation: bool = False
    has_help_center: bool = False
    content_depth_score: Optional[float] = Field(None, ge=0, le=10)
    
    # AI Readiness Assessment
    ai_readiness_level: str = Field("low", pattern="^(high|medium|low)$")
    
    findings: List[Finding] = Field(default_factory=list)
    recommendations: List[Recommendation] = Field(default_factory=list)


# =============================================================================
# Content Analysis Report
# =============================================================================

class PostAnalysis(BaseModel):
    """Analysis of a single social media post."""
    platform: str
    date: Optional[datetime] = None
    content_preview: Optional[str] = None
    likes: int = 0
    comments: int = 0
    shares: int = 0
    content_type: str = "text"  # text, image, video, link
    sentiment: Optional[str] = None  # positive, neutral, negative


class ContentReport(BaseModel):
    """
    Complete Recent Content & Social Posts Analysis report section.
    
    Analyzes the content strategy based on recent posts across platforms.
    """
    score: float = Field(..., ge=0, le=100)
    
    # Recent Posts
    recent_posts: List[PostAnalysis] = Field(default_factory=list)
    
    # Content Mix
    content_mix: Dict[str, float] = Field(
        default_factory=dict,
        description="Percentage breakdown: promotional, educational, community, etc."
    )
    
    # Sentiment Analysis
    overall_sentiment: Optional[str] = None  # positive, neutral, negative
    sentiment_breakdown: Dict[str, float] = Field(default_factory=dict)
    
    # Engagement Patterns
    best_performing_post: Optional[PostAnalysis] = None
    worst_performing_post: Optional[PostAnalysis] = None
    avg_engagement_per_post: Optional[float] = None
    
    # Content Format
    uses_images: bool = False
    uses_videos: bool = False
    uses_threads: bool = False
    multimedia_percentage: Optional[float] = None
    
    # Topics & Themes
    common_topics: List[str] = Field(default_factory=list)
    hashtags_used: List[str] = Field(default_factory=list)
    
    findings: List[Finding] = Field(default_factory=list)
    recommendations: List[Recommendation] = Field(default_factory=list)


# =============================================================================
# Team Presence Report
# =============================================================================

class TeamMember(BaseModel):
    """Information about a team member."""
    name: str
    role: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    twitter_followers: Optional[int] = None
    notable_background: Optional[str] = None  # e.g., "ex-Google"


class TeamPresenceReport(BaseModel):
    """
    Complete Team & Community Presence Evaluation report section.
    
    Analyzes the visibility and credibility of the team behind the brand.
    """
    score: float = Field(..., ge=0, le=100)
    
    # Team Information
    team_size_estimate: Optional[str] = None  # "1-10", "11-50", etc.
    team_members: List[TeamMember] = Field(default_factory=list)
    has_team_page: bool = False
    team_page_url: Optional[str] = None
    
    # LinkedIn Company Page
    linkedin_followers: Optional[int] = None
    linkedin_url: Optional[str] = None
    linkedin_active: bool = False
    
    # Founder Visibility
    founders_identified: int = 0
    founder_twitter_presence: bool = False
    founder_combined_following: Optional[int] = None
    
    # Credibility Signals
    has_notable_background: bool = False  # ex-FAANG, known companies
    has_advisors_listed: bool = False
    has_investors_listed: bool = False
    
    # Team Identity
    uses_real_identities: bool = True  # vs pseudonymous
    photos_on_website: bool = False
    
    findings: List[Finding] = Field(default_factory=list)
    recommendations: List[Recommendation] = Field(default_factory=list)


# =============================================================================
# Channel Fit Report
# =============================================================================

class ChannelScore(BaseModel):
    """Suitability score for a single marketing channel."""
    channel: str
    score: float = Field(..., ge=0, le=10)
    suitability: str  # high, medium, low
    rationale: str
    current_presence: bool = False
    recommendation: Optional[str] = None


class ChannelFitReport(BaseModel):
    """
    Complete Channel & Market Fit Scoring report section.
    
    Assesses which marketing channels are best suited for the brand.
    """
    score: float = Field(..., ge=0, le=100)
    
    # Channel Scores
    channels: List[ChannelScore] = Field(default_factory=list)
    
    # Top Recommendations
    top_channels: List[str] = Field(default_factory=list)
    underutilized_channels: List[str] = Field(default_factory=list)
    low_priority_channels: List[str] = Field(default_factory=list)
    
    # Analysis Inputs
    product_type: Optional[str] = None  # B2B, B2C, Developer, etc.
    target_audience: Optional[str] = None
    industry: Optional[str] = None
    
    findings: List[Finding] = Field(default_factory=list)
    recommendations: List[Recommendation] = Field(default_factory=list)


# =============================================================================
# Overall Scorecard
# =============================================================================

class ScoreCard(BaseModel):
    """
    Overall Scorecard & Recommendations Summary.
    
    Aggregates all module scores and provides a final assessment.
    """
    overall_score: float = Field(..., ge=0, le=100)
    
    # Individual Module Scores
    scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Scores for each module (0-100)"
    )
    
    # Score Interpretation
    grade: str = Field(..., description="Letter grade: A, B, C, D, F")
    summary: str = Field(..., description="One-paragraph overall assessment")
    
    # Key Insights
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    
    # Top Recommendations (prioritized from all modules)
    top_recommendations: List[Recommendation] = Field(default_factory=list)
    
    # Quick Wins (low effort, high impact)
    quick_wins: List[Recommendation] = Field(default_factory=list)


# =============================================================================
# Full Report
# =============================================================================

class FullReport(BaseModel):
    """
    Complete Brand Analysis Report containing all sections.
    
    This is the top-level model that aggregates all analysis modules.
    """
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    url: str
    brand_name: Optional[str] = None
    brand_logo_url: Optional[str] = None
    
    # Analysis Sections
    seo: SEOReport
    social_media: SocialMediaReport
    brand_messaging: BrandMessagingReport
    website_ux: UXReport
    ai_discoverability: AIDiscoverabilityReport
    content: ContentReport
    team_presence: TeamPresenceReport
    channel_fit: ChannelFitReport
    scorecard: ScoreCard
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com",
                "brand_name": "Example Brand",
                "scorecard": {
                    "overall_score": 75,
                    "grade": "B",
                    "summary": "Strong brand with good fundamentals..."
                }
            }
        }

