# =============================================================================
# Twitter/X API v2 Service
# =============================================================================
# This service handles interactions with the Twitter/X API v2.
# It provides user profile data, tweets, and engagement metrics.
# =============================================================================

from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import httpx
import logging
import re

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class TwitterUser:
    """Twitter user profile data."""

    id: str
    username: str
    name: str
    description: str = ""
    followers_count: int = 0
    following_count: int = 0
    tweet_count: int = 0
    verified: bool = False
    profile_image_url: Optional[str] = None
    created_at: Optional[datetime] = None
    location: Optional[str] = None
    url: Optional[str] = None


@dataclass
class Tweet:
    """A single tweet."""

    id: str
    text: str
    created_at: datetime
    like_count: int = 0
    retweet_count: int = 0
    reply_count: int = 0
    quote_count: int = 0
    impression_count: int = 0
    has_media: bool = False
    has_links: bool = False
    is_retweet: bool = False
    is_reply: bool = False


@dataclass
class TwitterAnalysis:
    """Complete Twitter analysis for a user."""

    success: bool
    username: str
    user: Optional[TwitterUser] = None
    recent_tweets: List[Tweet] = field(default_factory=list)

    # Engagement metrics
    avg_likes: float = 0
    avg_retweets: float = 0
    avg_replies: float = 0
    engagement_rate: float = 0  # (likes + retweets + replies) / followers

    # Posting patterns
    posts_per_week: float = 0
    last_post_date: Optional[datetime] = None
    days_since_last_post: int = 0

    # Content analysis
    tweet_types: Dict[str, int] = field(
        default_factory=dict
    )  # original, retweet, reply
    uses_media: bool = False
    uses_threads: bool = False

    error: Optional[str] = None


