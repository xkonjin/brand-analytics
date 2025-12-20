# =============================================================================
# Report Shape Validation Test Suite
# =============================================================================
# "Golden Report Shape" tests to ensure report structure remains consistent.
# These tests validate that reports contain all required fields and that
# all scores fall within valid ranges.
#
# Run with: pytest tests/test_report_shape.py -v
# =============================================================================

import pytest
from datetime import datetime

from pydantic import ValidationError

from app.models.report import (
    FullReport,
    ScoreCard,
    SEOReport,
    SocialMediaReport,
    BrandMessagingReport,
    UXReport,
    AIDiscoverabilityReport,
    ContentReport,
    TeamPresenceReport,
    ChannelFitReport,
    Finding,
    Recommendation,
    SeverityLevel,
    SocialPlatformMetrics,
    CoreWebVitals,
    MetaTagAnalysis,
    BrandArchetype,
    CTAAnalysis,
    PostAnalysis,
    TeamMember,
    ChannelScore,
)


# =============================================================================
# Fixtures - Sample Valid Data
# =============================================================================


@pytest.fixture
def valid_seo_report() -> SEOReport:
    """Create a valid SEO report for testing."""
    return SEOReport(
        score=75.0,
        performance_score=80.0,
        accessibility_score=85.0,
        best_practices_score=90.0,
        seo_score=78.0,
        core_web_vitals=CoreWebVitals(lcp=2.5, fid=100, cls=0.1, fcp=1.8, ttfb=0.8),
        page_load_time=3.2,
        mobile_friendly=True,
        meta_tags=MetaTagAnalysis(
            title="Test Brand - Innovation Platform",
            title_length=32,
            title_quality="good",
            description="A test description for the brand.",
            description_length=36,
            description_quality="good",
            has_og_tags=True,
            has_twitter_cards=True,
            has_canonical=True,
        ),
        pages_indexed=150,
        ranks_for_brand_name=True,
        has_knowledge_panel=False,
        has_schema_markup=True,
        schema_types_found=["Organization", "WebSite"],
        domain_authority=45.0,
        page_authority=42.0,
        spam_score=2.0,
        linking_domains=120,
        total_backlinks=500,
        findings=[],
        recommendations=[],
    )


@pytest.fixture
def valid_social_report() -> SocialMediaReport:
    """Create a valid social media report for testing."""
    return SocialMediaReport(
        score=68.0,
        platforms=[
            SocialPlatformMetrics(
                platform="twitter",
                url="https://twitter.com/testbrand",
                handle="@testbrand",
                followers=5000,
                following=200,
                posts_last_30_days=15,
                engagement_rate=1.5,
            ),
        ],
        total_followers=5000,
        platforms_active=1,
        platforms_dormant=0,
        platforms_missing=["linkedin", "instagram"],
        overall_engagement_rate=1.5,
        has_discord=False,
        has_telegram=False,
        findings=[],
        recommendations=[],
    )


@pytest.fixture
def valid_brand_report() -> BrandMessagingReport:
    """Create a valid brand messaging report for testing."""
    return BrandMessagingReport(
        score=73.0,
        archetype=BrandArchetype(
            primary="Innovator",
            secondary="Creator",
            confidence=0.85,
            description="Brands that innovate and create new solutions.",
            example_brands=["Apple", "Tesla"],
        ),
        value_proposition="Making innovation accessible to everyone.",
        value_proposition_clarity=8.0,
        tagline="Innovation for All",
        tone_keywords=["professional", "innovative", "accessible"],
        tone_description="Professional and forward-thinking.",
        tone_consistency=7.5,
        readability_score=65.0,
        reading_grade_level=10.0,
        is_jargon_heavy=False,
        key_themes=["innovation", "accessibility", "simplicity"],
        emotional_hooks=["empowerment", "possibility"],
        findings=[],
        recommendations=[],
    )


