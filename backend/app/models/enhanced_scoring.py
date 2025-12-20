# =============================================================================
# Enhanced Scoring Models
# =============================================================================
# Extended scoring system with normalization, confidence, benchmarking, and provenance.
# These models extend the existing scoring system without breaking backward compatibility.
# =============================================================================

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
import uuid
from uuid import UUID

from pydantic import BaseModel, Field


class ConfidenceLevel(str, Enum):
    """Confidence level in the score based on data quality and availability."""

    VERY_HIGH = "very_high"  # 90-100% confidence
    HIGH = "high"  # 75-89% confidence
    MEDIUM = "medium"  # 50-74% confidence
    LOW = "low"  # 25-49% confidence
    VERY_LOW = "very_low"  # 0-24% confidence


class NormalizationMethod(str, Enum):
    """Standardized scoring methodologies for consistent normalization."""

    PERCENTILE_RANK = "percentile_rank"  # Based on industry percentiles
    Z_SCORE = "z_score"  # Standard deviation from mean
    BENCHMARK_COMPARISON = "benchmark_comparison"  # Against industry benchmarks
    WEIGHTED_FACTORS = "weighted_factors"  # Traditional weighted scoring
    RAW_METRIC = "raw_metric"  # Direct metric conversion


class DataSource(BaseModel):
    """Information about a data source used in scoring."""

    name: str = Field(
        ..., description="Data source name (e.g., 'Google PageSpeed', 'Moz API')"
    )
    type: str = Field(..., description="Data source type (api, scraped, cached, mock)")
    url: Optional[str] = Field(None, description="Source URL if applicable")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="When data was collected"
    )
    version: Optional[str] = Field(
        None, description="API version or data format version"
    )
    reliability_score: Optional[float] = Field(
        None, ge=0, le=1, description="Data source reliability (0-1)"
    )


class ConfidenceFactors(BaseModel):
    """Factors that contribute to confidence calculation."""

    data_completeness: float = Field(
        ..., ge=0, le=1, description="How complete the data is (0-1)"
    )
    data_freshness: float = Field(
        ..., ge=0, le=1, description="How recent the data is (0-1)"
    )
    source_reliability: float = Field(
        ..., ge=0, le=1, description="Reliability of data sources (0-1)"
    )
    methodology_robustness: float = Field(
        ..., ge=0, le=1, description="How robust the scoring method is (0-1)"
    )
    sample_size: Optional[int] = Field(None, description="Number of data points used")


class BenchmarkComparison(BaseModel):
    """Comparison against industry benchmarks."""

    benchmark_value: float = Field(..., description="Industry benchmark value (0-100)")
    benchmark_source: str = Field(..., description="Source of benchmark data")
    percentile_rank: float = Field(
        ..., ge=0, le=100, description="Percentile rank (0-100)"
    )
    difference_from_benchmark: float = Field(
        ..., description="Difference from benchmark (can be negative)"
    )
    benchmark_category: str = Field(
        ..., description="Benchmark category (e.g., 'B2B SaaS', 'E-commerce')"
    )
    benchmark_year: Optional[int] = Field(
        None, description="Year the benchmark data is from"
    )


class ProvenanceRecord(BaseModel):
    """Complete provenance information for a score."""

    score_id: UUID = Field(
        default_factory=uuid.uuid4,
        description="Unique identifier for this score calculation",
    )
    analyzer_version: str = Field(
        ..., description="Version of the analyzer that produced this score"
    )
    scoring_methodology: str = Field(..., description="Scoring methodology used")
    normalization_method: Optional[NormalizationMethod] = None
    data_sources: List[DataSource] = Field(
        default_factory=list, description="All data sources used"
    )
    calculation_steps: List[str] = Field(
        default_factory=list, description="Step-by-step calculation process"
    )
    assumptions_made: List[str] = Field(
        default_factory=list, description="Assumptions made during scoring"
    )
    limitations: List[str] = Field(
        default_factory=list, description="Known limitations of this score"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


class NormalizedScore(BaseModel):
    """
    Enhanced score with normalization, confidence, benchmarking, and provenance.

    This wraps the traditional score with additional metadata while maintaining
    backward compatibility through the 'value' field.
    """

    # Core score (maintains backward compatibility)
    value: float = Field(
        ..., ge=0, le=100, description="The normalized score value (0-100)"
    )

    # Enhanced metadata (optional for backward compatibility)
    confidence_level: Optional[ConfidenceLevel] = None
    confidence_score: Optional[float] = Field(
        None, ge=0, le=1, description="Numerical confidence score (0-1)"
    )
    confidence_factors: Optional[ConfidenceFactors] = None

    benchmark_comparison: Optional[BenchmarkComparison] = None

    provenance: Optional[ProvenanceRecord] = None

    # Raw score before normalization (for debugging/transparency)
    raw_score: Optional[float] = Field(
        None, description="Raw score before normalization"
    )
    normalization_method: Optional[NormalizationMethod] = None

    # Additional context
    score_range: Optional[Dict[str, float]] = Field(
        None,
        description="Score range context (e.g., {'min': 0, 'max': 100, 'mean': 65})",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "value": 75.5,
                "confidence_level": "high",
                "confidence_score": 0.85,
                "benchmark_comparison": {
                    "benchmark_value": 70,
                    "percentile_rank": 75,
                    "difference_from_benchmark": 5.5,
                },
                "raw_score": 78.2,
                "normalization_method": "benchmark_comparison",
            }
        }


