"""
Domain entities for SolStein.

Pure Python objects representing the core business concepts,
now powered directly by Pydantic for end-to-end validation.
"""

import sys
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .source_contract import canonical_source_uri, normalize_source_key

if sys.version_info >= (3, 11):  # noqa: UP036
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        def __str__(self) -> str:
            return self.value


class ConfidenceLevel(StrEnum):
    """Confidence levels for data points."""

    CONFIRMED = "Confirmed"
    ESTIMATED = "Estimated"
    UNKNOWN = "Unknown"
    SYNTHETIC = "Synthetic"


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


class ErrorCategory(StrEnum):
    """Error categorization for enrichment failures."""

    API_ERROR = "API_ERROR"
    DATA_ERROR = "DATA_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNKNOWN = "UNKNOWN"


class ErrorSeverity(StrEnum):
    """Error severity levels for prioritization."""

    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"


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
    ebitda_margin: float | None = None
    recurring_revenue_pct: float | None = None
    funding_raised: float | None = None
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
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data_source: str | None = None
    notes: str | None = None
    source_links: list[str] = Field(default_factory=list)
    metric_sources: dict[str, list[str]] = Field(default_factory=dict)
    metric_justifications: dict[str, str] = Field(default_factory=dict)
    metric_observations: dict[str, list[dict[str, Any]]] = Field(default_factory=dict)
    signal_confidences: dict[str, float] = Field(default_factory=dict)
    enrichment_source_count: int = 0
    data_quality_tier: str = "unknown"
    data_source_type: str = "unknown"  # 'synthetic', 'real', 'mixed', 'unknown'
    enrichment_quality_metrics: dict[str, Any] = Field(default_factory=dict)  # EPIC-004: Preserve quality metrics

    # External Identifiers for Connector Lookups

    ticker: str | None = None

    company_number: str | None = None

    isin: str | None = None

    geography_code: str | None = None

    # Enrichment Tracking

    enrichment_sources: list[str] = Field(default_factory=list)

    enrichment_timestamps: dict[str, datetime] = Field(default_factory=dict)

    enrichment_errors: list[str] = Field(default_factory=list)

    # Phase 2.B: Error Tracking Infrastructure
    enrichment_errors_per_field: dict[str, list[str]] = Field(default_factory=dict)  # Track errors by field
    enrichment_error_timestamps: dict[str, datetime] = Field(default_factory=dict)  # When each error occurred
    enrichment_error_count: int = 0  # Total error count for metrics
    enrichment_error_categories: dict[str, int] = Field(
        default_factory=dict
    )  # Count by category (API_ERROR, DATA_ERROR, etc)
    # Scores (Calculated)
    growth_score: float | None = None
    financial_health_score: float | None = None
    competitive_position_score: float | None = None
    composite_score: float | None = None
    scoring_breakdown: dict[str, Any] = Field(default_factory=dict)
    classification: str | None = None

    revenue_timeline: list[dict[str, Any]] = Field(default_factory=list)
    revenue_cagr_3yr: float | None = None
    revenue_cagr_5yr: float | None = None

    # EPIC-010: Standardized field access methods
    def get_field(self, field_name: str, default: Any = None) -> Any:
        """Safely get any field by name.

        Args:
            field_name: Name of the field to get
            default: Default value if field doesn't exist

        Returns:
            Field value or default
        """
        try:
            return getattr(self, field_name, default)
        except AttributeError:
            return default

    def get_financial_field(self, field_name: str, default: Any = None) -> Any:
        """Safely get a field from financials.

        Args:
            field_name: Name of the financial field
            default: Default value if field doesn't exist

        Returns:
            Financial field value or default
        """
        if self.financials is None:
            return default
        return getattr(self.financials, field_name, default)

    def set_field(self, field_name: str, value: Any) -> bool:
        """Safely set a field value.

        Args:
            field_name: Name of the field to set
            value: Value to set

        Returns:
            True if successful, False if field doesn't exist
        """
        try:
            if hasattr(self, field_name):
                setattr(self, field_name, value)
                return True
            return False
        except (AttributeError, ValueError):
            return False

    def has_field(self, field_name: str) -> bool:
        """Check if a field exists and has a non-None value.

        Args:
            field_name: Name of the field to check

        Returns:
            True if field exists and is not None
        """
        try:
            value = getattr(self, field_name, None)
            return value is not None
        except AttributeError:
            return False

    def get_data_completeness(self) -> float:
        """Calculate data completeness percentage.

        Returns:
            Percentage of key fields that have values (0-100)
        """
        key_fields = [
            "name",
            "industry",
            "description",
            "website",
            "headquarters",
            "founded_year",
            "employees",
            "revenue",
            "funding_raised",
        ]

        filled = 0
        for field in key_fields:
            if field in ["employees", "revenue", "funding_raised"]:
                # These are in financials
                if self.financials and getattr(self.financials, field, None) is not None:
                    filled += 1
            else:
                if getattr(self, field, None) is not None:
                    filled += 1

        return (filled / len(key_fields)) * 100 if key_fields else 0.0

    profit_margin: float | None = None
    ebitda_margin: float | None = None
    recurring_revenue_pct: float | None = None
    revenue_per_employee_eur_k: float | None = None
    profitability_raw_metrics: dict[str, Any] = Field(default_factory=dict)

    funding_rounds: list[dict[str, Any]] = Field(default_factory=list)
    total_funding_raised_eur: float | None = None
    latest_valuation_eur: float | None = None
    lead_investors: list[str] = Field(default_factory=list)
    funding_war_chest: str | None = None

    employee_count: int | None = None
    employee_cagr_3yr: float | None = None
    open_positions: int | None = None

    ai_score: float | None = None
    ai_signal_level: str | None = None
    ai_key_capabilities: str | None = None
    ai_in_production: bool | None = None

    data_availability: str | None = None

    @field_validator("ai_score")
    @classmethod
    def validate_ai_score(cls, v: float | None) -> float | None:
        if v is not None and (v < 0 or v > 10):
            raise ValueError("AI score must be between 0 and 10")
        return v

    @field_validator("saas_maturity")
    @classmethod
    def validate_saas_maturity(cls, v: int) -> int:
        if v < 0 or v > 10:
            raise ValueError("SaaS maturity must be between 0 and 10")
        return v

    @field_validator("revenue_cagr_3yr", "revenue_cagr_5yr")
    @classmethod
    def validate_cagr(cls, v: float | None) -> float | None:
        if v is not None and v < -100:
            raise ValueError("CAGR cannot be less than -100%")
        return v

    @field_validator("profit_margin", "ebitda_margin", "recurring_revenue_pct")
    @classmethod
    def validate_percentage(cls, v: float | None) -> float | None:
        if v is not None and (v < -100 or v > 100):
            raise ValueError("Percentage must be between -100 and 100")
        return v

    @field_validator("employee_count", "open_positions")
    @classmethod
    def validate_positive_int(cls, v: int | None) -> int | None:
        if v is not None and v < 0:
            raise ValueError("Employee count cannot be negative")
        return v

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, v: str | None) -> str | None:
        """Validate US stock ticker format: 1-5 uppercase alphanumeric characters."""
        if v is None:
            return v
        v = v.strip()
        if not v:
            return None
        if not (1 <= len(v) <= 5):
            raise ValueError(f"Ticker must be 1-5 characters, got {len(v)}")
        if not v.isupper():
            raise ValueError(f"Ticker must be uppercase, got '{v}'")
        if not v.isalnum():
            raise ValueError(f"Ticker must be alphanumeric, got '{v}'")
        return v

    @field_validator("company_number")
    @classmethod
    def validate_company_number(cls, v: str | None) -> str | None:
        """Validate UK Companies House company number: 8-digit format."""
        if v is None:
            return v
        v = v.strip()
        if not v:
            return None
        if not v.isdigit() or len(v) != 8:
            raise ValueError(f"Company number must be 8 digits, got '{v}'")
        return v

    @field_validator("isin")
    @classmethod
    def validate_isin(cls, v: str | None) -> str | None:
        """Validate ISIN format: 2-letter country code + 9 alphanumeric + 1 check digit."""
        if v is None:
            return v
        v = v.strip().upper()
        if not v:
            return None
        if len(v) != 12:
            raise ValueError(f"ISIN must be 12 characters, got {len(v)}")
        if not v[:2].isalpha():
            raise ValueError(f"ISIN country code must be 2 letters, got '{v[:2]}'")
        if not v[2:11].isalnum():
            raise ValueError(f"ISIN security ID must be alphanumeric, got '{v[2:11]}'")
        if not v[11].isdigit():
            raise ValueError(f"ISIN check digit must be numeric, got '{v[11]}'")
        return v

    @field_validator("geography_code")
    @classmethod
    def validate_geography_code(cls, v: str | None) -> str | None:
        """Validate geography code: must be US, UK, EU, or OTHER."""
        if v is None:
            return v
        v = v.strip().upper()
        if not v:
            return None
        valid_codes = {"US", "UK", "EU", "OTHER"}
        if v not in valid_codes:
            raise ValueError(f"Geography code must be one of {valid_codes}, got '{v}'")
        return v

    @property
    def is_large_cap(self) -> bool:
        """Domain logic: Check if company is large cap (valuation > €100M)."""
        return self.financials.valuation is not None and self.financials.valuation > 100_000_000

    @property
    def is_high_growth(self) -> bool:
        """Domain logic: Check if company is high growth."""
        return self.financials.growth_rate is not None and self.financials.growth_rate > 20

    @property
    def is_profitable(self) -> bool:
        """Domain logic: Check if company is profitable."""
        return self.financials.profit_margin is not None and self.financials.profit_margin > 0


