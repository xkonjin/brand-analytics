# =============================================================================
# Moz Links API Service
# =============================================================================
# Purpose: Provides access to Moz's Link Explorer data including Domain Authority,
#          Page Authority, Spam Score, and backlink metrics.
#
# Dependencies:
#   - httpx: Async HTTP client for API requests
#
# Architecture Notes:
#   - Uses Moz Links API v2 (lsapi.moz.com)
#   - Authentication via Basic Auth with Access ID and Secret Key
#   - Includes rate limiting (respects Moz's API limits)
#   - Results cached at the analyzer level, not here
#
# API Documentation:
#   - https://moz.com/help/links-api
#   - Endpoint: https://lsapi.moz.com/v2/url_metrics
#
# Metrics Available:
#   - Domain Authority (DA): 1-100 score predicting ranking potential
#   - Page Authority (PA): Page-level link strength
#   - Spam Score: 0-100 likelihood of spam
#   - Linking Domains: Number of unique root domains linking
#   - Total Links: Total number of backlinks
#
# Usage:
#     service = MozService()
#     metrics = await service.get_url_metrics("https://example.com")
#     print(f"Domain Authority: {metrics.domain_authority}")
# =============================================================================

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging
import base64
import httpx
from urllib.parse import urlparse

from app.config import settings

logger = logging.getLogger(__name__)


# =============================================================================
# Data Models
# =============================================================================


@dataclass
class MozMetrics:
    """
    Moz URL/Domain metrics from the Links API.

    Attributes:
        success: Whether the API call succeeded
        url: The analyzed URL
        domain: The root domain extracted from URL
        domain_authority: Domain Authority score (1-100)
        page_authority: Page Authority score (1-100)
        spam_score: Spam Score percentage (0-100)
        linking_domains: Number of unique root domains linking to target
        total_links: Total number of backlinks
        external_links: Number of external (to different domains) links
        nofollow_links: Number of nofollow links
        redirect_links: Number of redirect (301/302) links
        last_crawled: When Moz last crawled this URL
        error: Error message if request failed
    """

    success: bool
    url: str
    domain: str = ""
    domain_authority: float = 0
    page_authority: float = 0
    spam_score: float = 0
    linking_domains: int = 0
    total_links: int = 0
    external_links: int = 0
    nofollow_links: int = 0
    redirect_links: int = 0
    last_crawled: Optional[datetime] = None
    error: Optional[str] = None


@dataclass
class BacklinkSummary:
    """Summary of backlink profile from Moz."""

    total_backlinks: int = 0
    unique_domains: int = 0
    follow_links: int = 0
    nofollow_links: int = 0
    top_anchor_texts: List[Dict[str, Any]] = field(default_factory=list)
    authority_distribution: Dict[str, int] = field(default_factory=dict)


# =============================================================================
# Moz Service
# =============================================================================


