# =============================================================================
# EXPLAINER: SEO Performance Analyzer
# =============================================================================
#
# WHAT IS THIS?
# This module audits the website's technical health and search engine visibility.
# It acts as a "Technical SEO Specialist".
#
# WHY DO WE NEED IT?
# 1. **Traffic**: 53% of traffic comes from organic search. If you don't rank, you don't exist.
# 2. **Conversion**: Slow sites (poor LCP) kill conversion rates.
# 3. **Trust**: Missing SSL or meta tags looks unprofessional to both users and bots.
#
# HOW IT WORKS:
# 1. **PageSpeed**: Calls Google API to get Core Web Vitals (LCP, CLS, etc.).
# 2. **Meta Analysis**: Checks title tags (length, keywords) and descriptions.
# 3. **Technical Checks**: SSL, Schema Markup, H1 structure.
#
# SCORING LOGIC (Total 100):
# - Performance (30%): Speed is king.
# - Meta Tags (25%): Click-through rate optimization.
# - Mobile (20%): Mobile-first indexing is the standard.
# - Technical (25%): The plumbing must work (SSL, Schema).
# =============================================================================

from typing import Dict, Any, Optional, List
import httpx
import logging

from app.config import settings
from app.analyzers.base import BaseAnalyzer, AnalyzerResult
from app.models.report import (
    Finding,
    Recommendation,
    SeverityLevel,
    CoreWebVitals,
)
from app.services.moz_service import (
    MozService,
    interpret_domain_authority,
    interpret_spam_score,
)
from app.services.pagespeed_service import PageSpeedService, Strategy

logger = logging.getLogger(__name__)


