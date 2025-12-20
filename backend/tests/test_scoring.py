# =============================================================================
# Scoring Utilities Test Suite
# =============================================================================
# Regression tests for scoring functions to ensure consistent behavior
# when scoring algorithms are modified or enhanced.
#
# Run with: pytest tests/test_scoring.py -v
# =============================================================================

import pytest
from typing import Dict

from app.utils.scoring import weighted_average, score_to_grade, normalize_score
from app.analyzers.base import BaseAnalyzer


# =============================================================================
# Test weighted_average()
# =============================================================================

class TestWeightedAverage:
    """Tests for the weighted_average scoring function."""

    def test_basic_weighted_average(self):
        """Test basic weighted average calculation."""
        scores = {"seo": 80.0, "social": 60.0, "brand": 70.0}
        weights = {"seo": 0.4, "social": 0.3, "brand": 0.3}
        
        result = weighted_average(scores, weights)
        
        # Expected: (80*0.4 + 60*0.3 + 70*0.3) = 32 + 18 + 21 = 71
        assert result == 71.0

    def test_equal_weights(self):
        """Test with equal weights (should be regular average)."""
        scores = {"a": 100.0, "b": 50.0, "c": 50.0}
        weights = {"a": 1.0, "b": 1.0, "c": 1.0}
        
        result = weighted_average(scores, weights)
        
        # Expected: (100 + 50 + 50) / 3 = 66.67
        assert abs(result - 66.67) < 0.01

    def test_missing_weight_ignored(self):
        """Test that scores without corresponding weights are ignored."""
        scores = {"seo": 80.0, "social": 60.0, "orphan": 100.0}
        weights = {"seo": 0.5, "social": 0.5}  # orphan has no weight
        
        result = weighted_average(scores, weights)
        
        # Expected: (80*0.5 + 60*0.5) / (0.5 + 0.5) = 70
        assert result == 70.0

    def test_extra_weights_ignored(self):
        """Test that extra weights without scores don't affect result."""
        scores = {"seo": 80.0}
        weights = {"seo": 0.5, "social": 0.5}  # social has no score
        
        result = weighted_average(scores, weights)
        
        # Only seo is counted: 80*0.5 / 0.5 = 80
        assert result == 80.0

    def test_empty_scores(self):
        """Test with empty scores returns 0."""
        scores: Dict[str, float] = {}
        weights = {"seo": 0.5, "social": 0.5}
        
        result = weighted_average(scores, weights)
        
        assert result == 0

    def test_empty_weights(self):
        """Test with empty weights returns 0."""
        scores = {"seo": 80.0, "social": 60.0}
        weights: Dict[str, float] = {}
        
        result = weighted_average(scores, weights)
        
        assert result == 0

    def test_zero_weights(self):
        """Test with all zero weights returns 0."""
        scores = {"seo": 80.0, "social": 60.0}
        weights = {"seo": 0.0, "social": 0.0}
        
        result = weighted_average(scores, weights)
        
        assert result == 0

    def test_single_category(self):
        """Test with single category returns that score."""
        scores = {"seo": 85.0}
        weights = {"seo": 1.0}
        
        result = weighted_average(scores, weights)
        
        assert result == 85.0

    def test_zero_score(self):
        """Test that zero scores are properly weighted."""
        scores = {"seo": 0.0, "social": 100.0}
        weights = {"seo": 0.5, "social": 0.5}
        
        result = weighted_average(scores, weights)
        
        # Expected: (0*0.5 + 100*0.5) = 50
        assert result == 50.0

    def test_fractional_scores(self):
        """Test with fractional score values."""
        scores = {"seo": 75.5, "social": 82.3}
        weights = {"seo": 0.6, "social": 0.4}
        
        result = weighted_average(scores, weights)
        
        # Expected: (75.5*0.6 + 82.3*0.4) / 1.0 = 45.3 + 32.92 = 78.22
        assert abs(result - 78.22) < 0.01


# =============================================================================
# Test score_to_grade()
# =============================================================================

class TestScoreToGrade:
    """Tests for the score_to_grade conversion function."""

    def test_grade_a(self):
        """Test A grade for scores 90-100."""
        assert score_to_grade(100) == "A"
        assert score_to_grade(95) == "A"
        assert score_to_grade(90) == "A"

    def test_grade_b(self):
        """Test B grade for scores 80-89."""
        assert score_to_grade(89) == "B"
        assert score_to_grade(85) == "B"
        assert score_to_grade(80) == "B"

    def test_grade_c(self):
        """Test C grade for scores 70-79."""
        assert score_to_grade(79) == "C"
        assert score_to_grade(75) == "C"
        assert score_to_grade(70) == "C"

    def test_grade_d(self):
        """Test D grade for scores 60-69."""
        assert score_to_grade(69) == "D"
        assert score_to_grade(65) == "D"
        assert score_to_grade(60) == "D"

    def test_grade_f(self):
        """Test F grade for scores below 60."""
        assert score_to_grade(59) == "F"
        assert score_to_grade(50) == "F"
        assert score_to_grade(30) == "F"
        assert score_to_grade(0) == "F"

    def test_boundary_values(self):
        """Test exact boundary values."""
        assert score_to_grade(89.999) == "B"  # Just under 90
        assert score_to_grade(90.001) == "A"  # Just over 90
        assert score_to_grade(79.999) == "C"  # Just under 80
        assert score_to_grade(59.999) == "F"  # Just under 60