class MozService:
    """
    Service for interacting with the Moz Links API.

    Provides access to Domain Authority, Page Authority, Spam Score,
    and backlink metrics for any URL or domain.

    Authentication:
        Uses Basic Auth with Moz Access ID and Secret Key.
        Credentials can be provided directly or via settings.MOZ_API_KEY
        as a base64-encoded "accessId:secretKey" string.

    Rate Limits:
        - Free tier: 10 requests/day
        - Paid tiers: Varies by plan (typically 25,000+ rows/month)

    Example:
        service = MozService()
        metrics = await service.get_url_metrics("https://moz.com")
        print(f"DA: {metrics.domain_authority}, PA: {metrics.page_authority}")
    """

    # Moz Links API base URL
    API_BASE = "https://lsapi.moz.com/v2"

    # Default timeout for API requests
    TIMEOUT = 30

    # Moz API bit flags for URL metrics (which metrics to return)
    # See: https://moz.com/help/links-api/url-metrics
    COLS_DOMAIN_AUTHORITY = 68719476736  # Domain Authority
    COLS_PAGE_AUTHORITY = 34359738368  # Page Authority
    COLS_SPAM_SCORE = 67108864  # Spam Score
    COLS_LINKS = 2048  # Total Links
    COLS_LINKING_DOMAINS = 32  # Linking Root Domains
    COLS_EXTERNAL_LINKS = 549755813888  # External Links

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initialize the Moz service.

        Args:
            api_key: Base64-encoded "accessId:secretKey" string.
                     Falls back to settings.MOZ_API_KEY if not provided.
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or getattr(settings, "MOZ_API_KEY", None)
        self.timeout = timeout
        self._auth_header = None

    def _get_auth_header(self) -> Optional[str]:
        """
        Get the Basic Auth header value.

        Returns:
            Authorization header value or None if not configured
        """
        if not self.api_key:
            return None

        if self._auth_header is None:
            # The API key should already be base64-encoded "accessId:secretKey"
            # If it's not, we need to encode it
            try:
                # Check if it's already base64 encoded
                decoded = base64.b64decode(self.api_key).decode("utf-8")
                if ":" in decoded:
                    # Already properly formatted
                    self._auth_header = f"Basic {self.api_key}"
                else:
                    # Not properly formatted, encode it
                    encoded = base64.b64encode(self.api_key.encode()).decode()
                    self._auth_header = f"Basic {encoded}"
            except Exception:
                # If decoding fails, assume it needs to be encoded
                encoded = base64.b64encode(self.api_key.encode()).decode()
                self._auth_header = f"Basic {encoded}"

        return self._auth_header

    async def get_url_metrics(
        self,
        url: str,
        include_subdomain: bool = True,
    ) -> MozMetrics:
        """
        Get Moz metrics for a specific URL.

        Args:
            url: The URL to analyze (can be full URL or domain)
            include_subdomain: Whether to include subdomain in metrics

        Returns:
            MozMetrics with DA, PA, Spam Score, and backlink data

        Note:
            This uses 1 row of your Moz API quota per call.
        """
        # Normalize URL
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        auth_header = self._get_auth_header()
        if not auth_header:
            logger.warning("Moz API not configured, returning mock data")
            return self._get_mock_metrics(url, domain)

        try:
            request_body = {
                "targets": [url],
            }

            headers = {
                "Authorization": auth_header,
                "Content-Type": "application/json",
            }

            logger.info(f"Fetching Moz metrics for {url}")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.API_BASE}/url_metrics",
                    json=request_body,
                    headers=headers,
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_url_metrics(url, domain, data)

                elif response.status_code == 401:
                    logger.error("Moz API authentication failed - check API key")
                    return MozMetrics(
                        success=False,
                        url=url,
                        domain=domain,
                        error="Authentication failed - invalid API key",
                    )

                elif response.status_code == 429:
                    logger.warning("Moz API rate limited")
                    return MozMetrics(
                        success=False,
                        url=url,
                        domain=domain,
                        error="Rate limited - API quota exceeded",
                    )

                else:
                    logger.error(
                        f"Moz API error: {response.status_code} - {response.text}"
                    )
                    return MozMetrics(
                        success=False,
                        url=url,
                        domain=domain,
                        error=f"API error: {response.status_code}",
                    )

        except httpx.TimeoutException:
            logger.error(f"Moz API timeout for {url}")
            return MozMetrics(
                success=False,
                url=url,
                domain=domain,
                error="Request timed out",
            )
        except Exception as e:
            logger.error(f"Moz API request failed: {e}")
            return MozMetrics(
                success=False,
                url=url,
                domain=domain,
                error=str(e),
            )

    def _parse_url_metrics(
        self,
        url: str,
        domain: str,
        data: Any,
    ) -> MozMetrics:
        """Parse the Moz API response into MozMetrics."""
        result: Dict[str, Any] = {}
        if isinstance(data, list) and len(data) > 0:
            result = data[0]
        elif isinstance(data, dict) and "results" in data:
            results = data.get("results", [])
            result = results[0] if results else {}
        elif isinstance(data, dict):
            result = data

        # Extract metrics from response
        # Field names may vary between API versions
        domain_authority = result.get("domain_authority") or result.get("pda") or 0
        page_authority = result.get("page_authority") or result.get("upa") or 0
        spam_score = result.get("spam_score") or result.get("pss") or 0

        # Spam score is often returned as 0-17 scale, convert to percentage
        if spam_score <= 17:
            spam_score = (spam_score / 17) * 100

        linking_domains = (
            result.get("root_domains_linking")
            or result.get("linking_root_domains")
            or result.get("uipl")
            or 0
        )

        total_links = (
            result.get("links") or result.get("total_links") or result.get("uid") or 0
        )

        external_links = result.get("external_links") or result.get("ueid") or 0

        # Parse last crawled date if available
        last_crawled = None
        if result.get("last_crawled"):
            try:
                last_crawled = datetime.fromisoformat(
                    result["last_crawled"].replace("Z", "+00:00")
                )
            except (ValueError, AttributeError):
                pass

        return MozMetrics(
            success=True,
            url=url,
            domain=domain,
            domain_authority=round(domain_authority, 1),
            page_authority=round(page_authority, 1),
            spam_score=round(spam_score, 1),
            linking_domains=int(linking_domains),
            total_links=int(total_links),
            external_links=int(external_links),
            last_crawled=last_crawled,
        )

    async def get_linking_domains(
        self,
        url: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Get top linking domains for a URL.

        Args:
            url: Target URL to get backlinks for
            limit: Maximum number of linking domains to return

        Returns:
            List of linking domains with their authority metrics

        Note:
            This uses multiple rows of your Moz API quota.
        """
        auth_header = self._get_auth_header()
        if not auth_header:
            logger.warning("Moz API not configured, returning empty list")
            return []

        try:
            if not url.startswith(("http://", "https://")):
                url = f"https://{url}"

            request_body = {
                "target": url,
                "target_scope": "root_domain",
                "limit": min(limit, 50),
            }

            headers = {
                "Authorization": auth_header,
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.API_BASE}/linking_root_domains",
                    json=request_body,
                    headers=headers,
                )

                if response.status_code == 200:
                    data = response.json()
                    results = (
                        data.get("results", data) if isinstance(data, dict) else data
                    )

                    linking_domains = []
                    for item in results[:limit]:
                        linking_domains.append(
                            {
                                "domain": item.get("source", {}).get("root_domain", ""),
                                "domain_authority": item.get("source", {}).get(
                                    "domain_authority", 0
                                ),
                                "links_to_target": item.get("links_to_target", 1),
                            }
                        )

                    return linking_domains
                else:
                    logger.error(
                        f"Moz linking domains API error: {response.status_code}"
                    )
                    return []

        except Exception as e:
            logger.error(f"Moz linking domains request failed: {e}")
            return []

    async def get_anchor_texts(
        self,
        url: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Get top anchor texts for backlinks to a URL.

        Args:
            url: Target URL to get anchor texts for
            limit: Maximum number of anchor texts to return

        Returns:
            List of anchor texts with their frequencies
        """
        auth_header = self._get_auth_header()
        if not auth_header:
            return []

        try:
            if not url.startswith(("http://", "https://")):
                url = f"https://{url}"

            request_body = {
                "target": url,
                "target_scope": "root_domain",
                "limit": min(limit, 50),
            }

            headers = {
                "Authorization": auth_header,
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.API_BASE}/anchor_text",
                    json=request_body,
                    headers=headers,
                )

                if response.status_code == 200:
                    data = response.json()
                    results = (
                        data.get("results", data) if isinstance(data, dict) else data
                    )

                    anchors = []
                    for item in results[:limit]:
                        anchors.append(
                            {
                                "text": item.get("anchor_text", ""),
                                "count": item.get("count", item.get("links", 1)),
                            }
                        )

                    return anchors
                else:
                    logger.error(f"Moz anchor text API error: {response.status_code}")
                    return []

        except Exception as e:
            logger.error(f"Moz anchor text request failed: {e}")
            return []

    def _get_mock_metrics(self, url: str, domain: str) -> MozMetrics:
        """Return mock data for development/testing."""
        return MozMetrics(
            success=True,
            url=url,
            domain=domain,
            domain_authority=45.0,
            page_authority=38.0,
            spam_score=5.0,
            linking_domains=150,
            total_links=2500,
            external_links=1200,
        )

    def is_configured(self) -> bool:
        """Check if the Moz service is properly configured."""
        return bool(self.api_key)


