"""
Domain entities for SolStein.

These are pure Python objects representing the core business concepts.
They are NOT coupled to any framework (Pydantic, FastAPI, SQLAlchemy).
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


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


@dataclass
class FinancialMetric:
    """Financial metrics domain entity."""

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


@dataclass
class Company:
    """Company domain entity."""

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
    tech_stack: list[str] = field(default_factory=list)

    # Financials
    financials: FinancialMetric = field(default_factory=FinancialMetric)

    # Market
    geographic_presence: list[str] = field(default_factory=list)
    key_customers: list[str] = field(default_factory=list)

    # Structure
    parent_company: str | None = None
    subsidiaries: list[str] = field(default_factory=list)
    acquisitions: list[dict[str, Any]] = field(default_factory=list)

    # Metadata
    last_updated: datetime = field(default_factory=datetime.now)
    data_source: str | None = None
    notes: str | None = None

    # Scores (Calculated)
    growth_score: float | None = None
    financial_health_score: float | None = None
    competitive_position_score: float | None = None
    scoring_breakdown: dict[str, ScoringExplanation] = field(default_factory=dict)

    @property
    def is_public(self) -> bool:
        """Domain logic: Check if company is publicly traded."""
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


@dataclass
class MarketAnalysis:
    """Market-level analysis domain entity."""

    market_name: str
    analysis_date: datetime = field(default_factory=datetime.now)
    companies: list[Company] = field(default_factory=list)

    # Market metrics
    total_market_size: float | None = None
    growth_rate: float | None = None

    # Competitive landscape
    concentration_ratio: float | None = None
    barriers_to_entry: list[str] = field(default_factory=list)

    # Trends
    key_trends: list[str] = field(default_factory=list)
    regulatory_environment: list[str] = field(default_factory=list)

    # Analysis
    swot_analysis: dict[str, list[str]] | None = None
    recommendations: list[str] = field(default_factory=list)

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


@dataclass
class ScoreComponent:
    """A single component of a score calculation."""

    name: str
    value: float
    formula: str
    reasoning: str


@dataclass
class ScoringExplanation:
    """Detailed explanation of how a final score was calculated."""

    base_score: float
    components: list[ScoreComponent] = field(default_factory=list)
    final_score: float = 0.0


@dataclass
class CompetitiveOverlap:
    """Competitive overlap domain entity."""

    company_a_id: str
    company_b_id: str
    overlap_score: float
    overlap_areas: list[str] = field(default_factory=list)
    competitive_intensity: str = "Medium"
    notes: str | None = None
