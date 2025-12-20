# =============================================================================
# Website Scraper
# =============================================================================
# This module provides comprehensive website scraping capabilities.
# It extracts content, meta tags, social links, and structural information.
# =============================================================================

import re
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup


class WebsiteScraper:
    """
    Scrapes website content and extracts useful information.

    This scraper:
    1. Fetches the homepage HTML
    2. Extracts meta tags (title, description, OG tags, etc.)
    3. Finds social media links
    4. Extracts main text content
    5. Analyzes page structure (headings, CTAs, etc.)

    Usage:
        scraper = WebsiteScraper("https://example.com")
        data = await scraper.scrape()

    Attributes:
        url: Website URL to scrape
        timeout: Request timeout in seconds
    """

    # Common social media platforms to detect
    SOCIAL_PLATFORMS = {
        "twitter": ["twitter.com", "x.com"],
        "linkedin": ["linkedin.com"],
        "instagram": ["instagram.com"],
        "facebook": ["facebook.com", "fb.com"],
        "youtube": ["youtube.com"],
        "tiktok": ["tiktok.com"],
        "discord": ["discord.gg", "discord.com"],
        "telegram": ["t.me", "telegram.me"],
        "github": ["github.com"],
        "medium": ["medium.com"],
    }

    # Headers to appear as a regular browser
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }

    def __init__(self, url: str, timeout: int = 30):
        """
        Initialize the scraper.

        Args:
            url: Website URL to scrape
            timeout: Request timeout in seconds
        """
        self.url = url.rstrip("/")
        self.timeout = timeout
        self._soup: Optional[BeautifulSoup] = None
        self._html: str = ""

    async def scrape(self) -> Dict[str, Any]:
        """
        Scrape the website and extract all relevant data.

        Returns:
            dict: Extracted website data including:
                - html: Raw HTML content
                - title: Page title
                - meta_description: Meta description
                - og_tags: Open Graph tags
                - social_links: Detected social media links
                - text_content: Main text content
                - headings: H1-H6 headings
                - ctas: Detected call-to-action buttons/links
                - images: Image information
                - schema_markup: Schema.org data if present
                - links: Important internal/external links
        """
        # Fetch the homepage
        html = await self._fetch_page(self.url)
        if not html:
            return {"error": "Failed to fetch page", "html": ""}

        self._html = html
        self._soup = BeautifulSoup(html, "lxml")

        # Also try to fetch About page for more context
        about_content = await self._fetch_about_page()

        # Extract all data
        return {
            "html": html,
            "url": self.url,
            "domain": urlparse(self.url).netloc.replace("www.", ""),
            # Meta information
            "title": self._extract_title(),
            "meta_description": self._extract_meta_description(),
            "og_tags": self._extract_og_tags(),
            "twitter_cards": self._extract_twitter_cards(),
            "canonical_url": self._extract_canonical(),
            "favicon": self._extract_favicon(),
            "logo_url": self._extract_logo(),
            # Content
            "text_content": self._extract_text_content(),
            "about_content": about_content,
            "headings": self._extract_headings(),
            "paragraphs": self._extract_paragraphs(),
            # Structure
            "navigation": self._extract_navigation(),
            "ctas": self._extract_ctas(),
            "forms": self._extract_forms(),
            # Social & External
            "social_links": self._extract_social_links(),
            "external_links": self._extract_external_links(),
            # Technical
            "schema_markup": self._extract_schema_markup(),
            "has_ssl": self.url.startswith("https"),
            # Derived
            "brand_name": self._infer_brand_name(),
            "word_count": len(self._extract_text_content().split()),
        }

    async def _fetch_page(self, url: str) -> str:
        """
        Fetch a page's HTML content.

        Args:
            url: URL to fetch

        Returns:
            str: HTML content or empty string on failure
        """
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
            ) as client:
                response = await client.get(url, headers=self.DEFAULT_HEADERS)
                response.raise_for_status()
                return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return ""

    async def _fetch_about_page(self) -> str:
        """
        Try to fetch the About page for additional brand context.

        Returns:
            str: About page text content or empty string
        """
        # Common about page paths
        about_paths = ["/about", "/about-us", "/company", "/who-we-are"]

        for path in about_paths:
            about_url = urljoin(self.url, path)
            html = await self._fetch_page(about_url)
            if html:
                soup = BeautifulSoup(html, "lxml")
                # Extract main content
                main = soup.find("main") or soup.find("article") or soup.find("body")
                if main:
                    # Remove script and style elements
                    for tag in main.find_all(["script", "style", "nav", "footer"]):
                        tag.decompose()
                    return main.get_text(separator=" ", strip=True)[:5000]

        return ""

    def _extract_title(self) -> str:
        """Extract the page title."""
        if not self._soup:
            return ""

        title_tag = self._soup.find("title")
        if title_tag:
            return title_tag.get_text(strip=True)

        # Fallback to OG title
        og_title = self._soup.find("meta", property="og:title")
        if og_title:
            return og_title.get("content", "")

        return ""

    def _extract_meta_description(self) -> str:
        """Extract the meta description."""
        if not self._soup:
            return ""

        desc = self._soup.find("meta", attrs={"name": "description"})
        if desc:
            return desc.get("content", "")

        # Fallback to OG description
        og_desc = self._soup.find("meta", property="og:description")
        if og_desc:
            return og_desc.get("content", "")

        return ""

    def _extract_og_tags(self) -> Dict[str, str]:
        """Extract Open Graph meta tags."""
        if not self._soup:
            return {}

        og_tags = {}
        for meta in self._soup.find_all("meta", property=re.compile(r"^og:")):
            prop = meta.get("property", "").replace("og:", "")
            content = meta.get("content", "")
            if prop and content:
                og_tags[prop] = content

        return og_tags

    def _extract_twitter_cards(self) -> Dict[str, str]:
        """Extract Twitter Card meta tags."""
        if not self._soup:
            return {}

        twitter_tags = {}
        for meta in self._soup.find_all(
            "meta", attrs={"name": re.compile(r"^twitter:")}
        ):
            name = meta.get("name", "").replace("twitter:", "")
            content = meta.get("content", "")
            if name and content:
                twitter_tags[name] = content

        return twitter_tags

    def _extract_canonical(self) -> Optional[str]:
        """Extract the canonical URL."""
        if not self._soup:
            return None

        link = self._soup.find("link", rel="canonical")
        if link:
            return link.get("href")

        return None

    def _extract_favicon(self) -> Optional[str]:
        """Extract the favicon URL."""
        if not self._soup:
            return None

        # Try multiple favicon formats
        for rel in ["icon", "shortcut icon", "apple-touch-icon"]:
            link = self._soup.find("link", rel=rel)
            if link:
                href = link.get("href", "")
                if href:
                    return urljoin(self.url, href)

        # Default favicon location
        return urljoin(self.url, "/favicon.ico")

    def _extract_logo(self) -> Optional[str]:
        """Try to extract the brand logo URL."""
        if not self._soup:
            return None

        # Common logo patterns
        logo_selectors = [
            'img[class*="logo"]',
            'img[id*="logo"]',
            'img[alt*="logo"]',
            ".logo img",
            "#logo img",
            "header img:first-of-type",
            'a[class*="logo"] img',
        ]

        for selector in logo_selectors:
            try:
                img = self._soup.select_one(selector)
                if img and img.get("src"):
                    return urljoin(self.url, img["src"])
            except Exception:
                continue

        return None

    def _extract_text_content(self) -> str:
        """Extract the main text content from the page."""
        if not self._soup:
            return ""

        # Clone the soup to avoid modifying the original
        soup_copy = BeautifulSoup(str(self._soup), "lxml")

        # Remove non-content elements
        for tag in soup_copy.find_all(
            [
                "script",
                "style",
                "nav",
                "footer",
                "header",
                "aside",
                "noscript",
                "iframe",
                "form",
            ]
        ):
            tag.decompose()

        # Try to find main content area
        main = (
            soup_copy.find("main")
            or soup_copy.find("article")
            or soup_copy.find(id=re.compile(r"(main|content|body)", re.I))
            or soup_copy.find(class_=re.compile(r"(main|content|body)", re.I))
            or soup_copy.find("body")
        )

        if main:
            text = main.get_text(separator=" ", strip=True)
            # Clean up whitespace
            text = re.sub(r"\s+", " ", text)
            return text[:10000]  # Limit to 10k chars

        return ""

    def _extract_headings(self) -> Dict[str, List[str]]:
        """Extract all headings organized by level."""
        if not self._soup:
            return {}

        headings = {}
        for level in range(1, 7):
            tag = f"h{level}"
            headings[tag] = [
                h.get_text(strip=True)
                for h in self._soup.find_all(tag)
                if h.get_text(strip=True)
            ]

        return headings

    def _extract_paragraphs(self) -> List[str]:
        """Extract paragraph text."""
        if not self._soup:
            return []

        paragraphs = []
        for p in self._soup.find_all("p"):
            text = p.get_text(strip=True)
            if len(text) > 20:  # Skip very short paragraphs
                paragraphs.append(text)

        return paragraphs[:20]  # Limit to first 20

    def _extract_navigation(self) -> List[Dict[str, str]]:
        """Extract navigation menu items."""
        if not self._soup:
            return []

        nav_items = []

        # Find navigation elements
        navs = self._soup.find_all(["nav", "header"])
        for nav in navs:
            for link in nav.find_all("a"):
                text = link.get_text(strip=True)
                href = link.get("href", "")
                if text and href and not href.startswith("#"):
                    nav_items.append(
                        {
                            "text": text,
                            "href": urljoin(self.url, href),
                        }
                    )

        # Deduplicate
        seen = set()
        unique = []
        for item in nav_items:
            if item["text"] not in seen:
                seen.add(item["text"])
                unique.append(item)

        return unique[:20]  # Limit to 20 items

    def _extract_ctas(self) -> List[Dict[str, Any]]:
        """Extract call-to-action buttons and links."""
        if not self._soup:
            return []

        ctas = []

        # Common CTA patterns
        cta_keywords = [
            "get started",
            "sign up",
            "try",
            "start",
            "demo",
            "contact",
            "buy",
            "subscribe",
            "join",
            "download",
            "free trial",
            "book",
            "schedule",
            "learn more",
        ]

        # Find buttons
        for button in self._soup.find_all(["button", "a"]):
            text = button.get_text(strip=True).lower()
            classes = " ".join(button.get("class", []))

            # Check if it looks like a CTA
            is_cta = (
                any(kw in text for kw in cta_keywords)
                or "btn" in classes
                or "button" in classes
                or "cta" in classes
            )

            if is_cta:
                ctas.append(
                    {
                        "text": button.get_text(strip=True),
                        "href": button.get("href", ""),
                        "tag": button.name,
                        "classes": button.get("class", []),
                    }
                )

        return ctas[:10]  # Limit to 10 CTAs

    def _extract_forms(self) -> List[Dict[str, Any]]:
        """Extract form information."""
        if not self._soup:
            return []

        forms = []
        for form in self._soup.find_all("form"):
            fields = []
            for input_tag in form.find_all(["input", "textarea", "select"]):
                fields.append(
                    {
                        "type": input_tag.get("type", input_tag.name),
                        "name": input_tag.get("name", ""),
                        "placeholder": input_tag.get("placeholder", ""),
                    }
                )

            forms.append(
                {
                    "action": form.get("action", ""),
                    "method": form.get("method", "get"),
                    "field_count": len(fields),
                    "fields": fields[:5],  # Limit fields
                }
            )

        return forms

    def _extract_social_links(self) -> Dict[str, str]:
        """Extract social media profile links."""
        if not self._soup:
            return {}

        social_links = {}

        for link in self._soup.find_all("a", href=True):
            href = link["href"].lower()

            for platform, domains in self.SOCIAL_PLATFORMS.items():
                if any(domain in href for domain in domains):
                    # Store the full URL
                    social_links[platform] = link["href"]
                    break

        return social_links

    def _extract_external_links(self) -> List[str]:
        """Extract external links (excluding social media)."""
        if not self._soup:
            return []

        external_links = []
        our_domain = urlparse(self.url).netloc.replace("www.", "")

        for link in self._soup.find_all("a", href=True):
            href = link["href"]
            if href.startswith(("http://", "https://")):
                link_domain = urlparse(href).netloc.replace("www.", "")
                if link_domain != our_domain:
                    # Not a social link
                    is_social = any(
                        domain in href.lower()
                        for domains in self.SOCIAL_PLATFORMS.values()
                        for domain in domains
                    )
                    if not is_social:
                        external_links.append(href)

        return list(set(external_links))[:20]  # Dedupe and limit

    def _extract_schema_markup(self) -> List[Dict[str, Any]]:
        """Extract Schema.org structured data."""
        if not self._soup:
            return []

        schemas = []

        # Find JSON-LD scripts
        for script in self._soup.find_all("script", type="application/ld+json"):
            try:
                import json

                data = json.loads(script.string)
                if isinstance(data, list):
                    schemas.extend(data)
                else:
                    schemas.append(data)
            except Exception:
                continue

        return schemas

    def _infer_brand_name(self) -> str:
        """Try to infer the brand name from available data."""
        if not self._soup:
            return ""

        # Try OG site_name first
        og_site_name = self._soup.find("meta", property="og:site_name")
        if og_site_name:
            return og_site_name.get("content", "")

        # Try title (often in format "Page - Brand Name")
        title = self._extract_title()
        if " - " in title:
            return title.split(" - ")[-1].strip()
        if " | " in title:
            return title.split(" | ")[-1].strip()

        # Use domain as fallback
        domain = urlparse(self.url).netloc.replace("www.", "")
        return domain.split(".")[0].title()
