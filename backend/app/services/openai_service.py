# =============================================================================
# EXPLAINER: OpenAI Service (The "Brain")
# =============================================================================
#
# WHAT IS THIS?
# This service is the interface to OpenAI's Large Language Models (LLMs).
# It handles all "intelligence" tasks: figuring out brand archetypes, analyzing sentiment,
# and writing marketing recommendations.
#
# WHY DO WE NEED IT?
# Raw data (like page speed or follower counts) is useful, but it doesn't tell the "story".
# We use LLMs to synthesize this data into human-readable insights.
# - Instead of just saying "Text is Grade 12 level", we say "Your text is too complex for a consumer brand."
# - Instead of just "You use words like 'hero'", we identify the "Hero Archetype".
#
# KEY FEATURES:
# 1. **Prompt Engineering**: Structured prompts to get consistent JSON outputs from the LLM.
# 2. **Resilience**: Uses `tenacity` for exponential backoff retries (crucial for API stability).
# 3. **Type Safety**: Returns dataclasses, not raw dicts, so the rest of the app is safe.
# 4. **Cost Control**: Truncates content to avoid hitting token limits and excessive costs.
# =============================================================================

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import httpx
import json
import logging
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import settings

logger = logging.getLogger(__name__)


class BrandArchetype(str, Enum):
    """The 12 Jungian brand archetypes."""
    HERO = "Hero"
    OUTLAW = "Outlaw"
    MAGICIAN = "Magician"
    EVERYMAN = "Everyman"
    LOVER = "Lover"
    JESTER = "Jester"
    CAREGIVER = "Caregiver"
    RULER = "Ruler"
    CREATOR = "Creator"
    INNOCENT = "Innocent"
    SAGE = "Sage"
    EXPLORER = "Explorer"


@dataclass
class ArchetypeAnalysis:
    """Result of brand archetype analysis."""
    primary_archetype: str
    secondary_archetype: Optional[str] = None
    confidence: float = 0.0
    reasoning: str = ""
    archetype_description: str = ""
    example_brands: List[str] = field(default_factory=list)


@dataclass
class ToneAnalysis:
    """Result of brand tone analysis."""
    primary_tone: str = ""
    tone_descriptors: List[str] = field(default_factory=list)
    formality_level: str = "neutral"  # formal, neutral, casual
    emotional_appeal: str = ""
    consistency_score: float = 0.0
    issues: List[str] = field(default_factory=list)


@dataclass
class ValuePropositionAnalysis:
    """Analysis of the brand's value proposition."""
    clarity_score: float = 0.0  # 0-100
    value_proposition: str = ""
    target_audience: str = ""
    key_benefits: List[str] = field(default_factory=list)
    differentiation: str = ""
    issues: List[str] = field(default_factory=list)


@dataclass
class ContentThemeAnalysis:
    """Analysis of content themes."""
    themes: List[Dict[str, Any]] = field(default_factory=list)
    content_mix: Dict[str, float] = field(default_factory=dict)  # promotional, educational, etc.
    sentiment: str = "neutral"
    sentiment_score: float = 0.0