@pytest.fixture
def valid_ux_report() -> UXReport:
    """Create a valid UX report for testing."""
    return UXReport(
        score=77.0,
        first_impression_clarity=8.0,
        answers_what=True,
        answers_who=True,
        answers_why=False,
        cta_analysis=CTAAnalysis(
            cta_text="Get Started",
            is_visible_above_fold=True,
            has_contrast=True,
            cta_count=3,
            primary_cta_present=True,
        ),
        menu_items_count=6,
        has_clear_navigation=True,
        has_search=False,
        clicks_to_pricing=2,
        clicks_to_contact=1,
        has_testimonials=True,
        has_client_logos=True,
        has_case_studies=False,
        has_security_badges=False,
        has_social_proof_numbers=True,
        trust_signals_count=3,
        mobile_responsive=True,
        has_privacy_policy=True,
        has_terms_of_service=True,
        findings=[],
        recommendations=[],
    )


@pytest.fixture
def valid_ai_report() -> AIDiscoverabilityReport:
    """Create a valid AI discoverability report for testing."""
    return AIDiscoverabilityReport(
        score=45.0,
        has_wikipedia_page=False,
        has_knowledge_panel=False,
        appears_in_top_10=True,
        brand_search_position=3,
        mentioned_in_major_publications=False,
        has_faq_schema=True,
        has_organization_schema=True,
        has_product_schema=False,
        schema_types=["FAQPage", "Organization"],
        blog_post_count=25,
        has_documentation=True,
        has_help_center=False,
        content_depth_score=6.0,
        ai_readiness_level="medium",
        findings=[],
        recommendations=[],
    )


@pytest.fixture
def valid_content_report() -> ContentReport:
    """Create a valid content report for testing."""
    return ContentReport(
        score=82.0,
        recent_posts=[
            PostAnalysis(
                platform="twitter",
                content_preview="Excited to announce our new feature!",
                likes=150,
                comments=25,
                shares=40,
                content_type="text",
                sentiment="positive",
            ),
        ],
        content_mix={"promotional": 0.3, "educational": 0.5, "community": 0.2},
        overall_sentiment="positive",
        sentiment_breakdown={"positive": 0.7, "neutral": 0.25, "negative": 0.05},
        avg_engagement_per_post=75.0,
        uses_images=True,
        uses_videos=True,
        uses_threads=False,
        multimedia_percentage=65.0,
        common_topics=["product", "innovation", "community"],
        hashtags_used=["#innovation", "#tech"],
        findings=[],
        recommendations=[],
    )


@pytest.fixture
def valid_team_report() -> TeamPresenceReport:
    """Create a valid team presence report for testing."""
    return TeamPresenceReport(
        score=55.0,
        team_size_estimate="11-50",
        team_members=[
            TeamMember(
                name="Jane Doe",
                role="CEO",
                linkedin_url="https://linkedin.com/in/janedoe",
                twitter_url="https://twitter.com/janedoe",
                twitter_followers=2500,
                notable_background="ex-Google",
            ),
        ],
        has_team_page=True,
        team_page_url="https://example.com/team",
        linkedin_followers=1200,
        linkedin_url="https://linkedin.com/company/testbrand",
        linkedin_active=True,
        founders_identified=2,
        founder_twitter_presence=True,
        founder_combined_following=5000,
        has_notable_background=True,
        has_advisors_listed=False,
        has_investors_listed=True,
        uses_real_identities=True,
        photos_on_website=True,
        findings=[],
        recommendations=[],
    )


@pytest.fixture
def valid_channel_report() -> ChannelFitReport:
    """Create a valid channel fit report for testing."""
    return ChannelFitReport(
        score=60.0,
        channels=[
            ChannelScore(
                channel="Twitter/X",
                score=8.0,
                suitability="high",
                rationale="High engagement potential for tech audience.",
                current_presence=True,
            ),
            ChannelScore(
                channel="LinkedIn",
                score=7.0,
                suitability="high",
                rationale="Good for B2B credibility.",
                current_presence=False,
            ),
        ],
        top_channels=["Twitter/X", "LinkedIn"],
        underutilized_channels=["LinkedIn"],
        low_priority_channels=["TikTok"],
        product_type="B2B SaaS",
        target_audience="Tech professionals",
        industry="Technology",
        findings=[],
        recommendations=[],
    )


