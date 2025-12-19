# =============================================================================
# Analysis Orchestrator
# =============================================================================
# This module coordinates the execution of all analysis modules.
# It handles parallel execution, progress tracking, and result aggregation.
# =============================================================================

import asyncio
from typing import Dict, Any, Optional, Callable, Awaitable, List
from datetime import datetime

from app.config import settings
from app.models.report import (
    FullReport,
    SEOReport,
    SocialMediaReport,
    BrandMessagingReport,
    UXReport,
    AIDiscoverabilityReport,
    ContentReport,
    TeamPresenceReport,
    ChannelFitReport,
    ScoreCard,
    Recommendation,
)
from app.analyzers.base import AnalysisContext, AnalyzerResult
from app.scrapers.website import WebsiteScraper


class AnalysisOrchestrator:
    """
    Orchestrates the complete brand analysis pipeline.
    
    This class:
    1. Scrapes the website for shared data
    2. Runs all analysis modules (with parallelization where possible)
    3. Aggregates results into the final report
    4. Calculates overall scores and generates top recommendations
    
    Usage:
        orchestrator = AnalysisOrchestrator(url="https://example.com")
        report = await orchestrator.run(progress_callback=my_callback)
    
    Attributes:
        url: Website URL to analyze
        description: Optional business description
        industry: Optional industry category
        context: Shared analysis context
    """
    
    def __init__(
        self,
        url: str,
        description: Optional[str] = None,
        industry: Optional[str] = None,
    ):
        """
        Initialize the orchestrator.
        
        Args:
            url: Website URL to analyze
            description: Optional business description
            industry: Optional industry category
        """
        self.url = url.rstrip("/")
        self.description = description
        self.industry = industry
        
        # Extract domain
        from urllib.parse import urlparse
        parsed = urlparse(url)
        self.domain = (parsed.netloc or parsed.path).replace("www.", "")
        
        # Initialize context (will be populated during run)
        self.context: Optional[AnalysisContext] = None
    
    async def run(
        self,
        progress_callback: Optional[Callable[[str, str], Awaitable[None]]] = None,
    ) -> FullReport:
        """
        Run the complete analysis pipeline.
        
        This is the main entry point. It:
        1. Scrapes the website
        2. Runs all analyzers
        3. Generates the final report
        
        Args:
            progress_callback: Async function to call with (module, status) updates
        
        Returns:
            FullReport: Complete analysis report
        """
        # ---------------------------------------------------------------------
        # Initialize Context
        # ---------------------------------------------------------------------
        self.context = AnalysisContext(
            url=self.url,
            domain=self.domain,
            description=self.description,
            industry=self.industry,
            progress_callback=progress_callback,
        )
        
        # ---------------------------------------------------------------------
        # Phase 1: Scrape Website
        # ---------------------------------------------------------------------
        await self._update_progress("seo", "running")
        
        scraper = WebsiteScraper(self.url)
        scraped_data = await scraper.scrape()
        self.context.scraped_data = scraped_data
        
        # ---------------------------------------------------------------------
        # Phase 2: Run Analysis Modules
        # ---------------------------------------------------------------------
        # Import all analyzers
        from app.analyzers.seo import SEOAnalyzer
        from app.analyzers.social import SocialMediaAnalyzer
        from app.analyzers.brand import BrandMessagingAnalyzer
        from app.analyzers.ux import UXAnalyzer
        from app.analyzers.ai_discoverability import AIDiscoverabilityAnalyzer
        from app.analyzers.content import ContentAnalyzer
        from app.analyzers.team import TeamPresenceAnalyzer
        from app.analyzers.channel_fit import ChannelFitAnalyzer
        
        # Create analyzer instances
        analyzers = {
            "seo": SEOAnalyzer(
                url=self.url,
                description=self.description,
                industry=self.industry,
                scraped_data=scraped_data,
            ),
            "social_media": SocialMediaAnalyzer(
                url=self.url,
                description=self.description,
                industry=self.industry,
                scraped_data=scraped_data,
            ),
            "brand_messaging": BrandMessagingAnalyzer(
                url=self.url,
                description=self.description,
                industry=self.industry,
                scraped_data=scraped_data,
            ),
            "website_ux": UXAnalyzer(
                url=self.url,
                description=self.description,
                industry=self.industry,
                scraped_data=scraped_data,
            ),
            "ai_discoverability": AIDiscoverabilityAnalyzer(
                url=self.url,
                description=self.description,
                industry=self.industry,
                scraped_data=scraped_data,
            ),
            "content": ContentAnalyzer(
                url=self.url,
                description=self.description,
                industry=self.industry,
                scraped_data=scraped_data,
            ),
            "team_presence": TeamPresenceAnalyzer(
                url=self.url,
                description=self.description,
                industry=self.industry,
                scraped_data=scraped_data,
            ),
            "channel_fit": ChannelFitAnalyzer(
                url=self.url,
                description=self.description,
                industry=self.industry,
                scraped_data=scraped_data,
            ),
        }
        
        results = await self._run_analyzers_parallel(analyzers)
        self.context.results = results
        
        # ---------------------------------------------------------------------
        # Phase 3: Generate Scorecard
        # ---------------------------------------------------------------------
        await self._update_progress("scorecard", "running")
        scorecard = self._generate_scorecard(results)
        await self._update_progress("scorecard", "completed")
        
        # ---------------------------------------------------------------------
        # Phase 4: Build Final Report
        # ---------------------------------------------------------------------
        report = self._build_report(results, scorecard, scraped_data)
        
        return report
    
    async def _run_analyzers_parallel(
        self,
        analyzers: Dict[str, Any],
    ) -> Dict[str, AnalyzerResult]:
        """
        Run all analyzers in parallel for faster execution.
        
        Analyzers are grouped into waves to manage resource usage:
        - Wave 1: SEO, Social, AI Discoverability (external API heavy)
        - Wave 2: Brand, UX, Content (compute heavy)
        - Wave 3: Team, Channel Fit (depends on other results)
        
        Returns:
            Dict mapping module names to their results
        """
        results: Dict[str, AnalyzerResult] = {}
        
        wave_1 = ["seo", "social_media", "ai_discoverability"]
        wave_2 = ["brand_messaging", "website_ux", "content"]
        wave_3 = ["team_presence", "channel_fit"]
        
        per_analyzer_timeout = settings.ANALYSIS_TIMEOUT / 3
        
        for wave in [wave_1, wave_2, wave_3]:
            wave_analyzers = {k: v for k, v in analyzers.items() if k in wave}
            wave_results = await self._execute_wave(
                wave_analyzers,
                timeout=per_analyzer_timeout,
            )
            results.update(wave_results)
        
        return results
    
    async def _execute_wave(
        self,
        wave_analyzers: Dict[str, Any],
        timeout: float,
    ) -> Dict[str, AnalyzerResult]:
        """Execute a wave of analyzers in parallel."""
        results: Dict[str, AnalyzerResult] = {}
        
        async def run_single(name: str, analyzer) -> tuple[str, AnalyzerResult]:
            await self._update_progress(name, "running")
            try:
                result = await asyncio.wait_for(
                    analyzer.analyze(),
                    timeout=timeout,
                )
                await self._update_progress(name, "completed")
                return name, result
            except asyncio.TimeoutError:
                await self._update_progress(name, "failed")
                return name, AnalyzerResult(
                    score=0,
                    error=f"Analysis timed out after {timeout:.0f}s",
                )
            except Exception as e:
                await self._update_progress(name, "failed")
                return name, AnalyzerResult(
                    score=0,
                    error=str(e),
                )
        
        tasks = [
            run_single(name, analyzer)
            for name, analyzer in wave_analyzers.items()
        ]
        
        completed = await asyncio.gather(*tasks, return_exceptions=False)
        
        for name, result in completed:
            results[name] = result
        
        return results
    
    async def _update_progress(self, module: str, status: str) -> None:
        """Update progress via callback if provided."""
        if self.context and self.context.progress_callback:
            await self.context.progress_callback(module, status)
    
    def _generate_scorecard(
        self,
        results: Dict[str, AnalyzerResult],
    ) -> ScoreCard:
        """
        Generate the overall scorecard from module results.
        
        This method:
        1. Calculates weighted overall score
        2. Determines letter grade
        3. Identifies strengths and weaknesses
        4. Aggregates top recommendations
        
        Args:
            results: Results from all analyzer modules
        
        Returns:
            ScoreCard: Complete scorecard
        """
        # Weight configuration
        weights = {
            "seo": settings.WEIGHT_SEO,
            "social_media": settings.WEIGHT_SOCIAL_MEDIA,
            "brand_messaging": settings.WEIGHT_BRAND_MESSAGING,
            "website_ux": settings.WEIGHT_WEBSITE_UX,
            "ai_discoverability": settings.WEIGHT_AI_DISCOVERABILITY,
            "content": settings.WEIGHT_CONTENT,
            "team_presence": settings.WEIGHT_TEAM_PRESENCE,
            "channel_fit": settings.WEIGHT_CHANNEL_FIT,
        }
        
        # Calculate weighted score
        total_weight = 0
        weighted_sum = 0
        scores = {}
        
        for module, result in results.items():
            weight = weights.get(module, 0.1)
            if result.is_success():
                weighted_sum += result.score * weight
                total_weight += weight
            scores[module] = result.score
        
        overall_score = weighted_sum / total_weight if total_weight > 0 else 0
        
        # Determine grade using enhanced A+ to F scale
        # Based on marketing industry standards and a16z benchmarks
        grade = self._calculate_grade(overall_score)
        
        # Calculate benchmark comparison for each module
        benchmark_comparison = self._calculate_benchmark_comparison(scores)
        
        # Identify strengths (modules with score >= 75)
        strengths = []
        for module, result in results.items():
            if result.is_success() and result.score >= 75:
                strengths.append(f"Strong {module.replace('_', ' ')} performance (score: {result.score:.0f})")
        
        # Identify weaknesses (modules with score < 60)
        weaknesses = []
        for module, result in results.items():
            if result.is_success() and result.score < 60:
                weaknesses.append(f"Needs improvement: {module.replace('_', ' ')} (score: {result.score:.0f})")
        
        # Aggregate all recommendations and sort by priority
        all_recommendations: List[Recommendation] = []
        for result in results.values():
            all_recommendations.extend(result.recommendations)
        
        # Sort by priority (critical > high > medium > low)
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        all_recommendations.sort(
            key=lambda r: priority_order.get(r.priority.value, 4)
        )
        
        # Get top 5 recommendations
        top_recommendations = all_recommendations[:5]
        
        # Identify quick wins (high impact, low effort)
        quick_wins = [
            r for r in all_recommendations
            if r.impact == "high" and r.effort == "low"
        ][:3]
        
        # Generate summary
        summary = self._generate_summary(overall_score, grade, strengths, weaknesses)
        
        return ScoreCard(
            overall_score=overall_score,
            scores=scores,
            grade=grade,
            summary=summary,
            strengths=strengths,
            weaknesses=weaknesses,
            opportunities=[],  # Could be derived from recommendations
            top_recommendations=top_recommendations,
            quick_wins=quick_wins,
            benchmark_comparison=benchmark_comparison,  # Include benchmark data
        )
    
    def _calculate_grade(self, score: float) -> str:
        """
        Calculate letter grade from score using enhanced A+ to F scale.
        
        Grade Scale (based on marketing industry standards):
        - A+ (90-100): Exceptional - Industry leader
        - A  (80-89):  Excellent - Strong foundation
        - B  (70-79):  Good - Above average
        - C  (60-69):  Average - Room for improvement
        - D  (50-59):  Below average - Needs attention
        - F  (0-49):   Critical - Immediate action needed
        
        Args:
            score: Numeric score (0-100)
        
        Returns:
            str: Letter grade
        """
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"
    
    def _calculate_benchmark_comparison(
        self,
        scores: Dict[str, float],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compare scores against industry benchmarks.
        
        Benchmarks are based on research from:
        - Google PageSpeed Insights (SEO)
        - Sprout Social (Social Media)
        - StoryBrand (Brand Messaging)
        - Nielsen Norman Group (UX)
        - Schema.org adoption rates (AI Discoverability)
        
        Args:
            scores: Module scores
        
        Returns:
            Dict: Comparison data for each module
        """
        # Industry benchmark values (70th percentile)
        benchmarks = {
            "seo": 65,
            "social_media": 55,
            "brand_messaging": 60,
            "website_ux": 70,
            "ai_discoverability": 40,
            "content": 60,
            "team_presence": 50,
            "channel_fit": 55,
        }
        
        comparison = {}
        for module, score in scores.items():
            benchmark = benchmarks.get(module, 50)
            diff = score - benchmark
            
            comparison[module] = {
                "score": score,
                "benchmark": benchmark,
                "difference": diff,
                "percentile": "above" if diff > 5 else ("below" if diff < -5 else "at"),
                "label": (
                    f"+{diff:.0f} above average" if diff > 5
                    else f"{diff:.0f} below average" if diff < -5
                    else "At industry average"
                ),
            }
        
        return comparison
    
    def _generate_summary(
        self,
        score: float,
        grade: str,
        strengths: List[str],
        weaknesses: List[str],
    ) -> str:
        """Generate a human-readable summary of the analysis."""
        if score >= 80:
            opening = f"This brand demonstrates strong overall performance with a score of {score:.0f}/100 (Grade {grade})."
        elif score >= 60:
            opening = f"This brand shows solid fundamentals with a score of {score:.0f}/100 (Grade {grade}), though there's room for improvement."
        else:
            opening = f"This brand has significant opportunities for improvement, with a current score of {score:.0f}/100 (Grade {grade})."
        
        strength_text = ""
        if strengths:
            strength_text = f" Key strengths include {', '.join(strengths[:2]).lower()}."
        
        weakness_text = ""
        if weaknesses:
            weakness_text = f" Priority areas for improvement are {', '.join(weaknesses[:2]).lower()}."
        
        return f"{opening}{strength_text}{weakness_text}"
    
    def _build_report(
        self,
        results: Dict[str, AnalyzerResult],
        scorecard: ScoreCard,
        scraped_data: Dict[str, Any],
    ) -> FullReport:
        """
        Build the complete report from all analyzer results.
        
        Args:
            results: Results from all analyzers
            scorecard: Generated scorecard
            scraped_data: Original scraped data
        
        Returns:
            FullReport: Complete analysis report
        """
        # Helper to get result data with defaults
        def get_section(module: str, report_class):
            result = results.get(module, AnalyzerResult())
            data = result.data or {}
            
            # Merge findings and recommendations
            data["findings"] = [f.model_dump() for f in result.findings]
            data["recommendations"] = [r.model_dump() for r in result.recommendations]
            data["score"] = result.score
            
            return report_class(**data)
        
        # Build each section
        return FullReport(
            generated_at=datetime.utcnow(),
            url=self.url,
            brand_name=scraped_data.get("brand_name"),
            brand_logo_url=scraped_data.get("logo_url"),
            seo=get_section("seo", SEOReport),
            social_media=get_section("social_media", SocialMediaReport),
            brand_messaging=get_section("brand_messaging", BrandMessagingReport),
            website_ux=get_section("website_ux", UXReport),
            ai_discoverability=get_section("ai_discoverability", AIDiscoverabilityReport),
            content=get_section("content", ContentReport),
            team_presence=get_section("team_presence", TeamPresenceReport),
            channel_fit=get_section("channel_fit", ChannelFitReport),
            scorecard=scorecard,
        )

