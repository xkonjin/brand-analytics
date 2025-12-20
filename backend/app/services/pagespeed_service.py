# =============================================================================
# EXPLAINER: Google PageSpeed Service
# =============================================================================
#
# WHAT IS THIS?
# This service talks to the Google PageSpeed Insights API (Lighthouse) to measure
# website performance.
#
# WHY DO WE NEED IT?
# 1. **User Experience**: Slow sites = high bounce rates. Amazon found 100ms latency = 1% revenue loss.
# 2. **SEO**: Google explicitly uses "Core Web Vitals" as a ranking factor.
# 3. **Mobile First**: Google indexes the mobile version of sites. If mobile is slow, you lose rank.
#
# KEY METRICS (CORE WEB VITALS):
# - **LCP (Largest Contentful Paint)**: How fast the main content loads. (<2.5s is good).
# - **FID (First Input Delay)**: How responsive the site is to clicks. (<100ms is good).
# - **CLS (Cumulative Layout Shift)**: Visual stability. Does stuff jump around? (<0.1 is good).
#
# HOW IT WORKS:
# - We check mobile strategy by default (since it's harder and more important).
# - We cache results for 6 hours because this data doesn't change minute-by-minute.
# - We implement retries because Lighthouse scans can time out on complex sites.
# =============================================================================

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
import httpx
import asyncio
import logging

from app.config import settings
from app.utils.cache import cache, rate_limiters

logger = logging.getLogger(__name__)


class Strategy(str, Enum):
    """PageSpeed analysis strategy."""

    MOBILE = "mobile"
    DESKTOP = "desktop"


class Category(str, Enum):
    """PageSpeed audit categories."""

    PERFORMANCE = "performance"
    ACCESSIBILITY = "accessibility"
    BEST_PRACTICES = "best-practices"
    SEO = "seo"


@dataclass
class CoreWebVitals:
    """
    Core Web Vitals metrics.
    These are the "vital signs" of a healthy website.
    """

    lcp: Optional[float] = None  # Largest Contentful Paint (seconds)
    fid: Optional[float] = None  # First Input Delay (milliseconds)
    cls: Optional[float] = None  # Cumulative Layout Shift (score)
    fcp: Optional[float] = None  # First Contentful Paint (seconds)
    ttfb: Optional[float] = None  # Time to First Byte (seconds)
    tti: Optional[float] = None  # Time to Interactive (seconds)
    tbt: Optional[float] = None  # Total Blocking Time (milliseconds)
    si: Optional[float] = None  # Speed Index (seconds)


@dataclass
class PageSpeedResult:
    """Structured PageSpeed analysis result."""

    success: bool
    url: str
    strategy: Strategy

    # Category scores (0-100)
    performance_score: float = 0
    accessibility_score: float = 0
    best_practices_score: float = 0
    seo_score: float = 0

    # Core Web Vitals
    core_web_vitals: Optional[CoreWebVitals] = None

    # Page load time (seconds)
    page_load_time: Optional[float] = None

    # Is mobile-friendly
    mobile_friendly: bool = True

    # Opportunities for improvement
    opportunities: List[Dict[str, Any]] = None

    # Diagnostics (technical details)
    diagnostics: List[Dict[str, Any]] = None

    # Error message if failed
    error: Optional[str] = None

    # Raw API response
    raw_data: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.opportunities is None:
            self.opportunities = []
        if self.diagnostics is None:
            self.diagnostics = []


