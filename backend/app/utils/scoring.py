# =============================================================================
# Scoring Utilities
# =============================================================================
# Common scoring algorithms and helpers used across analyzers.
# =============================================================================

from typing import Dict


def weighted_average(scores: Dict[str, float], weights: Dict[str, float]) -> float:
    """
    Calculate weighted average of scores.

    Args:
        scores: Dictionary of {category: score}
        weights: Dictionary of {category: weight}

    Returns:
        float: Weighted average score
    """
    total_weight = 0
    weighted_sum = 0

    for category, score in scores.items():
        weight = weights.get(category, 0)
        weighted_sum += score * weight
        total_weight += weight

    return weighted_sum / total_weight if total_weight > 0 else 0


def score_to_grade(score: float) -> str:
    """Convert numeric score to letter grade."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    return "F"


def normalize_score(value: float, min_val: float, max_val: float) -> float:
    """Normalize a value to 0-100 scale."""
    if max_val <= min_val:
        return 50
    normalized = ((value - min_val) / (max_val - min_val)) * 100
    return max(0, min(100, normalized))
