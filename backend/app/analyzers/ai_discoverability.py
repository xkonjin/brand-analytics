# =============================================================================
# AI Discoverability Analyzer
# =============================================================================
# Evaluates how well the brand can be discovered by AI assistants.
# =============================================================================

from typing import Dict, Any, List
import httpx

from app.config import settings
from app.analyzers.base import BaseAnalyzer, AnalyzerResult
from app.models.report import Finding, Recommendation, SeverityLevel


class AIDiscoverabilityAnalyzer(BaseAnalyzer):
    """Analyzes AI Discoverability - Wikipedia, Knowledge Graph, structured data."""
    
    MODULE_NAME = "ai_discoverability"
    WEIGHT = 0.10
    
    async def analyze(self) -> AnalyzerResult:
        try:
            self._raw_data = {}
            
            # Check Wikipedia presence
            wiki = await self._check_wikipedia()
            self._raw_data["wikipedia"] = wiki
            
            # Analyze structured data
            schema = self._analyze_schema_markup()
            self._raw_data["schema"] = schema
            
            # Analyze content depth
            content = self._analyze_content_depth()
            self._raw_data["content_depth"] = content
            
            score = self._calculate_score()
            self._findings = self._generate_findings()
            self._recommendations = self._generate_recommendations()
            
            result_data = {
                "score": score,
                "has_wikipedia_page": wiki.get("exists", False),
                "wikipedia_url": wiki.get("url"),
                "has_knowledge_panel": False,  # Would need search API
                "has_faq_schema": "FAQPage" in schema.get("types", []),
                "has_organization_schema": "Organization" in schema.get("types", []),
                "schema_types": schema.get("types", []),
                "blog_post_count": content.get("blog_count", 0),
                "has_documentation": content.get("has_docs", False),
                "content_depth_score": content.get("score", 5),
                "ai_readiness_level": self._get_readiness_level(score),
            }
            
            return AnalyzerResult(
                score=score,
                findings=self._findings,
                recommendations=self._recommendations,
                data=result_data,
            )
        except Exception as e:
            return AnalyzerResult(score=0, error=str(e))
    
    async def _check_wikipedia(self) -> Dict[str, Any]:
        """Check if brand has a Wikipedia page."""
        brand_name = self.scraped_data.get("brand_name", self.domain)
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    "https://en.wikipedia.org/w/api.php",
                    params={
                        "action": "query",
                        "titles": brand_name,
                        "format": "json",
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    pages = data.get("query", {}).get("pages", {})
                    exists = "-1" not in pages
                    return {"exists": exists, "url": f"https://en.wikipedia.org/wiki/{brand_name}" if exists else None}
        except:
            pass
        return {"exists": False}
    
    def _analyze_schema_markup(self) -> Dict[str, Any]:
        """Analyze Schema.org structured data."""
        schemas = self.scraped_data.get("schema_markup", [])
        types = [s.get("@type", "") for s in schemas if isinstance(s, dict)]
        return {"types": types, "count": len(schemas)}
    
    def _analyze_content_depth(self) -> Dict[str, Any]:
        """Analyze content depth for AI indexing."""
        nav = self.scraped_data.get("navigation", [])
        nav_texts = [n.get("text", "").lower() for n in nav]
        
        has_blog = any("blog" in t for t in nav_texts)
        has_docs = any(d in nav_texts for d in ["docs", "documentation", "help", "support"])
        
        word_count = self.scraped_data.get("word_count", 0)
        score = min(10, word_count / 500 + (3 if has_blog else 0) + (2 if has_docs else 0))
        
        return {"has_blog": has_blog, "has_docs": has_docs, "blog_count": 0, "score": score}
    
    def _get_readiness_level(self, score: float) -> str:
        if score >= 70: return "high"
        elif score >= 40: return "medium"
        return "low"
    
    def _calculate_score(self) -> float:
        score = 0.0
        wiki = self._raw_data.get("wikipedia", {})
        schema = self._raw_data.get("schema", {})
        content = self._raw_data.get("content_depth", {})
        
        if wiki.get("exists"): score += 30
        score += min(30, schema.get("count", 0) * 10)
        score += content.get("score", 0) * 4
        
        return self.clamp_score(score)
    
    def _generate_findings(self) -> List[Finding]:
        findings = []
        wiki = self._raw_data.get("wikipedia", {})
        schema = self._raw_data.get("schema", {})
        
        if not wiki.get("exists"):
            findings.append(Finding(
                title="No Wikipedia Presence",
                detail="No Wikipedia page found. AI assistants often reference Wikipedia for factual information.",
                severity=SeverityLevel.MEDIUM,
            ))
        
        if schema.get("count", 0) == 0:
            findings.append(Finding(
                title="No Structured Data",
                detail="No Schema.org markup found. Structured data helps AI and search engines understand your content.",
                severity=SeverityLevel.MEDIUM,
            ))
        
        return findings
    
    def _generate_recommendations(self) -> List[Recommendation]:
        recommendations = []
        schema = self._raw_data.get("schema", {})
        
        if schema.get("count", 0) < 2:
            recommendations.append(Recommendation(
                title="Add Schema.org Structured Data",
                description="Implement Organization, FAQ, and Product schema to help AI systems understand your brand. "
                           "This improves discoverability in AI-powered search results.",
                priority=SeverityLevel.MEDIUM,
                category="ai_discoverability",
                impact="medium",
                effort="medium",
            ))
        
        recommendations.append(Recommendation(
            title="Create Authoritative Content",
            description="Publish in-depth articles answering common industry questions. AI systems favor authoritative, "
                       "well-structured content that demonstrates expertise.",
            priority=SeverityLevel.MEDIUM,
            category="ai_discoverability",
            impact="high",
            effort="high",
        ))
        
        return recommendations

