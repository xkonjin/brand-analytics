import httpx
import json
import logging
import re
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class BrandResearch:
    """Perplexity brand research results with discovered social profiles and company info."""

    success: bool = False
    error: Optional[str] = None
    social_profiles: Dict[str, str] = field(default_factory=dict)
    company_name: Optional[str] = None
    company_description: Optional[str] = None
    founders: List[str] = field(default_factory=list)
    team_size: Optional[str] = None
    headquarters: Optional[str] = None
    year_founded: Optional[str] = None
    industry: Optional[str] = None
    raw_response: Optional[str] = None


class PerplexityService:
    """Research brand information using Perplexity API before analysis."""

    API_URL = "https://api.perplexity.ai/chat/completions"
    MODEL = "sonar"

    def __init__(self):
        self.api_key = settings.PERPLEXITY_API_KEY

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def research_brand(
        self, domain: str, brand_name: Optional[str] = None
    ) -> BrandResearch:
        if not self.is_configured():
            logger.warning("Perplexity API not configured, skipping research")
            return BrandResearch(success=False, error="Perplexity API not configured")

        try:
            query = self._build_research_query(domain, brand_name)
            response = await self._call_api(query)
            return self._parse_response(response, domain)
        except Exception as e:
            logger.error(f"Perplexity research failed: {e}")
            return BrandResearch(success=False, error=str(e))

    def _build_research_query(self, domain: str, brand_name: Optional[str]) -> str:
        name_part = f" ({brand_name})" if brand_name else ""

        return f"""Research the company/brand at {domain}{name_part} and provide the following information in JSON format:

1. "social_profiles": Object with platform names as keys and full URLs as values. Find ALL official accounts:
   - "linkedin": LinkedIn company page URL (format: linkedin.com/company/...)
   - "twitter": Twitter/X profile URL
   - "instagram": Instagram profile URL
   - "youtube": YouTube channel URL
   - "discord": Discord invite URL
   - "telegram": Telegram group/channel URL
   - "github": GitHub organization URL
   - "tiktok": TikTok profile URL

2. "company_name": Official company/brand name

3. "company_description": One sentence description of what they do

4. "founders": Array of founder names (first and last name)

5. "team_size": Approximate team size (e.g., "10-50", "50-200", "startup", "unknown")

6. "headquarters": City and country of headquarters

7. "year_founded": Year the company was founded

8. "industry": Primary industry/sector

IMPORTANT: 
- Only include social profiles you are confident are official accounts for this company
- Use full URLs for social profiles (e.g., "https://linkedin.com/company/plasma" not just "plasma")
- If you cannot find information, use null for that field
- Return ONLY valid JSON, no markdown or explanation

JSON Response:"""

    async def _call_api(self, query: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a research assistant that finds company information. Always respond with valid JSON only, no markdown formatting.",
                },
                {"role": "user", "content": query},
            ],
            "temperature": 0.1,
            "max_tokens": 1000,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.API_URL, headers=headers, json=payload)
            
            if response.status_code != 200:
                logger.error(f"Perplexity API error {response.status_code}: {response.text}")
                response.raise_for_status()
                
            data = response.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "")

    def _parse_response(self, response: str, domain: str) -> BrandResearch:
        result = BrandResearch(raw_response=response)

        try:
            cleaned = self._strip_markdown_fences(response)
            data = json.loads(cleaned)

            profiles = data.get("social_profiles", {})
            if isinstance(profiles, dict):
                for platform, url in profiles.items():
                    if url and isinstance(url, str) and len(url) > 5:
                        normalized_url = (
                            url if url.startswith("http") else f"https://{url}"
                        )
                        result.social_profiles[platform.lower()] = normalized_url

            result.company_name = data.get("company_name")
            result.company_description = data.get("company_description")
            result.founders = data.get("founders", []) or []
            result.team_size = data.get("team_size")
            result.headquarters = data.get("headquarters")
            result.year_founded = data.get("year_founded")
            result.industry = data.get("industry")
            result.success = True

            logger.info(
                f"Research for {domain}: Found {len(result.social_profiles)} social profiles"
            )

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse Perplexity response as JSON: {e}")
            result.error = f"JSON parse error: {e}"
            result.social_profiles = self._extract_urls_fallback(response)
            if result.social_profiles:
                result.success = True

        return result

    def _strip_markdown_fences(self, text: str) -> str:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            lines = [
                line
                for line in cleaned.split("\n")
                if not line.strip().startswith("```")
            ]
            return "\n".join(lines)
        return cleaned

    def _extract_urls_fallback(self, text: str) -> Dict[str, str]:
        """Regex fallback to extract social URLs when JSON parsing fails."""
        profiles = {}

        patterns = {
            "linkedin": r"linkedin\.com/company/[\w-]+",
            "twitter": r"(?:twitter|x)\.com/[\w-]+",
            "instagram": r"instagram\.com/[\w.-]+",
            "youtube": r"youtube\.com/(?:c/|channel/|@)[\w-]+",
            "discord": r"discord\.(?:gg|com/invite)/[\w-]+",
            "telegram": r"t\.me/[\w-]+",
            "github": r"github\.com/[\w-]+",
            "tiktok": r"tiktok\.com/@[\w.-]+",
        }

        for platform, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                url = match.group(0)
                profiles[platform] = url if url.startswith("http") else f"https://{url}"

        return profiles
