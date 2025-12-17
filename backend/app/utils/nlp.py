# =============================================================================
# NLP Utilities
# =============================================================================
# Natural language processing utilities for text analysis.
# =============================================================================

from typing import List, Dict, Any
import re


def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """
    Extract top keywords from text using simple frequency analysis.
    
    Args:
        text: Input text
        top_n: Number of keywords to return
    
    Returns:
        List of top keywords
    """
    # Common stop words to filter out
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "can", "this", "that", "these",
        "those", "it", "its", "we", "our", "you", "your", "they", "their"
    }
    
    # Tokenize and count
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    word_counts: Dict[str, int] = {}
    
    for word in words:
        if word not in stop_words:
            word_counts[word] = word_counts.get(word, 0) + 1
    
    # Sort by frequency
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    
    return [word for word, count in sorted_words[:top_n]]


def simple_sentiment(text: str) -> str:
    """
    Simple rule-based sentiment analysis.
    
    Args:
        text: Input text
    
    Returns:
        str: 'positive', 'negative', or 'neutral'
    """
    positive_words = [
        "great", "excellent", "amazing", "wonderful", "fantastic", "love",
        "best", "awesome", "good", "happy", "success", "perfect", "excited"
    ]
    negative_words = [
        "bad", "terrible", "awful", "horrible", "hate", "worst", "poor",
        "disappointing", "fail", "problem", "issue", "error", "broken"
    ]
    
    text_lower = text.lower()
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    return "neutral"