# =============================================================================
# Test normalize_score()
# =============================================================================

class TestNormalizeScore:
    """Tests for the normalize_score function."""

    def test_basic_normalization(self):
        """Test basic normalization to 0-100 scale."""
        # Value 50 in range 0-100 should remain 50
        result = normalize_score(50, 0, 100)
        assert result == 50.0

    def test_scale_up(self):
        """Test scaling up from smaller range."""
        # Value 5 in range 0-10 should become 50
        result = normalize_score(5, 0, 10)
        assert result == 50.0

    def test_scale_down(self):
        """Test scaling down from larger range."""
        # Value 500 in range 0-1000 should become 50
        result = normalize_score(500, 0, 1000)
        assert result == 50.0

    def test_non_zero_min(self):
        """Test normalization with non-zero minimum."""
        # Value 75 in range 50-100 should become 50 (midpoint)
        result = normalize_score(75, 50, 100)
        assert result == 50.0

    def test_at_minimum(self):
        """Test value at minimum returns 0."""
        result = normalize_score(10, 10, 100)
        assert result == 0.0

    def test_at_maximum(self):
        """Test value at maximum returns 100."""
        result = normalize_score(100, 0, 100)
        assert result == 100.0

    def test_below_minimum_clamped(self):
        """Test value below minimum is clamped to 0."""
        result = normalize_score(-10, 0, 100)
        assert result == 0.0

    def test_above_maximum_clamped(self):
        """Test value above maximum is clamped to 100."""
        result = normalize_score(150, 0, 100)
        assert result == 100.0

    def test_equal_min_max_returns_50(self):
        """Test that equal min/max returns 50 (fallback)."""
        result = normalize_score(50, 50, 50)
        assert result == 50.0

    def test_inverted_range_returns_50(self):
        """Test that inverted range (max < min) returns 50."""
        result = normalize_score(50, 100, 0)
        assert result == 50.0


# =============================================================================
# Test BaseAnalyzer.clamp_score()
# =============================================================================

class TestClampScore:
    """Tests for BaseAnalyzer.clamp_score static method."""

    def test_within_range(self):
        """Test values within 0-100 are unchanged."""
        assert BaseAnalyzer.clamp_score(50) == 50.0
        assert BaseAnalyzer.clamp_score(0) == 0.0
        assert BaseAnalyzer.clamp_score(100) == 100.0
        assert BaseAnalyzer.clamp_score(75.5) == 75.5

    def test_below_minimum(self):
        """Test values below 0 are clamped to 0."""
        assert BaseAnalyzer.clamp_score(-10) == 0.0
        assert BaseAnalyzer.clamp_score(-0.1) == 0.0
        assert BaseAnalyzer.clamp_score(-1000) == 0.0

    def test_above_maximum(self):
        """Test values above 100 are clamped to 100."""
        assert BaseAnalyzer.clamp_score(110) == 100.0
        assert BaseAnalyzer.clamp_score(100.1) == 100.0
        assert BaseAnalyzer.clamp_score(1000) == 100.0


# =============================================================================
# Test BaseAnalyzer.score_to_rating()
# =============================================================================

class TestScoreToRating:
    """Tests for BaseAnalyzer.score_to_rating static method."""

    def test_excellent_rating(self):
        """Test excellent rating for scores 90+."""
        assert BaseAnalyzer.score_to_rating(100) == "excellent"
        assert BaseAnalyzer.score_to_rating(95) == "excellent"
        assert BaseAnalyzer.score_to_rating(90) == "excellent"

    def test_good_rating(self):
        """Test good rating for scores 75-89."""
        assert BaseAnalyzer.score_to_rating(89) == "good"
        assert BaseAnalyzer.score_to_rating(80) == "good"
        assert BaseAnalyzer.score_to_rating(75) == "good"

    def test_fair_rating(self):
        """Test fair rating for scores 60-74."""
        assert BaseAnalyzer.score_to_rating(74) == "fair"
        assert BaseAnalyzer.score_to_rating(67) == "fair"
        assert BaseAnalyzer.score_to_rating(60) == "fair"

    def test_poor_rating(self):
        """Test poor rating for scores 40-59."""
        assert BaseAnalyzer.score_to_rating(59) == "poor"
        assert BaseAnalyzer.score_to_rating(50) == "poor"
        assert BaseAnalyzer.score_to_rating(40) == "poor"

    def test_critical_rating(self):
        """Test critical rating for scores below 40."""
        assert BaseAnalyzer.score_to_rating(39) == "critical"
        assert BaseAnalyzer.score_to_rating(20) == "critical"
        assert BaseAnalyzer.score_to_rating(0) == "critical"


