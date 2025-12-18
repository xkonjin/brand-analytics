# =============================================================================
# EXPLAINER: AI Discoverability Analyzer
# =============================================================================
#
# WHAT IS THIS?
# This module answers the question: "Does ChatGPT/Claude/Gemini know who you are?"
#
# WHY DO WE NEED IT?
# 1. **The New SEO**: Search is moving from 10 blue links to AI-generated answers.
# 2. **Training Data**: AI models trust authoritative sources like Wikipedia and Knowledge Graphs.
# 3. **Structured Data**: Schema.org markup is the language AI reads directly.
#
# HOW IT WORKS:
# 1. **Wikipedia Check**: Do you have a page? Are you mentioned? (High authority signal).
# 2. **Knowledge Graph**: Is there a Google Knowledge Panel for the brand?
# 3. **Schema Audit**: Do you use Organization/Product schema?
# 4. **Content Depth**: Do you have enough deep content (blogs/docs) for AI to "read"?
#
# SCORING LOGIC (Total 100):
# - Wikipedia (30%): The gold standard for entity recognition.
# - Structured Data (25%): Direct feed to machines.
# - Content Depth (20%): Volume of training data.
# - SERP Visibility (15%): Traditional signals still matter.
# - Knowledge Panel (10%): Google's entity verification.
# =============================================================================

from typing import Dict, Any, List, Optional

from app.config import settings
from app.analyzers.base import BaseAnalyzer, AnalyzerResult
from app.models.report import Finding, Recommendation, SeverityLevel
from app.services.wikipedia_service import WikipediaService, WikipediaPresence
from app.services.google_search_service import GoogleSearchService, SERPAnalysis


