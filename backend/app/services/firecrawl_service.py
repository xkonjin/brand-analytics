"""
Firecrawl Service for JavaScript-capable website scraping.

Firecrawl renders JavaScript-heavy sites (React, Vue, Angular) and returns
clean HTML/markdown content. Used as a fallback when BeautifulSoup fails
to extract meaningful content from SPA sites.
"""

from typing import Optional, Dict, Any
import httpx
from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)

FIRECRAWL_API_URL = "https://api.firecrawl.dev/v1"


class FirecrawlService:
    def __init__(self):
        self.api_key = settings.FIRECRAWL_API_KEY
        self.timeout = 60

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def scrape_url(self, url: str) -> Optional[Dict[str, Any]]:
        if not self.is_configured:
            logger.warning("Firecrawl API key not configured")
            return None

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{FIRECRAWL_API_URL}/scrape",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "url": url,
                        "formats": ["html", "markdown"],
                        "onlyMainContent": False,
                        "waitFor": 3000,
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        return {
                            "html": data.get("data", {}).get("html", ""),
                            "markdown": data.get("data", {}).get("markdown", ""),
                            "metadata": data.get("data", {}).get("metadata", {}),
                            "source": "firecrawl",
                        }

                logger.warning(
                    f"Firecrawl scrape failed: {response.status_code} - {response.text[:200]}"
                )
                return None

        except httpx.TimeoutException:
            logger.warning(f"Firecrawl timeout for {url}")
            return None
        except Exception as e:
            logger.error(f"Firecrawl error: {e}")
            return None


firecrawl_service = FirecrawlService()