class PageSpeedService:
    """
    Service for interacting with Google PageSpeed Insights API.
    """

    API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    TIMEOUT = 60  # PageSpeed can take a while
    MAX_RETRIES = 2

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the PageSpeed service.
        """
        self.api_key = api_key or settings.GOOGLE_API_KEY

    async def analyze(
        self,
        url: str,
        strategy: Strategy = Strategy.MOBILE,
        categories: Optional[List[Category]] = None,
    ) -> PageSpeedResult:
        """
        Analyze a URL using PageSpeed Insights API.

        Results are cached for 6 hours to reduce API calls.
        Rate limiting is applied to stay within quota.
        """
        if not self.api_key:
            logger.warning("No Google API key configured, using mock data")
            return self._get_mock_result(url, strategy)

        # Check cache first
        cache_key = cache._make_key("pagespeed", url, strategy.value)
        cached_result = await cache.get(cache_key)
        if cached_result:
            logger.info(f"PageSpeed cache hit for {url}")
            # Reconstruct PageSpeedResult from cached dict
            return self._dict_to_result(cached_result)

        # Check rate limit
        rate_limiter = rate_limiters.get("google_pagespeed")
        if rate_limiter and not await rate_limiter.is_allowed():
            logger.warning("PageSpeed API rate limited, using mock data")
            return self._get_mock_result(url, strategy)

        if categories is None:
            categories = [
                Category.PERFORMANCE,
                Category.ACCESSIBILITY,
                Category.BEST_PRACTICES,
                Category.SEO,
            ]

        # Build request parameters
        params = {
            "url": url,
            "key": self.api_key,
            "strategy": strategy.value,
            "category": [c.value for c in categories],
        }

        # Make request with retries
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                    response = await client.get(self.API_URL, params=params)

                    if response.status_code == 200:
                        data = response.json()
                        result = self._parse_response(url, strategy, data)
                        # Cache the result
                        await cache.set(
                            cache_key, self._result_to_dict(result), ttl=3600 * 6
                        )
                        return result

                    elif response.status_code == 429:
                        # Rate limited - wait and retry
                        if attempt < self.MAX_RETRIES:
                            wait_time = (attempt + 1) * 2
                            logger.warning(
                                f"Rate limited, waiting {wait_time}s before retry"
                            )
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            return PageSpeedResult(
                                success=False,
                                url=url,
                                strategy=strategy,
                                error="Rate limited by PageSpeed API",
                            )

                    elif response.status_code == 400:
                        error_data = response.json()
                        error_msg = error_data.get("error", {}).get(
                            "message", "Bad request"
                        )
                        return PageSpeedResult(
                            success=False,
                            url=url,
                            strategy=strategy,
                            error=f"Invalid request: {error_msg}",
                        )

                    else:
                        logger.error(f"PageSpeed API error: {response.status_code}")
                        return PageSpeedResult(
                            success=False,
                            url=url,
                            strategy=strategy,
                            error=f"API error: {response.status_code}",
                        )

            except httpx.TimeoutException:
                if attempt < self.MAX_RETRIES:
                    logger.warning(
                        f"PageSpeed timeout, retrying ({attempt + 1}/{self.MAX_RETRIES})"
                    )
                    continue
                return PageSpeedResult(
                    success=False,
                    url=url,
                    strategy=strategy,
                    error="Request timed out",
                )
            except Exception as e:
                logger.error(f"PageSpeed request failed: {e}")
                return PageSpeedResult(
                    success=False,
                    url=url,
                    strategy=strategy,
                    error=str(e),
                )

        return PageSpeedResult(
            success=False,
            url=url,
            strategy=strategy,
            error="Max retries exceeded",
        )

    async def analyze_both_strategies(self, url: str) -> Dict[str, PageSpeedResult]:
        """
        Analyze a URL for both mobile and desktop.
        """
        mobile_task = self.analyze(url, Strategy.MOBILE)
        desktop_task = self.analyze(url, Strategy.DESKTOP)

        mobile_result, desktop_result = await asyncio.gather(mobile_task, desktop_task)

        return {
            "mobile": mobile_result,
            "desktop": desktop_result,
        }

    def _parse_response(
        self,
        url: str,
        strategy: Strategy,
        data: Dict[str, Any],
    ) -> PageSpeedResult:
        """Parse the PageSpeed API response into a structured result."""
        lighthouse = data.get("lighthouseResult", {})
        categories = lighthouse.get("categories", {})
        audits = lighthouse.get("audits", {})

        # Extract category scores (convert 0-1 to 0-100)
        performance_score = categories.get("performance", {}).get("score", 0) * 100
        accessibility_score = categories.get("accessibility", {}).get("score", 0) * 100
        best_practices_score = (
            categories.get("best-practices", {}).get("score", 0) * 100
        )
        seo_score = categories.get("seo", {}).get("score", 0) * 100

        # Extract Core Web Vitals
        core_web_vitals = CoreWebVitals(
            lcp=self._extract_metric_seconds(audits, "largest-contentful-paint"),
            fid=self._extract_metric_ms(audits, "max-potential-fid"),
            cls=self._extract_metric_raw(audits, "cumulative-layout-shift"),
            fcp=self._extract_metric_seconds(audits, "first-contentful-paint"),
            ttfb=self._extract_metric_seconds(audits, "server-response-time"),
            tti=self._extract_metric_seconds(audits, "interactive"),
            tbt=self._extract_metric_ms(audits, "total-blocking-time"),
            si=self._extract_metric_seconds(audits, "speed-index"),
        )

        # Extract page load time (Time to Interactive)
        page_load_time = core_web_vitals.tti

        # Determine mobile-friendliness
        mobile_friendly = self._check_mobile_friendly(audits, performance_score)

        # Extract opportunities (things that can be improved)
        opportunities = self._extract_opportunities(audits)

        # Extract diagnostics
        diagnostics = self._extract_diagnostics(audits)

        return PageSpeedResult(
            success=True,
            url=url,
            strategy=strategy,
            performance_score=performance_score,
            accessibility_score=accessibility_score,
            best_practices_score=best_practices_score,
            seo_score=seo_score,
            core_web_vitals=core_web_vitals,
            page_load_time=page_load_time,
            mobile_friendly=mobile_friendly,
            opportunities=opportunities,
            diagnostics=diagnostics,
            raw_data=data,
        )

    def _extract_metric_seconds(self, audits: Dict, metric: str) -> Optional[float]:
        """Extract a metric and convert from ms to seconds."""
        value = audits.get(metric, {}).get("numericValue")
        if value is not None:
            return round(value / 1000, 2)
        return None

    def _extract_metric_ms(self, audits: Dict, metric: str) -> Optional[float]:
        """Extract a metric in milliseconds."""
        value = audits.get(metric, {}).get("numericValue")
        if value is not None:
            return round(value, 1)
        return None

    def _extract_metric_raw(self, audits: Dict, metric: str) -> Optional[float]:
        """Extract a raw metric value."""
        value = audits.get(metric, {}).get("numericValue")
        if value is not None:
            return round(value, 3)
        return None

    def _check_mobile_friendly(self, audits: Dict, perf_score: float) -> bool:
        """Check if the site is mobile-friendly based on audits."""
        # Check viewport audit
        viewport = audits.get("viewport", {})
        if viewport.get("score", 1) < 1:
            return False

        # Check font size
        font_size = audits.get("font-size", {})
        if font_size.get("score", 1) < 0.5:
            return False

        # Check tap targets
        tap_targets = audits.get("tap-targets", {})
        if tap_targets.get("score", 1) < 0.5:
            return False

        # If performance is very low, consider not mobile-friendly
        if perf_score < 30:
            return False

        return True

    def _extract_opportunities(self, audits: Dict) -> List[Dict[str, Any]]:
        """Extract improvement opportunities from audits."""
        opportunities = []

        # List of opportunity audits
        opportunity_keys = [
            "render-blocking-resources",
            "uses-responsive-images",
            "offscreen-images",
            "unminified-css",
            "unminified-javascript",
            "unused-css-rules",
            "unused-javascript",
            "uses-optimized-images",
            "modern-image-formats",
            "uses-text-compression",
            "uses-rel-preconnect",
            "server-response-time",
            "redirects",
            "uses-rel-preload",
            "efficient-animated-content",
            "duplicated-javascript",
            "legacy-javascript",
            "preload-lcp-image",
            "total-byte-weight",
            "uses-long-cache-ttl",
        ]

        for key in opportunity_keys:
            audit = audits.get(key, {})
            if audit.get("score") is not None and audit.get("score") < 1:
                savings = audit.get("details", {}).get("overallSavingsMs", 0)
                if savings > 0 or audit.get("score", 1) < 0.9:
                    opportunities.append(
                        {
                            "id": key,
                            "title": audit.get("title", key),
                            "description": audit.get("description", ""),
                            "score": audit.get("score", 0),
                            "savings_ms": savings,
                            "display_value": audit.get("displayValue", ""),
                        }
                    )

        # Sort by potential savings
        opportunities.sort(key=lambda x: x.get("savings_ms", 0), reverse=True)

        return opportunities[:10]  # Top 10 opportunities

    def _extract_diagnostics(self, audits: Dict) -> List[Dict[str, Any]]:
        """Extract diagnostic information from audits."""
        diagnostics = []

        # List of diagnostic audits
        diagnostic_keys = [
            "largest-contentful-paint-element",
            "lcp-lazy-loaded",
            "layout-shift-elements",
            "long-tasks",
            "non-composited-animations",
            "unsized-images",
            "viewport",
            "document-title",
            "html-has-lang",
            "meta-description",
            "link-text",
            "crawlable-anchors",
            "is-crawlable",
            "robots-txt",
            "hreflang",
            "canonical",
            "font-display",
            "third-party-summary",
            "mainthread-work-breakdown",
            "bootup-time",
            "dom-size",
        ]

        for key in diagnostic_keys:
            audit = audits.get(key, {})
            if audit.get("score") is not None and audit.get("score") < 1:
                diagnostics.append(
                    {
                        "id": key,
                        "title": audit.get("title", key),
                        "description": audit.get("description", ""),
                        "score": audit.get("score", 0),
                        "display_value": audit.get("displayValue", ""),
                    }
                )

        return diagnostics[:10]  # Top 10 diagnostics

    def _result_to_dict(self, result: PageSpeedResult) -> Dict[str, Any]:
        """Convert PageSpeedResult to a JSON-serializable dict for caching."""
        return {
            "success": result.success,
            "url": result.url,
            "strategy": result.strategy.value
            if isinstance(result.strategy, Strategy)
            else result.strategy,
            "performance_score": result.performance_score,
            "accessibility_score": result.accessibility_score,
            "best_practices_score": result.best_practices_score,
            "seo_score": result.seo_score,
            "core_web_vitals": asdict(result.core_web_vitals)
            if result.core_web_vitals
            else None,
            "page_load_time": result.page_load_time,
            "mobile_friendly": result.mobile_friendly,
            "opportunities": result.opportunities,
            "diagnostics": result.diagnostics,
            "error": result.error,
        }

    def _dict_to_result(self, data: Dict[str, Any]) -> PageSpeedResult:
        """Convert a cached dict back to a PageSpeedResult."""
        # Reconstruct CoreWebVitals if present
        cwv_data = data.get("core_web_vitals")
        core_web_vitals = CoreWebVitals(**cwv_data) if cwv_data else None

        # Reconstruct Strategy enum
        strategy = Strategy(data.get("strategy", "mobile"))

        return PageSpeedResult(
            success=data.get("success", False),
            url=data.get("url", ""),
            strategy=strategy,
            performance_score=data.get("performance_score", 0),
            accessibility_score=data.get("accessibility_score", 0),
            best_practices_score=data.get("best_practices_score", 0),
            seo_score=data.get("seo_score", 0),
            core_web_vitals=core_web_vitals,
            page_load_time=data.get("page_load_time"),
            mobile_friendly=data.get("mobile_friendly", True),
            opportunities=data.get("opportunities", []),
            diagnostics=data.get("diagnostics", []),
            error=data.get("error"),
        )

    def _get_mock_result(self, url: str, strategy: Strategy) -> PageSpeedResult:
        """Return mock data for development without API key."""
        return PageSpeedResult(
            success=True,
            url=url,
            strategy=strategy,
            performance_score=72,
            accessibility_score=85,
            best_practices_score=90,
            seo_score=82,
            core_web_vitals=CoreWebVitals(
                lcp=2.5,
                fid=100,
                cls=0.1,
                fcp=1.5,
                ttfb=0.5,
                tti=3.5,
                tbt=150,
                si=2.8,
            ),
            page_load_time=3.5,
            mobile_friendly=True,
            opportunities=[
                {
                    "id": "render-blocking-resources",
                    "title": "Eliminate render-blocking resources",
                    "description": "Resources are blocking the first paint of your page.",
                    "score": 0.5,
                    "savings_ms": 450,
                },
                {
                    "id": "uses-optimized-images",
                    "title": "Properly size images",
                    "description": "Serve images that are appropriately-sized.",
                    "score": 0.7,
                    "savings_ms": 200,
                },
            ],
            diagnostics=[
                {
                    "id": "largest-contentful-paint-element",
                    "title": "Largest Contentful Paint element",
                    "description": "This is the largest contentful element painted.",
                    "score": 0.8,
                },
            ],
        )


# Convenience function for quick analysis
async def analyze_pagespeed(
    url: str, strategy: Strategy = Strategy.MOBILE
) -> PageSpeedResult:
    """
    Quick function to analyze a URL with PageSpeed Insights.
    """
    service = PageSpeedService()
    return await service.analyze(url, strategy)