class TwitterService:
    """
    Service for interacting with Twitter/X API v2.

    This service provides:
    - User profile lookup
    - Recent tweets retrieval
    - Engagement metrics calculation
    - Posting pattern analysis

    Requires a Twitter API v2 Bearer Token from developer.twitter.com
    Free tier allows 500k tweet reads per month.

    Usage:
        service = TwitterService()
        analysis = await service.analyze_account("username")
    """

    API_BASE = "https://api.twitter.com/2"
    TIMEOUT = 20
    MAX_RETRIES = 2

    def __init__(self, bearer_token: Optional[str] = None):
        """
        Initialize the Twitter service.

        Args:
            bearer_token: Twitter API v2 Bearer Token. Falls back to settings.
        """
        self.bearer_token = bearer_token or getattr(
            settings, "TWITTER_BEARER_TOKEN", None
        )

    async def analyze_account(
        self,
        username: str,
        tweet_count: int = 10,
    ) -> TwitterAnalysis:
        """
        Perform complete analysis of a Twitter account.

        Args:
            username: Twitter username (without @)
            tweet_count: Number of recent tweets to analyze

        Returns:
            TwitterAnalysis: Complete account analysis
        """
        username = username.lstrip("@").lower()

        if not self.bearer_token:
            logger.warning("Twitter API not configured, using mock data")
            return self._get_mock_analysis(username)

        # Step 1: Get user profile
        user = await self._get_user(username)
        if not user:
            return TwitterAnalysis(
                success=False,
                username=username,
                error="User not found or API error",
            )

        # Step 2: Get recent tweets
        tweets = await self._get_user_tweets(user.id, tweet_count)

        # Step 3: Calculate metrics
        analysis = self._calculate_metrics(username, user, tweets)

        return analysis

    async def _get_user(self, username: str) -> Optional[TwitterUser]:
        """
        Get user profile by username.

        Args:
            username: Twitter username

        Returns:
            TwitterUser or None
        """
        url = f"{self.API_BASE}/users/by/username/{username}"
        params = {
            "user.fields": "created_at,description,location,profile_image_url,public_metrics,url,verified",
        }

        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(
                    url,
                    params=params,
                    headers={"Authorization": f"Bearer {self.bearer_token}"},
                )

                if response.status_code == 200:
                    data = response.json().get("data", {})
                    if not data:
                        return None

                    metrics = data.get("public_metrics", {})

                    created_at = None
                    if data.get("created_at"):
                        try:
                            created_at = datetime.fromisoformat(
                                data["created_at"].replace("Z", "+00:00")
                            )
                        except ValueError:
                            pass

                    return TwitterUser(
                        id=data["id"],
                        username=data["username"],
                        name=data.get("name", ""),
                        description=data.get("description", ""),
                        followers_count=metrics.get("followers_count", 0),
                        following_count=metrics.get("following_count", 0),
                        tweet_count=metrics.get("tweet_count", 0),
                        verified=data.get("verified", False),
                        profile_image_url=data.get("profile_image_url"),
                        created_at=created_at,
                        location=data.get("location"),
                        url=data.get("url"),
                    )

                elif response.status_code == 404:
                    logger.warning(f"Twitter user not found: {username}")
                    return None

                elif response.status_code == 429:
                    logger.warning("Twitter API rate limited")
                    return None

                else:
                    logger.error(f"Twitter API error: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"Twitter user lookup failed: {e}")
            return None

    async def _get_user_tweets(
        self,
        user_id: str,
        count: int = 10,
    ) -> List[Tweet]:
        """
        Get recent tweets for a user.

        Args:
            user_id: Twitter user ID
            count: Number of tweets to fetch

        Returns:
            List of Tweet objects
        """
        url = f"{self.API_BASE}/users/{user_id}/tweets"
        params = {
            "max_results": min(count, 100),
            "tweet.fields": "created_at,public_metrics,entities,referenced_tweets",
            "exclude": "retweets",  # Only get original tweets
        }

        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(
                    url,
                    params=params,
                    headers={"Authorization": f"Bearer {self.bearer_token}"},
                )

                if response.status_code == 200:
                    data = response.json()
                    tweets_data = data.get("data", [])

                    tweets = []
                    for t in tweets_data:
                        metrics = t.get("public_metrics", {})
                        entities = t.get("entities", {})
                        refs = t.get("referenced_tweets", [])

                        created_at = datetime.now()
                        if t.get("created_at"):
                            try:
                                created_at = datetime.fromisoformat(
                                    t["created_at"].replace("Z", "+00:00")
                                )
                            except ValueError:
                                pass

                        tweets.append(
                            Tweet(
                                id=t["id"],
                                text=t.get("text", ""),
                                created_at=created_at,
                                like_count=metrics.get("like_count", 0),
                                retweet_count=metrics.get("retweet_count", 0),
                                reply_count=metrics.get("reply_count", 0),
                                quote_count=metrics.get("quote_count", 0),
                                impression_count=metrics.get("impression_count", 0),
                                has_media=bool(entities.get("urls")),
                                has_links=bool(entities.get("urls")),
                                is_retweet=any(
                                    r.get("type") == "retweeted" for r in refs
                                ),
                                is_reply=any(
                                    r.get("type") == "replied_to" for r in refs
                                ),
                            )
                        )

                    return tweets

                else:
                    logger.error(f"Twitter tweets API error: {response.status_code}")
                    return []

        except Exception as e:
            logger.error(f"Twitter tweets lookup failed: {e}")
            return []

    def _calculate_metrics(
        self,
        username: str,
        user: TwitterUser,
        tweets: List[Tweet],
    ) -> TwitterAnalysis:
        """Calculate engagement and activity metrics."""
        now = datetime.now(
            tweets[0].created_at.tzinfo
            if tweets and tweets[0].created_at.tzinfo
            else None
        )

        # Calculate averages
        if tweets:
            avg_likes = sum(t.like_count for t in tweets) / len(tweets)
            avg_retweets = sum(t.retweet_count for t in tweets) / len(tweets)
            avg_replies = sum(t.reply_count for t in tweets) / len(tweets)

            # Engagement rate
            total_engagement = avg_likes + avg_retweets + avg_replies
            engagement_rate = (total_engagement / max(user.followers_count, 1)) * 100

            # Posting frequency
            oldest = min(t.created_at for t in tweets)
            newest = max(t.created_at for t in tweets)
            days_span = max((newest - oldest).days, 1)
            posts_per_week = (len(tweets) / days_span) * 7

            # Last post
            last_post_date = newest
            days_since_last_post = (
                (now.replace(tzinfo=None) - newest.replace(tzinfo=None)).days
                if newest
                else 0
            )

            # Tweet types
            original = sum(1 for t in tweets if not t.is_retweet and not t.is_reply)
            retweet_count = sum(1 for t in tweets if t.is_retweet)
            reply_count = sum(1 for t in tweets if t.is_reply)

            tweet_types = {
                "original": original,
                "retweet": retweet_count,
                "reply": reply_count,
            }

            # Content features
            uses_media = any(t.has_media for t in tweets)
        else:
            avg_likes = avg_retweets = avg_replies = 0
            engagement_rate = 0
            posts_per_week = 0
            last_post_date = None
            days_since_last_post = 999
            tweet_types = {}
            uses_media = False

        return TwitterAnalysis(
            success=True,
            username=username,
            user=user,
            recent_tweets=tweets,
            avg_likes=round(avg_likes, 1),
            avg_retweets=round(avg_retweets, 1),
            avg_replies=round(avg_replies, 1),
            engagement_rate=round(engagement_rate, 4),
            posts_per_week=round(posts_per_week, 1),
            last_post_date=last_post_date,
            days_since_last_post=days_since_last_post,
            tweet_types=tweet_types,
            uses_media=uses_media,
        )

    def _get_mock_analysis(self, username: str) -> TwitterAnalysis:
        """Return mock data for development."""
        now = datetime.now()

        mock_user = TwitterUser(
            id="123456789",
            username=username,
            name=f"{username.capitalize()} Official",
            description="Building the future of technology. Official account.",
            followers_count=15000,
            following_count=500,
            tweet_count=2500,
            verified=False,
            created_at=now - timedelta(days=365 * 3),
        )

        mock_tweets = [
            Tweet(
                id=str(i),
                text=f"Sample tweet #{i} about our exciting new features!",
                created_at=now - timedelta(days=i),
                like_count=50 + i * 10,
                retweet_count=10 + i * 2,
                reply_count=5 + i,
            )
            for i in range(10)
        ]

        return TwitterAnalysis(
            success=True,
            username=username,
            user=mock_user,
            recent_tweets=mock_tweets,
            avg_likes=95,
            avg_retweets=19,
            avg_replies=9.5,
            engagement_rate=0.82,
            posts_per_week=3.5,
            last_post_date=now,
            days_since_last_post=0,
            tweet_types={"original": 8, "retweet": 1, "reply": 1},
            uses_media=True,
        )


def extract_twitter_username(url_or_username: str) -> Optional[str]:
    """
    Extract Twitter username from URL or raw username.

    Args:
        url_or_username: Twitter URL or username

    Returns:
        Cleaned username or None
    """
    if not url_or_username:
        return None

    # Clean up
    text = url_or_username.strip()

    # Handle URLs
    patterns = [
        r"(?:twitter\.com|x\.com)/([a-zA-Z0-9_]+)",
        r"@([a-zA-Z0-9_]+)",
        r"^([a-zA-Z0-9_]+)$",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            username = match.group(1)
            # Filter out common non-usernames
            if username.lower() not in ["intent", "share", "search", "home", "explore"]:
                return username.lower()

    return None


# Convenience function
async def analyze_twitter_account(username: str) -> TwitterAnalysis:
    """Quick function to analyze a Twitter account."""
    service = TwitterService()
    return await service.analyze_account(username)