@pytest.fixture
def valid_scorecard() -> ScoreCard:
    """Create a valid scorecard for testing."""
    return ScoreCard(
        overall_score=67.5,
        scores={
            "seo": 75.0,
            "social_media": 68.0,
            "brand_messaging": 73.0,
            "website_ux": 77.0,
            "ai_discoverability": 45.0,
            "content": 82.0,
            "team_presence": 55.0,
            "channel_fit": 60.0,
        },
        grade="C",
        summary="Good brand foundation with room for improvement in AI discoverability and team visibility.",
        strengths=["Content quality", "Website UX", "SEO fundamentals"],
        weaknesses=["AI discoverability", "Team presence"],
        opportunities=["Wikipedia page", "LinkedIn presence"],
        benchmark_comparison={},
        top_recommendations=[],
        quick_wins=[],
    )


@pytest.fixture
def valid_full_report(
    valid_seo_report,
    valid_social_report,
    valid_brand_report,
    valid_ux_report,
    valid_ai_report,
    valid_content_report,
    valid_team_report,
    valid_channel_report,
    valid_scorecard,
) -> FullReport:
    """Create a complete valid report for testing."""
    return FullReport(
        generated_at=datetime.utcnow(),
        url="https://example.com",
        brand_name="Test Brand",
        brand_logo_url="https://example.com/logo.png",
        seo=valid_seo_report,
        social_media=valid_social_report,
        brand_messaging=valid_brand_report,
        website_ux=valid_ux_report,
        ai_discoverability=valid_ai_report,
        content=valid_content_report,
        team_presence=valid_team_report,
        channel_fit=valid_channel_report,
        scorecard=valid_scorecard,
    )


# =============================================================================
# Test Report Structure
# =============================================================================


class TestReportStructure:
    """Tests for validating report structure and required fields."""

    def test_full_report_has_all_sections(self, valid_full_report: FullReport):
        """Test that full report contains all required sections."""
        required_sections = [
            "seo",
            "social_media",
            "brand_messaging",
            "website_ux",
            "ai_discoverability",
            "content",
            "team_presence",
            "channel_fit",
            "scorecard",
        ]

        report_dict = valid_full_report.model_dump()

        for section in required_sections:
            assert section in report_dict, f"Missing section: {section}"
            assert report_dict[section] is not None, f"Section {section} is None"

    def test_full_report_has_metadata(self, valid_full_report: FullReport):
        """Test that full report contains metadata fields."""
        assert valid_full_report.url is not None
        assert valid_full_report.generated_at is not None
        assert isinstance(valid_full_report.generated_at, datetime)

    def test_all_sections_have_score(self, valid_full_report: FullReport):
        """Test that every section has a score field."""
        sections = [
            valid_full_report.seo,
            valid_full_report.social_media,
            valid_full_report.brand_messaging,
            valid_full_report.website_ux,
            valid_full_report.ai_discoverability,
            valid_full_report.content,
            valid_full_report.team_presence,
            valid_full_report.channel_fit,
        ]

        for section in sections:
            assert hasattr(section, "score"), (
                f"Section {type(section).__name__} missing score"
            )
            assert section.score is not None

    def test_scorecard_has_all_module_scores(self, valid_scorecard: ScoreCard):
        """Test that scorecard contains scores for all modules."""
        required_modules = [
            "seo",
            "social_media",
            "brand_messaging",
            "website_ux",
            "ai_discoverability",
            "content",
            "team_presence",
            "channel_fit",
        ]

        for module in required_modules:
            assert module in valid_scorecard.scores, f"Missing module score: {module}"


# =============================================================================
# Test Score Ranges
# =============================================================================


