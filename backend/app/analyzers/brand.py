# =============================================================================
# Brand Messaging & Archetype Analyzer
# =============================================================================
# This module analyzes brand messaging, voice, and identifies the brand archetype.
# It uses GPT-4 for semantic analysis and textstat for readability metrics.
# =============================================================================

from typing import Dict, Any, Optional, List
import textstat

from app.config import settings
from app.analyzers.base import BaseAnalyzer, AnalyzerResult
from app.models.report import (
    Finding, Recommendation, SeverityLevel,
    BrandArchetype,
)
from app.services.openai_service import OpenAIService


class BrandMessagingAnalyzer(BaseAnalyzer):
    """
    Analyzes Brand Messaging & Archetype.
    
    This analyzer evaluates:
    - Brand archetype (using 12 Jungian archetypes)
    - Value proposition clarity
    - Tone and voice characteristics
    - Readability and jargon usage
    - Messaging consistency
    
    Score Calculation:
    - Archetype clarity: 25%
    - Value proposition: 30%
    - Readability: 25%
    - Tone consistency: 20%
    """
    
    MODULE_NAME = "brand_messaging"
    WEIGHT = 0.15
    
    # The 12 Brand Archetypes
    ARCHETYPES = {
        "hero": {
            "description": "Seeks to prove worth through courage and determination",
            "keywords": ["win", "power", "strength", "champion", "courage", "overcome"],
            "examples": ["Nike", "FedEx", "BMW"],
        },
        "outlaw": {
            "description": "Seeks revolution and breaking rules",
            "keywords": ["rebel", "disrupt", "revolution", "break", "freedom", "change"],
            "examples": ["Harley-Davidson", "Virgin", "Diesel"],
        },
        "magician": {
            "description": "Makes dreams come true through transformation",
            "keywords": ["transform", "magic", "vision", "dream", "imagine", "create"],
            "examples": ["Apple", "Disney", "Tesla"],
        },
        "everyman": {
            "description": "Seeks belonging and connection",
            "keywords": ["belong", "honest", "real", "friendly", "everyday", "trust"],
            "examples": ["IKEA", "eBay", "Target"],
        },
        "lover": {
            "description": "Seeks intimacy and sensory pleasure",
            "keywords": ["passion", "beauty", "intimacy", "sensual", "desire", "luxury"],
            "examples": ["Chanel", "Victoria's Secret", "Godiva"],
        },
        "jester": {
            "description": "Seeks enjoyment and playfulness",
            "keywords": ["fun", "play", "humor", "enjoy", "laugh", "light"],
            "examples": ["Old Spice", "M&Ms", "Skittles"],
        },
        "caregiver": {
            "description": "Seeks to protect and care for others",
            "keywords": ["care", "protect", "help", "support", "nurture", "safe"],
            "examples": ["Johnson & Johnson", "Volvo", "UNICEF"],
        },
        "ruler": {
            "description": "Seeks control and leadership",
            "keywords": ["lead", "control", "power", "success", "status", "premium"],
            "examples": ["Rolex", "Mercedes-Benz", "American Express"],
        },
        "creator": {
            "description": "Seeks to create something of enduring value",
            "keywords": ["create", "build", "innovate", "design", "craft", "art"],
            "examples": ["Lego", "Adobe", "Pinterest"],
        },
        "innocent": {
            "description": "Seeks happiness and simplicity",
            "keywords": ["simple", "pure", "honest", "good", "happy", "natural"],
            "examples": ["Coca-Cola", "Dove", "Nintendo"],
        },
        "sage": {
            "description": "Seeks truth and understanding",
            "keywords": ["know", "learn", "truth", "wisdom", "expert", "research"],
            "examples": ["Google", "BBC", "Harvard"],
        },
        "explorer": {
            "description": "Seeks freedom through exploration",
            "keywords": ["discover", "explore", "adventure", "freedom", "journey", "new"],
            "examples": ["Jeep", "Patagonia", "National Geographic"],
        },
    }
    
    async def analyze(self) -> AnalyzerResult:
        """
        Run the brand messaging analysis.
        
        Steps:
        1. Extract text content from scraped data
        2. Analyze with GPT-4 for archetype and tone
        3. Calculate readability metrics
        4. Evaluate value proposition clarity
        
        Returns:
            AnalyzerResult: Brand messaging analysis results
        """
        try:
            self._raw_data = {}
            
            # ----------------------------------------------------------------
            # Get content for analysis
            # ----------------------------------------------------------------
            homepage_content = self.scraped_data.get("text_content", "")
            about_content = self.scraped_data.get("about_content", "")
            combined_content = f"{homepage_content}\n\n{about_content}"[:8000]
            
            # ----------------------------------------------------------------
            # Analyze with GPT-4 (or fallback to heuristics)
            # ----------------------------------------------------------------
            if settings.OPENAI_API_KEY and len(combined_content) > 100:
                gpt_analysis = await self._analyze_with_gpt(combined_content)
            else:
                gpt_analysis = self._analyze_with_heuristics(combined_content)
            
            self._raw_data["gpt_analysis"] = gpt_analysis
            
            # ----------------------------------------------------------------
            # Readability Analysis
            # ----------------------------------------------------------------
            readability = self._analyze_readability(combined_content)
            self._raw_data["readability"] = readability
            
            # ----------------------------------------------------------------
            # Value Proposition Analysis
            # ----------------------------------------------------------------
            value_prop = self._analyze_value_proposition()
            self._raw_data["value_proposition"] = value_prop
            
            # ----------------------------------------------------------------
            # Calculate score
            # ----------------------------------------------------------------
            score = self._calculate_score()
            
            # ----------------------------------------------------------------
            # Generate findings and recommendations
            # ----------------------------------------------------------------
            self._findings = self._generate_findings()
            self._recommendations = self._generate_recommendations()
            
            # ----------------------------------------------------------------
            # Build result data
            # ----------------------------------------------------------------
            archetype_data = gpt_analysis.get("archetype", {})
            result_data = {
                "score": score,
                "archetype": archetype_data,
                "value_proposition": value_prop.get("proposition"),
                "value_proposition_clarity": value_prop.get("clarity", 5),
                "tagline": self.scraped_data.get("title", "").split(" - ")[0] if " - " in self.scraped_data.get("title", "") else None,
                "tone_keywords": gpt_analysis.get("tone_keywords", []),
                "tone_description": gpt_analysis.get("tone_description"),
                "tone_consistency": gpt_analysis.get("tone_consistency", 7),
                "readability_score": readability.get("flesch_reading_ease"),
                "reading_grade_level": readability.get("grade_level"),
                "is_jargon_heavy": readability.get("is_jargon_heavy", False),
                "jargon_examples": readability.get("jargon_examples", []),
                "key_themes": gpt_analysis.get("themes", []),
                "emotional_hooks": gpt_analysis.get("emotional_hooks", []),
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
                error=f"Brand messaging analysis failed: {str(e)}",
            )
    
    async def _analyze_with_gpt(self, content: str) -> Dict[str, Any]:
        """
        Analyze brand messaging using the enhanced OpenAI service.
        
        Uses the OpenAIService for:
        - Brand archetype identification
        - Tone analysis
        - Value proposition clarity
        
        Args:
            content: Website text content
        
        Returns:
            dict: GPT analysis results
        """
        try:
            # Initialize OpenAI service
            openai_service = OpenAIService()
            
            # Get brand name for context
            brand_name = self.scraped_data.get("brand_name") or self.domain
            
            # Run archetype and tone analysis in parallel
            archetype_result = await openai_service.analyze_archetype(content, brand_name)
            tone_result = await openai_service.analyze_tone(content)
            
            # Build result from service responses
            return {
                "archetype": {
                    "primary": archetype_result.primary_archetype,
                    "secondary": archetype_result.secondary_archetype,
                    "confidence": archetype_result.confidence,
                    "description": archetype_result.reasoning or archetype_result.archetype_description,
                    "example_brands": archetype_result.example_brands,
                },
                "tone_keywords": tone_result.tone_descriptors,
                "tone_description": f"{tone_result.primary_tone} tone. {tone_result.emotional_appeal}" if tone_result.emotional_appeal else tone_result.primary_tone,
                "themes": [],  # Will be populated by content analysis if available
                "emotional_hooks": [tone_result.emotional_appeal] if tone_result.emotional_appeal else [],
                "tone_consistency": int(tone_result.consistency_score * 10),
                "formality_level": tone_result.formality_level,
                "tone_issues": tone_result.issues,
            }
                    
        except Exception as e:
            print(f"GPT analysis failed: {e}")
            return self._analyze_with_heuristics(content)
    
    def _analyze_with_heuristics(self, content: str) -> Dict[str, Any]:
        """
        Fallback analysis using keyword matching.
        
        Args:
            content: Website text content
        
        Returns:
            dict: Heuristic analysis results
        """
        content_lower = content.lower()
        
        # Score each archetype based on keyword presence
        archetype_scores = {}
        for archetype, data in self.ARCHETYPES.items():
            score = sum(1 for kw in data["keywords"] if kw in content_lower)
            archetype_scores[archetype] = score
        
        # Get top archetype
        if archetype_scores:
            primary = max(archetype_scores, key=archetype_scores.get)
            primary_score = archetype_scores[primary]
            
            # Get secondary if close
            sorted_archetypes = sorted(archetype_scores.items(), key=lambda x: x[1], reverse=True)
            secondary = sorted_archetypes[1][0] if len(sorted_archetypes) > 1 and sorted_archetypes[1][1] > 0 else None
            
            archetype_info = self.ARCHETYPES[primary]
        else:
            primary = "everyman"
            primary_score = 0
            secondary = None
            archetype_info = self.ARCHETYPES["everyman"]
        
        return {
            "archetype": {
                "primary": primary.title(),
                "secondary": secondary.title() if secondary else None,
                "confidence": min(0.9, primary_score / 10 + 0.3),
                "description": archetype_info["description"],
                "example_brands": archetype_info["examples"],
            },
            "tone_keywords": ["professional", "informative"],
            "tone_description": "The brand uses a professional tone focused on conveying information.",
            "themes": ["innovation", "quality"],
            "emotional_hooks": ["trust", "reliability"],
            "tone_consistency": 6,
        }
    
    def _analyze_readability(self, content: str) -> Dict[str, Any]:
        """
        Analyze text readability using textstat.
        
        Args:
            content: Text content
        
        Returns:
            dict: Readability metrics
        """
        if len(content) < 100:
            return {
                "flesch_reading_ease": 50,
                "grade_level": 10,
                "is_jargon_heavy": False,
                "jargon_examples": [],
            }
        
        # Flesch Reading Ease (higher is easier)
        flesch_score = textstat.flesch_reading_ease(content)
        
        # Grade level
        grade_level = textstat.flesch_kincaid_grade(content)
        
        # Check for common jargon/buzzwords
        jargon_terms = [
            "synergy", "paradigm", "leverage", "holistic", "ecosystem",
            "disrupt", "blockchain", "Web3", "tokenomics", "DeFi",
            "scalable", "innovative", "revolutionary", "next-generation",
            "cutting-edge", "best-in-class", "world-class"
        ]
        
        found_jargon = [term for term in jargon_terms if term.lower() in content.lower()]
        is_jargon_heavy = len(found_jargon) >= 3
        
        return {
            "flesch_reading_ease": flesch_score,
            "grade_level": grade_level,
            "is_jargon_heavy": is_jargon_heavy,
            "jargon_examples": found_jargon[:5],
        }
    
    def _analyze_value_proposition(self) -> Dict[str, Any]:
        """
        Analyze the clarity of the value proposition.
        
        Returns:
            dict: Value proposition analysis
        """
        # Get homepage heading
        headings = self.scraped_data.get("headings", {})
        h1s = headings.get("h1", [])
        title = self.scraped_data.get("title", "")
        meta_desc = self.scraped_data.get("meta_description", "")
        
        # Try to identify value proposition
        proposition = h1s[0] if h1s else title.split(" - ")[0] if " - " in title else title
        
        # Evaluate clarity (heuristic)
        clarity = 5  # Default
        
        if proposition:
            # Check if it explains what the product is
            action_words = ["get", "create", "build", "discover", "start", "learn", "buy", "try"]
            has_action = any(word in proposition.lower() for word in action_words)
            
            # Check length (too short or too long is bad)
            word_count = len(proposition.split())
            good_length = 5 <= word_count <= 15
            
            # Check for vagueness
            vague_words = ["innovative", "amazing", "best", "unique", "revolutionary"]
            is_vague = any(word in proposition.lower() for word in vague_words)
            
            if has_action and good_length and not is_vague:
                clarity = 8
            elif has_action or good_length:
                clarity = 6
            elif is_vague:
                clarity = 4
        
        return {
            "proposition": proposition,
            "clarity": clarity,
            "has_clear_benefit": clarity >= 6,
        }
    
    def _calculate_score(self) -> float:
        """Calculate the brand messaging score."""
        score = 0.0
        gpt = self._raw_data.get("gpt_analysis", {})
        readability = self._raw_data.get("readability", {})
        value_prop = self._raw_data.get("value_proposition", {})
        
        # Archetype clarity (25%)
        archetype = gpt.get("archetype", {})
        confidence = archetype.get("confidence", 0.5)
        archetype_score = confidence * 100
        score += archetype_score * 0.25
        
        # Value proposition (30%)
        clarity = value_prop.get("clarity", 5)
        vp_score = clarity * 10
        score += vp_score * 0.30
        
        # Readability (25%)
        flesch = readability.get("flesch_reading_ease", 50)
        # Flesch: 60-70 is ideal for general audience
        if 50 <= flesch <= 80:
            read_score = 90
        elif 30 <= flesch < 50 or 80 < flesch <= 100:
            read_score = 70
        else:
            read_score = 40
        
        if readability.get("is_jargon_heavy"):
            read_score -= 20
        
        score += read_score * 0.25
        
        # Tone consistency (20%)
        consistency = gpt.get("tone_consistency", 5)
        consistency_score = consistency * 10
        score += consistency_score * 0.20
        
        return self.clamp_score(score)
    
    def _generate_findings(self) -> List[Finding]:
        """Generate findings based on the analysis."""
        findings = []
        gpt = self._raw_data.get("gpt_analysis", {})
        readability = self._raw_data.get("readability", {})
        value_prop = self._raw_data.get("value_proposition", {})
        
        # Archetype findings
        archetype = gpt.get("archetype", {})
        if archetype.get("primary"):
            findings.append(Finding(
                title=f"Brand Archetype: {archetype['primary']}",
                detail=f"{archetype.get('description', '')} Examples of this archetype: "
                       f"{', '.join(archetype.get('example_brands', [])[:3])}.",
                severity=SeverityLevel.INFO,
            ))
        
        # Readability findings
        grade = readability.get("grade_level", 10)
        if grade > 12:
            findings.append(Finding(
                title="Content Readability is Too Complex",
                detail=f"Reading level is grade {grade:.0f}, which is too complex for most audiences. "
                       "Aim for grade 8-10 for broader accessibility.",
                severity=SeverityLevel.MEDIUM,
            ))
        elif grade < 6:
            findings.append(Finding(
                title="Content May Be Too Simple",
                detail=f"Reading level is grade {grade:.0f}. While accessible, ensure the content "
                       "still conveys expertise and credibility.",
                severity=SeverityLevel.LOW,
            ))
        
        if readability.get("is_jargon_heavy"):
            findings.append(Finding(
                title="Heavy Use of Jargon",
                detail=f"Found multiple buzzwords/jargon: {', '.join(readability['jargon_examples'][:3])}. "
                       "This may confuse or alienate potential customers.",
                severity=SeverityLevel.MEDIUM,
            ))
        
        # Value proposition findings
        if value_prop.get("clarity", 5) < 5:
            findings.append(Finding(
                title="Unclear Value Proposition",
                detail="The homepage doesn't clearly communicate what the product/service does "
                       "or who it's for. Visitors may leave confused.",
                severity=SeverityLevel.HIGH,
            ))
        
        return findings
    
    def _generate_recommendations(self) -> List[Recommendation]:
        """Generate recommendations based on findings."""
        recommendations = []
        gpt = self._raw_data.get("gpt_analysis", {})
        readability = self._raw_data.get("readability", {})
        value_prop = self._raw_data.get("value_proposition", {})
        
        # Value proposition
        if value_prop.get("clarity", 5) < 7:
            recommendations.append(Recommendation(
                title="Clarify Your Value Proposition",
                description="Rewrite your homepage headline to clearly state: What you do, "
                           "Who it's for, and What makes you different. Follow the format: "
                           "'[Product] helps [audience] do [benefit] by [how].'",
                priority=SeverityLevel.HIGH,
                category="brand_messaging",
                impact="high",
                effort="low",
            ))
        
        # Readability
        if readability.get("grade_level", 10) > 12:
            recommendations.append(Recommendation(
                title="Simplify Your Copy",
                description="Reduce reading complexity to grade 8-10 level. Use shorter sentences, "
                           "common words, and break up long paragraphs. Tools like Hemingway Editor "
                           "can help identify overly complex sentences.",
                priority=SeverityLevel.MEDIUM,
                category="brand_messaging",
                impact="medium",
                effort="medium",
            ))
        
        if readability.get("is_jargon_heavy"):
            recommendations.append(Recommendation(
                title="Reduce Jargon and Buzzwords",
                description=(
                    "Replace industry jargon with plain language. Instead of 'leveraging "
                    "synergies', say 'working together'. Clear language builds trust "
                    "and converts better."
                ),
                priority=SeverityLevel.MEDIUM,
                category="brand_messaging",
                impact="medium",
                effort="low",
            ))
        
        # Archetype consistency
        archetype = gpt.get("archetype", {})
        if archetype.get("primary"):
            recommendations.append(Recommendation(
                title=f"Lean Into Your {archetype['primary']} Archetype",
                description=f"Your brand shows {archetype['primary']} characteristics. Embrace this "
                           "across all touchpoints - website, social media, and communications. "
                           "Consistent brand personality builds stronger emotional connections.",
                priority=SeverityLevel.LOW,
                category="brand_messaging",
                impact="medium",
                effort="medium",
            ))
        
        return recommendations