# =============================================================================
# Regression Tests - Known Score Scenarios
# =============================================================================

class TestScoringRegression:
    """
    Regression tests for specific scoring scenarios.
    
    These tests lock in expected behavior for real-world scoring scenarios
    to prevent unintended changes during refactoring.
    """

    def test_typical_brand_analysis_scores(self):
        """Test weighted average for typical brand analysis scenario."""
        # Typical brand analysis weights (from README)
        weights = {
            "social_media": 0.20,
            "seo": 0.15,
            "brand_messaging": 0.15,
            "website_ux": 0.15,
            "ai_discoverability": 0.10,
            "content": 0.10,
            "team_presence": 0.10,
            "channel_fit": 0.05,
        }
        
        # Sample scores (similar to linear.app test result)
        scores = {
            "social_media": 68.7,
            "seo": 81.0,
            "brand_messaging": 73.5,
            "website_ux": 77.0,
            "ai_discoverability": 10.0,
            "content": 100.0,
            "team_presence": 55.0,
            "channel_fit": 50.0,
        }
        
        result = weighted_average(scores, weights)
        
        # Lock in the expected result
        # 68.7*0.20 + 81*0.15 + 73.5*0.15 + 77*0.15 + 10*0.10 + 100*0.10 + 55*0.10 + 50*0.05
        # = 13.74 + 12.15 + 11.025 + 11.55 + 1.0 + 10.0 + 5.5 + 2.5 = 67.465
        assert abs(result - 67.465) < 0.01

    def test_perfect_scores(self):
        """Test weighted average with all perfect scores."""
        weights = {
            "social_media": 0.20,
            "seo": 0.15,
            "brand_messaging": 0.15,
            "website_ux": 0.15,
            "ai_discoverability": 0.10,
            "content": 0.10,
            "team_presence": 0.10,
            "channel_fit": 0.05,
        }
        
        scores = {key: 100.0 for key in weights.keys()}
        
        result = weighted_average(scores, weights)
        
        assert result == 100.0

    def test_worst_case_scores(self):
        """Test weighted average with all zero scores."""
        weights = {
            "social_media": 0.20,
            "seo": 0.15,
            "brand_messaging": 0.15,
            "website_ux": 0.15,
            "ai_discoverability": 0.10,
            "content": 0.10,
            "team_presence": 0.10,
            "channel_fit": 0.05,
        }
        
        scores = {key: 0.0 for key in weights.keys()}
        
        result = weighted_average(scores, weights)
        
        assert result == 0.0

    def test_grade_boundaries_comprehensive(self):
        """Comprehensive test of all grade boundaries."""
        # Test exact boundaries and one point above/below
        test_cases = [
            (100, "A"),
            (90, "A"),
            (89.99, "B"),
            (80, "B"),
            (79.99, "C"),
            (70, "C"),
            (69.99, "D"),
            (60, "D"),
            (59.99, "F"),
            (0, "F"),
        ]
        
        for score, expected_grade in test_cases:
            result = score_to_grade(score)
            assert result == expected_grade, f"Score {score} expected {expected_grade}, got {result}"


# =============================================================================
# Edge Case Tests
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and unusual inputs."""

    def test_weighted_average_with_large_numbers(self):
        """Test weighted average with large score values."""
        scores = {"a": 1000000.0, "b": 2000000.0}
        weights = {"a": 0.5, "b": 0.5}
        
        result = weighted_average(scores, weights)
        
        assert result == 1500000.0

    def test_weighted_average_with_tiny_weights(self):
        """Test weighted average with very small weights."""
        scores = {"a": 100.0, "b": 0.0}
        weights = {"a": 0.0001, "b": 0.9999}
        
        result = weighted_average(scores, weights)
        
        # Should be approximately 0.01 (100 * 0.0001 / 1.0)
        assert abs(result - 0.01) < 0.001

    def test_normalize_score_negative_range(self):
        """Test normalization with negative range values."""
        # Temperature-like scale: -20 to 40, value at 10
        # 10 is at position (10 - (-20)) / (40 - (-20)) = 30/60 = 0.5 = 50%
        result = normalize_score(10, -20, 40)
        assert result == 50.0

    def test_clamp_preserves_precision(self):
        """Test that clamp preserves decimal precision."""
        result = BaseAnalyzer.clamp_score(75.123456789)
        assert result == 75.123456789
