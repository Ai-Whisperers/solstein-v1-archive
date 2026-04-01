"""Company domain model - Refactored.

EPIC-022: Refactored to use mixins and external validators.

The Company class now uses:
- CompanyUtilityMixin for utility methods (get_field, set_field, has_field, etc.)
- CompanyPropertyMixin for computed properties (is_large_cap, is_high_growth, is_profitable)
- CompanySyncMixin for synchronization methods (sync_financial_fields)
- External validators from domain.validators.company module
"""

# pyright: reportMissingImports=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import ConfigDict, Field, field_validator, model_validator

from ..models.financial import FinancialMetric
from ..validators.company import CompanyValidators
from .mixins import CompanyPropertyMixin, CompanySyncMixin, CompanyUtilityMixin


class Company(CompanyUtilityMixin, CompanyPropertyMixin, CompanySyncMixin):
    """Company domain entity with modular validation and utilities.

    EPIC-022: Refactored to use mixins for shared functionality
    and external validators for field validation.
    """

    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True)

    # Core identification
    id: str = Field(..., description="Unique company identifier")
    name: str
    company_name: str | None = None
    industry: str = "Energy Software"
    description: str | None = None
    website: str | None = None
    headquarters: str | None = None
    founded_year: int | None = None

    # Metadata
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data_source: str | None = None
    notes: str | None = None
    source_links: list[str] = Field(default_factory=list)
    metric_sources: dict[str, list[str]] = Field(default_factory=dict)
    metric_justifications: dict[str, str] = Field(default_factory=dict)
    metric_observations: dict[str, list[dict[str, Any]]] = Field(default_factory=dict)
    signal_confidences: dict[str, float] = Field(default_factory=dict)

    # Classification
    tier: str | None = None
    threat_level: str | None = None
    classification: str | None = None
    ai_maturity: str | None = None
    saas_maturity: int = Field(default=0, ge=0, le=10)

    # AI metrics
    ai_score: float | None = Field(default=None, ge=0, le=10)
    ai_signal_level: str | None = None
    ai_key_capabilities: str | None = None
    ai_in_production: bool | None = None

    # STORY-145: AI Readiness Assessment (EPIC-038)
    ai_readiness_score: float | None = None  # 0-100 composite score
    ai_readiness_tier: str | None = None  # AI-Ready / AI-Capable / AI-Challenged / AI-Resistant
    ai_readiness_breakdown: dict[str, float] = Field(default_factory=dict)

    # Identifiers
    ticker: str | None = None
    company_number: str | None = None
    isin: str | None = None
    geography_code: str | None = None

    # Financials container
    financials: FinancialMetric = Field(default_factory=FinancialMetric)

    # Scoring
    growth_score: float | None = None
    financial_health_score: float | None = None
    competitive_position_score: float | None = None
    composite_score: float | None = None
    scoring_breakdown: dict[str, Any] = Field(default_factory=dict)

    # Revenue metrics
    revenue: float | None = None
    revenue_eur_m: float | None = None
    revenue_confidence: str | None = None
    growth_rate: float | None = None
    growth_confidence: str | None = None
    revenue_cagr_3yr: float | None = None
    revenue_cagr_5yr: float | None = None
    revenue_timeline: list[dict[str, Any]] = Field(default_factory=list)

    # Profitability
    profit_margin: float | None = None
    ebitda_margin: float | None = None
    recurring_revenue_pct: float | None = None
    revenue_per_employee_eur_k: float | None = None
    profitability_raw_metrics: dict[str, Any] = Field(default_factory=dict)

    # Funding
    funding_raised: float | None = None
    funding_rounds: list[dict[str, Any]] = Field(default_factory=list)
    total_funding_raised_eur: float | None = None
    latest_valuation_eur: float | None = None
    lead_investors: list[str] = Field(default_factory=list)
    funding_war_chest: str | None = None

    # Employees
    employee_count: int | None = Field(default=None, ge=0)
    employees: int | None = Field(default=None, ge=0)
    employee_cagr_3yr: float | None = None
    open_positions: int | None = Field(default=None, ge=0)

    # Data quality
    data_availability: str | None = None
    confidence_scores: dict[str, float] = Field(default_factory=dict)

    # STORY-146: AI Transformation Readiness (EPIC-038)
    transformation_time_months: float | None = None
    transformation_cost_eur: float | None = None
    transformation_efficiency_gain_pct: float | None = None
    transformation_risk_level: str | None = None
    transformation_breakdown: dict[str, Any] = Field(default_factory=dict)

    # STORY-149: Energy Compliance (EPIC-039)
    energy_compliance_score: float | None = None  # 0-100 composite
    energy_compliance_risk: str | None = None  # high / medium / low
    energy_control_tier: str | None = None  # advanced / standard / legacy / unknown
    energy_compliance_breakdown: dict[str, Any] = Field(default_factory=dict)

    # STORY-150: Energy Market Forecasting (EPIC-039)
    energy_market_score: float | None = None  # 0-100 composite
    energy_market_positioning: str | None = None
    energy_market_segments: list[str] = Field(default_factory=list)
    energy_market_breakdown: dict[str, Any] = Field(default_factory=dict)

    # STORY-151: Trading Platform & Digital Infrastructure (EPIC-039)
    energy_trading_score: float | None = None
    energy_platform_maturity: str | None = None
    energy_infrastructure_tier: str | None = None
    energy_trading_breakdown: dict[str, Any] = Field(default_factory=dict)

    # STORY-152: Grid Integration & Smart Infrastructure (EPIC-039)
    energy_grid_score: float | None = None
    energy_grid_readiness: str | None = None
    energy_smart_infra_level: str | None = None
    energy_grid_breakdown: dict[str, Any] = Field(default_factory=dict)


    # Aliases for backward compatibility
    @property
    def funding(self) -> float | None:
        return self.funding_raised

    @funding.setter
    def funding(self, value: float | None) -> None:
        self.funding_raised = value

    # External validators
    validate_id = field_validator("id")(CompanyValidators.validate_id)
    validate_ai_score_value = field_validator("ai_score")(CompanyValidators.validate_ai_score_value)
    validate_saas_maturity = field_validator("saas_maturity")(CompanyValidators.validate_saas_maturity)
    validate_cagr = field_validator("revenue_cagr_3yr", "revenue_cagr_5yr")(CompanyValidators.validate_cagr)
    validate_percentage = field_validator("profit_margin", "ebitda_margin", "recurring_revenue_pct")(
        CompanyValidators.validate_percentage
    )
    validate_positive_int = field_validator("employee_count", "open_positions")(CompanyValidators.validate_positive_int)
    validate_ticker = field_validator("ticker")(CompanyValidators.validate_ticker)
    validate_company_number = field_validator("company_number")(CompanyValidators.validate_company_number)
    validate_isin = field_validator("isin")(CompanyValidators.validate_isin)
    validate_geography_code = field_validator("geography_code")(CompanyValidators.validate_geography_code)

    @model_validator(mode="after")
    def require_primary_financial_metric(self) -> Company:
        revenue = self.revenue if self.revenue is not None else getattr(self.financials, "revenue", None)
        employees = self.employees if self.employees is not None else getattr(self.financials, "employees", None)
        if revenue is None and employees is None:
            raise ValueError("At least revenue OR employees required")
        return self
