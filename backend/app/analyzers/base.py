# =============================================================================
# Base Analyzer Class
# =============================================================================
# This module defines the abstract base class that all analyzers inherit from.
# It provides a consistent interface and common utilities for analysis.
# =============================================================================

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable, Awaitable
from dataclasses import dataclass, field

from app.models.report import Finding, Recommendation, SeverityLevel


@dataclass
class AnalyzerResult:
    """
    Standard result container for all analyzers.

    Each analyzer returns this structured result containing:
    - score: Numeric score (0-100) for this aspect
    - findings: Observations and issues discovered
    - recommendations: Actionable improvement suggestions
    - data: Raw/processed data for the report section

    Attributes:
        score: Analysis score from 0-100
        findings: List of findings/observations
        recommendations: List of actionable recommendations
        data: Module-specific data for the report
        error: Error message if analysis failed
    """

    score: float = 0.0
    findings: List[Finding] = field(default_factory=list)
    recommendations: List[Recommendation] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def is_success(self) -> bool:
        """Check if the analysis completed successfully."""
        return self.error is None


class BaseAnalyzer(ABC):
    """
    Abstract base class for all brand analysis modules.

    Each analyzer follows a consistent pattern:
    1. Initialize with URL and optional context
    2. Run the analyze() method to collect and process data
    3. Return an AnalyzerResult with score, findings, and recommendations

    Subclasses must implement:
    - analyze(): Main analysis logic
    - _calculate_score(): Score calculation algorithm
    - _generate_findings(): Finding generation logic
    - _generate_recommendations(): Recommendation generation

    Attributes:
        url: The website URL being analyzed
        domain: Extracted domain from the URL
        description: Optional business description
        industry: Optional industry category
        scraped_data: Shared scraped website data
    """

    # -------------------------------------------------------------------------
    # Class-level configuration
    # -------------------------------------------------------------------------
    # Name of this analyzer module (for logging and progress tracking)
    MODULE_NAME: str = "base"

    # Weight of this module in overall score (should sum to 1.0 across modules)
    WEIGHT: float = 0.10

    # Maximum time allowed for this analyzer (in seconds)
    TIMEOUT: int = 60

    def __init__(
        self,
        url: str,
        description: Optional[str] = None,
        industry: Optional[str] = None,
        scraped_data: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the analyzer with target URL and context.

        Args:
            url: Website URL to analyze
            description: Optional business description from user
            industry: Optional industry category for context
            scraped_data: Pre-scraped website data (shared across analyzers)
        """
        self.url = url.rstrip("/")
        self.domain = self._extract_domain(url)
        self.description = description
        self.industry = industry
        self.scraped_data = scraped_data or {}

        # Results storage
        self._raw_data: Dict[str, Any] = {}
        self._findings: List[Finding] = []
        self._recommendations: List[Recommendation] = []

    @abstractmethod
    async def analyze(self) -> AnalyzerResult:
        """
        Run the analysis and return results.

        This is the main entry point for each analyzer. It should:
        1. Fetch/process required data
        2. Calculate the score
        3. Generate findings based on data
        4. Generate recommendations based on findings
        5. Return a complete AnalyzerResult

        Returns:
            AnalyzerResult: Complete analysis results

        Raises:
            Exception: If analysis fails (will be caught and logged)
        """
        pass

    @abstractmethod
    def _calculate_score(self) -> float:
        """
        Calculate the module score (0-100) based on collected data.

        Each analyzer implements its own scoring algorithm based on:
        - Industry benchmarks
        - Best practices
        - Weighted factors

        Returns:
            float: Score from 0 to 100
        """
        pass

    @abstractmethod
    def _generate_findings(self) -> List[Finding]:
        """
        Generate findings/observations from the analysis.

        Findings should be:
        - Specific and data-driven
        - Assigned appropriate severity
        - Actionable (when possible)

        Returns:
            List[Finding]: List of findings
        """
        pass

    @abstractmethod
    def _generate_recommendations(self) -> List[Recommendation]:
        """
        Generate actionable recommendations.

        Recommendations should:
        - Be prioritized by impact
        - Include expected effort
        - Reference relevant findings
        - Be specific and implementable

        Returns:
            List[Recommendation]: List of recommendations
        """
        pass

    # -------------------------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------------------------

    def _extract_domain(self, url: str) -> str:
        """
        Extract the domain from a URL.

        Args:
            url: Full URL (e.g., https://www.example.com/page)

        Returns:
            str: Domain (e.g., example.com)
        """
        from urllib.parse import urlparse

        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path

        # Remove www. prefix if present
        if domain.startswith("www."):
            domain = domain[4:]

        return domain

    def add_finding(
        self,
        title: str,
        detail: str,
        severity: SeverityLevel = SeverityLevel.INFO,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add a finding to the results.

        Args:
            title: Short description of the finding
            detail: Detailed explanation
            severity: How significant this finding is
            data: Optional associated data/metrics
        """
        self._findings.append(
            Finding(
                title=title,
                detail=detail,
                severity=severity,
                data=data,
            )
        )

    def add_recommendation(
        self,
        title: str,
        description: str,
        priority: SeverityLevel = SeverityLevel.MEDIUM,
        impact: str = "medium",
        effort: str = "medium",
    ) -> None:
        """
        Add a recommendation to the results.

        Args:
            title: Short recommendation title
            description: Detailed explanation of what to do and why
            priority: How urgent this recommendation is
            impact: Expected impact (high/medium/low)
            effort: Estimated effort (high/medium/low)
        """
        self._recommendations.append(
            Recommendation(
                title=title,
                description=description,
                priority=priority,
                category=self.MODULE_NAME,
                impact=impact,
                effort=effort,
            )
        )

    def get_scraped_content(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the shared scraped data.

        Args:
            key: Key to look up
            default: Default value if key not found

        Returns:
            The value or default
        """
        return self.scraped_data.get(key, default)

    @staticmethod
    def clamp_score(score: float) -> float:
        """
        Clamp a score to the valid range [0, 100].

        Args:
            score: Raw score value

        Returns:
            float: Score clamped to 0-100
        """
        return max(0.0, min(100.0, score))

    @staticmethod
    def score_to_rating(score: float) -> str:
        """
        Convert a numeric score to a qualitative rating.

        Args:
            score: Score from 0-100

        Returns:
            str: Rating (excellent/good/fair/poor/critical)
        """
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 60:
            return "fair"
        elif score >= 40:
            return "poor"
        else:
            return "critical"


# =============================================================================
# Analysis Context
# =============================================================================
@dataclass
class AnalysisContext:
    """
    Shared context passed to all analyzers.

    This contains:
    - The target URL and metadata
    - Pre-scraped website data
    - Callback for progress updates
    - Results from other analyzers (for cross-module insights)

    Attributes:
        url: Website URL being analyzed
        domain: Extracted domain
        description: User-provided business description
        industry: User-provided industry category
        scraped_data: Shared scraped website content
        progress_callback: Function to call for progress updates
        results: Results from completed analyzers
    """

    url: str
    domain: str
    description: Optional[str] = None
    industry: Optional[str] = None
    scraped_data: Dict[str, Any] = field(default_factory=dict)
    progress_callback: Optional[Callable[[str, str], Awaitable[None]]] = None
    results: Dict[str, AnalyzerResult] = field(default_factory=dict)

    async def update_progress(self, module: str, status: str) -> None:
        """
        Update progress for a module.

        Args:
            module: Module name
            status: Status (pending/running/completed/failed)
        """
        if self.progress_callback:
            await self.progress_callback(module, status)
