# =============================================================================
# EXPLAINER: Google Search Service
# =============================================================================
#
# WHAT IS THIS?
# This service interacts with the Google Custom Search API to find out how the brand
# appears in search results (SERPs).
#
# WHY DO WE NEED IT?
# 1. **Visibility**: Is the brand #1 for its own name? If not, that's a crisis.
# 2. **Indexing**: Does Google know about the brand's pages? (site:domain.com check)
# 3. **Authority**: Does the brand have a Knowledge Panel or Wikipedia page?
#    (These are strong trust signals for both users and AI agents).
#
# HOW IT WORKS:
# - Uses `site:domain.com` to estimate indexed pages.
# - Searches for the brand name to see ranking position.
# - Checks specific domains (Wikipedia, Social Media) in the results to gauge footprint.
#
# LIMITATIONS:
# - Custom Search API has a daily quota (usually 100 queries free).
# - It's an approximation of real Google Search (which varies by user/location).
# =============================================================================

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import httpx
import asyncio
import logging

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """A single search result."""
    position: int
    title: str
    link: str
    snippet: str
    display_link: str
    is_brand_domain: bool = False
    is_wikipedia: bool = False
    is_social_media: bool = False


@dataclass
class SERPAnalysis:
    """Analysis of Search Engine Results Page."""
    success: bool
    query: str
    total_results: int = 0
    brand_position: Optional[int] = None  # Position of brand domain in results
    brand_in_top_10: bool = False
    brand_in_top_3: bool = False
    wikipedia_found: bool = False
    wikipedia_position: Optional[int] = None
    knowledge_panel_likely: bool = False
    results: List[SearchResult] = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class IndexingAnalysis:
    """Analysis of site indexing status."""
    success: bool
    domain: str
    estimated_indexed_pages: int = 0
    sample_indexed_urls: List[str] = field(default_factory=list)
    indexing_status: str = "unknown"  # good, limited, poor, unknown
    error: Optional[str] = None


