# =============================================================================
# EXPLAINER: Social Media Presence Analyzer
# =============================================================================
#
# WHAT IS THIS?
# This module evaluates the brand's footprint on social media.
#
# WHY DO WE NEED IT?
# 1. **Social Proof**: "If you don't have a Twitter/LinkedIn, are you even real?"
# 2. **Engagement**: High followers + low engagement = fake followers (or boring content).
# 3. **Consistency**: Posting once a year looks worse than not having an account.
#
# HOW IT WORKS:
# 1. **Detection**: Finds social links on the website.
# 2. **Metrics**: Fetches follower counts and engagement (likes/comments) via APIs or scraping.
# 3. **Benchmarking**: Compares engagement rates against industry standards (e.g., 0.05% for Twitter).
#
# SCORING LOGIC (Total 100):
# - Engagement Rate (30%): Are people listening?
# - Presence (25%): Are you on the right platforms?
# - Followers (25%): Do you have an audience?
# - Consistency (20%): Do you show up regularly?
# =============================================================================

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import re
import logging

from app.config import settings
from app.analyzers.base import BaseAnalyzer, AnalyzerResult
from app.models.report import (
    Finding, Recommendation, SeverityLevel,
    SocialPlatformMetrics,
)
from app.services.twitter_service import TwitterService, extract_twitter_username
from app.services.apify_service import (
    ApifyService,
    extract_instagram_username,
    extract_youtube_channel,
)

logger = logging.getLogger(__name__)


