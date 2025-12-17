# =============================================================================
# Social Media Presence Analyzer
# =============================================================================
# This module analyzes social media presence across major platforms.
# It evaluates follower counts, engagement rates, and posting consistency.
# =============================================================================

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import re

from app.config import settings
from app.analyzers.base import BaseAnalyzer, AnalyzerResult
from app.models.report import (
    Finding, Recommendation, SeverityLevel,
    SocialPlatformMetrics,
)


class SocialMediaAnalyzer(BaseAnalyzer):
    """
    Analyzes Social Media Presence & Engagement.
    
    This analyzer evaluates:
    - Presence across major platforms (Twitter, LinkedIn, Instagram, etc.)
    - Follower counts and growth indicators
    - Engagement rates (likes, comments, shares)
    - Posting frequency and consistency
    - Community channels (Discord, Telegram)
    
    Score Calculation:
    - Platform presence (having accounts): 25%
    - Follower count (relative to industry): 25%
    - Engagement rate: 30%
    - Posting consistency: 20%
    """
    
    MODULE_NAME = "social_media"
    WEIGHT = 0.20
    
    # Engagement rate benchmarks by platform (2024 data)
    ENGAGEMENT_BENCHMARKS = {
        "twitter": 0.05,      # 0.05% is average
        "instagram": 1.5,     # 1.5% is average
        "linkedin": 2.0,      # 2% is average for companies
        "tiktok": 5.0,        # 5% is average
        "facebook": 0.5,      # 0.5% is average
    }
    
    async def analyze(self) -> AnalyzerResult:
        """
        Run the social media analysis.
        
        Steps:
        1. Identify linked social profiles from scraped data
        2. Fetch metrics for each platform (via APIs or estimation)
        3. Calculate engagement rates
        4. Generate score and insights
        
        Returns:
            AnalyzerResult: Social media analysis results
        """
        try:
            self._raw_data = {}
            
            # ----------------------------------------------------------------
            # Get social links from scraped data
            # ----------------------------------------------------------------
            social_links = self.scraped_data.get("social_links", {})
            self._raw_data["social_links"] = social_links
            
            # ----------------------------------------------------------------
            # Analyze each platform
            # ----------------------------------------------------------------
            platforms = []
            for platform, url in social_links.items():
                metrics = await self._analyze_platform(platform, url)
                if metrics:
                    platforms.append(metrics)
            
            self._raw_data["platforms"] = platforms
            
            # ----------------------------------------------------------------
            # Check for community channels
            # ----------------------------------------------------------------
            community = self._analyze_community_channels()
            self._raw_data["community"] = community
            
            # ----------------------------------------------------------------
            # Calculate overall metrics
            # ----------------------------------------------------------------
            self._raw_data["summary"] = self._calculate_summary(platforms)
            
            # ----------------------------------------------------------------
            # Calculate score
            # ----------------------------------------------------------------
            score = self._calculate_score()
            
            # ----------------------------------------------------------------
            # Generate findings and recommendations
            # ----------------------------------------------------------------
            self._findings = self._generate_findings()
            self._recommendations = self._generate_recommendations()
            
            # ----------------------------------------------------------------
            # Build result data
            # ----------------------------------------------------------------
            result_data = {
                "score": score,
                "platforms": [p.model_dump() for p in platforms],
                "total_followers": sum(p.followers or 0 for p in platforms),
                "platforms_active": len([p for p in platforms if self._is_active(p)]),
                "platforms_dormant": len([p for p in platforms if not self._is_active(p)]),
                "platforms_missing": self._get_missing_platforms(social_links),
                "overall_engagement_rate": self._raw_data["summary"].get("avg_engagement"),
                "has_discord": community.get("has_discord", False),
                "discord_members": community.get("discord_members"),
                "discord_url": community.get("discord_url"),
                "has_telegram": community.get("has_telegram", False),
                "telegram_members": community.get("telegram_members"),
                "telegram_url": community.get("telegram_url"),
            }
            
            return AnalyzerResult(
                score=score,
                findings=self._findings,
                recommendations=self._recommendations,
                data=result_data,
            )
            
        except Exception as e:
            return AnalyzerResult(
                score=0,
                error=f"Social media analysis failed: {str(e)}",
            )
    
    async def _analyze_platform(
        self,
        platform: str,
        url: str
    ) -> Optional[SocialPlatformMetrics]:
        """
        Analyze a specific social media platform.
        
        For MVP, we use estimated/mock data. In production, this would
        integrate with Apify or platform APIs.
        
        Args:
            platform: Platform name (twitter, linkedin, etc.)
            url: Profile URL
        
        Returns:
            SocialPlatformMetrics: Platform metrics
        """
        # In production, this would call Apify or scrape the platform
        # For now, return estimated metrics based on platform type
        
        if platform == "twitter":
            return SocialPlatformMetrics(
                platform="twitter",
                url=url,
                followers=self._estimate_followers(platform),
                posts_last_30_days=self._estimate_posts(),
                engagement_rate=0.08,  # Slightly above average
                avg_likes=15,
                avg_comments=2,
                avg_shares=3,
            )
        elif platform == "linkedin":
            return SocialPlatformMetrics(
                platform="linkedin",
                url=url,
                followers=self._estimate_followers(platform),
                posts_last_30_days=4,
                engagement_rate=1.5,
            )
        elif platform == "instagram":
            return SocialPlatformMetrics(
                platform="instagram",
                url=url,
                followers=self._estimate_followers(platform),
                posts_last_30_days=8,
                engagement_rate=2.0,
            )
        else:
            return SocialPlatformMetrics(
                platform=platform,
                url=url,
                followers=self._estimate_followers(platform),
            )
    
    def _estimate_followers(self, platform: str) -> int:
        """Estimate follower count (placeholder for API data)."""
        # This would be replaced with actual API data
        estimates = {
            "twitter": 5000,
            "linkedin": 2000,
            "instagram": 3000,
            "tiktok": 1000,
            "facebook": 1500,
            "youtube": 500,
        }
        return estimates.get(platform, 1000)
    
    def _estimate_posts(self) -> int:
        """Estimate posts in last 30 days."""
        return 8  # Placeholder
    
    def _is_active(self, platform: SocialPlatformMetrics) -> bool:
        """Check if a platform is actively used."""
        posts = platform.posts_last_30_days or 0
        return posts >= 2  # At least 2 posts in 30 days
    
    def _analyze_community_channels(self) -> Dict[str, Any]:
        """Analyze community channels (Discord, Telegram)."""
        social_links = self.scraped_data.get("social_links", {})
        
        return {
            "has_discord": "discord" in social_links,
            "discord_url": social_links.get("discord"),
            "discord_members": None,  # Would need API call
            "has_telegram": "telegram" in social_links,
            "telegram_url": social_links.get("telegram"),
            "telegram_members": None,  # Would need API call
        }
    
    def _calculate_summary(self, platforms: List[SocialPlatformMetrics]) -> Dict[str, Any]:
        """Calculate summary metrics across all platforms."""
        total_followers = sum(p.followers or 0 for p in platforms)
        
        engagement_rates = [p.engagement_rate for p in platforms if p.engagement_rate]
        avg_engagement = sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0
        
        active_platforms = len([p for p in platforms if self._is_active(p)])
        
        return {
            "total_followers": total_followers,
            "avg_engagement": avg_engagement,
            "active_platforms": active_platforms,
            "total_platforms": len(platforms),
        }
    
    def _get_missing_platforms(self, social_links: Dict[str, str]) -> List[str]:
        """Identify important platforms not being used."""
        important_platforms = ["twitter", "linkedin", "instagram"]
        return [p for p in important_platforms if p not in social_links]
    
    def _calculate_score(self) -> float:
        """
        Calculate the social media score.
        
        Components:
        - Platform presence: 25%
        - Follower count: 25%
        - Engagement rate: 30%
        - Posting consistency: 20%
        """
        score = 0.0
        summary = self._raw_data.get("summary", {})
        platforms = self._raw_data.get("platforms", [])
        community = self._raw_data.get("community", {})
        
        # Platform presence (25%)
        # Having 3+ platforms is ideal
        platform_count = len(platforms)
        if platform_count >= 3:
            presence_score = 100
        elif platform_count == 2:
            presence_score = 75
        elif platform_count == 1:
            presence_score = 50
        else:
            presence_score = 10
        
        # Bonus for community channels
        if community.get("has_discord") or community.get("has_telegram"):
            presence_score = min(100, presence_score + 20)
        
        score += presence_score * 0.25
        
        # Follower count (25%)
        # Scale based on total followers
        total_followers = summary.get("total_followers", 0)
        if total_followers >= 50000:
            follower_score = 100
        elif total_followers >= 10000:
            follower_score = 80
        elif total_followers >= 5000:
            follower_score = 60
        elif total_followers >= 1000:
            follower_score = 40
        else:
            follower_score = 20
        score += follower_score * 0.25
        
        # Engagement rate (30%)
        avg_engagement = summary.get("avg_engagement", 0)
        if avg_engagement >= 2.0:
            engagement_score = 100
        elif avg_engagement >= 1.0:
            engagement_score = 80
        elif avg_engagement >= 0.5:
            engagement_score = 60
        elif avg_engagement > 0:
            engagement_score = 40
        else:
            engagement_score = 20
        score += engagement_score * 0.30
        
        # Posting consistency (20%)
        active_platforms = summary.get("active_platforms", 0)
        total_platforms = summary.get("total_platforms", 1)
        consistency_ratio = active_platforms / max(total_platforms, 1)
        consistency_score = consistency_ratio * 100
        score += consistency_score * 0.20
        
        return self.clamp_score(score)
    
    def _generate_findings(self) -> List[Finding]:
        """Generate findings based on the analysis."""
        findings = []
        summary = self._raw_data.get("summary", {})
        platforms = self._raw_data.get("platforms", [])
        community = self._raw_data.get("community", {})
        
        # Platform presence findings
        if len(platforms) >= 3:
            findings.append(Finding(
                title="Strong Multi-Platform Presence",
                detail=f"Active on {len(platforms)} social platforms, providing good reach.",
                severity=SeverityLevel.INFO,
            ))
        elif len(platforms) == 0:
            findings.append(Finding(
                title="No Social Media Presence Detected",
                detail="No social media links found on the website. This limits reach and credibility.",
                severity=SeverityLevel.CRITICAL,
            ))
        
        # Engagement findings
        avg_engagement = summary.get("avg_engagement", 0)
        if avg_engagement >= 2.0:
            findings.append(Finding(
                title="Excellent Engagement Rate",
                detail=f"Average engagement of {avg_engagement:.1f}% is well above industry average.",
                severity=SeverityLevel.INFO,
            ))
        elif avg_engagement < 0.5:
            findings.append(Finding(
                title="Low Engagement Rate",
                detail=f"Engagement rate of {avg_engagement:.2f}% is below average. "
                       "Content may not be resonating with the audience.",
                severity=SeverityLevel.HIGH,
            ))
        
        # Community findings
        if community.get("has_discord") and community.get("has_telegram"):
            findings.append(Finding(
                title="Strong Community Channels",
                detail="Both Discord and Telegram are present, showing commitment to community building.",
                severity=SeverityLevel.INFO,
            ))
        elif not community.get("has_discord") and not community.get("has_telegram"):
            if self.industry and "crypto" in self.industry.lower():
                findings.append(Finding(
                    title="Missing Community Channels",
                    detail="No Discord or Telegram found. These are essential for crypto projects.",
                    severity=SeverityLevel.HIGH,
                ))
        
        # Missing important platforms
        missing = self._get_missing_platforms(self._raw_data.get("social_links", {}))
        if "twitter" in missing:
            findings.append(Finding(
                title="Missing Twitter/X Presence",
                detail="Twitter is the primary platform for crypto and tech. Not having presence there limits visibility.",
                severity=SeverityLevel.HIGH,
            ))
        
        return findings
    
    def _generate_recommendations(self) -> List[Recommendation]:
        """Generate recommendations based on findings."""
        recommendations = []
        summary = self._raw_data.get("summary", {})
        platforms = self._raw_data.get("platforms", [])
        community = self._raw_data.get("community", {})
        
        # Platform presence recommendations
        missing = self._get_missing_platforms(self._raw_data.get("social_links", {}))
        if "twitter" in missing:
            recommendations.append(Recommendation(
                title="Establish Twitter/X Presence",
                description="Create and actively maintain a Twitter account. It's essential for "
                           "real-time engagement and is where most industry conversations happen. "
                           "Aim for 3-5 tweets per week minimum.",
                priority=SeverityLevel.HIGH,
                category="social_media",
                impact="high",
                effort="low",
            ))
        
        if "linkedin" in missing:
            recommendations.append(Recommendation(
                title="Create LinkedIn Company Page",
                description="Establish a LinkedIn presence for B2B credibility and professional networking. "
                           "Share company updates, thought leadership, and job postings.",
                priority=SeverityLevel.MEDIUM,
                category="social_media",
                impact="medium",
                effort="low",
            ))
        
        # Engagement recommendations
        avg_engagement = summary.get("avg_engagement", 0)
        if avg_engagement < 1.0:
            recommendations.append(Recommendation(
                title="Improve Social Engagement",
                description="Boost engagement by: 1) Asking questions in posts, 2) Responding to "
                           "all comments promptly, 3) Using more visuals and videos, 4) Running "
                           "polls and interactive content. Engagement builds community.",
                priority=SeverityLevel.HIGH,
                category="social_media",
                impact="high",
                effort="medium",
            ))
        
        # Posting consistency recommendations
        if summary.get("active_platforms", 0) < summary.get("total_platforms", 0):
            recommendations.append(Recommendation(
                title="Increase Posting Consistency",
                description="Some platforms appear dormant. Either commit to regular posting "
                           "(minimum 2x/week) or remove inactive accounts. Dormant accounts "
                           "hurt credibility.",
                priority=SeverityLevel.MEDIUM,
                category="social_media",
                impact="medium",
                effort="medium",
            ))
        
        # Community recommendations
        if not community.get("has_discord") and not community.get("has_telegram"):
            recommendations.append(Recommendation(
                title="Launch a Community Channel",
                description="Create a Discord server or Telegram group to build direct relationships "
                           "with users. This enables real-time support, feedback collection, and "
                           "creates a loyal community of advocates.",
                priority=SeverityLevel.HIGH,
                category="social_media",
                impact="high",
                effort="medium",
            ))
        
        return recommendations

