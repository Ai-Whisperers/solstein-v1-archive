"""
Data models for SolStein competitive intelligence platform.

All models use Pydantic for validation and serialization.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ConfidenceLevel(str, Enum):
    """Confidence levels for data points."""
    CONFIRMED = "Confirmed"
    ESTIMATED = "Estimated"
    UNKNOWN = "Unknown"


class AIMaturity(str, Enum):
    """AI adoption maturity levels."""
    NONE = "None"
    LOW = "Low"
    MODERATE = "Moderate"
    STRONG = "Strong"
    VERY_STRONG = "Very Strong"


class ThreatLevel(str, Enum):
    """Competitive threat levels."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class CompanyTier(str, Enum):
    """Company size/market position tiers."""
    TIER_1 = "Tier 1"  # Market leaders
    TIER_2 = "Tier 2"  # Strong competitors
    TIER_3 = "Tier 3"  # Niche players
    TIER_4 = "Tier 4"  # Emerging/startups


class FinancialMetric(BaseModel):
    """Financial metrics for a company."""
    model_config = ConfigDict(extra="forbid")

    revenue: float | None = Field(
        None,
        description="Annual revenue in EUR",
        ge=0,
        examples=[1000000.0, 50000000.0]
    )
    revenue_confidence: ConfidenceLevel = Field(
        default=ConfidenceLevel.UNKNOWN,
        description="Confidence level for revenue data"
    )

    growth_rate: float | None = Field(
        None,
        description="Annual growth rate in percentage",
        ge=-100,
        le=1000,
        examples=[15.5, -2.3, 120.0]
    )
    growth_confidence: ConfidenceLevel = Field(
        default=ConfidenceLevel.UNKNOWN
    )

    employees: int | None = Field(
        None,
        description="Number of employees",
        ge=0,
        examples=[50, 1000, 10000]
    )
    employees_confidence: ConfidenceLevel = Field(
        default=ConfidenceLevel.UNKNOWN
    )

    profit_margin: float | None = Field(
        None,
        description="Profit margin in percentage",
        ge=-100,
        le=100,
        examples=[12.5, -5.2, 25.0]
    )
    margin_confidence: ConfidenceLevel = Field(
        default=ConfidenceLevel.UNKNOWN
    )

    funding_raised: float | None = Field(
        None,
        description="Total funding raised in EUR",
        ge=0,
        examples=[5000000.0, 100000000.0]
    )
    funding_confidence: ConfidenceLevel = Field(
        default=ConfidenceLevel.UNKNOWN
    )

    valuation: float | None = Field(
        None,
        description="Company valuation in EUR",
        ge=0,
        examples=[50000000.0, 1000000000.0]
    )
    valuation_confidence: ConfidenceLevel = Field(
        default=ConfidenceLevel.UNKNOWN
    )

    @field_validator("revenue", "growth_rate", "employees", "profit_margin", "funding_raised", "valuation", mode='before')
    def validate_numeric_fields(cls, v):
        """Convert string numbers to floats/ints."""
        if v is None or v == "":
            return None
        if isinstance(v, str):
            # Remove currency symbols, commas, percentage signs, etc.
            v = v.replace("€", "").replace("$", "").replace(",", "").replace(" ", "").replace("%", "")
            if v.endswith("M"):
                return float(v[:-1]) * 1_000_000
            elif v.endswith("B"):
                return float(v[:-1]) * 1_000_000_000
            elif v.endswith("K"):
                return float(v[:-1]) * 1_000
        return v