class OpenAIService:
    """
    Comprehensive OpenAI service for brand analysis.
    
    Uses Tenacity for robust retries on API failures.
    """
    
    API_URL = "https://api.openai.com/v1/chat/completions"
    TIMEOUT = 60
    
    # Archetype descriptions for context
    # These are passed to the frontend or used in report generation
    ARCHETYPE_INFO = {
        "Hero": {
            "description": "Courageous, bold, inspirational. Seeks to prove worth through mastery.",
            "examples": ["Nike", "FedEx", "BMW", "Duracell"],
            "keywords": ["achieve", "win", "overcome", "strength", "courage", "mastery"],
        },
        "Outlaw": {
            "description": "Rebellious, disruptive, liberating. Challenges the status quo.",
            "examples": ["Harley-Davidson", "Virgin", "Diesel", "Uber"],
            "keywords": ["revolution", "break", "disrupt", "freedom", "rebel", "change"],
        },
        "Magician": {
            "description": "Visionary, transformative, innovative. Makes dreams come true.",
            "examples": ["Apple", "Disney", "Tesla", "Dyson"],
            "keywords": ["transform", "vision", "imagine", "magic", "innovation", "future"],
        },
        "Everyman": {
            "description": "Relatable, authentic, down-to-earth. Connects through belonging.",
            "examples": ["IKEA", "Target", "eBay", "Budweiser"],
            "keywords": ["everyone", "together", "community", "real", "honest", "simple"],
        },
        "Lover": {
            "description": "Passionate, sensual, intimate. Creates emotional connections.",
            "examples": ["Chanel", "Victoria's Secret", "Godiva", "Hallmark"],
            "keywords": ["love", "passion", "beauty", "desire", "intimate", "sensual"],
        },
        "Jester": {
            "description": "Fun, playful, entertaining. Lives in the moment with joy.",
            "examples": ["Old Spice", "M&M's", "Geico", "Dollar Shave Club"],
            "keywords": ["fun", "play", "enjoy", "laugh", "humor", "entertainment"],
        },
        "Caregiver": {
            "description": "Nurturing, compassionate, protective. Helps and protects others.",
            "examples": ["Johnson & Johnson", "Volvo", "UNICEF", "Pampers"],
            "keywords": ["care", "protect", "help", "support", "nurture", "safe"],
        },
        "Ruler": {
            "description": "Authoritative, refined, successful. Provides order and stability.",
            "examples": ["Mercedes-Benz", "Rolex", "Microsoft", "American Express"],
            "keywords": ["premium", "exclusive", "quality", "control", "power", "success"],
        },
        "Creator": {
            "description": "Creative, artistic, innovative. Values self-expression.",
            "examples": ["Lego", "Adobe", "Pinterest", "Crayola"],
            "keywords": ["create", "build", "design", "imagine", "express", "craft"],
        },
        "Innocent": {
            "description": "Pure, optimistic, simple. Seeks happiness and paradise.",
            "examples": ["Coca-Cola", "Dove", "Nintendo", "Whole Foods"],
            "keywords": ["simple", "pure", "honest", "happy", "natural", "good"],
        },
        "Sage": {
            "description": "Wise, knowledgeable, trusted. Seeks truth and understanding.",
            "examples": ["Google", "BBC", "TED", "The Economist"],
            "keywords": ["know", "learn", "understand", "truth", "wisdom", "expert"],
        },
        "Explorer": {
            "description": "Adventurous, independent, pioneering. Seeks discovery and freedom.",
            "examples": ["Jeep", "The North Face", "Starbucks", "GoPro"],
            "keywords": ["discover", "explore", "freedom", "adventure", "journey", "new"],
        },
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI service.
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
    )
    async def _call_api(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 1500,
        json_mode: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Make a call to the OpenAI API with retry logic.
        
        Uses Tenacity decorators to handle:
        - Network errors (httpx.RequestError)
        - HTTP 5xx errors (via raise_for_status logic inside)
        - Rate limiting (429) usually needs specific handling, but exponential backoff often helps.
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            temperature: Creativity level (0-1)
            max_tokens: Maximum response tokens
            json_mode: Whether to enforce JSON response
        """
        if not self.api_key:
            logger.warning("OpenAI API key not configured")
            return None
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        request_body = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if json_mode:
            request_body["response_format"] = {"type": "json_object"}
        
        async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
            response = await client.post(
                self.API_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=request_body,
            )
            
            # Raise exception for 4xx/5xx to trigger retry
            # Note: We might want to avoid retrying 400 Bad Request, but 429/500/503 are good to retry
            if response.status_code in [429, 500, 502, 503, 504]:
                response.raise_for_status()
            elif response.status_code != 200:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                return None
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            if json_mode:
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    logger.error("Failed to decode JSON from OpenAI response")
                    return None
            return {"text": content}
    
    async def analyze_archetype(
        self,
        content: str,
        brand_name: Optional[str] = None,
    ) -> ArchetypeAnalysis:
        """
        Analyze brand archetype from website content.
        """
        # Truncate content to fit token limits (heuristic)
        content = content[:4000]
        
        # PROMPT STRATEGY:
        # We define the 12 archetypes in the system prompt to ground the model.
        # We ask for "key indicators" to make the reasoning transparent.
        system_prompt = """You are a brand strategist expert in Jungian brand archetypes. 
Analyze the brand content and identify the primary and secondary archetypes.
The 12 archetypes are: Hero, Outlaw, Magician, Everyman, Lover, Jester, Caregiver, Ruler, Creator, Innocent, Sage, Explorer."""
        
        prompt = f"""Analyze this brand content and identify the brand archetype.

Brand Name: {brand_name or "Unknown"}

Content:
{content}

Respond with JSON:
{{
    "primary_archetype": "Archetype name",
    "secondary_archetype": "Second archetype or null",
    "confidence": 0.0-1.0,
    "reasoning": "Explanation of why this archetype fits",
    "key_indicators": ["word or phrase 1", "word or phrase 2", ...],
    "brand_personality_traits": ["trait1", "trait2", ...]
}}"""
        
        try:
            result = await self._call_api(prompt, system_prompt)
        except Exception as e:
            logger.error(f"Archetype analysis failed after retries: {e}")
            result = None
        
        if not result:
            return ArchetypeAnalysis(
                primary_archetype="Sage",  # Default fallback
                confidence=0.5,
                reasoning="Unable to analyze - using default",
            )
        
        primary = result.get("primary_archetype", "Sage")
        archetype_info = self.ARCHETYPE_INFO.get(primary, {})
        
        return ArchetypeAnalysis(
            primary_archetype=primary,
            secondary_archetype=result.get("secondary_archetype"),
            confidence=result.get("confidence", 0.7),
            reasoning=result.get("reasoning", ""),
            archetype_description=archetype_info.get("description", ""),
            example_brands=archetype_info.get("examples", []),
        )
    
    async def analyze_tone(self, content: str) -> ToneAnalysis:
        """
        Analyze the brand's tone and voice.
        """
        content = content[:4000]
        
        system_prompt = """You are a brand voice and tone expert. Analyze the content and describe the brand's communication style."""
        
        prompt = f"""Analyze the tone and voice of this brand content.

Content:
{content}

Respond with JSON:
{{
    "primary_tone": "Main tone (e.g., Professional, Friendly, Authoritative)",
    "tone_descriptors": ["descriptor1", "descriptor2", ...],
    "formality_level": "formal" | "neutral" | "casual",
    "emotional_appeal": "What emotion does it evoke?",
    "consistency_score": 0.0-1.0,
    "voice_characteristics": ["characteristic1", "characteristic2"],
    "issues": ["Any tone inconsistencies or problems"]
}}"""
        
        try:
            result = await self._call_api(prompt, system_prompt)
        except Exception:
            result = None
        
        if not result:
            return ToneAnalysis(
                primary_tone="Professional",
                formality_level="neutral",
                consistency_score=0.7,
            )
        
        return ToneAnalysis(
            primary_tone=result.get("primary_tone", "Neutral"),
            tone_descriptors=result.get("tone_descriptors", []),
            formality_level=result.get("formality_level", "neutral"),
            emotional_appeal=result.get("emotional_appeal", ""),
            consistency_score=result.get("consistency_score", 0.7),
            issues=result.get("issues", []),
        )
    
    async def analyze_value_proposition(
        self,
        content: str,
        brand_name: Optional[str] = None,
    ) -> ValuePropositionAnalysis:
        """
        Analyze the clarity of the brand's value proposition.
        """
        content = content[:3000]
        
        # PROMPT STRATEGY:
        # We specifically ask about "clarity in 5 seconds" because that's the web usability standard.
        system_prompt = """You are a marketing strategist. Analyze whether the brand clearly communicates what they do, for whom, and why it matters."""
        
        prompt = f"""Analyze the value proposition clarity of this brand content.

Brand: {brand_name or "Unknown"}
Content:
{content}

Respond with JSON:
{{
    "clarity_score": 0-100,
    "value_proposition": "One sentence summary of what they offer",
    "target_audience": "Who is the content for?",
    "key_benefits": ["benefit1", "benefit2", ...],
    "differentiation": "What makes them unique?",
    "is_clear_in_5_seconds": true/false,
    "issues": ["clarity issue 1", "clarity issue 2"]
}}"""
        
        try:
            result = await self._call_api(prompt, system_prompt)
        except Exception:
            result = None
        
        if not result:
            return ValuePropositionAnalysis(clarity_score=60)
        
        return ValuePropositionAnalysis(
            clarity_score=result.get("clarity_score", 60),
            value_proposition=result.get("value_proposition", ""),
            target_audience=result.get("target_audience", ""),
            key_benefits=result.get("key_benefits", []),
            differentiation=result.get("differentiation", ""),
            issues=result.get("issues", []),
        )
    
    async def analyze_content_themes(
        self,
        posts: List[str],
    ) -> ContentThemeAnalysis:
        """
        Analyze themes and sentiment across content pieces (tweets, blogs).
        """
        if not posts:
            return ContentThemeAnalysis()

        # Join posts for analysis
        posts_text = "\n".join([f"- {p}" for p in posts[:20]])
        
        system_prompt = """You are a content strategist. Analyze the themes, content mix, and sentiment of these posts."""
        
        prompt = f"""Analyze these content pieces:

{posts_text}

Respond with JSON:
{{
    "themes": [
        {{"name": "theme name", "frequency": "high/medium/low", "examples": ["post1", "post2"]}}
    ],
    "content_mix": {{
        "promotional": 0.0-1.0,
        "educational": 0.0-1.0,
        "community": 0.0-1.0,
        "news": 0.0-1.0,
        "entertainment": 0.0-1.0
    }},
    "sentiment": "positive" | "neutral" | "negative",
    "sentiment_score": -1.0 to 1.0,
    "top_topics": ["topic1", "topic2"]
}}"""
        
        try:
            result = await self._call_api(prompt, system_prompt)
        except Exception:
            result = None
        
        if not result:
            return ContentThemeAnalysis(
                sentiment="neutral",
                sentiment_score=0.0,
            )
        
        return ContentThemeAnalysis(
            themes=result.get("themes", []),
            content_mix=result.get("content_mix", {}),
            sentiment=result.get("sentiment", "neutral"),
            sentiment_score=result.get("sentiment_score", 0.0),
        )
    
    async def generate_recommendations(
        self,
        findings: List[Dict[str, Any]],
        context: str,
        industry: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized recommendations based on findings.
        """
        # Filter and format findings for context
        findings_text = "\n".join([
            f"- {f.get('title', '')}: {f.get('detail', '')}"
            for f in findings[:10]
        ])
        
        system_prompt = """You are a marketing consultant. Generate specific, actionable recommendations based on the analysis findings."""
        
        prompt = f"""Based on these brand analysis findings, generate 5 specific recommendations.

Industry: {industry or 'General'}
Context: {context}

Findings:
{findings_text}

Respond with JSON:
{{
    "recommendations": [
        {{
            "title": "Short action title",
            "description": "Detailed, specific recommendation",
            "priority": "critical" | "high" | "medium" | "low",
            "impact": "high" | "medium" | "low",
            "effort": "high" | "medium" | "low",
            "category": "seo" | "branding" | "content" | "social" | "ux" | "technical"
        }}
    ]
}}"""
        
        try:
            result = await self._call_api(prompt, system_prompt, temperature=0.5)
        except Exception:
            result = None
        
        if not result:
            return []
        
        return result.get("recommendations", [])
    
    async def analyze_readability(self, content: str) -> Dict[str, Any]:
        """
        Analyze content readability and complexity.
        
        Uses heuristic algorithms (Flesch-Kincaid style) instead of LLM to save costs and latency.
        """
        # Calculate basic metrics without API
        words = content.split()
        word_count = len(words)
        sentences = content.replace("!", ".").replace("?", ".").split(".")
        sentence_count = len([s for s in sentences if s.strip()])
        
        avg_words_per_sentence = word_count / max(sentence_count, 1)
        
        # Estimate grade level (simplified Flesch-Kincaid)
        syllables = sum(self._count_syllables(word) for word in words)
        if word_count > 0 and sentence_count > 0:
            grade_level = 0.39 * (word_count / sentence_count) + 11.8 * (syllables / word_count) - 15.59
            grade_level = max(0, min(18, grade_level))
        else:
            grade_level = 8
        
        # Determine readability rating
        if grade_level <= 6:
            rating = "very_easy"
        elif grade_level <= 8:
            rating = "easy"
        elif grade_level <= 10:
            rating = "moderate"
        elif grade_level <= 12:
            rating = "difficult"
        else:
            rating = "very_difficult"
        
        return {
            "grade_level": round(grade_level, 1),
            "rating": rating,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_words_per_sentence": round(avg_words_per_sentence, 1),
            "is_optimal": 6 <= grade_level <= 10,
            "suggestion": self._get_readability_suggestion(grade_level),
        }
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)."""
        word = word.lower()
        count = 0
        vowels = "aeiouy"
        prev_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_vowel:
                count += 1
            prev_vowel = is_vowel
        
        # Adjust for silent e
        if word.endswith("e"):
            count -= 1
        
        return max(1, count)
    
    def _get_readability_suggestion(self, grade_level: float) -> str:
        """Get suggestion based on grade level."""
        if grade_level > 12:
            return "Content is too complex. Simplify sentences and use common words to reach a broader audience."
        elif grade_level > 10:
            return "Content is somewhat complex. Consider breaking long sentences and reducing jargon."
        elif grade_level < 6:
            return "Content is very simple. This is fine for broad audiences but may seem too basic for professional contexts."
        else:
            return "Readability is at an optimal level for most audiences."


# Convenience functions for backwards compatibility
async def analyze_brand_archetype(content: str) -> Dict[str, Any]:
    """Legacy function - use OpenAIService.analyze_archetype instead."""
    service = OpenAIService()
    result = await service.analyze_archetype(content)
    return {
        "archetype": result.primary_archetype,
        "secondary_archetype": result.secondary_archetype,
        "confidence": result.confidence,
        "reasoning": result.reasoning,
        "description": result.archetype_description,
        "examples": result.example_brands,
    }


async def generate_recommendations(findings: list, context: str) -> list:
    """Legacy function - use OpenAIService.generate_recommendations instead."""
    service = OpenAIService()
    return await service.generate_recommendations(findings, context)