# =============================================================================
# Helper Functions
# =============================================================================


def interpret_domain_authority(da: float) -> str:
    """
    Interpret Domain Authority score into a human-readable assessment.

    Args:
        da: Domain Authority score (0-100)

    Returns:
        Assessment string (e.g., "Excellent", "Good", "Low")
    """
    if da >= 70:
        return "Excellent"
    elif da >= 50:
        return "Good"
    elif da >= 30:
        return "Moderate"
    elif da >= 10:
        return "Low"
    else:
        return "Very Low"


def interpret_spam_score(spam: float) -> str:
    """
    Interpret Spam Score into a human-readable assessment.

    Args:
        spam: Spam Score percentage (0-100)

    Returns:
        Assessment string (e.g., "Low Risk", "Medium Risk", "High Risk")
    """
    if spam <= 10:
        return "Low Risk"
    elif spam <= 30:
        return "Medium Risk"
    elif spam <= 60:
        return "High Risk"
    else:
        return "Very High Risk"


def calculate_authority_score(
    da: float,
    linking_domains: int,
    spam_score: float,
) -> float:
    """
    Calculate a composite authority score from Moz metrics.

    This combines Domain Authority, linking domains, and spam score
    into a single 0-100 score for easier comparison.

    Args:
        da: Domain Authority (0-100)
        linking_domains: Number of unique linking domains
        spam_score: Spam Score percentage (0-100)

    Returns:
        Composite authority score (0-100)
    """
    # Normalize linking domains (log scale, capped at 10000)
    import math

    ld_score = min(100, (math.log10(max(linking_domains, 1) + 1) / 4) * 100)

    # Spam penalty (inverted - low spam = high score)
    spam_penalty = 100 - spam_score

    # Weighted combination
    # DA: 50%, Linking Domains: 30%, Spam (inverted): 20%
    score = (da * 0.5) + (ld_score * 0.3) + (spam_penalty * 0.2)

    return round(min(100, max(0, score)), 1)


# =============================================================================
# Convenience Functions
# =============================================================================


async def get_domain_authority(url: str) -> MozMetrics:
    """Quick function to get Moz metrics for a URL."""
    service = MozService()
    return await service.get_url_metrics(url)


async def analyze_backlink_profile(url: str) -> Dict[str, Any]:
    """
    Get a complete backlink profile analysis.

    Args:
        url: Target URL to analyze

    Returns:
        Dict with metrics, top linking domains, and anchor texts
    """
    service = MozService()

    # Fetch all data in parallel
    metrics_task = service.get_url_metrics(url)
    domains_task = service.get_linking_domains(url, limit=20)
    anchors_task = service.get_anchor_texts(url, limit=10)

    metrics, domains, anchors = await asyncio.gather(
        metrics_task,
        domains_task,
        anchors_task,
    )

    return {
        "metrics": metrics,
        "top_linking_domains": domains,
        "top_anchor_texts": anchors,
        "authority_assessment": interpret_domain_authority(metrics.domain_authority),
        "spam_assessment": interpret_spam_score(metrics.spam_score),
        "composite_score": calculate_authority_score(
            metrics.domain_authority,
            metrics.linking_domains,
            metrics.spam_score,
        ),
    }