class EnhancedScoreCard(BaseModel):
    """
    Enhanced scorecard with normalized scores and comprehensive metadata.

    Extends the traditional ScoreCard with enhanced scoring information.
    """

    # Traditional fields (maintains backward compatibility)
    overall_score: float = Field(..., ge=0, le=100)
    scores: Dict[str, float] = Field(default_factory=dict)
    grade: str
    summary: str
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    benchmark_comparison: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    top_recommendations: List[Any] = Field(default_factory=list)
    quick_wins: List[Any] = Field(default_factory=list)

    # Enhanced fields (optional)
    normalized_overall_score: Optional[NormalizedScore] = None
    normalized_module_scores: Optional[Dict[str, NormalizedScore]] = Field(
        default_factory=dict
    )

    # Analysis metadata
    analysis_metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Analysis metadata (versions, timestamps, etc.)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "overall_score": 75.5,
                "grade": "B",
                "normalized_overall_score": {
                    "value": 75.5,
                    "confidence_level": "high",
                    "confidence_score": 0.85,
                },
            }
        }


# =============================================================================
# Scoring Framework Base Classes
# =============================================================================


class BaseScorer:
    """
    Base class for standardized scoring with normalization and confidence.

    Analyzers can inherit from this to get enhanced scoring capabilities
    while maintaining backward compatibility.
    """

    def __init__(self, module_key: str):
        self.module_key = module_key
        self.data_sources: List[DataSource] = []
        self.calculation_steps: List[str] = []
        self.assumptions: List[str] = []
        self.limitations: List[str] = []

    def add_data_source(self, name: str, type: str, **kwargs):
        """Add a data source to the provenance record."""
        self.data_sources.append(DataSource(name=name, type=type, **kwargs))

    def add_calculation_step(self, step: str):
        """Add a calculation step for provenance."""
        self.calculation_steps.append(step)

    def add_assumption(self, assumption: str):
        """Add an assumption made during scoring."""
        self.assumptions.append(assumption)

    def add_limitation(self, limitation: str):
        """Add a known limitation."""
        self.limitations.append(limitation)

    def calculate_confidence(self, factors: ConfidenceFactors) -> ConfidenceLevel:
        """Calculate overall confidence level from factors."""
        # Simple weighted average for now
        weights = {
            "data_completeness": 0.3,
            "data_freshness": 0.2,
            "source_reliability": 0.3,
            "methodology_robustness": 0.2,
        }

        confidence_score = sum(
            getattr(factors, factor) * weight for factor, weight in weights.items()
        )

        if confidence_score >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif confidence_score >= 0.75:
            return ConfidenceLevel.HIGH
        elif confidence_score >= 0.5:
            return ConfidenceLevel.MEDIUM
        elif confidence_score >= 0.25:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

    def normalize_score(
        self,
        raw_score: float,
        method: NormalizationMethod,
        benchmark_value: Optional[float] = None,
    ) -> float:
        """Normalize a raw score using the specified method."""
        if method == NormalizationMethod.BENCHMARK_COMPARISON and benchmark_value:
            # Normalize relative to benchmark
            # Scores above benchmark get bonus, below get penalty
            difference = raw_score - benchmark_value
            normalized = raw_score + (difference * 0.5)  # Dampen the effect
            return max(0, min(100, normalized))

        elif method == NormalizationMethod.PERCENTILE_RANK:
            # Assume raw_score is already a percentile (0-100)
            return raw_score

        else:
            # Default: return raw score
            return raw_score

    def create_normalized_score(
        self,
        raw_score: float,
        confidence_factors: ConfidenceFactors,
        benchmark_value: Optional[float] = None,
        normalization_method: Optional[NormalizationMethod] = None,
    ) -> NormalizedScore:
        """Create a complete normalized score with all metadata."""

        # Calculate confidence
        confidence_level = self.calculate_confidence(confidence_factors)
        confidence_score = sum(
            [
                confidence_factors.data_completeness * 0.3,
                confidence_factors.data_freshness * 0.2,
                confidence_factors.source_reliability * 0.3,
                confidence_factors.methodology_robustness * 0.2,
            ]
        )

        # Normalize the score
        if normalization_method and benchmark_value:
            normalized_value = self.normalize_score(
                raw_score, normalization_method, benchmark_value
            )
        else:
            normalized_value = raw_score

        # Create benchmark comparison if benchmark available
        benchmark_comparison = None
        if benchmark_value is not None:
            difference = normalized_value - benchmark_value
            # Estimate percentile (simplified)
            if difference > 10:
                percentile = 80
            elif difference > 0:
                percentile = 60
            elif difference > -10:
                percentile = 40
            else:
                percentile = 20

            benchmark_comparison = BenchmarkComparison(
                benchmark_value=benchmark_value,
                benchmark_source="Industry Average",
                percentile_rank=percentile,
                difference_from_benchmark=difference,
                benchmark_category="General",
                benchmark_year=datetime.utcnow().year,
            )

        # Create provenance record
        provenance = ProvenanceRecord(
            analyzer_version="2.0.0",  # Would be dynamic
            scoring_methodology=f"{self.module_key}_enhanced_scoring",
            normalization_method=normalization_method,
            data_sources=self.data_sources,
            calculation_steps=self.calculation_steps,
            assumptions_made=self.assumptions,
            limitations=self.limitations,
        )

        return NormalizedScore(
            value=normalized_value,
            confidence_level=confidence_level,
            confidence_score=confidence_score,
            confidence_factors=confidence_factors,
            benchmark_comparison=benchmark_comparison,
            provenance=provenance,
            raw_score=raw_score,
            normalization_method=normalization_method,
        )
