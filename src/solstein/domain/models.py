"""
Domain entities for SolStein.

Pure Python objects representing the core business concepts,
now powered directly by Pydantic for end-to-end validation.
"""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ConfidenceLevel(StrEnum):
    """Confidence levels for data points."""

    CONFIRMED = "Confirmed"
    ESTIMATED = "Estimated"
    UNKNOWN = "Unknown"


class AIMaturity(StrEnum):
    """AI adoption maturity levels."""

    NONE = "None"
    LOW = "Low"
    MODERATE = "Moderate"
    STRONG = "Strong"
    VERY_STRONG = "Very Strong"


class ThreatLevel(StrEnum):
    """Competitive threat levels."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class CompanyTier(StrEnum):
    """Company size/market position tiers."""

    TIER_1 = "Tier 1"
    TIER_2 = "Tier 2"
    TIER_3 = "Tier 3"
    TIER_4 = "Tier 4"


class FinancialMetric(BaseModel):
    """Financial metrics domain entity."""

    model_config = ConfigDict(validate_assignment=True)

    revenue: float | None = None
    revenue_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    growth_rate: float | None = None
    growth_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    employees: int | None = None
    employees_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    profit_margin: float | None = None
    margin_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    funding_raised: float | None = None
    funding_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    valuation: float | None = None
    valuation_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN

    @field_validator("employees")
    @classmethod
    def validate_employees(cls, v: int | None) -> int | None:
        if v is not None and v < 0:
            raise ValueError("Employees cannot be negative")
        return v


class Company(BaseModel):
    """Company domain entity."""

    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True)

    id: str
    name: str
    industry: str = "Energy Software"
    description: str | None = None
    website: str | None = None
    headquarters: str | None = None
    founded_year: int | None = None

    # Positioning
    tier: CompanyTier = CompanyTier.TIER_3
    threat_level: ThreatLevel = ThreatLevel.MEDIUM

    # Tech
    ai_maturity: AIMaturity = AIMaturity.NONE
    saas_maturity: int = 1
    tech_stack: list[str] = Field(default_factory=list)

    # Financials
    financials: FinancialMetric = Field(default_factory=FinancialMetric)

    # Market
    geographic_presence: list[str] = Field(default_factory=list)
    key_customers: list[str] = Field(default_factory=list)

    # Structure
    parent_company: str | None = None
    subsidiaries: list[str] = Field(default_factory=list)
    acquisitions: list[dict[str, Any]] = Field(default_factory=list)

    # Metadata
    last_updated: datetime = Field(default_factory=lambda: datetime.now(UTC))
    data_source: str | None = None
    notes: str | None = None

    # Scores (Calculated)
    growth_score: float | None = None
    financial_health_score: float | None = None
    competitive_position_score: float | None = None
    composite_score: float | None = None
    scoring_breakdown: dict[str, Any] = Field(default_factory=dict)
    classification: str | None = None

    @property
    def is_large_cap(self) -> bool:
        """Domain logic: Check if company is large cap (valuation > €100M)."""
        return (
            self.financials.valuation is not None
            and self.financials.valuation > 100_000_000
        )

    @property
    def is_high_growth(self) -> bool:
        """Domain logic: Check if company is high growth."""
        return (
            self.financials.growth_rate is not None and self.financials.growth_rate > 20
        )

    @property
    def is_profitable(self) -> bool:
        """Domain logic: Check if company is profitable."""
        return (
            self.financials.profit_margin is not None
            and self.financials.profit_margin > 0
        )


class MarketAnalysis(BaseModel):
    """Market-level analysis domain entity."""

    model_config = ConfigDict(validate_assignment=True)

    market_name: str
    analysis_date: datetime = Field(default_factory=lambda: datetime.now(UTC))
    companies: list[Company] = Field(default_factory=list)

    # Market metrics
    total_market_size: float | None = None
    growth_rate: float | None = None

    # Competitive landscape
    concentration_ratio: float | None = None
    barriers_to_entry: list[str] = Field(default_factory=list)

    # Trends
    key_trends: list[str] = Field(default_factory=list)
    regulatory_environment: list[str] = Field(default_factory=list)

    # Analysis
    swot_analysis: dict[str, list[str]] | None = None
    recommendations: list[str] = Field(default_factory=list)

    @property
    def company_count(self) -> int:
        return len(self.companies)

    @property
    def average_growth_rate(self) -> float | None:
        growth_rates = [
            c.financials.growth_rate
            for c in self.companies
            if c.financials.growth_rate is not None
        ]
        if not growth_rates:
            return None
        return sum(growth_rates) / len(growth_rates)

    @property
    def market_leaders(self) -> list[Company]:
        return [c for c in self.companies if c.tier == CompanyTier.TIER_1]


class ScoreComponent(BaseModel):
    """A single component of a score calculation."""

    model_config = ConfigDict(validate_assignment=True)

    name: str
    value: float
    formula: str
    reasoning: str


class ScoringExplanation(BaseModel):
    """Detailed explanation of how a final score was calculated."""

    model_config = ConfigDict(validate_assignment=True)

    base_score: float
    components: list[ScoreComponent] = Field(default_factory=list)
    final_score: float = 0.0


class CompetitiveOverlap(BaseModel):
    """Competitive overlap domain entity."""

    model_config = ConfigDict(validate_assignment=True)

    company_a_id: str
    company_b_id: str
    overlap_score: float
    overlap_areas: list[str] = Field(default_factory=list)
    competitive_intensity: str = "Medium"
    notes: str | None = None


# ============================================================================
# AI DATA GATHERING MODELS (Multi-layer transparency architecture)
# ============================================================================


class DataSourceType(StrEnum):
    """Types of data sources for gathering."""

    GITHUB = "github"
    COMPANY_FILINGS = "company_filings"
    NEWS = "news"
    CRUNCHBASE = "crunchbase"
    LINKEDIN = "linkedin"
    PATENTS = "patents"
    WEBSITE = "website"
    PRESS_RELEASE = "press_release"


class RawDataSource(BaseModel):
    """A single raw source document (article, filing, etc.)."""

    model_config = ConfigDict(validate_assignment=True)

    source_type: DataSourceType
    source_name: str  # e.g., "TechCrunch", "Companies House", "GitHub"
    raw_content: str | dict[str, Any]  # Original content (article text, JSON, etc.)
    url: str | None = None  # Where we got this from
    retrieval_timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    publication_date: datetime | None = None  # When source was published
    confidence: float = Field(default=0.5, ge=0, le=1)  # Initial confidence in source
    relevance_score: float = Field(default=0.5, ge=0, le=1)  # How relevant to company
    metadata: dict[str, Any] = Field(
        default_factory=dict
    )  # Extra info (author, category, etc.)
    extraction_method: str | None = None  # How we got this (API, scrape, manual, etc.)
    notes: str | None = None


class RawDataRecord(BaseModel):
    """Collection of raw sources for a single company analysis."""

    model_config = ConfigDict(validate_assignment=True)

    company_id: str
    gathering_batch_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    sources: list[RawDataSource] = Field(default_factory=list)
    total_sources_found: int = 0
    notes: str | None = None

    @property
    def source_count_by_type(self) -> dict[str, int]:
        """Count sources by type."""
        counts: dict[str, int] = {}
        for source in self.sources:
            counts[source.source_type] = counts.get(source.source_type, 0) + 1
        return counts


class AggregatedFact(BaseModel):
    """A single deduplicated fact extracted from multiple sources."""

    model_config = ConfigDict(validate_assignment=True)

    fact_type: str  # e.g., "revenue", "employee_count", "ai_maturity"
    value: Any  # The extracted value (can be number, string, enum, etc.)
    confidence: float = Field(default=0.5, ge=0, le=1)  # 0-1 confidence in this fact
    year: int | None = None  # For time-series facts

    # Source attribution
    sources_used: list[str] = Field(default_factory=list)  # Source names/URLs
    source_agreement_percentage: float = Field(default=0.5, ge=0, le=1)
    source_credibility_scores: dict[str, float] = Field(default_factory=dict)

    # Contradiction tracking
    contradictions_detected: list[dict[str, Any]] = Field(default_factory=list)
    contradiction_notes: str | None = None

    # Metadata
    extracted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_updated: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_verified: bool = False  # Human verification flag
    verification_notes: str | None = None


class AggregatedDataRecord(BaseModel):
    """Collection of aggregated facts for a company."""

    model_config = ConfigDict(validate_assignment=True)

    company_id: str
    gathering_batch_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    facts: list[AggregatedFact] = Field(default_factory=list)

    # Quality metrics
    total_facts: int = 0
    verified_facts: int = 0
    average_confidence: float = 0.0
    data_completeness_percentage: float = 0.0  # % of desired facts gathered

    def update_quality_metrics(self) -> None:
        """Recalculate quality metrics."""
        self.total_facts = len(self.facts)
        self.verified_facts = sum(1 for f in self.facts if f.is_verified)
        if self.facts:
            self.average_confidence = sum(f.confidence for f in self.facts) / len(
                self.facts
            )


class SignalExtraction(BaseModel):
    """A business signal extracted from facts (bridges facts → scoring)."""

    model_config = ConfigDict(validate_assignment=True)

    signal_name: str  # e.g., "revenue_growth_rate", "ai_maturity", "geographic_reach"
    signal_value: Any  # Processed value (number, enum, etc.)
    signal_confidence: float = Field(default=0.5, ge=0, le=1)

    # Calculation details
    source_facts: list[str] = Field(default_factory=list)  # Which facts went into this
    calculation_method: str  # "average", "max", "enum_classification", etc.
    calculation_formula: str | None = (
        None  # e.g., "(revenue_fy24 - revenue_fy23) / revenue_fy23"
    )

    # Reasoning
    reasoning: str | None = None  # Human-readable explanation
    why_it_matters: str | None = None  # Business context

    # Extracted at
    extracted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SignalExtractionRecord(BaseModel):
    """Collection of signals for a company."""

    model_config = ConfigDict(validate_assignment=True)

    company_id: str
    gathering_batch_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    signals: list[SignalExtraction] = Field(default_factory=list)


class GatheringBatch(BaseModel):
    """Metadata about a data gathering analysis."""

    model_config = ConfigDict(validate_assignment=True)

    batch_id: str  # e.g., "batch_20250220_001"
    market_name: str
    requested_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None

    # Scope
    companies_requested: list[str] = Field(default_factory=list)
    data_sources_enabled: list[DataSourceType] = Field(default_factory=list)
    refresh_mode: str = "full"  # "full" or "incremental"

    # Status
    status: str = "pending"  # pending, in_progress, completed, failed
    companies_completed: int = 0
    companies_failed: int = 0

    # Configuration
    confidence_threshold: float = 0.5  # Min confidence to include facts
    api_keys_used: dict[str, bool] = Field(
        default_factory=dict
    )  # Which APIs were enabled

    # Results summary
    total_sources_gathered: int = 0
    average_facts_per_company: float = 0.0
    average_confidence: float = 0.0
    errors: list[str] = Field(default_factory=list)


class CompanyAnalysisAuditTrail(BaseModel):
    """Complete audit trail for one company analysis."""

    model_config = ConfigDict(validate_assignment=True)

    company_id: str
    gathering_batch_id: str
    company_name: str

    # Analysis artifacts
    raw_data: RawDataRecord | None = None
    aggregated_facts: AggregatedDataRecord | None = None
    extracted_signals: SignalExtractionRecord | None = None

    # Final scores (from existing engine)
    growth_score: float | None = None
    financial_health_score: float | None = None
    competitive_position_score: float | None = None
    classification: str | None = None  # "Rocket", "Neutral", "Dinosaur"

    # Breakdown showing signal sources
    scoring_breakdown: dict[str, Any] = Field(default_factory=dict)

    # Timestamps
    analysis_started_at: datetime | None = None
    analysis_completed_at: datetime | None = None
    analysis_duration_seconds: float | None = None

    # Data quality
    data_completeness: float = 0.0  # % of desired fields gathered
    confidence_level: str = "unknown"  # "low", "medium", "high", "very_high"
    quality_notes: str | None = None

    # Errors/warnings
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