class TestScoreRanges:
    """Tests to validate all scores are within valid ranges (0-100)."""

    def test_seo_score_in_range(self, valid_seo_report: SEOReport):
        """Test SEO scores are within 0-100."""
        assert 0 <= valid_seo_report.score <= 100

        if valid_seo_report.performance_score is not None:
            assert 0 <= valid_seo_report.performance_score <= 100
        if valid_seo_report.accessibility_score is not None:
            assert 0 <= valid_seo_report.accessibility_score <= 100
        if valid_seo_report.domain_authority is not None:
            assert 0 <= valid_seo_report.domain_authority <= 100
        if valid_seo_report.spam_score is not None:
            assert 0 <= valid_seo_report.spam_score <= 100

    def test_social_score_in_range(self, valid_social_report: SocialMediaReport):
        """Test social media scores are within 0-100."""
        assert 0 <= valid_social_report.score <= 100

    def test_brand_score_in_range(self, valid_brand_report: BrandMessagingReport):
        """Test brand messaging scores are within 0-100."""
        assert 0 <= valid_brand_report.score <= 100

        if (
            valid_brand_report.archetype
            and valid_brand_report.archetype.confidence is not None
        ):
            assert 0 <= valid_brand_report.archetype.confidence <= 1

    def test_ux_score_in_range(self, valid_ux_report: UXReport):
        """Test UX scores are within 0-100."""
        assert 0 <= valid_ux_report.score <= 100

    def test_ai_score_in_range(self, valid_ai_report: AIDiscoverabilityReport):
        """Test AI discoverability scores are within 0-100."""
        assert 0 <= valid_ai_report.score <= 100

    def test_content_score_in_range(self, valid_content_report: ContentReport):
        """Test content scores are within 0-100."""
        assert 0 <= valid_content_report.score <= 100

    def test_team_score_in_range(self, valid_team_report: TeamPresenceReport):
        """Test team presence scores are within 0-100."""
        assert 0 <= valid_team_report.score <= 100

    def test_channel_score_in_range(self, valid_channel_report: ChannelFitReport):
        """Test channel fit scores are within 0-100."""
        assert 0 <= valid_channel_report.score <= 100

        for channel in valid_channel_report.channels:
            assert 0 <= channel.score <= 10  # Channel scores are 0-10

    def test_overall_score_in_range(self, valid_scorecard: ScoreCard):
        """Test overall score is within 0-100."""
        assert 0 <= valid_scorecard.overall_score <= 100

    def test_all_module_scores_in_range(self, valid_scorecard: ScoreCard):
        """Test all module scores in scorecard are within 0-100."""
        for module, score in valid_scorecard.scores.items():
            assert 0 <= score <= 100, f"Module {module} score {score} out of range"


# =============================================================================
# Test Model Validation
# =============================================================================


class TestModelValidation:
    """Tests for Pydantic model validation behavior."""

    def test_seo_report_rejects_invalid_score(self):
        """Test that SEO report rejects scores outside 0-100."""
        with pytest.raises(ValidationError):
            SEOReport(score=150.0)

    def test_seo_report_rejects_negative_score(self):
        """Test that SEO report rejects negative scores."""
        with pytest.raises(ValidationError):
            SEOReport(score=-10.0)

    def test_social_report_rejects_invalid_score(self):
        """Test that social media report rejects invalid scores."""
        with pytest.raises(ValidationError):
            SocialMediaReport(score=101.0)

    def test_brand_archetype_confidence_range(self):
        """Test archetype confidence must be 0-1."""
        with pytest.raises(ValidationError):
            BrandArchetype(
                primary="Test",
                confidence=1.5,  # Invalid - must be <= 1
                description="Test archetype",
            )

    def test_severity_level_enum_values(self):
        """Test that severity levels are valid enum values."""
        valid_severities = {"critical", "high", "medium", "low", "info"}

        for level in SeverityLevel:
            assert level.value in valid_severities

    def test_finding_accepts_all_severity_levels(self):
        """Test that Finding accepts all severity levels."""
        for severity in SeverityLevel:
            finding = Finding(
                title="Test Finding",
                detail="Test detail",
                severity=severity,
            )
            assert finding.severity == severity

    def test_recommendation_accepts_valid_impact_effort(self):
        """Test recommendation accepts valid impact/effort values."""
        valid_values = ["high", "medium", "low"]

        for impact in valid_values:
            for effort in valid_values:
                rec = Recommendation(
                    title="Test",
                    description="Test description",
                    category="test",
                    impact=impact,
                    effort=effort,
                )
                assert rec.impact == impact
                assert rec.effort == effort