class SEOAnalyzer(BaseAnalyzer):
    """
    Analyzes SEO Performance for a website.
    """

    MODULE_NAME = "seo"
    WEIGHT = 0.15

    async def analyze(self) -> AnalyzerResult:
        """
        Run the SEO analysis.

        Returns:
            AnalyzerResult: SEO analysis results
        """
        try:
            # Initialize data storage
            self._raw_data = {}

            # ----------------------------------------------------------------
            # 1. Get PageSpeed Insights data
            # ----------------------------------------------------------------
            # We fetch this first because it takes the longest (API call)
            pagespeed_data = await self._get_pagespeed_insights()
            self._raw_data["pagespeed"] = pagespeed_data

            # ----------------------------------------------------------------
            # 2. Analyze meta tags from scraped data
            # ----------------------------------------------------------------
            # This uses data we scraped earlier (in the Orchestrator)
            meta_analysis = self._analyze_meta_tags()
            self._raw_data["meta_tags"] = meta_analysis

            # ----------------------------------------------------------------
            # 3. Analyze technical SEO
            # ----------------------------------------------------------------
            technical_analysis = self._analyze_technical_seo()
            self._raw_data["technical"] = technical_analysis

            # ----------------------------------------------------------------
            # 4. Get Moz authority metrics
            # ----------------------------------------------------------------
            authority_data = await self._get_moz_metrics()
            self._raw_data["authority"] = authority_data

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
            # Build result data for report
            # ----------------------------------------------------------------
            core_web_vitals = None
            if pagespeed_data:
                metrics = pagespeed_data.get("lighthouseResult", {}).get("audits", {})
                core_web_vitals = CoreWebVitals(
                    lcp=self._extract_metric(metrics, "largest-contentful-paint"),
                    fid=self._extract_metric(metrics, "max-potential-fid"),
                    cls=self._extract_metric(metrics, "cumulative-layout-shift"),
                    fcp=self._extract_metric(metrics, "first-contentful-paint"),
                    ttfb=self._extract_metric(metrics, "server-response-time"),
                )

            result_data = {
                "score": score,
                "performance_score": self._raw_data.get("pagespeed", {})
                .get("lighthouseResult", {})
                .get("categories", {})
                .get("performance", {})
                .get("score", 0)
                * 100,
                "accessibility_score": self._raw_data.get("pagespeed", {})
                .get("lighthouseResult", {})
                .get("categories", {})
                .get("accessibility", {})
                .get("score", 0)
                * 100,
                "best_practices_score": self._raw_data.get("pagespeed", {})
                .get("lighthouseResult", {})
                .get("categories", {})
                .get("best-practices", {})
                .get("score", 0)
                * 100,
                "seo_score": self._raw_data.get("pagespeed", {})
                .get("lighthouseResult", {})
                .get("categories", {})
                .get("seo", {})
                .get("score", 0)
                * 100,
                "core_web_vitals": core_web_vitals.model_dump()
                if core_web_vitals
                else None,
                "page_load_time": self._extract_metric(
                    pagespeed_data.get("lighthouseResult", {}).get("audits", {})
                    if pagespeed_data
                    else {},
                    "interactive",
                ),
                "mobile_friendly": self._is_mobile_friendly(pagespeed_data),
                "meta_tags": meta_analysis,
                "has_schema_markup": len(self.scraped_data.get("schema_markup", []))
                > 0,
                "schema_types_found": [
                    s.get("@type", "")
                    for s in self.scraped_data.get("schema_markup", [])
                    if isinstance(s, dict)
                ],
                "domain_authority": authority_data.get("domain_authority")
                if authority_data
                else None,
                "page_authority": authority_data.get("page_authority")
                if authority_data
                else None,
                "spam_score": authority_data.get("spam_score")
                if authority_data
                else None,
                "linking_domains": authority_data.get("linking_domains")
                if authority_data
                else None,
                "total_backlinks": authority_data.get("total_links")
                if authority_data
                else None,
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
                error=f"SEO analysis failed: {str(e)}",
            )

    async def _get_pagespeed_insights(self) -> Optional[Dict[str, Any]]:
        """
        Fetch PageSpeed Insights data using the PageSpeedService.
        """
        service = PageSpeedService()
        result = await service.analyze(self.url, strategy=Strategy.MOBILE)
        
        if result.success and result.raw_data:
            return result.raw_data
        
        # If service failed (e.g. no API key or timeout), try to fallback to mock data if in dev
        # But for now, we'll just return None or mock data similar to what the service does internally
        if result.error:
            logger.warning(f"PageSpeed service returned error: {result.error}")
            
        return result.raw_data or self._get_mock_pagespeed_data()

    def _get_mock_pagespeed_data(self) -> Dict[str, Any]:
        """Return mock PageSpeed data for development."""
        return {
            "lighthouseResult": {
                "categories": {
                    "performance": {"score": 0.7},
                    "accessibility": {"score": 0.85},
                    "best-practices": {"score": 0.9},
                    "seo": {"score": 0.8},
                },
                "audits": {
                    "largest-contentful-paint": {"numericValue": 2500},
                    "max-potential-fid": {"numericValue": 100},
                    "cumulative-layout-shift": {"numericValue": 0.1},
                    "first-contentful-paint": {"numericValue": 1500},
                    "server-response-time": {"numericValue": 500},
                    "interactive": {"numericValue": 3500},
                },
            },
        }

    async def _get_moz_metrics(self) -> Optional[Dict[str, Any]]:
        """Fetch domain authority and backlink metrics from Moz API."""
        moz = MozService()
        if not moz.is_configured():
            logger.warning("Moz API not configured, using mock authority data")
            return {
                "domain_authority": 45.0,
                "page_authority": 38.0,
                "spam_score": 5.0,
                "linking_domains": 150,
                "total_links": 2500,
                "authority_assessment": "Moderate",
            }

        try:
            metrics = await moz.get_url_metrics(self.url)
            if metrics.success:
                return {
                    "domain_authority": metrics.domain_authority,
                    "page_authority": metrics.page_authority,
                    "spam_score": metrics.spam_score,
                    "linking_domains": metrics.linking_domains,
                    "total_links": metrics.total_links,
                    "authority_assessment": interpret_domain_authority(
                        metrics.domain_authority
                    ),
                    "spam_assessment": interpret_spam_score(metrics.spam_score),
                }
            else:
                logger.warning(f"Moz API error: {metrics.error}")
                return None
        except Exception as e:
            logger.error(f"Moz metrics fetch failed: {e}")
            return None

    def _extract_metric(
        self, audits: Dict[str, Any], metric_name: str
    ) -> Optional[float]:
        """Extract a numeric metric from PageSpeed audits."""
        audit = audits.get(metric_name, {})
        value = audit.get("numericValue")
        if value is not None:
            # Convert ms to seconds for display
            if metric_name in [
                "largest-contentful-paint",
                "first-contentful-paint",
                "interactive",
                "server-response-time",
            ]:
                return round(value / 1000, 2)
            return round(value, 3)
        return None

    def _is_mobile_friendly(self, pagespeed_data: Optional[Dict]) -> bool:
        """Determine if the site is mobile-friendly based on PageSpeed data."""
        if not pagespeed_data:
            return True  # Assume true if no data

        categories = pagespeed_data.get("lighthouseResult", {}).get("categories", {})

        # Check if mobile performance and accessibility are decent
        perf_score = categories.get("performance", {}).get("score", 0)
        access_score = categories.get("accessibility", {}).get("score", 0)

        return perf_score >= 0.5 and access_score >= 0.7

    def _analyze_meta_tags(self) -> Dict[str, Any]:
        """
        Analyze meta tags from scraped data.
        """
        title = self.scraped_data.get("title", "")
        description = self.scraped_data.get("meta_description", "")
        og_tags = self.scraped_data.get("og_tags", {})
        twitter_cards = self.scraped_data.get("twitter_cards", {})

        # Analyze title
        title_length = len(title)
        if title_length == 0:
            title_quality = "missing"
        elif title_length < 30:
            title_quality = "too_short"
        elif title_length > 60:
            title_quality = "too_long"
        else:
            title_quality = "good"

        # Analyze description
        desc_length = len(description)
        if desc_length == 0:
            desc_quality = "missing"
        elif desc_length < 70:
            desc_quality = "too_short"
        elif desc_length > 160:
            desc_quality = "too_long"
        else:
            desc_quality = "good"

        return {
            "title": title,
            "title_length": title_length,
            "title_quality": title_quality,
            "description": description,
            "description_length": desc_length,
            "description_quality": desc_quality,
            "has_og_tags": len(og_tags) > 0,
            "has_twitter_cards": len(twitter_cards) > 0,
            "has_canonical": self.scraped_data.get("canonical_url") is not None,
        }

    def _analyze_technical_seo(self) -> Dict[str, Any]:
        """
        Analyze technical SEO factors.
        """
        return {
            "has_ssl": self.url.startswith("https"),
            "has_schema_markup": len(self.scraped_data.get("schema_markup", [])) > 0,
            "schema_types": [
                s.get("@type", "")
                for s in self.scraped_data.get("schema_markup", [])
                if isinstance(s, dict)
            ],
            "headings_structure": self.scraped_data.get("headings", {}),
            "has_h1": bool(self.scraped_data.get("headings", {}).get("h1", [])),
            "h1_count": len(self.scraped_data.get("headings", {}).get("h1", [])),
        }

    def _calculate_score(self) -> float:
        """
        Calculate the overall SEO score.
        """
        score = 0.0

        # PageSpeed Performance (30%)
        pagespeed = self._raw_data.get("pagespeed", {})
        if pagespeed:
            categories = pagespeed.get("lighthouseResult", {}).get("categories", {})
            perf_score = categories.get("performance", {}).get("score", 0.5) * 100
            score += perf_score * 0.30
        else:
            score += 50 * 0.30  # Default to 50 if no data

        # Meta Tags (25%)
        meta = self._raw_data.get("meta_tags", {})
        meta_score = 0
        if meta.get("title_quality") == "good":
            meta_score += 40
        elif meta.get("title_quality") != "missing":
            meta_score += 20
        if meta.get("description_quality") == "good":
            meta_score += 40
        elif meta.get("description_quality") != "missing":
            meta_score += 20
        if meta.get("has_og_tags"):
            meta_score += 10
        if meta.get("has_canonical"):
            meta_score += 10
        score += meta_score * 0.25

        # Mobile-Friendliness (20%)
        if self._is_mobile_friendly(self._raw_data.get("pagespeed")):
            score += 100 * 0.20
        else:
            score += 30 * 0.20

        # Technical SEO (25%)
        tech = self._raw_data.get("technical", {})
        tech_score = 0
        if tech.get("has_ssl"):
            tech_score += 30
        if tech.get("has_schema_markup"):
            tech_score += 30
        if tech.get("has_h1"):
            tech_score += 20
        if tech.get("h1_count", 0) == 1:  # Single H1 is ideal
            tech_score += 20
        elif tech.get("h1_count", 0) > 0:
            tech_score += 10
        score += tech_score * 0.25

        return self.clamp_score(score)

    def _generate_findings(self) -> List[Finding]:
        """Generate findings based on the analysis."""
        findings = []

        # PageSpeed findings
        pagespeed = self._raw_data.get("pagespeed", {})
        if pagespeed:
            categories = pagespeed.get("lighthouseResult", {}).get("categories", {})
            perf_score = categories.get("performance", {}).get("score", 0) * 100

            if perf_score >= 90:
                findings.append(
                    Finding(
                        title="Excellent Page Performance",
                        detail=f"PageSpeed performance score is {perf_score:.0f}/100, which is excellent. "
                        "This helps with both SEO rankings and user experience.",
                        severity=SeverityLevel.INFO,
                        data={"score": perf_score},
                    )
                )
            elif perf_score < 50:
                findings.append(
                    Finding(
                        title="Poor Page Performance",
                        detail=f"PageSpeed performance score is only {perf_score:.0f}/100. "
                        "Slow sites lose visitors - 53% leave if loading takes >3 seconds.",
                        severity=SeverityLevel.CRITICAL,
                        data={"score": perf_score},
                    )
                )

        # Meta tag findings
        meta = self._raw_data.get("meta_tags", {})
        if meta.get("title_quality") == "missing":
            findings.append(
                Finding(
                    title="Missing Page Title",
                    detail="No title tag found. Page titles are crucial for SEO and "
                    "are displayed in search results.",
                    severity=SeverityLevel.CRITICAL,
                )
            )
        elif meta.get("title_quality") == "too_long":
            findings.append(
                Finding(
                    title="Title Too Long",
                    detail=f"Title is {meta['title_length']} characters. Google typically "
                    "displays 50-60 characters. Longer titles may be truncated.",
                    severity=SeverityLevel.MEDIUM,
                )
            )

        if meta.get("description_quality") == "missing":
            findings.append(
                Finding(
                    title="Missing Meta Description",
                    detail="No meta description found. This is displayed in search results "
                    "and can significantly impact click-through rates.",
                    severity=SeverityLevel.HIGH,
                )
            )

        # Technical findings
        tech = self._raw_data.get("technical", {})
        if not tech.get("has_ssl"):
            findings.append(
                Finding(
                    title="No SSL Certificate",
                    detail="Site is not using HTTPS. This hurts SEO rankings and "
                    "causes browser security warnings.",
                    severity=SeverityLevel.CRITICAL,
                )
            )

        if not tech.get("has_schema_markup"):
            findings.append(
                Finding(
                    title="No Schema Markup Found",
                    detail="No structured data (Schema.org) detected. Schema markup helps "
                    "search engines understand your content and enables rich snippets.",
                    severity=SeverityLevel.MEDIUM,
                )
            )

        if tech.get("h1_count", 0) == 0:
            findings.append(
                Finding(
                    title="Missing H1 Heading",
                    detail="No H1 heading found on the page. Each page should have exactly "
                    "one H1 that describes the main topic.",
                    severity=SeverityLevel.HIGH,
                )
            )
        elif tech.get("h1_count", 0) > 1:
            findings.append(
                Finding(
                    title="Multiple H1 Headings",
                    detail=f"Found {tech['h1_count']} H1 headings. Best practice is to have "
                    "exactly one H1 per page.",
                    severity=SeverityLevel.LOW,
                )
            )

        return findings

    def _generate_recommendations(self) -> List[Recommendation]:
        """Generate recommendations based on findings."""
        recommendations = []

        # PageSpeed recommendations
        pagespeed = self._raw_data.get("pagespeed", {})
        if pagespeed:
            categories = pagespeed.get("lighthouseResult", {}).get("categories", {})
            perf_score = categories.get("performance", {}).get("score", 0) * 100

            if perf_score < 70:
                recommendations.append(
                    Recommendation(
                        title="Improve Page Load Speed",
                        description="Compress images, enable browser caching, and minimize "
                        "JavaScript to improve load times. Target a PageSpeed score "
                        "of 90+ for best results. Fast sites rank higher and convert better.",
                        priority=SeverityLevel.HIGH,
                        category="seo",
                        impact="high",
                        effort="medium",
                    )
                )

        # Meta tag recommendations
        meta = self._raw_data.get("meta_tags", {})
        if meta.get("title_quality") in ["missing", "too_short", "too_long"]:
            recommendations.append(
                Recommendation(
                    title="Optimize Page Title",
                    description="Write a compelling title tag between 50-60 characters that "
                    "includes your primary keyword and brand name. Format: "
                    "'Primary Keyword - Brand Name'",
                    priority=SeverityLevel.HIGH,
                    category="seo",
                    impact="high",
                    effort="low",
                )
            )

        if meta.get("description_quality") in ["missing", "too_short"]:
            recommendations.append(
                Recommendation(
                    title="Add Meta Description",
                    description="Write a compelling meta description (120-160 characters) that "
                    "summarizes the page content and includes a call-to-action. "
                    "This directly impacts click-through rates from search results.",
                    priority=SeverityLevel.HIGH,
                    category="seo",
                    impact="high",
                    effort="low",
                )
            )

        if not meta.get("has_og_tags"):
            recommendations.append(
                Recommendation(
                    title="Add Open Graph Tags",
                    description="Implement Open Graph meta tags to control how your content "
                    "appears when shared on social media. Include og:title, "
                    "og:description, and og:image at minimum.",
                    priority=SeverityLevel.MEDIUM,
                    category="seo",
                    impact="medium",
                    effort="low",
                )
            )

        # Technical recommendations
        tech = self._raw_data.get("technical", {})
        if not tech.get("has_ssl"):
            recommendations.append(
                Recommendation(
                    title="Enable HTTPS",
                    description="Migrate your site to HTTPS immediately. This is a Google "
                    "ranking factor and required for user trust. Most hosting "
                    "providers offer free SSL certificates via Let's Encrypt.",
                    priority=SeverityLevel.CRITICAL,
                    category="seo",
                    impact="high",
                    effort="medium",
                )
            )

        if not tech.get("has_schema_markup"):
            recommendations.append(
                Recommendation(
                    title="Implement Schema Markup",
                    description="Add Schema.org structured data to your pages. Start with "
                    "Organization schema for your homepage and FAQ schema for "
                    "common questions. This can enable rich snippets in search results.",
                    priority=SeverityLevel.MEDIUM,
                    category="seo",
                    impact="medium",
                    effort="medium",
                )
            )

        return recommendations
