# =============================================================================
# EXPLAINER: Content Analysis Module
# =============================================================================
#
# WHAT IS THIS?
# This module evaluates the brand's content strategy (blogs, social posts).
#
# WHY DO WE NEED IT?
# 1. **Balance**: Too much "Buy My Stuff" (Promotional) kills engagement.
# 2. **Topics**: Are you talking about things your audience cares about?
# 3. **Consistency**: Is the content feed alive?
#
# HOW IT WORKS:
# 1. **Topic Modeling**: Extracts keywords/themes from website text.
# 2. **Post Analysis**: (Mocked for now) Categorizes social posts into:
#    - Promotional (Sales)
#    - Educational (Value)
#    - Community (Engagement)
# 3. **The 3-2-1 Rule**: We check if the mix aligns with best practices.
#
# SCORING LOGIC:
# - Mix Quality: Is it balanced?
# - Topic Relevance: Do topics match the industry?
# =============================================================================

from typing import Dict, Any, List
from datetime import datetime

from app.analyzers.base import BaseAnalyzer, AnalyzerResult
from app.models.report import Finding, Recommendation, SeverityLevel, PostAnalysis


class ContentAnalyzer(BaseAnalyzer):
    """Analyzes content strategy based on recent posts and blog content."""
    
    MODULE_NAME = "content"
    WEIGHT = 0.10
    
    async def analyze(self) -> AnalyzerResult:
        try:
            self._raw_data = {}
            
            # Analyze content from website
            web_content = self._analyze_web_content()
            self._raw_data["web"] = web_content
            
            # Mock social post analysis (would use API in production)
            # This is a placeholder until we have full social history access
            posts = self._mock_post_analysis()
            self._raw_data["posts"] = posts
            
            score = self._calculate_score()
            self._findings = self._generate_findings()
            self._recommendations = self._generate_recommendations()
            
            result_data = {
                "score": score,
                "recent_posts": [p.model_dump() for p in posts.get("items", [])],
                "content_mix": posts.get("content_mix", {}),
                "overall_sentiment": "positive",
                "uses_images": True,
                "uses_videos": False,
                "common_topics": web_content.get("topics", []),
            }
            
            return AnalyzerResult(
                score=score,
                findings=self._findings,
                recommendations=self._recommendations,
                data=result_data,
            )
        except Exception as e:
            return AnalyzerResult(score=0, error=str(e))
    
    def _analyze_web_content(self) -> Dict[str, Any]:
        """Analyze website content themes."""
        text = self.scraped_data.get("text_content", "").lower()
        
        # Simple topic detection
        topics = []
        topic_keywords = {
            "technology": ["tech", "software", "platform", "api"],
            "finance": ["payment", "financial", "money", "invest"],
            "crypto": ["blockchain", "crypto", "defi", "web3"],
            "community": ["community", "users", "members", "together"],
        }
        
        for topic, keywords in topic_keywords.items():
            if any(kw in text for kw in keywords):
                topics.append(topic)
        
        return {"topics": topics[:3], "word_count": len(text.split())}
    
    def _mock_post_analysis(self) -> Dict[str, Any]:
        """Mock post analysis - would use Twitter API in production."""
        return {
            "items": [
                PostAnalysis(
                    platform="twitter",
                    content_preview="Exciting update coming soon! Stay tuned...",
                    likes=45,
                    comments=5,
                    shares=10,
                    content_type="text",
                    sentiment="positive",
                ),
            ],
            "content_mix": {
                "promotional": 0.5,
                "educational": 0.3,
                "community": 0.2,
            },
        }
    
    def _calculate_score(self) -> float:
        web = self._raw_data.get("web", {})
        posts = self._raw_data.get("posts", {})
        
        score = 50  # Base score
        if len(web.get("topics", [])) >= 2:
            score += 20
        if posts.get("items"):
            score += 30
        
        return self.clamp_score(score)
    
    def _generate_findings(self) -> List[Finding]:
        posts = self._raw_data.get("posts", {})
        mix = posts.get("content_mix", {})
        
        findings = []
        if mix.get("promotional", 0) > 0.6:
            findings.append(Finding(
                title="Content is Heavily Promotional",
                detail="Over 60% of content is promotional. Consider diversifying with educational content.",
                severity=SeverityLevel.MEDIUM,
            ))
        return findings
    
    def _generate_recommendations(self) -> List[Recommendation]:
        return [
            Recommendation(
                title="Diversify Content Mix",
                description="Follow the 3-2-1 rule: 3 valuable/educational posts, 2 community posts, "
                           "1 promotional post. This keeps your feed engaging rather than salesy.",
                priority=SeverityLevel.MEDIUM,
                category="content",
                impact="medium",
                effort="medium",
            ),
        ]
