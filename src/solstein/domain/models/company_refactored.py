"""Company domain model with integrated mixins.

EPIC-022: Refactored to use mixins for shared functionality.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..models.financial import FinancialMetric


class CompanyMixin:
    """Mixin providing utility methods for Company model."""

    def get_field(self, field_name: str, default: Any = None) -> Any:
        """Safely get any field by name."""
        try:
            return getattr(self, field_name, default)
        except AttributeError:
            return default

    def get_financial_field(self, field_name: str, default: Any = None) -> Any:
        """Safely get a field from financials."""
        if self.financials is None:
            return default
        return getattr(self.financials, field_name, default)

    def set_field(self, field_name: str, value: Any) -> bool:
        """Safely set a field value."""
        try:
            if hasattr(self, field_name):
                setattr(self, field_name, value)
                return True
            return False
        except (AttributeError, ValueError):
            return False

    def has_field(self, field_name: str) -> bool:
        """Check if a field exists and has a non-None value."""
        try:
            value = getattr(self, field_name, None)
            return value is not None
        except AttributeError:
            return False

    def get_data_completeness(self) -> float:
        """Calculate data completeness score (0.0 to 1.0)."""
        required_fields = ["name", "industry", "revenue", "employees", "growth_rate", "headquarters"]
        present_count = sum(1 for field in required_fields if self.has_field(field))
        return present_count / len(required_fields)


class CompanyPropertyMixin:
    """Mixin providing computed properties for Company model."""

    @property
    def is_large_cap(self) -> bool:
        """Check if company is large cap (valuation > €100M)."""
        return self.financials.valuation is not None and self.financials.valuation > 100_000_000

    @property
    def is_high_growth(self) -> bool:
        """Check if company is high growth."""
        return self.financials.growth_rate is not None and self.financials.growth_rate > 20

    @property
    def is_profitable(self) -> bool:
        """Check if company is profitable."""
        return self.financials.profit_margin is not None and self.financials.profit_margin > 0


class CompanySyncMixin:
    """Mixin providing synchronization methods for Company model."""

    def sync_financial_fields(self) -> Company:
        """Synchronize financial fields between top-level and financials object."""
        # Ensure company_name is set
        if self.company_name is None:
            self.company_name = self.name

        # Ensure financials object exists
        if self.financials is None:
            self.financials = FinancialMetric()

        # Sync fields bidirectionally
        self._sync_field("revenue", "revenue")
        self._sync_field("employees", "employees")
        self._sync_field("growth_rate", "growth_rate")
        self._sync_field("profit_margin", "profit_margin")
        self._sync_field("valuation", "valuation")

        # Special case for funding/funding_raised
        funding_value = self.funding
        financial_funding = self.financials.funding_raised
        if funding_value is None and financial_funding is not None:
            self.funding = financial_funding
        elif funding_value is not None and financial_funding is None:
            self.financials.funding_raised = funding_value

        # Sync confidence scores
        if not self.confidence_scores and self.signal_confidences:
            self.confidence_scores = dict(self.signal_confidences)
        elif self.confidence_scores and not self.signal_confidences:
            self.signal_confidences = dict(self.confidence_scores)

        return self

    def _sync_field(self, field_name: str, financial_name: str) -> None:
        """Sync a single field between top-level and financials."""
        value = getattr(self, field_name)
        financial_value = getattr(self.financials, financial_name)

        if value is None and financial_value is not None:
            setattr(self, field_name, financial_value)
        elif value is not None and financial_value is None:
            setattr(self.financials, financial_name, value)


class Company(CompanyMixin, CompanyPropertyMixin, CompanySyncMixin, BaseModel):
    """Company domain entity with modular validation and utilities.

    EPIC-022: Refactored to use mixins for shared functionality.
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
    funding: float | None = None
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

    # Validators
    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        if not v:
            raise ValueError("Company ID cannot be empty")
        if len(v) < 3:
            raise ValueError("Company ID must be at least 3 characters")
        if " " in v:
            raise ValueError("Company ID cannot contain spaces")
        return v.strip()

    @field_validator("ai_score")
    @classmethod
    def validate_ai_score_value(cls, v: float | None) -> float | None:
        if v is not None and (v < 0 or v > 10):
            raise ValueError("AI score must be between 0 and 10")
        return v

    @field_validator("saas_maturity")
    @classmethod
    def validate_saas_maturity(cls, v: int) -> int:
        if v < 1 or v > 10:
            raise ValueError("SaaS maturity must be between 1 and 10")
        return v

    @field_validator("revenue_cagr_3yr", "revenue_cagr_5yr")
    @classmethod
    def validate_cagr(cls, v: float | None) -> float | None:
        if v is not None and (v < -0.5 or v > 2.0):
            raise ValueError("CAGR must be between -50% and +200%")
        return v

    @field_validator("profit_margin", "ebitda_margin", "recurring_revenue_pct")
    @classmethod
    def validate_percentage(cls, v: float | None) -> float | None:
        if v is not None and (v < -1.0 or v > 10.0):
            raise ValueError("Percentage must be between -100% and +1000%")
        return v

    @field_validator("employee_count", "open_positions")
    @classmethod
    def validate_positive_int(cls, v: int | None) -> int | None:
        if v is not None and v < 0:
            raise ValueError("Value must be non-negative")
        return v

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip().upper()
        if not v:
            return None
        if not re.match(r"^[A-Z]{1,5}([.][A-Z]{1,4})?$", v):
            raise ValueError("Ticker must be 1-5 uppercase letters, optionally with exchange suffix")
        return v

    @field_validator("company_number")
    @classmethod
    def validate_company_number(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip().upper()
        if not v:
            return None
        if not re.match(r"^[A-Z0-9\-]{5,20}$", v):
            raise ValueError("Company number must be 5-20 alphanumeric characters")
        return v

    @field_validator("isin")
    @classmethod
    def validate_isin(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip().upper()
        if not v:
            return None
        if not re.match(r"^[A-Z]{2}[A-Z0-9]{9}[0-9]$", v):
            raise ValueError("ISIN must be 12 characters: 2 letters + 9 alphanumeric + 1 digit")
        return v

    @field_validator("geography_code")
    @classmethod
    def validate_geography_code(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip().upper()
        if not v:
            return None
        if not re.match(r"^[A-Z]{2,3}$", v):
            raise ValueError("Geography code must be 2-3 uppercase letters")
        return v