# =============================================================================
# Test Report Serialization
# =============================================================================


class TestReportSerialization:
    """Tests for report JSON serialization."""

    def test_full_report_to_json(self, valid_full_report: FullReport):
        """Test that full report can be serialized to JSON."""
        json_str = valid_full_report.model_dump_json()
        assert isinstance(json_str, str)
        assert len(json_str) > 0

    def test_full_report_to_dict(self, valid_full_report: FullReport):
        """Test that full report can be converted to dict."""
        report_dict = valid_full_report.model_dump()
        assert isinstance(report_dict, dict)
        assert "scorecard" in report_dict
        assert "seo" in report_dict

    def test_report_json_contains_all_scores(self, valid_full_report: FullReport):
        """Test that serialized report contains all section scores."""
        report_dict = valid_full_report.model_dump()

        assert report_dict["seo"]["score"] == 75.0
        assert report_dict["social_media"]["score"] == 68.0
        assert report_dict["brand_messaging"]["score"] == 73.0
        assert report_dict["website_ux"]["score"] == 77.0
        assert report_dict["ai_discoverability"]["score"] == 45.0
        assert report_dict["content"]["score"] == 82.0
        assert report_dict["team_presence"]["score"] == 55.0
        assert report_dict["channel_fit"]["score"] == 60.0
        assert report_dict["scorecard"]["overall_score"] == 67.5


# =============================================================================
# Test Edge Cases
# =============================================================================


class TestReportEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_report_with_zero_scores(self):
        """Test report can have all zero scores."""
        scorecard = ScoreCard(
            overall_score=0.0,
            scores={
                "seo": 0.0,
                "social_media": 0.0,
                "brand_messaging": 0.0,
                "website_ux": 0.0,
                "ai_discoverability": 0.0,
                "content": 0.0,
                "team_presence": 0.0,
                "channel_fit": 0.0,
            },
            grade="F",
            summary="Needs significant improvement across all areas.",
        )
        assert scorecard.overall_score == 0.0

    def test_report_with_perfect_scores(self):
        """Test report can have all perfect scores."""
        scorecard = ScoreCard(
            overall_score=100.0,
            scores={
                "seo": 100.0,
                "social_media": 100.0,
                "brand_messaging": 100.0,
                "website_ux": 100.0,
                "ai_discoverability": 100.0,
                "content": 100.0,
                "team_presence": 100.0,
                "channel_fit": 100.0,
            },
            grade="A",
            summary="Exceptional performance across all metrics.",
        )
        assert scorecard.overall_score == 100.0

    def test_report_with_empty_lists(self):
        """Test report handles empty lists correctly."""
        seo_report = SEOReport(
            score=50.0,
            schema_types_found=[],
            findings=[],
            recommendations=[],
        )
        assert seo_report.schema_types_found == []
        assert seo_report.findings == []
        assert seo_report.recommendations == []

    def test_report_with_none_optional_fields(self):
        """Test report handles None optional fields."""
        seo_report = SEOReport(
            score=50.0,
            performance_score=None,
            core_web_vitals=None,
            domain_authority=None,
        )
        assert seo_report.performance_score is None
        assert seo_report.core_web_vitals is None
        assert seo_report.domain_authority is None

    def test_social_report_with_no_platforms(self):
        """Test social media report with no platforms detected."""
        social_report = SocialMediaReport(
            score=10.0,  # Low score due to no presence
            platforms=[],
            total_followers=0,
            platforms_active=0,
            platforms_dormant=0,
            platforms_missing=["twitter", "linkedin", "instagram"],
        )
        assert len(social_report.platforms) == 0
        assert social_report.total_followers == 0

    def test_boundary_score_values(self):
        """Test exact boundary score values."""
        # Test 0
        report_0 = SEOReport(score=0.0)
        assert report_0.score == 0.0

        # Test 100
        report_100 = SEOReport(score=100.0)
        assert report_100.score == 100.0

        # Test midpoint
        report_50 = SEOReport(score=50.0)
        assert report_50.score == 50.0