class CompanyProfile(BaseModel):
    """Complete company profile for competitive intelligence."""
    model_config = ConfigDict(extra="forbid")

    # Core identifiers
    id: str = Field(
        ...,
        description="Unique company identifier",
        examples=["eneve", "hansen-technologies", "volue"]
    )
    name: str = Field(
        ...,
        description="Company name",
        examples=["Eneve", "Hansen Technologies", "Volue"]
    )

    # Basic information
    industry: str = Field(
        default="Energy Software",
        description="Primary industry",
        examples=["Energy Software", "FinTech", "Healthcare IT"]
    )
    description: str | None = Field(
        None,
        description="Company description"
    )
    website: str | None = Field(
        None,
        description="Company website URL"
    )
    headquarters: str | None = Field(
        None,
        description="Headquarters location"
    )
    founded_year: int | None = Field(
        None,
        description="Year company was founded",
        ge=1800,
        le=datetime.now().year
    )

    # Competitive positioning
    tier: CompanyTier = Field(
        default=CompanyTier.TIER_3,
        description="Market position tier"
    )
    threat_level: ThreatLevel = Field(
        default=ThreatLevel.MEDIUM,
        description="Competitive threat level"
    )

    # Technology assessment
    ai_maturity: AIMaturity = Field(
        default=AIMaturity.NONE,
        description="AI adoption maturity level"
    )
    saas_maturity: int = Field(
        default=1,
        description="SaaS maturity score (1-10)",
        ge=1,
        le=10
    )
    tech_stack: list[str] = Field(
        default_factory=list,
        description="Technology stack"
    )

    # Financial data
    financials: FinancialMetric = Field(
        default_factory=FinancialMetric
    )

    # Market presence
    geographic_presence: list[str] = Field(
        default_factory=list,
        description="Countries/regions where company operates"
    )
    key_customers: list[str] = Field(
        default_factory=list,
        description="Notable customers"
    )

    # Corporate structure
    parent_company: str | None = Field(
        None,
        description="Parent company if subsidiary"
    )
    subsidiaries: list[str] = Field(
        default_factory=list,
        description="Subsidiary companies"
    )
    acquisitions: list[dict[str, Any]] = Field(
        default_factory=list,
        description="M&A history"
    )

    # Metadata
    last_updated: datetime = Field(
        default_factory=datetime.now,
        description="When this profile was last updated"
    )
    data_source: str | None = Field(
        None,
        description="Source of this data"
    )
    notes: str | None = Field(
        None,
        description="Additional notes"
    )

    # Calculated fields (will be populated by analytics)
    growth_score: float | None = Field(
        None,
        description="Overall growth score (0-10)",
        ge=0,
        le=10
    )
    financial_health_score: float | None = Field(
        None,
        description="Financial health score (0-10)",
        ge=0,
        le=10
    )
    competitive_position_score: float | None = Field(
        None,
        description="Competitive position score (0-10)",
        ge=0,
        le=10
    )

    @property
    def is_public(self) -> bool:
        """Check if company is publicly traded."""
        return self.financials.valuation is not None and self.financials.valuation > 100_000_000

    @property
    def is_high_growth(self) -> bool:
        """Check if company is high growth (>20% annually)."""
        return (
            self.financials.growth_rate is not None
            and self.financials.growth_rate > 20
        )

    @property
    def is_profitable(self) -> bool:
        """Check if company is profitable."""
        return (
            self.financials.profit_margin is not None
            and self.financials.profit_margin > 0
        )


class MarketAnalysis(BaseModel):
    """Market-level analysis across multiple companies."""
    model_config = ConfigDict(extra="forbid")

    market_name: str = Field(
        ...,
        description="Name of the market/industry",
        examples=["European Energy Software", "US FinTech", "Global Healthcare IT"]
    )
    analysis_date: datetime = Field(
        default_factory=datetime.now,
        description="When this analysis was conducted"
    )

    companies: list[CompanyProfile] = Field(
        default_factory=list,
        description="Companies in this market"
    )

    # Market metrics
    total_market_size: float | None = Field(
        None,
        description="Total market size in EUR",
        ge=0
    )
    growth_rate: float | None = Field(
        None,
        description="Market growth rate in percentage",
        ge=-100,
        le=1000
    )

    # Competitive landscape
    concentration_ratio: float | None = Field(
        None,
        description="Market concentration ratio (CR4)",
        ge=0,
        le=100
    )
    barriers_to_entry: list[str] = Field(
        default_factory=list,
        description="Barriers to entry in this market"
    )

    # Trends
    key_trends: list[str] = Field(
        default_factory=list,
        description="Key market trends"
    )
    regulatory_environment: list[str] = Field(
        default_factory=list,
        description="Regulatory factors"
    )

    # Analysis
    swot_analysis: dict[str, list[str]] | None = Field(
        None,
        description="SWOT analysis for the market"
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="Strategic recommendations"
    )

    @property
    def company_count(self) -> int:
        """Number of companies in the analysis."""
        return len(self.companies)

    @property
    def average_growth_rate(self) -> float | None:
        """Average growth rate of companies in the market."""
        growth_rates = [
            c.financials.growth_rate for c in self.companies
            if c.financials.growth_rate is not None
        ]
        if not growth_rates:
            return None
        return sum(growth_rates) / len(growth_rates)

    @property
    def market_leaders(self) -> list[CompanyProfile]:
        """Get Tier 1 companies (market leaders)."""
        return [c for c in self.companies if c.tier == CompanyTier.TIER_1]


class CompetitiveOverlap(BaseModel):
    """Competitive overlap between companies."""
    model_config = ConfigDict(extra="forbid")

    company_a_id: str = Field(..., description="First company ID")
    company_b_id: str = Field(..., description="Second company ID")

    overlap_score: float = Field(
        ...,
        description="Overlap score (0-1)",
        ge=0,
        le=1
    )

    overlap_areas: list[str] = Field(
        default_factory=list,
        description="Areas of overlap"
    )

    competitive_intensity: str = Field(
        default="Medium",
        description="Intensity of competition",
        examples=["Low", "Medium", "High", "Direct"]
    )

    notes: str | None = Field(
        None,
        description="Additional notes on the competitive relationship"
    )
