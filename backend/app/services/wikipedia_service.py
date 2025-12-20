# =============================================================================
# Wikipedia API Service
# =============================================================================
# This service handles interactions with Wikipedia's free REST API.
# It provides brand presence checks, article summaries, and notability signals.
# No API key required.
# =============================================================================

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from urllib.parse import quote
import httpx
import logging

logger = logging.getLogger(__name__)


@dataclass
class WikipediaArticle:
    """A Wikipedia article."""

    title: str
    page_id: int
    extract: str = ""  # Summary text
    description: str = ""  # Short description
    url: str = ""
    thumbnail_url: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    is_disambiguation: bool = False
    is_redirect: bool = False
    content_length: int = 0  # Approximate article length


@dataclass
class WikipediaPresence:
    """Analysis of a brand's Wikipedia presence."""

    success: bool
    brand_name: str
    has_wikipedia_page: bool = False
    article: Optional[WikipediaArticle] = None

    # Alternative mentions
    mentioned_in_other_articles: List[str] = field(default_factory=list)
    related_articles: List[str] = field(default_factory=list)

    # Notability signals
    notability_score: float = 0  # 0-100
    signals: List[str] = field(default_factory=list)

    error: Optional[str] = None


class WikipediaService:
    """
    Service for interacting with Wikipedia's API.

    This service provides:
    - Brand page existence check
    - Article summary retrieval
    - Notability signals analysis
    - Related article discovery

    Uses the free Wikipedia REST API (no key required).

    Usage:
        service = WikipediaService()
        presence = await service.check_brand_presence("Apple Inc")
    """

    # Wikipedia REST API endpoints
    SUMMARY_API = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
    SEARCH_API = "https://en.wikipedia.org/w/api.php"
    TIMEOUT = 15

    async def check_brand_presence(
        self,
        brand_name: str,
        include_search: bool = True,
    ) -> WikipediaPresence:
        """
        Check if a brand has a Wikipedia presence.

        Args:
            brand_name: Name of the brand to search
            include_search: Whether to search for mentions if no direct page

        Returns:
            WikipediaPresence: Complete presence analysis
        """
        if not brand_name:
            return WikipediaPresence(
                success=False,
                brand_name=brand_name,
                error="No brand name provided",
            )

        # Step 1: Try to get direct article
        article = await self._get_article(brand_name)

        if article and not article.is_disambiguation:
            # Found a direct article
            signals = self._analyze_notability_signals(article)
            notability_score = self._calculate_notability_score(article, signals)

            return WikipediaPresence(
                success=True,
                brand_name=brand_name,
                has_wikipedia_page=True,
                article=article,
                notability_score=notability_score,
                signals=signals,
            )

        # Step 2: Search for mentions if no direct page
        mentioned_in = []
        related = []

        if include_search:
            search_results = await self._search(brand_name)

            for result in search_results[:5]:
                title = result.get("title", "")
                snippet = result.get("snippet", "").lower()

                if brand_name.lower() in snippet:
                    mentioned_in.append(title)
                else:
                    related.append(title)

        # Calculate score without direct page
        notability_score = 0
        signals = []

        if mentioned_in:
            notability_score += len(mentioned_in) * 5
            signals.append(f"Mentioned in {len(mentioned_in)} Wikipedia articles")

        if article and article.is_disambiguation:
            notability_score += 10
            signals.append("Has a disambiguation page (name is notable)")

        return WikipediaPresence(
            success=True,
            brand_name=brand_name,
            has_wikipedia_page=False,
            article=article if article and article.is_disambiguation else None,
            mentioned_in_other_articles=mentioned_in,
            related_articles=related,
            notability_score=min(notability_score, 40),  # Cap without direct page
            signals=signals if signals else ["No Wikipedia presence detected"],
        )

    async def _get_article(self, title: str) -> Optional[WikipediaArticle]:
        """
        Get a Wikipedia article by title.

        Args:
            title: Article title

        Returns:
            WikipediaArticle or None
        """
        # Clean and encode title
        title = title.strip().replace(" ", "_")
        url = self.SUMMARY_API.format(title=quote(title))

        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(
                    url,
                    headers={"Accept": "application/json"},
                )

                if response.status_code == 200:
                    data = response.json()

                    # Check article type
                    article_type = data.get("type", "")
                    is_disambiguation = article_type == "disambiguation"
                    is_redirect = "redirects" in data

                    # Get thumbnail
                    thumbnail = data.get("thumbnail", {})
                    thumbnail_url = thumbnail.get("source") if thumbnail else None

                    return WikipediaArticle(
                        title=data.get("title", title),
                        page_id=data.get("pageid", 0),
                        extract=data.get("extract", ""),
                        description=data.get("description", ""),
                        url=data.get("content_urls", {})
                        .get("desktop", {})
                        .get("page", ""),
                        thumbnail_url=thumbnail_url,
                        is_disambiguation=is_disambiguation,
                        is_redirect=is_redirect,
                        content_length=len(data.get("extract", "")),
                    )

                elif response.status_code == 404:
                    # Article doesn't exist
                    return None

                else:
                    logger.error(f"Wikipedia API error: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"Wikipedia article fetch failed: {e}")
            return None

    async def _search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search Wikipedia for articles matching a query.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of search results
        """
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": limit,
            "format": "json",
            "utf8": 1,
        }

        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(
                    self.SEARCH_API,
                    params=params,
                )

                if response.status_code == 200:
                    data = response.json()
                    return data.get("query", {}).get("search", [])

                return []

        except Exception as e:
            logger.error(f"Wikipedia search failed: {e}")
            return []

    async def get_article_categories(self, title: str) -> List[str]:
        """
        Get categories for a Wikipedia article.

        Args:
            title: Article title

        Returns:
            List of category names
        """
        params = {
            "action": "query",
            "titles": title,
            "prop": "categories",
            "cllimit": 50,
            "format": "json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(
                    self.SEARCH_API,
                    params=params,
                )

                if response.status_code == 200:
                    data = response.json()
                    pages = data.get("query", {}).get("pages", {})

                    for page_id, page_data in pages.items():
                        if page_id != "-1":
                            categories = page_data.get("categories", [])
                            return [
                                cat.get("title", "").replace("Category:", "")
                                for cat in categories
                            ]

                return []

        except Exception as e:
            logger.error(f"Wikipedia categories fetch failed: {e}")
            return []

    def _analyze_notability_signals(self, article: WikipediaArticle) -> List[str]:
        """Analyze signals of notability from the article."""
        signals = []

        # Check article length
        if article.content_length > 500:
            signals.append("Has substantial article content")
        elif article.content_length > 200:
            signals.append("Has moderate article content")
        else:
            signals.append("Has brief article content")

        # Check for image
        if article.thumbnail_url:
            signals.append("Has image/logo in Wikipedia")

        # Check description quality
        if article.description and len(article.description) > 20:
            signals.append("Has detailed Wikipedia description")

        return signals

    def _calculate_notability_score(
        self,
        article: WikipediaArticle,
        signals: List[str],
    ) -> float:
        """Calculate a notability score based on Wikipedia presence."""
        score = 50  # Base score for having an article

        # Content length bonus
        if article.content_length > 1000:
            score += 25
        elif article.content_length > 500:
            score += 15
        elif article.content_length > 200:
            score += 10

        # Image bonus
        if article.thumbnail_url:
            score += 10

        # Description bonus
        if article.description:
            score += 5

        # Not a disambiguation page
        if not article.is_disambiguation:
            score += 10

        return min(score, 100)


async def check_wikipedia_presence(brand_name: str) -> WikipediaPresence:
    """Quick function to check Wikipedia presence."""
    service = WikipediaService()
    return await service.check_brand_presence(brand_name)


async def get_article_summary(title: str) -> Optional[WikipediaArticle]:
    """Quick function to get an article summary."""
    service = WikipediaService()
    return await service._get_article(title)