class MarketAnalysis(BaseModel):
    """Market-level analysis domain entity."""

    model_config = ConfigDict(validate_assignment=True)

    market_name: str
    analysis_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
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
        growth_rates = [c.financials.growth_rate for c in self.companies if c.financials.growth_rate is not None]
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
    confidence_weight: float = 1.0


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
    YAHOO_FINANCE = "yahoo_finance"
    EXA_SEARCH = "exa_search"
    GOOGLE_SEARCH = "google_search"
    USPTO = "uspto"
    GOOGLE_PATENTS = "google_patents"
    NEWSAPI = "newsapi"
    COMPETITOR_JSON = "competitor_json"
    STATIC_CATALOG = "static_catalog"


class RawDataSource(BaseModel):
    """A single raw source document (article, filing, etc.)."""

    model_config = ConfigDict(validate_assignment=True)

    source_type: DataSourceType
    source_name: str  # e.g., "TechCrunch", "Companies House", "GitHub"
    raw_content: str | dict[str, Any]  # Original content (article text, JSON, etc.)
    url: str | None = None  # Where we got this from
    source_key: str | None = None
    source_namespace: str | None = None
    source_uri: str | None = None
    producer: str | None = None
    job_run_id: str | None = None
    logic_version: str | None = None
    correlation_id: str | None = None
    retrieval_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    publication_date: datetime | None = None  # When source was published
    confidence: float = Field(default=0.5, ge=0, le=1)  # Initial confidence in source
    relevance_score: float = Field(default=0.5, ge=0, le=1)  # How relevant to company
    metadata: dict[str, Any] = Field(default_factory=dict)  # Extra info (author, category, etc.)
    extraction_method: str | None = None  # How we got this (API, scrape, manual, etc.)
    notes: str | None = None

    @model_validator(mode="after")
    def _normalize_provenance(self) -> "RawDataSource":
        if not self.source_namespace:
            self.source_namespace = "solstein"
        if not self.source_key:
            self.source_key = normalize_source_key(
                source_type=self.source_type.value,
                source_name=self.source_name,
                source_namespace=self.source_namespace,
            )
        self.source_uri = canonical_source_uri(
            source_uri=self.source_uri,
            fallback_url=self.url,
            source_key=self.source_key,
        )
        return self