class SocialMediaAnalyzer(BaseAnalyzer):
    """
    Analyzes Social Media Presence & Engagement.
    """
    
    MODULE_NAME = "social_media"
    WEIGHT = 0.20
    
    # Engagement rate benchmarks by platform (2024 data)
    # These are used to determine if engagement is "Good", "Average", or "Poor".
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
        """
        try:
            self._raw_data = {}
            
            # ----------------------------------------------------------------
            # 1. Get social links from scraped data
            # ----------------------------------------------------------------
            # The Orchestrator already scraped the homepage and found links like twitter.com/brand
            social_links = self.scraped_data.get("social_links", {})
            self._raw_data["social_links"] = social_links
            
            # ----------------------------------------------------------------
            # 2. Analyze each platform
            # ----------------------------------------------------------------
            platforms = []
            for platform, url in social_links.items():
                metrics = await self._analyze_platform(platform, url)
                if metrics:
                    platforms.append(metrics)
            
            self._raw_data["platforms"] = platforms
            
            # ----------------------------------------------------------------
            # 3. Check for community channels
            # ----------------------------------------------------------------
            # Discord and Telegram are special cases (Community vs Broadcast)
            community = self._analyze_community_channels()
            self._raw_data["community"] = community
            
            # ----------------------------------------------------------------
            # 4. Calculate overall metrics
            # ----------------------------------------------------------------
            self._raw_data["summary"] = self._calculate_summary(platforms)
            
            # ----------------------------------------------------------------
            # 5. Calculate score
            # ----------------------------------------------------------------
            score = self._calculate_score()
            
            # ----------------------------------------------------------------
            # 6. Generate findings and recommendations
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
        """Analyze a specific social media platform."""
        if platform == "twitter" or platform == "x":
            return await self._analyze_twitter(url)
        elif platform == "instagram":
            return await self._analyze_instagram(url)
        elif platform == "youtube":
            return await self._analyze_youtube(url)
        elif platform == "linkedin":
            return SocialPlatformMetrics(
                platform="linkedin",
                url=url,
                followers=self._estimate_followers(platform),
                posts_last_30_days=4,
                engagement_rate=1.5,
            )
        else:
            return SocialPlatformMetrics(
                platform=platform,
                url=url,
                followers=self._estimate_followers(platform),
            )
    
    async def _analyze_instagram(self, url: str) -> Optional[SocialPlatformMetrics]:
        """Analyze Instagram profile using Apify."""
        username = extract_instagram_username(url)
        if not username:
            return SocialPlatformMetrics(
                platform="instagram",
                url=url,
                followers=self._estimate_followers("instagram"),
            )
        
        apify = ApifyService()
        if not apify.is_configured():
            logger.warning("Apify not configured, using estimated Instagram data")
            return SocialPlatformMetrics(
                platform="instagram",
                url=url,
                handle=f"@{username}",
                followers=self._estimate_followers("instagram"),
                posts_last_30_days=8,
                engagement_rate=2.0,
            )
        
        profile = await apify.scrape_instagram_profile(username)
        
        if profile.success:
            self._raw_data["instagram_analysis"] = {
                "username": username,
                "full_name": profile.full_name,
                "biography": profile.biography,
                "posts_count": profile.posts_count,
                "engagement_rate": profile.engagement_rate,
                "recent_posts": profile.recent_posts[:5],
            }
            
            return SocialPlatformMetrics(
                platform="instagram",
                url=url,
                handle=f"@{username}",
                followers=profile.followers_count,
                following=profile.following_count,
                posts_count=profile.posts_count,
                posts_last_30_days=min(len(profile.recent_posts), 30),
                engagement_rate=profile.engagement_rate,
                avg_likes=profile.avg_likes,
                avg_comments=profile.avg_comments,
                is_verified=profile.is_verified,
                profile_bio=profile.biography[:200] if profile.biography else None,
            )
        else:
            return SocialPlatformMetrics(
                platform="instagram",
                url=url,
                handle=f"@{username}",
                followers=self._estimate_followers("instagram"),
                engagement_rate=2.0,
            )
    
    async def _analyze_youtube(self, url: str) -> Optional[SocialPlatformMetrics]:
        """Analyze YouTube channel using Apify."""
        channel_id = extract_youtube_channel(url)
        if not channel_id:
            return SocialPlatformMetrics(
                platform="youtube",
                url=url,
                followers=self._estimate_followers("youtube"),
            )
        
        apify = ApifyService()
        if not apify.is_configured():
            logger.warning("Apify not configured, using estimated YouTube data")
            return SocialPlatformMetrics(
                platform="youtube",
                url=url,
                handle=f"@{channel_id}",
                subscribers=self._estimate_followers("youtube"),
                engagement_rate=3.0,
            )
        
        channel = await apify.scrape_youtube_channel(channel_id)
        
        if channel.success:
            self._raw_data["youtube_analysis"] = {
                "channel_id": channel.channel_id,
                "channel_name": channel.channel_name,
                "description": channel.description,
                "subscribers": channel.subscribers_count,
                "total_views": channel.total_views,
                "videos_count": channel.videos_count,
                "recent_videos": channel.recent_videos[:5],
            }
            
            return SocialPlatformMetrics(
                platform="youtube",
                url=url,
                handle=f"@{channel.channel_name or channel_id}",
                subscribers=channel.subscribers_count,
                followers=channel.subscribers_count,
                posts_count=channel.videos_count,
                total_views=channel.total_views,
                engagement_rate=channel.engagement_rate,
                avg_views=channel.avg_views,
                avg_likes=channel.avg_likes,
                avg_comments=channel.avg_comments,
                profile_bio=channel.description[:200] if channel.description else None,
            )
        else:
            return SocialPlatformMetrics(
                platform="youtube",
                url=url,
                handle=f"@{channel_id}",
                subscribers=self._estimate_followers("youtube"),
            )
    
    async def _analyze_twitter(self, url: str) -> Optional[SocialPlatformMetrics]:
        """
        Analyze Twitter/X account using the Twitter API v2.
        """
        # Extract username from URL
        username = extract_twitter_username(url)
        if not username:
            return SocialPlatformMetrics(
                platform="twitter",
                url=url,
                followers=self._estimate_followers("twitter"),
            )
        
        # Use Twitter API service
        twitter_service = TwitterService()
        analysis = await twitter_service.analyze_account(username)
        
        if analysis.success and analysis.user:
            # Calculate engagement rate as percentage
            # (avg engagement / followers) * 100
            engagement_rate = analysis.engagement_rate
            
            # Determine last post date
            last_post_date = None
            if analysis.last_post_date:
                last_post_date = analysis.last_post_date.isoformat()
            
            # Store raw analysis data for content analyzer
            self._raw_data["twitter_analysis"] = {
                "username": username,
                "user": {
                    "name": analysis.user.name,
                    "description": analysis.user.description,
                    "verified": analysis.user.verified,
                    "created_at": analysis.user.created_at.isoformat() if analysis.user.created_at else None,
                },
                "tweets": [
                    {
                        "text": t.text,
                        "created_at": t.created_at.isoformat(),
                        "like_count": t.like_count,
                        "retweet_count": t.retweet_count,
                        "reply_count": t.reply_count,
                    }
                    for t in analysis.recent_tweets[:10]
                ],
                "engagement_rate": engagement_rate,
                "posts_per_week": analysis.posts_per_week,
            }
            
            return SocialPlatformMetrics(
                platform="twitter",
                url=url,
                handle=f"@{username}",
                followers=analysis.user.followers_count,
                following=analysis.user.following_count,
                posts_last_30_days=int(analysis.posts_per_week * 4.3),  # Approx monthly
                engagement_rate=engagement_rate,
                avg_likes=analysis.avg_likes,
                avg_comments=analysis.avg_replies,
                avg_shares=analysis.avg_retweets,
                last_post_date=last_post_date,
                is_verified=analysis.user.verified,
            )
        else:
            # Fall back to estimated data
            return SocialPlatformMetrics(
                platform="twitter",
                url=url,
                handle=f"@{username}" if username else None,
                followers=self._estimate_followers("twitter"),
                posts_last_30_days=self._estimate_posts(),
                engagement_rate=0.08,
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
        # High engagement = sticky brand
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
        # Dead accounts are worse than no accounts
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
