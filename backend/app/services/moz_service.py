from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging
import httpx
from urllib.parse import urlparse

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class MozMetrics:
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
    total_backlinks: int = 0
    unique_domains: int = 0
    follow_links: int = 0
    nofollow_links: int = 0
    top_anchor_texts: List[Dict[str, Any]] = field(default_factory=list)
    authority_distribution: Dict[str, int] = field(default_factory=dict)


class MozService:
    """Service for Moz Unified API (JSON-RPC)."""

    API_URL = "https://api.moz.com/jsonrpc"
    TIMEOUT = 30

    def __init__(self, api_key: Optional[str] = None, timeout: int = 30):
        self.api_key = api_key or getattr(settings, "MOZ_API_KEY", None)
        self.timeout = timeout

    async def get_url_metrics(self, url: str, include_subdomain: bool = True) -> MozMetrics:
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        if not self.api_key:
            logger.warning("Moz API not configured, returning mock data")
            return self._get_mock_metrics(url, domain)

        # Determine auth method (Token vs Basic Auth)
        headers = {
            "Content-Type": "application/json",
        }
        
        # Check if legacy key format (base64) - if so, use Basic Auth which V2 supports
        is_legacy_key = "==" in self.api_key or ":" in self.api_key
        
        if is_legacy_key:
            headers["Authorization"] = f"Basic {self.api_key}"
        else:
            headers["x-moz-token"] = self.api_key

        try:
            payload = {
                "jsonrpc": "2.0",
                "id": "brand-analytics-1-moz-v2-req", # Needs to be > 24 chars
                "method": "data.site.metrics.fetch",
                "params": {
                    "site_query": {
                        "query": domain,
                        "scope": "domain",
                    }
                },
            }

            logger.info(f"Fetching Moz metrics for {domain}")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(self.API_URL, json=payload, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    if "error" in data:
                        error_msg = data["error"].get("message", "Unknown error")
                        logger.error(f"Moz API error: {error_msg}")
                        return MozMetrics(
                            success=False,
                            url=url,
                            domain=domain,
                            error=error_msg,
                        )
                    return self._parse_response(url, domain, data)

                elif response.status_code == 401:
                    logger.error("Moz API authentication failed - check API token")
                    return MozMetrics(
                        success=False,
                        url=url,
                        domain=domain,
                        error="Authentication failed - invalid API token",
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
                    logger.error(f"Moz API error: {response.status_code} - {response.text}")
                    return MozMetrics(
                        success=False,
                        url=url,
                        domain=domain,
                        error=f"API error: {response.status_code}",
                    )

        except httpx.TimeoutException:
            logger.error(f"Moz API timeout for {url}")
            return MozMetrics(success=False, url=url, domain=domain, error="Request timed out")
        except Exception as e:
            logger.error(f"Moz API request failed: {e}")
            return MozMetrics(success=False, url=url, domain=domain, error=str(e))

    def _parse_response(self, url: str, domain: str, data: Dict[str, Any]) -> MozMetrics:
        result = data.get("result", {})
        site_metrics = result.get("site_metrics", {})

        domain_authority = site_metrics.get("domain_authority", 0) or 0
        page_authority = site_metrics.get("page_authority", 0) or 0
        spam_score = site_metrics.get("spam_score", 0) or 0
        linking_domains = site_metrics.get("root_domains_to_root_domain", 0) or 0
        total_links = site_metrics.get("external_pages_to_root_domain", 0) or 0

        return MozMetrics(
            success=True,
            url=url,
            domain=domain,
            domain_authority=round(float(domain_authority), 1),
            page_authority=round(float(page_authority), 1),
            spam_score=round(float(spam_score), 1),
            linking_domains=int(linking_domains),
            total_links=int(total_links),
        )

    async def get_linking_domains(self, url: str, limit: int = 50) -> List[Dict[str, Any]]:
        if not self.api_key:
            logger.warning("Moz API not configured, returning empty list")
            return []

        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        try:
            # Determine auth method (Token vs Basic Auth)
            headers = {
                "Content-Type": "application/json",
            }
            
            # Check if legacy key format (base64)
            is_legacy_key = "==" in self.api_key or ":" in self.api_key
            
            if is_legacy_key:
                headers["Authorization"] = f"Basic {self.api_key}"
            else:
                headers["x-moz-token"] = self.api_key

            payload = {
                "jsonrpc": "2.0",
                "id": "brand-analytics-2-moz-v2-req",
                "method": "data.link.lists.linking_domains",
                "params": {
                    "target": domain,
                    "target_scope": "root_domain",
                    "limit": min(limit, 50),
                },
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(self.API_URL, json=payload, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    if "error" in data:
                        return []
                    
                    results = data.get("result", {}).get("linking_domains", [])
                    return [
                        {
                            "domain": item.get("source_domain", ""),
                            "domain_authority": item.get("domain_authority", 0),
                            "links_to_target": item.get("links_to_target", 1),
                        }
                        for item in results[:limit]
                    ]
                return []

        except Exception as e:
            logger.error(f"Moz linking domains request failed: {e}")
            return []

    async def get_anchor_texts(self, url: str, limit: int = 20) -> List[Dict[str, Any]]:
        if not self.api_key:
            return []

        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        try:
            # Determine auth method (Token vs Basic Auth)
            headers = {
                "Content-Type": "application/json",
            }
            
            # Check if legacy key format (base64)
            is_legacy_key = "==" in self.api_key or ":" in self.api_key
            
            if is_legacy_key:
                headers["Authorization"] = f"Basic {self.api_key}"
            else:
                headers["x-moz-token"] = self.api_key

            payload = {
                "jsonrpc": "2.0",
                "id": "brand-analytics-3-moz-v2-req",
                "method": "data.link.lists.anchor_text",
                "params": {
                    "target": domain,
                    "target_scope": "root_domain",
                    "limit": min(limit, 50),
                },
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(self.API_URL, json=payload, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    if "error" in data:
                        return []
                    
                    results = data.get("result", {}).get("anchor_texts", [])
                    return [
                        {
                            "text": item.get("anchor_text", ""),
                            "count": item.get("count", item.get("links", 1)),
                        }
                        for item in results[:limit]
                    ]
                return []

        except Exception as e:
            logger.error(f"Moz anchor text request failed: {e}")
            return []

    def _get_mock_metrics(self, url: str, domain: str) -> MozMetrics:
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
        return bool(self.api_key)


def interpret_domain_authority(da: float) -> str:
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
    if spam <= 10:
        return "Low Risk"
    elif spam <= 30:
        return "Medium Risk"
    elif spam <= 60:
        return "High Risk"
    else:
        return "Very High Risk"


def calculate_authority_score(da: float, linking_domains: int, spam_score: float) -> float:
    import math

    ld_score = min(100, (math.log10(max(linking_domains, 1) + 1) / 4) * 100)
    spam_penalty = 100 - spam_score
    score = (da * 0.5) + (ld_score * 0.3) + (spam_penalty * 0.2)

    return round(min(100, max(0, score)), 1)


async def get_domain_authority(url: str) -> MozMetrics:
    service = MozService()
    return await service.get_url_metrics(url)


async def analyze_backlink_profile(url: str) -> Dict[str, Any]:
    service = MozService()

    metrics_task = service.get_url_metrics(url)
    domains_task = service.get_linking_domains(url, limit=20)
    anchors_task = service.get_anchor_texts(url, limit=10)

    metrics, domains, anchors = await asyncio.gather(
        metrics_task, domains_task, anchors_task
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