class AIDiscoverabilityAnalyzer(BaseAnalyzer):
    """
    Analyzes AI Discoverability (AEO - Answer Engine Optimization).
    """
    
    MODULE_NAME = "ai_discoverability"
    WEIGHT = 0.10
    
    async def analyze(self) -> AnalyzerResult:
        """Run the AI discoverability analysis."""
        try:
            self._raw_data = {}
            
            # Get brand name from scraped data or URL
            brand_name = self._get_brand_name()
            self._raw_data["brand_name"] = brand_name
            
            # ----------------------------------------------------------------
            # 1. Check Wikipedia presence
            # ----------------------------------------------------------------
            # Wikipedia is the primary "fact source" for most LLMs.
            wiki_service = WikipediaService()
            wiki_presence = await wiki_service.check_brand_presence(brand_name)
            self._raw_data["wikipedia"] = {
                "exists": wiki_presence.has_wikipedia_page,
                "url": wiki_presence.article.url if wiki_presence.article else None,
                "description": wiki_presence.article.description if wiki_presence.article else None,
                "extract": wiki_presence.article.extract[:500] if wiki_presence.article and wiki_presence.article.extract else None,
                "notability_score": wiki_presence.notability_score,
                "signals": wiki_presence.signals,
                "mentioned_in": wiki_presence.mentioned_in_other_articles,
            }
            
            # ----------------------------------------------------------------
            # 2. Check SERP visibility
            # ----------------------------------------------------------------
            # If Google trusts you (Knowledge Panel), AI likely trusts you too.
            serp_data = await self._check_serp_visibility(brand_name)
            self._raw_data["serp"] = serp_data
            
            # ----------------------------------------------------------------
            # 3. Analyze structured data (Schema)
            # ----------------------------------------------------------------
            # This is how we "speak machine" to search engines.
            schema = self._analyze_schema_markup()
            self._raw_data["schema"] = schema
            
            # ----------------------------------------------------------------
            # 4. Analyze content depth
            # ----------------------------------------------------------------
            # More high-quality text = higher chance of being in training data.
            content = self._analyze_content_depth()
            self._raw_data["content_depth"] = content
            
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
            # Build result data
            # ----------------------------------------------------------------
            result_data = {
                "score": score,
                "brand_name": brand_name,
                
                # Wikipedia
                "has_wikipedia_page": wiki_presence.has_wikipedia_page,
                "wikipedia_url": wiki_presence.article.url if wiki_presence.article else None,
                "wikipedia_description": wiki_presence.article.description if wiki_presence.article else None,
                "wikipedia_notability_score": wiki_presence.notability_score,
                "mentioned_in_wikipedia_articles": len(wiki_presence.mentioned_in_other_articles),
                
                # SERP
                "brand_in_top_10": serp_data.get("brand_in_top_10", False),
                "serp_position": serp_data.get("brand_position"),
                "has_knowledge_panel": serp_data.get("knowledge_panel_likely", False),
                
                # Schema
                "has_faq_schema": "FAQPage" in schema.get("types", []),
                "has_organization_schema": "Organization" in schema.get("types", []),
                "schema_types": schema.get("types", []),
                "schema_count": schema.get("count", 0),
                
                # Content depth
                "has_blog": content.get("has_blog", False),
                "has_documentation": content.get("has_docs", False),
                "content_depth_score": content.get("score", 0),
                
                # Overall assessment
                "ai_readiness_level": self._get_readiness_level(score),
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
                error=f"AI Discoverability analysis failed: {str(e)}",
            )
    
    def _get_brand_name(self) -> str:
        """Extract brand name from scraped data or URL."""
        # Try to get from scraped data
        brand_name = self.scraped_data.get("brand_name")
        if brand_name:
            return brand_name
        
        # Try to get from title
        title = self.scraped_data.get("title", "")
        if title:
            # Often title is "Brand Name - Tagline" or "Brand Name | Description"
            for sep in [" - ", " | ", " — ", ":"]:
                if sep in title:
                    return title.split(sep)[0].strip()
        
        # Fall back to domain name
        domain = getattr(self, 'domain', self.url)
        if domain:
            # Remove TLD and www
            name = domain.replace("www.", "").split(".")[0]
            # Capitalize
            return name.capitalize()
        
        return "Unknown Brand"
    
    async def _check_serp_visibility(self, brand_name: str) -> Dict[str, Any]:
        """Check brand visibility in search results."""
        # Check if Google Search API is configured
        if not settings.GOOGLE_API_KEY or not settings.GOOGLE_SEARCH_ENGINE_ID:
            # Return mock/default data
            return {
                "available": False,
                "brand_position": None,
                "brand_in_top_10": False,
                "knowledge_panel_likely": False,
            }
        
        try:
            search_service = GoogleSearchService()
            serp = await search_service.search_brand(brand_name, self.domain)
            
            return {
                "available": True,
                "brand_position": serp.brand_position,
                "brand_in_top_10": serp.brand_in_top_10,
                "brand_in_top_3": serp.brand_in_top_3,
                "total_results": serp.total_results,
                "wikipedia_in_results": serp.wikipedia_found,
                "knowledge_panel_likely": serp.knowledge_panel_likely,
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
            }
    
    def _analyze_schema_markup(self) -> Dict[str, Any]:
        """Analyze Schema.org structured data on the website."""
        schemas = self.scraped_data.get("schema_markup", [])
        
        types = []
        for schema in schemas:
            if isinstance(schema, dict):
                schema_type = schema.get("@type", "")
                if schema_type and schema_type not in types:
                    types.append(schema_type)
        
        # Check for recommended schema types
        has_organization = "Organization" in types or "Corporation" in types
        has_faq = "FAQPage" in types
        has_product = "Product" in types or "SoftwareApplication" in types
        has_article = "Article" in types or "BlogPosting" in types
        has_breadcrumb = "BreadcrumbList" in types
        
        # Calculate schema score
        schema_score = 0
        if has_organization:
            schema_score += 30
        if has_faq:
            schema_score += 20
        if has_product:
            schema_score += 15
        if has_article:
            schema_score += 15
        if has_breadcrumb:
            schema_score += 10
        if len(types) > 3:
            schema_score += 10
        
        return {
            "types": types,
            "count": len(schemas),
            "has_organization": has_organization,
            "has_faq": has_faq,
            "has_product": has_product,
            "has_article": has_article,
            "schema_score": min(100, schema_score),
        }
    
    def _analyze_content_depth(self) -> Dict[str, Any]:
        """Analyze content depth for AI indexing potential."""
        # Check navigation for content sections
        nav = self.scraped_data.get("navigation", [])
        nav_texts = [n.get("text", "").lower() for n in nav if isinstance(n, dict)]
        
        # Check for common content sections
        has_blog = any("blog" in t or "news" in t or "articles" in t for t in nav_texts)
        has_docs = any(d in t for t in nav_texts for d in ["docs", "documentation", "help", "support", "guide", "learn"])
        has_resources = any("resource" in t or "library" in t or "faq" in t for t in nav_texts)
        has_about = any("about" in t or "company" in t or "team" in t for t in nav_texts)
        
        # Analyze content length
        word_count = self.scraped_data.get("word_count", 0)
        text_content = self.scraped_data.get("text_content", "")
        
        # Count paragraphs
        paragraphs = len([p for p in text_content.split("\n\n") if len(p) > 100])
        
        # Calculate content depth score (0-10)
        score = 0
        
        # Word count contribution
        if word_count >= 1000:
            score += 3
        elif word_count >= 500:
            score += 2
        elif word_count >= 200:
            score += 1
        
        # Content sections contribution
        if has_blog:
            score += 2
        if has_docs:
            score += 2
        if has_resources:
            score += 1
        if has_about:
            score += 1
        
        # Paragraph structure contribution
        if paragraphs >= 5:
            score += 1
        
        return {
            "has_blog": has_blog,
            "has_docs": has_docs,
            "has_resources": has_resources,
            "has_about": has_about,
            "word_count": word_count,
            "paragraph_count": paragraphs,
            "score": min(10, score),
        }
    
    def _get_readiness_level(self, score: float) -> str:
        """Determine AI readiness level based on score."""
        if score >= 75:
            return "high"
        elif score >= 50:
            return "medium"
        elif score >= 25:
            return "low"
        return "very_low"
    
    def _calculate_score(self) -> float:
        """
        Calculate the overall AI discoverability score.
        """
        score = 0.0
        
        # Wikipedia presence (30%)
        # It's hard to get, but extremely valuable for AI trust
        wiki = self._raw_data.get("wikipedia", {})
        if wiki.get("exists"):
            # Full Wikipedia page
            notability = wiki.get("notability_score", 50)
            score += (notability / 100) * 30
        elif wiki.get("mentioned_in"):
            # Mentioned in other articles (better than nothing)
            score += min(15, len(wiki.get("mentioned_in", [])) * 5)
        
        # Structured data (25%)
        # Easy technical win
        schema = self._raw_data.get("schema", {})
        schema_score = schema.get("schema_score", 0)
        score += (schema_score / 100) * 25
        
        # Content depth (20%)
        # AI feeds on text
        content = self._raw_data.get("content_depth", {})
        content_score = content.get("score", 0)
        score += (content_score / 10) * 20
        
        # SERP visibility (15%)
        serp = self._raw_data.get("serp", {})
        if serp.get("brand_in_top_3"):
            score += 15
        elif serp.get("brand_in_top_10"):
            score += 10
        elif serp.get("brand_position"):
            score += 5
        
        # Knowledge panel (10%)
        if serp.get("knowledge_panel_likely"):
            score += 10
        elif wiki.get("exists"):
            score += 5  # Likely to have knowledge panel with Wikipedia
        
        return self.clamp_score(score)
    
    def _generate_findings(self) -> List[Finding]:
        """Generate findings based on the analysis."""
        findings = []
        
        wiki = self._raw_data.get("wikipedia", {})
        schema = self._raw_data.get("schema", {})
        serp = self._raw_data.get("serp", {})
        content = self._raw_data.get("content_depth", {})
        
        # Wikipedia findings
        if wiki.get("exists"):
            findings.append(Finding(
                title="Wikipedia Page Found",
                detail=f"Your brand has a Wikipedia page, which significantly improves AI discoverability. "
                       f"AI assistants often cite Wikipedia as an authoritative source.",
                severity=SeverityLevel.INFO,
                data={"url": wiki.get("url"), "description": wiki.get("description")},
            ))
        elif wiki.get("mentioned_in"):
            findings.append(Finding(
                title="Mentioned in Wikipedia",
                detail=f"Your brand is mentioned in {len(wiki.get('mentioned_in', []))} Wikipedia articles, "
                       f"but doesn't have a dedicated page. This provides some discoverability.",
                severity=SeverityLevel.LOW,
                data={"articles": wiki.get("mentioned_in", [])[:3]},
            ))
        else:
            findings.append(Finding(
                title="No Wikipedia Presence",
                detail="No Wikipedia page or mentions found for your brand. AI assistants may have "
                       "limited information about your company. Consider working toward Wikipedia notability.",
                severity=SeverityLevel.MEDIUM,
            ))
        
        # Schema findings
        if schema.get("count", 0) == 0:
            findings.append(Finding(
                title="No Structured Data Found",
                detail="No Schema.org markup detected on your website. Structured data helps AI and "
                       "search engines understand your content better, enabling rich results.",
                severity=SeverityLevel.MEDIUM,
            ))
        elif not schema.get("has_organization"):
            findings.append(Finding(
                title="Missing Organization Schema",
                detail="No Organization or Corporation schema found. This is the most important "
                       "structured data for brand identification by AI systems.",
                severity=SeverityLevel.MEDIUM,
                data={"current_schemas": schema.get("types", [])},
            ))
        else:
            types_count = len(schema.get("types", []))
            findings.append(Finding(
                title=f"Structured Data Present ({types_count} types)",
                detail=f"Found {types_count} schema types: {', '.join(schema.get('types', [])[:5])}. "
                       f"This helps AI understand your content.",
                severity=SeverityLevel.INFO,
            ))
        
        # SERP findings
        if serp.get("available"):
            if serp.get("brand_in_top_3"):
                findings.append(Finding(
                    title="Strong SERP Position",
                    detail=f"Your brand ranks in the top 3 for brand name searches (position {serp.get('brand_position')}). "
                           f"This indicates strong search visibility.",
                    severity=SeverityLevel.INFO,
                ))
            elif not serp.get("brand_in_top_10"):
                findings.append(Finding(
                    title="Weak SERP Position",
                    detail="Your brand doesn't appear in the top 10 search results for your brand name. "
                           "This may indicate SEO issues or brand name conflicts.",
                    severity=SeverityLevel.HIGH,
                ))
        
        # Content depth findings
        if content.get("score", 0) <= 3:
            findings.append(Finding(
                title="Limited Content Depth",
                detail="Your website has limited content depth. AI systems favor websites with "
                       "substantial, authoritative content. Consider adding a blog, documentation, "
                       "or resource center.",
                severity=SeverityLevel.MEDIUM,
            ))
        
        return findings
    
    def _generate_recommendations(self) -> List[Recommendation]:
        """Generate recommendations based on findings."""
        recommendations = []
        
        wiki = self._raw_data.get("wikipedia", {})
        schema = self._raw_data.get("schema", {})
        content = self._raw_data.get("content_depth", {})
        
        # Wikipedia recommendation
        if not wiki.get("exists"):
            recommendations.append(Recommendation(
                title="Work Toward Wikipedia Notability",
                description="Getting a Wikipedia page significantly boosts AI discoverability. Focus on: "
                           "1) Getting coverage in reliable sources (press, industry publications), "
                           "2) Building notable achievements or milestones, "
                           "3) Ensuring your company information is verifiable from independent sources. "
                           "Note: Don't create your own Wikipedia page - that's against their policies.",
                priority=SeverityLevel.MEDIUM,
                category="ai_discoverability",
                impact="high",
                effort="high",
            ))
        
        # Schema recommendations
        if not schema.get("has_organization"):
            recommendations.append(Recommendation(
                title="Add Organization Schema",
                description="Implement Organization schema markup on your homepage. Include: name, logo, "
                           "url, description, social profiles, founding date, and founders. This helps "
                           "AI systems accurately identify and describe your brand.",
                priority=SeverityLevel.HIGH,
                category="ai_discoverability",
                impact="high",
                effort="low",
            ))
        
        if not schema.get("has_faq"):
            recommendations.append(Recommendation(
                title="Add FAQ Schema",
                description="Create an FAQ section with Schema.org FAQPage markup. FAQ content is "
                           "directly consumed by AI assistants when answering questions about your "
                           "brand or industry. Focus on common questions your customers ask.",
                priority=SeverityLevel.MEDIUM,
                category="ai_discoverability",
                impact="medium",
                effort="low",
            ))
        
        # Content recommendations
        if not content.get("has_blog"):
            recommendations.append(Recommendation(
                title="Start Publishing Content",
                description="Create a blog or resource center with in-depth articles about your industry. "
                           "AI systems are trained on web content, so publishing authoritative articles "
                           "increases the chance of AI assistants knowing about and recommending your brand.",
                priority=SeverityLevel.MEDIUM,
                category="ai_discoverability",
                impact="high",
                effort="medium",
            ))
        
        if not content.get("has_docs") and content.get("word_count", 0) < 1000:
            recommendations.append(Recommendation(
                title="Create Comprehensive Documentation",
                description="Build detailed documentation or help content. This signals expertise and "
                           "provides AI systems with accurate information about your products/services. "
                           "Consider creating how-to guides, use cases, and detailed product descriptions.",
                priority=SeverityLevel.LOW,
                category="ai_discoverability",
                impact="medium",
                effort="medium",
            ))
        
        return recommendations
