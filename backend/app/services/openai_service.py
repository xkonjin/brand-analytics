# =============================================================================
# OpenAI Service
# =============================================================================
# Service for interacting with OpenAI's GPT-4 API.
# =============================================================================

from typing import Dict, Any, Optional
import httpx
import json

from app.config import settings


async def analyze_brand_archetype(content: str) -> Dict[str, Any]:
    """
    Use GPT-4 to analyze brand archetype from website content.
    
    Args:
        content: Website text content
    
    Returns:
        dict: Analysis results with archetype, tone, themes
    """
    if not settings.OPENAI_API_KEY:
        return {"error": "OpenAI API key not configured"}
    
    prompt = f"""Analyze this brand's website content and identify:
1. Primary brand archetype (Hero, Outlaw, Magician, Everyman, Lover, Jester, Caregiver, Ruler, Creator, Innocent, Sage, Explorer)
2. Key brand voice characteristics
3. Main messaging themes

Respond in JSON format with: archetype, confidence, tone_keywords, themes

Content: {content[:3000]}"""
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.OPENAI_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "response_format": {"type": "json_object"},
                },
            )
            
            if response.status_code == 200:
                result = response.json()
                return json.loads(result["choices"][0]["message"]["content"])
            return {"error": f"API returned {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


async def generate_recommendations(findings: list, context: str) -> list:
    """
    Use GPT-4 to generate personalized recommendations.
    
    Args:
        findings: List of analysis findings
        context: Brand/industry context
    
    Returns:
        list: Personalized recommendations
    """
    if not settings.OPENAI_API_KEY:
        return []
    
    prompt = f"""Based on these brand analysis findings, generate 5 specific, actionable recommendations:

Findings: {findings[:5]}
Context: {context}

Respond in JSON with: recommendations (array of {{title, description, priority, impact}})"""
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.OPENAI_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.5,
                    "response_format": {"type": "json_object"},
                },
            )
            
            if response.status_code == 200:
                result = response.json()
                data = json.loads(result["choices"][0]["message"]["content"])
                return data.get("recommendations", [])
    except Exception:
        pass
    return []