class RawDataRecord(BaseModel):
    """Collection of raw sources for a single company analysis."""

    model_config = ConfigDict(validate_assignment=True)

    company_id: str
    gathering_batch_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
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
    extracted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_verified: bool = False  # Human verification flag
    verification_notes: str | None = None


class AggregatedDataRecord(BaseModel):
    """Collection of aggregated facts for a company."""

    model_config = ConfigDict(validate_assignment=True)

    company_id: str
    gathering_batch_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
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
            self.average_confidence = sum(f.confidence for f in self.facts) / len(self.facts)


class SignalExtraction(BaseModel):
    """A business signal extracted from facts (bridges facts → scoring)."""

    model_config = ConfigDict(validate_assignment=True)

    signal_name: str  # e.g., "revenue_growth_rate", "ai_maturity", "geographic_reach"
    signal_value: Any  # Processed value (number, enum, etc.)
    signal_confidence: float = Field(default=0.5, ge=0, le=1)

    # Calculation details
    source_facts: list[str] = Field(default_factory=list)  # Which facts went into this
    calculation_method: str  # "average", "max", "enum_classification", etc.
    calculation_formula: str | None = None  # e.g., "(revenue_fy24 - revenue_fy23) / revenue_fy23"

    # Reasoning
    reasoning: str | None = None  # Human-readable explanation
    why_it_matters: str | None = None  # Business context

    # Extracted at
    extracted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SignalExtractionRecord(BaseModel):
    """Collection of signals for a company."""

    model_config = ConfigDict(validate_assignment=True)

    company_id: str
    gathering_batch_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
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
    api_keys_used: dict[str, bool] = Field(default_factory=dict)  # Which APIs were enabled

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
    classification: str | None = None  # "Phoenix", "Salt", "Lead"

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