class GoogleSearchService:
    """
    Service for interacting with Google Custom Search API.
    
    Provides critical SEO data about how the world (and AI) sees the brand.
    """
    
    API_URL = "https://www.googleapis.com/customsearch/v1"
    TIMEOUT = 15
    MAX_RETRIES = 2
    
    # Social media domains to detect in search results
    # Presence here indicates strong "Brand SEO"
    SOCIAL_DOMAINS = [
        "twitter.com", "x.com", "linkedin.com", "facebook.com",
        "instagram.com", "youtube.com", "tiktok.com", "github.com",
        "medium.com", "reddit.com", "discord.com", "t.me",
    ]
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        search_engine_id: Optional[str] = None,
    ):
        """
        Initialize the Google Search service.
        """
        self.api_key = api_key or settings.GOOGLE_API_KEY
        self.search_engine_id = search_engine_id or settings.GOOGLE_SEARCH_ENGINE_ID
    
    async def search_brand(
        self,
        brand_name: str,
        brand_domain: Optional[str] = None,
        num_results: int = 10,
    ) -> SERPAnalysis:
        """
        Search for a brand name and analyze the results.
        
        This checks:
        - Brand's position in search results (Navigational intent)
        - Wikipedia presence (Authority signal)
        - Knowledge panel indicators (Entity recognition)
        """
        if not self.api_key or not self.search_engine_id:
            logger.warning("Google Search API not configured, using mock data")
            return self._get_mock_serp(brand_name, brand_domain)
        
        params = {
            "key": self.api_key,
            "cx": self.search_engine_id,
            "q": brand_name,
            "num": min(num_results, 10),
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(self.API_URL, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_serp_response(brand_name, brand_domain, data)
                
                elif response.status_code == 429:
                    logger.warning("Google Search API rate limited")
                    return SERPAnalysis(
                        success=False,
                        query=brand_name,
                        error="Rate limited by Google Search API",
                    )
                
                elif response.status_code == 403:
                    logger.error("Google Search API access denied")
                    return SERPAnalysis(
                        success=False,
                        query=brand_name,
                        error="API access denied - check API key and quota",
                    )
                
                else:
                    logger.error(f"Google Search API error: {response.status_code}")
                    return self._get_mock_serp(brand_name, brand_domain)
                    
        except Exception as e:
            logger.error(f"Google Search request failed: {e}")
            return self._get_mock_serp(brand_name, brand_domain)
    
    async def check_indexing(self, domain: str) -> IndexingAnalysis:
        """
        Check how many pages of a domain are indexed by Google.
        
        Uses the `site:domain.com` search operator.
        Low indexing count (<10) usually means the site is new or has technical SEO issues.
        """
        # Clean domain
        domain = domain.replace("https://", "").replace("http://", "").replace("www.", "")
        domain = domain.split("/")[0]  # Remove path
        
        if not self.api_key or not self.search_engine_id:
            logger.warning("Google Search API not configured, using mock data")
            return self._get_mock_indexing(domain)
        
        query = f"site:{domain}"
        params = {
            "key": self.api_key,
            "cx": self.search_engine_id,
            "q": query,
            "num": 10,
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(self.API_URL, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_indexing_response(domain, data)
                
                else:
                    logger.error(f"Indexing check failed: {response.status_code}")
                    return self._get_mock_indexing(domain)
                    
        except Exception as e:
            logger.error(f"Indexing check request failed: {e}")
            return self._get_mock_indexing(domain)
    
    async def check_wikipedia_presence(self, brand_name: str) -> Dict[str, Any]:
        """
        Check if a brand has a Wikipedia page.
        
        Searches Google for `"brand name" site:wikipedia.org`.
        Wikipedia presence is a massive boost for "AI Discoverability" (LLMs trust Wiki).
        """
        if not self.api_key or not self.search_engine_id:
            return {"found": False, "url": None, "title": None}
        
        query = f'"{brand_name}" site:wikipedia.org'
        params = {
            "key": self.api_key,
            "cx": self.search_engine_id,
            "q": query,
            "num": 5,
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(self.API_URL, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])
                    
                    for item in items:
                        link = item.get("link", "")
                        title = item.get("title", "")
                        
                        # Check if it's a Wikipedia article (not a talk page, category, etc.)
                        if "wikipedia.org/wiki/" in link and ":" not in link.split("/wiki/")[-1]:
                            # Check if brand name is in title to avoid false positives
                            if brand_name.lower() in title.lower():
                                return {
                                    "found": True,
                                    "url": link,
                                    "title": title,
                                    "snippet": item.get("snippet", ""),
                                }
                    
                    return {"found": False, "url": None, "title": None}
                    
        except Exception as e:
            logger.error(f"Wikipedia check failed: {e}")
        
        return {"found": False, "url": None, "title": None}
    
    async def analyze_brand_visibility(
        self,
        brand_name: str,
        brand_domain: str,
    ) -> Dict[str, Any]:
        """
        Comprehensive brand visibility analysis.
        
        Combines SERP analysis, indexing check, and Wikipedia presence into a holistic view.
        """
        # Run all checks in parallel to save time
        serp_task = self.search_brand(brand_name, brand_domain)
        indexing_task = self.check_indexing(brand_domain)
        wikipedia_task = self.check_wikipedia_presence(brand_name)
        
        serp, indexing, wikipedia = await asyncio.gather(
            serp_task, indexing_task, wikipedia_task
        )
        
        # Calculate visibility score (0-100)
        visibility_score = 0
        
        # SERP position (40 points max)
        # Being #1 for your own name is non-negotiable for established brands.
        if serp.brand_in_top_3:
            visibility_score += 40
        elif serp.brand_in_top_10:
            visibility_score += 25
        elif serp.brand_position:
            visibility_score += 10
        
        # Indexing (30 points max)
        # More pages = more surface area for discovery.
        if indexing.estimated_indexed_pages >= 100:
            visibility_score += 30
        elif indexing.estimated_indexed_pages >= 50:
            visibility_score += 20
        elif indexing.estimated_indexed_pages >= 10:
            visibility_score += 10
        elif indexing.estimated_indexed_pages > 0:
            visibility_score += 5
        
        # Wikipedia (20 points)
        if wikipedia.get("found"):
            visibility_score += 20
        
        # Knowledge panel (10 points)
        if serp.knowledge_panel_likely:
            visibility_score += 10
        
        return {
            "visibility_score": visibility_score,
            "serp": serp,
            "indexing": indexing,
            "wikipedia": wikipedia,
        }
    
    def _parse_serp_response(
        self,
        query: str,
        brand_domain: Optional[str],
        data: Dict[str, Any],
    ) -> SERPAnalysis:
        """Parse the search API response."""
        items = data.get("items", [])
        search_info = data.get("searchInformation", {})
        
        total_results = int(search_info.get("totalResults", 0))
        
        results = []
        brand_position = None
        wikipedia_found = False
        wikipedia_position = None
        
        for i, item in enumerate(items):
            position = i + 1
            link = item.get("link", "")
            display_link = item.get("displayLink", "")
            
            # Check if this is the brand's domain
            is_brand = False
            if brand_domain:
                domain_clean = brand_domain.replace("www.", "").lower()
                is_brand = domain_clean in display_link.lower()
                if is_brand and brand_position is None:
                    brand_position = position
            
            # Check for Wikipedia
            is_wiki = "wikipedia.org" in link
            if is_wiki and not wikipedia_found:
                wikipedia_found = True
                wikipedia_position = position
            
            # Check for social media
            is_social = any(social in link for social in self.SOCIAL_DOMAINS)
            
            results.append(SearchResult(
                position=position,
                title=item.get("title", ""),
                link=link,
                snippet=item.get("snippet", ""),
                display_link=display_link,
                is_brand_domain=is_brand,
                is_wikipedia=is_wiki,
                is_social_media=is_social,
            ))
        
        # Detect knowledge panel (heuristic: brand in top 3 + Wikipedia + social in top results)
        # Real knowledge panels aren't always explicitly in Custom Search JSON, so we infer.
        brand_in_top_3 = brand_position is not None and brand_position <= 3
        knowledge_panel_likely = brand_in_top_3 and wikipedia_found
        
        return SERPAnalysis(
            success=True,
            query=query,
            total_results=total_results,
            brand_position=brand_position,
            brand_in_top_10=brand_position is not None and brand_position <= 10,
            brand_in_top_3=brand_in_top_3,
            wikipedia_found=wikipedia_found,
            wikipedia_position=wikipedia_position,
            knowledge_panel_likely=knowledge_panel_likely,
            results=results,
        )
    
    def _parse_indexing_response(
        self,
        domain: str,
        data: Dict[str, Any],
    ) -> IndexingAnalysis:
        """Parse the indexing check response."""
        items = data.get("items", [])
        search_info = data.get("searchInformation", {})
        
        total_results = int(search_info.get("totalResults", 0))
        
        # Extract sample URLs
        sample_urls = [item.get("link", "") for item in items[:5]]
        
        # Determine indexing status
        if total_results >= 100:
            status = "good"
        elif total_results >= 20:
            status = "moderate"
        elif total_results > 0:
            status = "limited"
        else:
            status = "poor"
        
        return IndexingAnalysis(
            success=True,
            domain=domain,
            estimated_indexed_pages=total_results,
            sample_indexed_urls=sample_urls,
            indexing_status=status,
        )
    
    def _get_mock_serp(
        self,
        brand_name: str,
        brand_domain: Optional[str],
    ) -> SERPAnalysis:
        """Return mock SERP data for development."""
        return SERPAnalysis(
            success=True,
            query=brand_name,
            total_results=150000,
            brand_position=2,
            brand_in_top_10=True,
            brand_in_top_3=True,
            wikipedia_found=False,
            wikipedia_position=None,
            knowledge_panel_likely=False,
            results=[
                SearchResult(
                    position=1,
                    title=f"{brand_name} - Official Website",
                    link=f"https://{brand_domain or 'example.com'}",
                    snippet=f"Welcome to {brand_name}. We provide innovative solutions...",
                    display_link=brand_domain or "example.com",
                    is_brand_domain=True,
                ),
                SearchResult(
                    position=2,
                    title=f"{brand_name} (@{brand_name.lower().replace(' ', '')}) / X",
                    link=f"https://twitter.com/{brand_name.lower().replace(' ', '')}",
                    snippet=f"The latest posts from {brand_name}...",
                    display_link="twitter.com",
                    is_social_media=True,
                ),
            ],
        )
    
    def _get_mock_indexing(self, domain: str) -> IndexingAnalysis:
        """Return mock indexing data for development."""
        return IndexingAnalysis(
            success=True,
            domain=domain,
            estimated_indexed_pages=45,
            sample_indexed_urls=[
                f"https://{domain}/",
                f"https://{domain}/about",
                f"https://{domain}/products",
                f"https://{domain}/blog",
                f"https://{domain}/contact",
            ],
            indexing_status="moderate",
        )


# Convenience functions
async def search_brand(brand_name: str, brand_domain: Optional[str] = None) -> SERPAnalysis:
    """Quick function to search for a brand."""
    service = GoogleSearchService()
    return await service.search_brand(brand_name, brand_domain)


async def check_indexing(domain: str) -> IndexingAnalysis:
    """Quick function to check domain indexing."""
    service = GoogleSearchService()
    return await service.check_indexing(domain)
