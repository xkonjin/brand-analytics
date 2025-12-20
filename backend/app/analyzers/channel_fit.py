# =============================================================================
# EXPLAINER: Channel Fit Analyzer
# =============================================================================
#
# WHAT IS THIS?
# This module answers: "Are you fishing where the fish are?"
# It determines which social/marketing channels best fit the brand's profile.
#
# WHY DO WE NEED IT?
# 1. **Efficiency**: Don't waste time on TikTok if you're selling enterprise SaaS.
# 2. **Opportunity Cost**: Missing Discord when you're a crypto project is fatal.
#
# HOW IT WORKS:
# 1. **Classification**: Infers if the brand is B2B or B2C based on keywords.
# 2. **Context**: Checks industry (e.g., Crypto needs Twitter/Discord).
# 3. **Scoring**: Ranks channels (Twitter, LinkedIn, etc.) on suitability.
# 4. **Gap Analysis**: Compares "Ideal Channels" vs "Actual Presence".
#
# SCORING LOGIC:
# - Alignment Score: How well does your actual presence match the ideal profile?
# =============================================================================

from typing import List

from app.analyzers.base import BaseAnalyzer, AnalyzerResult
from app.models.report import Finding, Recommendation, SeverityLevel, ChannelScore


class ChannelFitAnalyzer(BaseAnalyzer):
    """Analyzes channel suitability for the brand based on product and audience."""

    MODULE_NAME = "channel_fit"
    WEIGHT = 0.05

    CHANNELS = ["twitter", "linkedin", "tiktok", "youtube", "discord", "instagram"]

    async def analyze(self) -> AnalyzerResult:
        try:
            self._raw_data = {}

            # Score each channel
            channel_scores = self._score_channels()
            self._raw_data["channels"] = channel_scores

            score = self._calculate_score()
            self._findings = self._generate_findings()
            self._recommendations = self._generate_recommendations()

            result_data = {
                "score": score,
                "channels": [c.model_dump() for c in channel_scores],
                "top_channels": [c.channel for c in channel_scores if c.score >= 7][:3],
                "underutilized_channels": self._get_underutilized(),
                "low_priority_channels": [
                    c.channel for c in channel_scores if c.score <= 4
                ],
                "product_type": self._infer_product_type(),
                "industry": self.industry,
            }

            return AnalyzerResult(
                score=score,
                findings=self._findings,
                recommendations=self._recommendations,
                data=result_data,
            )
        except Exception as e:
            return AnalyzerResult(score=0, error=str(e))

    def _infer_product_type(self) -> str:
        """Infer B2B vs B2C from content."""
        text = self.scraped_data.get("text_content", "").lower()
        b2b_keywords = [
            "enterprise",
            "business",
            "teams",
            "company",
            "api",
            "integration",
        ]
        b2c_keywords = ["users", "people", "everyone", "personal", "free", "download"]

        b2b_score = sum(1 for kw in b2b_keywords if kw in text)
        b2c_score = sum(1 for kw in b2c_keywords if kw in text)

        return "B2B" if b2b_score > b2c_score else "B2C"

    def _score_channels(self) -> List[ChannelScore]:
        """Score each channel for suitability."""
        social_links = self.scraped_data.get("social_links", {})
        product_type = self._infer_product_type()
        is_crypto = self.industry and "crypto" in self.industry.lower()

        scores = []

        # Twitter - essential for tech/crypto
        twitter_score = 9 if is_crypto else 7 if product_type == "B2B" else 6
        scores.append(
            ChannelScore(
                channel="twitter",
                score=twitter_score,
                suitability="high" if twitter_score >= 7 else "medium",
                rationale="Essential for real-time engagement and industry conversations."
                if is_crypto
                else "Good for thought leadership and announcements.",
                current_presence="twitter" in social_links,
            )
        )

        # LinkedIn - great for B2B
        linkedin_score = 8 if product_type == "B2B" else 5
        scores.append(
            ChannelScore(
                channel="linkedin",
                score=linkedin_score,
                suitability="high" if linkedin_score >= 7 else "medium",
                rationale="Excellent for B2B credibility and investor visibility.",
                current_presence="linkedin" in social_links,
            )
        )

        # TikTok - consumer/visual products
        tiktok_score = 3 if product_type == "B2B" else 7
        scores.append(
            ChannelScore(
                channel="tiktok",
                score=tiktok_score,
                suitability="low" if tiktok_score <= 4 else "medium",
                rationale="Best for visual, consumer-focused content."
                if tiktok_score > 4
                else "Low priority for B2B/technical products.",
                current_presence="tiktok" in social_links,
            )
        )

        # YouTube - tutorials and demos
        # Generally high potential for everyone (Video is king)
        youtube_score = 7
        scores.append(
            ChannelScore(
                channel="youtube",
                score=youtube_score,
                suitability="high",
                rationale="Great for tutorials, demos, and educational content. High SEO value.",
                current_presence="youtube" in social_links,
            )
        )

        # Discord - community
        discord_score = 9 if is_crypto else 6
        scores.append(
            ChannelScore(
                channel="discord",
                score=discord_score,
                suitability="high" if discord_score >= 7 else "medium",
                rationale="Essential for community building in crypto/gaming."
                if is_crypto
                else "Good for engaged user communities.",
                current_presence="discord" in social_links,
            )
        )

        return sorted(scores, key=lambda x: x.score, reverse=True)

    def _get_underutilized(self) -> List[str]:
        """Find high-potential channels not being used."""
        channels = self._raw_data.get("channels", [])

        return [c.channel for c in channels if c.score >= 7 and not c.current_presence]

    def _calculate_score(self) -> float:
        """Score based on alignment between high-fit channels and actual presence."""
        channels = self._raw_data.get("channels", [])

        # Score based on presence on high-fit channels
        high_fit = [c for c in channels if c.score >= 7]
        present_on_high_fit = sum(1 for c in high_fit if c.current_presence)

        if not high_fit:
            return 50

        alignment = present_on_high_fit / len(high_fit)
        return self.clamp_score(alignment * 100)

    def _generate_findings(self) -> List[Finding]:
        underutilized = self._get_underutilized()

        findings = []
        if underutilized:
            findings.append(
                Finding(
                    title="Underutilized High-Potential Channels",
                    detail=f"These channels would be a good fit but aren't being used: {', '.join(underutilized)}",
                    severity=SeverityLevel.MEDIUM,
                )
            )
        return findings

    def _generate_recommendations(self) -> List[Recommendation]:
        underutilized = self._get_underutilized()

        recommendations = []
        for channel in underutilized[:2]:  # Top 2 underutilized
            recommendations.append(
                Recommendation(
                    title=f"Establish Presence on {channel.title()}",
                    description=f"{channel.title()} is well-suited for your brand but you're not active there. "
                    "Consider establishing a presence to capture this audience.",
                    priority=SeverityLevel.MEDIUM,
                    category="channel_fit",
                    impact="medium",
                    effort="medium",
                )
            )
        return recommendations
