"""
API Schemas.

These are Pydantic models used strictly for input/output validation.
They should mirror the structure expected by API clients.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Re-export Enums from domain to avoid duplication,
# or better yet, keep them in schemas if they are API specific.
# For now, we reuse domain enums for simplicity of mapping.
from ..domain.models import AIMaturity, CompanyTier, ConfidenceLevel, ThreatLevel


class FinancialMetricSchema(BaseModel):
    """Financial metrics schema."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    revenue: float | None = Field(default=None, description="Annual revenue in EUR")
    revenue_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    growth_rate: float | None = Field(default=None, description="Annual growth rate %")
    growth_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    employees: int | None = None
    employees_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    profit_margin: float | None = None
    margin_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    funding_raised: float | None = None
    funding_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    valuation: float | None = None
    valuation_confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN

    @field_validator(
        "revenue",
        "growth_rate",
        "employees",
        "profit_margin",
        "funding_raised",
        "valuation",
        mode="before",
    )
    @classmethod
    def validate_numeric_fields(cls, v: Any) -> Any:
        """Sanitize string inputs."""
        if v is None or v == "":
            return None
        if isinstance(v, str):
            v = (
                v.replace("€", "")
                .replace("$", "")
                .replace(",", "")
                .replace(" ", "")
                .replace("%", "")
            )
            if v.endswith("M"):
                return float(v[:-1]) * 1_000_000
            elif v.endswith("B"):
                return float(v[:-1]) * 1_000_000_000
            elif v.endswith("K"):
                return float(v[:-1]) * 1_000
        return v


class CompanyProfileSchema(BaseModel):
    """Company profile API schema."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: str
    name: str
    industry: str = "Energy Software"
    description: str | None = None
    website: str | None = None
    headquarters: str | None = None
    founded_year: int | None = None

    tier: CompanyTier = CompanyTier.TIER_3
    threat_level: ThreatLevel = ThreatLevel.MEDIUM
    ai_maturity: AIMaturity = AIMaturity.NONE
    saas_maturity: int = 1
    tech_stack: list[str] = Field(default_factory=list)
    
    financials: FinancialMetricSchema = Field(default_factory=lambda: FinancialMetricSchema())

    geographic_presence: list[str] = Field(default_factory=list)
    key_customers: list[str] = Field(default_factory=list)

    parent_company: str | None = None
    subsidiaries: list[str] = Field(default_factory=list)
    acquisitions: list[dict[str, Any]] = Field(default_factory=list)

    last_updated: datetime = Field(default_factory=datetime.now)
    data_source: str | None = None
    notes: str | None = None

    growth_score: float | None = None
    financial_health_score: float | None = None
    competitive_position_score: float | None = None


class ConditionSchema(BaseModel):
    """Market condition schema."""

    type: str
    name: str
    impact_factor: float
    description: str
    affected_industries: list[str] | None = None


class ScenarioSchema(BaseModel):
    """Simulation scenario schema."""

    id: str
    name: str
    description: str
    conditions: list[ConditionSchema]


class SimulationResultSchema(BaseModel):
    """Simulation result schema."""

    company_id: str
    company_name: str
    base_valuation: float
    simulated_valuation: float
    valuation_change_pct: float
    base_growth_score: float
    simulated_growth_score: float
    growth_score_change: float
    notes: list[str]
