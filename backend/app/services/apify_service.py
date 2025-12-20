# =============================================================================
# Apify Service - Universal Social Media Scraping
# =============================================================================
# Purpose: Provides a unified interface for running Apify actors to scrape
#          social media platforms (Instagram, YouTube, Reddit, TikTok).
#
# Dependencies:
#   - apify-client: Official Apify Python client
#   - httpx: For async HTTP requests (fallback)
#
# Architecture Notes:
#   - Each platform has a dedicated method with platform-specific input schemas
#   - Results are normalized into dataclasses for consistent downstream usage
#   - Includes cost controls (max_items) to prevent runaway API costs
#   - Caching is handled at the analyzer level, not here
#
# Supported Actors:
#   - Instagram: apify/instagram-scraper
#   - YouTube: streamers/youtube-channel-scraper
#   - Reddit: trudax/reddit-scraper
#   - TikTok: clockworks/tiktok-scraper (deferred)
#
# Usage:
#     service = ApifyService()
#     profile = await service.scrape_instagram_profile("nike")
#     channel = await service.scrape_youtube_channel("mkbhd")
#     mentions = await service.scrape_reddit_mentions("bitcoin")
# =============================================================================

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging
import re

from app.config import settings

logger = logging.getLogger(__name__)


# =============================================================================
# Data Models
# =============================================================================


@dataclass
class InstagramProfile:
    """Instagram profile data from Apify scraper."""

    success: bool
    username: str
    full_name: Optional[str] = None
    biography: Optional[str] = None
    followers_count: int = 0
    following_count: int = 0
    posts_count: int = 0
    is_verified: bool = False
    is_business: bool = False
    profile_pic_url: Optional[str] = None
    external_url: Optional[str] = None
    recent_posts: List[Dict[str, Any]] = field(default_factory=list)
    avg_likes: float = 0
    avg_comments: float = 0
    engagement_rate: float = 0
    error: Optional[str] = None


@dataclass
class InstagramPost:
    """Single Instagram post data."""

    id: str
    shortcode: str
    caption: Optional[str] = None
    likes_count: int = 0
    comments_count: int = 0
    timestamp: Optional[datetime] = None
    is_video: bool = False
    video_view_count: int = 0
    url: Optional[str] = None


@dataclass
class YouTubeChannel:
    """YouTube channel data from Apify scraper."""

    success: bool
    channel_id: str
    channel_name: Optional[str] = None
    description: Optional[str] = None
    subscribers_count: int = 0
    videos_count: int = 0
    total_views: int = 0
    joined_date: Optional[str] = None
    country: Optional[str] = None
    channel_url: Optional[str] = None
    recent_videos: List[Dict[str, Any]] = field(default_factory=list)
    avg_views: float = 0
    avg_likes: float = 0
    avg_comments: float = 0
    engagement_rate: float = 0
    error: Optional[str] = None


@dataclass
class YouTubeVideo:
    """Single YouTube video data."""

    id: str
    title: str
    description: Optional[str] = None
    views_count: int = 0
    likes_count: int = 0
    comments_count: int = 0
    published_at: Optional[datetime] = None
    duration: Optional[str] = None
    url: Optional[str] = None


@dataclass
class RedditMention:
    """Single Reddit post/comment mentioning the brand."""

    id: str
    subreddit: str
    author: str
    title: Optional[str] = None
    body: Optional[str] = None
    score: int = 0
    num_comments: int = 0
    created_at: Optional[datetime] = None
    url: Optional[str] = None
    is_post: bool = True  # False if it's a comment


@dataclass
class RedditAnalysis:
    """Reddit brand mention analysis from Apify scraper."""

    success: bool
    query: str
    total_mentions: int = 0
    mentions: List[RedditMention] = field(default_factory=list)
    subreddits: List[str] = field(default_factory=list)
    avg_score: float = 0
    avg_comments: float = 0
    sentiment_positive: int = 0
    sentiment_negative: int = 0
    sentiment_neutral: int = 0
    top_subreddits: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None


# =============================================================================
# Apify Service
# =============================================================================


class ApifyService:
    """
    Universal Apify actor runner for social media scraping.

    Provides methods to scrape Instagram profiles, YouTube channels,
    and Reddit mentions using Apify's actor ecosystem.

    Attributes:
        api_token: Apify API token for authentication
        timeout: Maximum wait time for actor runs (seconds)

    Cost Controls:
        - Instagram: max 50 posts per profile (~$0.50-1.00)
        - YouTube: max 20 videos per channel (~$0.30-0.50)
        - Reddit: max 100 mentions per search (~$0.20-0.40)
    """

    # Actor IDs for each platform
    ACTORS = {
        "instagram": "apify/instagram-scraper",
        "youtube": "streamers/youtube-channel-scraper",
        "reddit": "trudax/reddit-scraper",
        "tiktok": "clockworks/tiktok-scraper",
    }

    # Default limits to control costs
    DEFAULT_LIMITS = {
        "instagram_posts": 50,
        "youtube_videos": 20,
        "reddit_mentions": 100,
        "tiktok_videos": 30,
    }

    def __init__(
        self,
        api_token: Optional[str] = None,
        timeout: int = 120,
    ):
        """
        Initialize the Apify service.

        Args:
            api_token: Apify API token. Falls back to settings.APIFY_API_TOKEN
            timeout: Maximum wait time for actor runs in seconds
        """
        self.api_token = api_token or getattr(settings, "APIFY_API_TOKEN", None)
        self.timeout = timeout
        self._client = None

    def _get_client(self):
        """
        Lazily initialize the Apify client.

        Returns:
            ApifyClient instance or None if token not configured
        """
        if not self.api_token:
            return None

        if self._client is None:
            try:
                from apify_client import ApifyClient

                self._client = ApifyClient(token=self.api_token)
            except ImportError:
                logger.error(
                    "apify-client not installed. Run: pip install apify-client"
                )
                return None

        return self._client

    # =========================================================================
    # Instagram Scraping
    # =========================================================================

    async def scrape_instagram_profile(
        self,
        username: str,
        max_posts: int = 50,
    ) -> InstagramProfile:
        """
        Scrape an Instagram profile using Apify.

        Args:
            username: Instagram username (without @)
            max_posts: Maximum number of recent posts to fetch

        Returns:
            InstagramProfile with profile data and recent posts

        Note:
            Estimated cost: ~$0.50-1.00 per profile with 50 posts
        """
        username = username.lstrip("@").lower()

        client = self._get_client()
        if not client:
            logger.warning("Apify not configured, returning mock Instagram data")
            return self._get_mock_instagram(username)

        try:
            # Run the Instagram scraper actor
            run_input = {
                "directUrls": [f"https://www.instagram.com/{username}/"],
                "resultsType": "posts",
                "resultsLimit": min(max_posts, self.DEFAULT_LIMITS["instagram_posts"]),
                "searchType": "user",
                "searchLimit": 1,
            }

            logger.info(f"Starting Instagram scrape for @{username}")

            # Run actor synchronously (blocking)
            # We use asyncio.to_thread to not block the event loop
            run = await asyncio.to_thread(
                client.actor(self.ACTORS["instagram"]).call,
                run_input=run_input,
                timeout_secs=self.timeout,
            )

            # Fetch results from dataset
            items = await asyncio.to_thread(
                lambda: list(client.dataset(run["defaultDatasetId"]).iterate_items())
            )

            if not items:
                return InstagramProfile(
                    success=False,
                    username=username,
                    error="No data returned from Instagram scraper",
                )

            # Parse the results
            return self._parse_instagram_results(username, items)

        except Exception as e:
            logger.error(f"Instagram scrape failed for @{username}: {e}")
            return InstagramProfile(
                success=False,
                username=username,
                error=str(e),
            )

    def _parse_instagram_results(
        self,
        username: str,
        items: List[Dict[str, Any]],
    ) -> InstagramProfile:
        """Parse raw Apify Instagram results into InstagramProfile."""
        # Find the profile data (first item usually contains user info)
        profile_data = {}
        posts = []

        for item in items:
            if item.get("type") == "user" or "followersCount" in item:
                profile_data = item
            elif item.get("type") == "post" or "likesCount" in item:
                posts.append(item)

        # If no explicit profile data, try to extract from posts
        if not profile_data and posts:
            first_post = posts[0]
            profile_data = first_post.get("ownerUser", first_post.get("owner", {}))

        # Calculate engagement metrics
        total_likes = sum(p.get("likesCount", 0) for p in posts)
        total_comments = sum(p.get("commentsCount", 0) for p in posts)
        num_posts = len(posts) if posts else 1

        avg_likes = total_likes / num_posts
        avg_comments = total_comments / num_posts

        followers = profile_data.get("followersCount", 0)
        engagement_rate = (
            ((avg_likes + avg_comments) / max(followers, 1)) * 100 if followers else 0
        )

        # Build recent posts list
        recent_posts = []
        for p in posts[:20]:  # Keep top 20 for analysis
            recent_posts.append(
                {
                    "id": p.get("id", ""),
                    "shortcode": p.get("shortCode", p.get("shortcode", "")),
                    "caption": p.get("caption", "")[:500] if p.get("caption") else None,
                    "likes": p.get("likesCount", 0),
                    "comments": p.get("commentsCount", 0),
                    "timestamp": p.get("timestamp", p.get("takenAt")),
                    "is_video": p.get("type") == "Video" or p.get("isVideo", False),
                    "views": p.get("videoViewCount", 0),
                }
            )

        return InstagramProfile(
            success=True,
            username=username,
            full_name=profile_data.get("fullName", profile_data.get("full_name")),
            biography=profile_data.get("biography", profile_data.get("bio")),
            followers_count=profile_data.get(
                "followersCount", profile_data.get("follower_count", 0)
            ),
            following_count=profile_data.get(
                "followingCount", profile_data.get("following_count", 0)
            ),
            posts_count=profile_data.get(
                "postsCount", profile_data.get("media_count", len(posts))
            ),
            is_verified=profile_data.get(
                "verified", profile_data.get("is_verified", False)
            ),
            is_business=profile_data.get(
                "isBusinessAccount", profile_data.get("is_business", False)
            ),
            profile_pic_url=profile_data.get(
                "profilePicUrl", profile_data.get("profile_pic_url")
            ),
            external_url=profile_data.get(
                "externalUrl", profile_data.get("external_url")
            ),
            recent_posts=recent_posts,
            avg_likes=round(avg_likes, 1),
            avg_comments=round(avg_comments, 1),
            engagement_rate=round(engagement_rate, 4),
        )

    def _get_mock_instagram(self, username: str) -> InstagramProfile:
        """Return mock Instagram data for development."""
        return InstagramProfile(
            success=True,
            username=username,
            full_name=f"{username.capitalize()} Official",
            biography="Building amazing products. Join us on our journey!",
            followers_count=15000,
            following_count=500,
            posts_count=250,
            is_verified=False,
            is_business=True,
            recent_posts=[
                {
                    "id": "1",
                    "likes": 500,
                    "comments": 25,
                    "caption": "New product launch!",
                },
                {
                    "id": "2",
                    "likes": 350,
                    "comments": 18,
                    "caption": "Behind the scenes",
                },
            ],
            avg_likes=425,
            avg_comments=21.5,
            engagement_rate=2.97,
        )

    # =========================================================================
    # YouTube Scraping
    # =========================================================================

    async def scrape_youtube_channel(
        self,
        channel_identifier: str,
        max_videos: int = 20,
    ) -> YouTubeChannel:
        """
        Scrape a YouTube channel using Apify.

        Args:
            channel_identifier: YouTube channel URL, handle (@name), or channel ID
            max_videos: Maximum number of recent videos to fetch

        Returns:
            YouTubeChannel with channel data and recent videos

        Note:
            Estimated cost: ~$0.30-0.50 per channel with 20 videos
        """
        # Normalize the identifier to a URL
        channel_url = self._normalize_youtube_url(channel_identifier)

        client = self._get_client()
        if not client:
            logger.warning("Apify not configured, returning mock YouTube data")
            return self._get_mock_youtube(channel_identifier)

        try:
            run_input = {
                "startUrls": [{"url": channel_url}],
                "maxResults": min(max_videos, self.DEFAULT_LIMITS["youtube_videos"]),
                "maxResultsShorts": 0,  # Skip shorts
                "maxResultStreams": 0,  # Skip streams
            }

            logger.info(f"Starting YouTube scrape for {channel_url}")

            run = await asyncio.to_thread(
                client.actor(self.ACTORS["youtube"]).call,
                run_input=run_input,
                timeout_secs=self.timeout,
            )

            items = await asyncio.to_thread(
                lambda: list(client.dataset(run["defaultDatasetId"]).iterate_items())
            )

            if not items:
                return YouTubeChannel(
                    success=False,
                    channel_id=channel_identifier,
                    error="No data returned from YouTube scraper",
                )

            return self._parse_youtube_results(channel_identifier, items)

        except Exception as e:
            logger.error(f"YouTube scrape failed for {channel_identifier}: {e}")
            return YouTubeChannel(
                success=False,
                channel_id=channel_identifier,
                error=str(e),
            )

    def _normalize_youtube_url(self, identifier: str) -> str:
        """Convert various YouTube identifiers to a channel URL."""
        identifier = identifier.strip()

        # Already a URL
        if "youtube.com" in identifier or "youtu.be" in identifier:
            return identifier

        # Handle @username format
        if identifier.startswith("@"):
            return f"https://www.youtube.com/{identifier}"

        # Assume it's a channel ID or name
        if identifier.startswith("UC") and len(identifier) == 24:
            return f"https://www.youtube.com/channel/{identifier}"

        # Try as a custom URL
        return f"https://www.youtube.com/@{identifier}"

    def _parse_youtube_results(
        self,
        channel_id: str,
        items: List[Dict[str, Any]],
    ) -> YouTubeChannel:
        """Parse raw Apify YouTube results into YouTubeChannel."""
        # Find channel info (usually in the first item or separate)
        channel_data = {}
        videos = []

        for item in items:
            if item.get("type") == "channel" or "subscriberCount" in item:
                channel_data = item
            elif item.get("type") == "video" or "viewCount" in item:
                videos.append(item)

        # If no explicit channel data, try to extract from videos
        if not channel_data and videos:
            first_video = videos[0]
            channel_data = first_video.get("channel", {})

        # Calculate engagement metrics
        total_views = sum(v.get("viewCount", 0) for v in videos)
        total_likes = sum(v.get("likeCount", 0) for v in videos)
        total_comments = sum(v.get("commentCount", 0) for v in videos)
        num_videos = len(videos) if videos else 1

        avg_views = total_views / num_videos
        avg_likes = total_likes / num_videos
        avg_comments = total_comments / num_videos

        # Engagement rate for YouTube: (likes + comments) / views
        engagement_rate = ((avg_likes + avg_comments) / max(avg_views, 1)) * 100

        # Build recent videos list
        recent_videos = []
        for v in videos[:20]:
            recent_videos.append(
                {
                    "id": v.get("id", ""),
                    "title": v.get("title", ""),
                    "views": v.get("viewCount", 0),
                    "likes": v.get("likeCount", 0),
                    "comments": v.get("commentCount", 0),
                    "published": v.get("date", v.get("publishedAt")),
                    "duration": v.get("duration"),
                    "url": v.get("url"),
                }
            )

        return YouTubeChannel(
            success=True,
            channel_id=channel_data.get("id", channel_id),
            channel_name=channel_data.get("name", channel_data.get("title")),
            description=channel_data.get("description", "")[:500]
            if channel_data.get("description")
            else None,
            subscribers_count=channel_data.get(
                "subscriberCount", channel_data.get("subscribers", 0)
            ),
            videos_count=channel_data.get("videoCount", len(videos)),
            total_views=channel_data.get("viewCount", total_views),
            joined_date=channel_data.get("joinedDate"),
            country=channel_data.get("country"),
            channel_url=channel_data.get("url"),
            recent_videos=recent_videos,
            avg_views=round(avg_views, 1),
            avg_likes=round(avg_likes, 1),
            avg_comments=round(avg_comments, 1),
            engagement_rate=round(engagement_rate, 4),
        )

    def _get_mock_youtube(self, channel_id: str) -> YouTubeChannel:
        """Return mock YouTube data for development."""
        return YouTubeChannel(
            success=True,
            channel_id=channel_id,
            channel_name=f"{channel_id.capitalize()} Channel",
            description="Creating awesome content for you!",
            subscribers_count=50000,
            videos_count=200,
            total_views=5000000,
            recent_videos=[
                {
                    "id": "1",
                    "title": "Latest Update",
                    "views": 25000,
                    "likes": 1500,
                    "comments": 200,
                },
                {
                    "id": "2",
                    "title": "Product Review",
                    "views": 18000,
                    "likes": 1200,
                    "comments": 150,
                },
            ],
            avg_views=21500,
            avg_likes=1350,
            avg_comments=175,
            engagement_rate=7.1,
        )

    # =========================================================================
    # Reddit Scraping
    # =========================================================================

    async def scrape_reddit_mentions(
        self,
        query: str,
        max_results: int = 100,
        subreddits: Optional[List[str]] = None,
    ) -> RedditAnalysis:
        """
        Search Reddit for brand mentions using Apify.

        Args:
            query: Search query (brand name)
            max_results: Maximum number of mentions to fetch
            subreddits: Optional list of subreddits to search in

        Returns:
            RedditAnalysis with mentions and sentiment breakdown

        Note:
            Estimated cost: ~$0.20-0.40 per search with 100 results
        """
        client = self._get_client()
        if not client:
            logger.warning("Apify not configured, returning mock Reddit data")
            return self._get_mock_reddit(query)

        try:
            run_input = {
                "searches": [query],
                "maxItems": min(max_results, self.DEFAULT_LIMITS["reddit_mentions"]),
                "maxPostCount": min(
                    max_results, self.DEFAULT_LIMITS["reddit_mentions"]
                ),
                "maxComments": 0,  # Skip comment threads for now
                "sort": "relevance",
                "time": "year",  # Look back 1 year
            }

            # Add subreddit filter if provided
            if subreddits:
                run_input["subreddits"] = subreddits

            logger.info(f"Starting Reddit scrape for '{query}'")

            run = await asyncio.to_thread(
                client.actor(self.ACTORS["reddit"]).call,
                run_input=run_input,
                timeout_secs=self.timeout,
            )

            items = await asyncio.to_thread(
                lambda: list(client.dataset(run["defaultDatasetId"]).iterate_items())
            )

            if not items:
                return RedditAnalysis(
                    success=True,  # No mentions is still a valid result
                    query=query,
                    total_mentions=0,
                )

            return self._parse_reddit_results(query, items)

        except Exception as e:
            logger.error(f"Reddit scrape failed for '{query}': {e}")
            return RedditAnalysis(
                success=False,
                query=query,
                error=str(e),
            )

    def _parse_reddit_results(
        self,
        query: str,
        items: List[Dict[str, Any]],
    ) -> RedditAnalysis:
        """Parse raw Apify Reddit results into RedditAnalysis."""
        mentions = []
        subreddit_counts: Dict[str, int] = {}
        total_score = 0
        total_comments = 0

        for item in items:
            subreddit = item.get("subreddit", item.get("communityName", "unknown"))

            # Count subreddit occurrences
            subreddit_counts[subreddit] = subreddit_counts.get(subreddit, 0) + 1

            score = item.get("score", item.get("upvotes", 0))
            num_comments = item.get("numberOfComments", item.get("numComments", 0))

            total_score += score
            total_comments += num_comments

            # Parse timestamp
            created_at = None
            if item.get("createdAt"):
                try:
                    created_at = datetime.fromisoformat(
                        item["createdAt"].replace("Z", "+00:00")
                    )
                except (ValueError, AttributeError):
                    pass

            mentions.append(
                RedditMention(
                    id=item.get("id", ""),
                    subreddit=subreddit,
                    title=item.get("title", ""),
                    body=item.get("body", item.get("text", ""))[:500]
                    if item.get("body") or item.get("text")
                    else None,
                    author=item.get("username", item.get("author", "unknown")),
                    score=score,
                    num_comments=num_comments,
                    created_at=created_at,
                    url=item.get("url", item.get("permalink")),
                    is_post=item.get("dataType", "post") == "post",
                )
            )

        # Calculate averages
        num_mentions = len(mentions) if mentions else 1
        avg_score = total_score / num_mentions
        avg_comments = total_comments / num_mentions

        # Get top subreddits
        top_subreddits = sorted(
            [{"name": k, "count": v} for k, v in subreddit_counts.items()],
            key=lambda x: x["count"],
            reverse=True,
        )[:10]

        # Basic sentiment analysis based on score
        # (In production, you'd use NLP here)
        sentiment_positive = sum(1 for m in mentions if m.score > 10)
        sentiment_negative = sum(1 for m in mentions if m.score < 0)
        sentiment_neutral = len(mentions) - sentiment_positive - sentiment_negative

        return RedditAnalysis(
            success=True,
            query=query,
            total_mentions=len(mentions),
            mentions=mentions[:50],  # Keep top 50 for analysis
            subreddits=list(subreddit_counts.keys()),
            avg_score=round(avg_score, 1),
            avg_comments=round(avg_comments, 1),
            sentiment_positive=sentiment_positive,
            sentiment_negative=sentiment_negative,
            sentiment_neutral=sentiment_neutral,
            top_subreddits=top_subreddits,
        )

    def _get_mock_reddit(self, query: str) -> RedditAnalysis:
        """Return mock Reddit data for development."""
        return RedditAnalysis(
            success=True,
            query=query,
            total_mentions=25,
            mentions=[
                RedditMention(
                    id="1",
                    subreddit="technology",
                    title=f"Discussion about {query}",
                    body="Really interesting product...",
                    author="user123",
                    score=150,
                    num_comments=45,
                    is_post=True,
                ),
            ],
            subreddits=["technology", "startups", "Entrepreneur"],
            avg_score=85,
            avg_comments=25,
            sentiment_positive=15,
            sentiment_negative=3,
            sentiment_neutral=7,
            top_subreddits=[
                {"name": "technology", "count": 10},
                {"name": "startups", "count": 8},
            ],
        )

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def is_configured(self) -> bool:
        """Check if the Apify service is properly configured."""
        return bool(self.api_token)


# =============================================================================
# Helper Functions
# =============================================================================


def extract_instagram_username(url_or_username: str) -> Optional[str]:
    """
    Extract Instagram username from URL or raw username.

    Args:
        url_or_username: Instagram URL or username

    Returns:
        Cleaned username or None
    """
    if not url_or_username:
        return None

    text = url_or_username.strip()

    patterns = [
        r"instagram\.com/([a-zA-Z0-9_.]+)",
        r"@([a-zA-Z0-9_.]+)",
        r"^([a-zA-Z0-9_.]+)$",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            username = match.group(1)
            # Filter out common non-usernames
            if username.lower() not in ["p", "reel", "stories", "explore", "direct"]:
                return username.lower()

    return None


def extract_youtube_channel(url_or_identifier: str) -> Optional[str]:
    """
    Extract YouTube channel identifier from URL or raw identifier.

    Args:
        url_or_identifier: YouTube URL, @handle, or channel ID

    Returns:
        Cleaned identifier or None
    """
    if not url_or_identifier:
        return None

    text = url_or_identifier.strip()

    patterns = [
        r"youtube\.com/@([a-zA-Z0-9_-]+)",
        r"youtube\.com/channel/([a-zA-Z0-9_-]+)",
        r"youtube\.com/c/([a-zA-Z0-9_-]+)",
        r"youtube\.com/user/([a-zA-Z0-9_-]+)",
        r"@([a-zA-Z0-9_-]+)",
        r"^(UC[a-zA-Z0-9_-]{22})$",  # Channel ID format
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)

    # If no pattern matched, return as-is if it looks valid
    if re.match(r"^[a-zA-Z0-9_-]+$", text):
        return text

    return None


# =============================================================================
# Convenience Functions
# =============================================================================


async def scrape_instagram(username: str) -> InstagramProfile:
    """Quick function to scrape an Instagram profile."""
    service = ApifyService()
    return await service.scrape_instagram_profile(username)


async def scrape_youtube(channel: str) -> YouTubeChannel:
    """Quick function to scrape a YouTube channel."""
    service = ApifyService()
    return await service.scrape_youtube_channel(channel)


async def scrape_reddit(query: str) -> RedditAnalysis:
    """Quick function to search Reddit for mentions."""
    service = ApifyService()
    return await service.scrape_reddit_mentions(query)
