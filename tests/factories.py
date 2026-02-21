"""
Test factory functions for SolStein domain objects.

Single source of truth for building test objects.
All test fixtures should delegate to these factories.
"""

from solstein.domain.models import (
    AIMaturity,
    Company,
    CompanyTier,
    FinancialMetric,
    ThreatLevel,
)


def make_financial_metric(**overrides) -> FinancialMetric:
    """Build a FinancialMetric with sensible defaults."""
    defaults = dict(
        revenue=100.0,  # EUR millions
        growth_rate=15.0,  # %
        profit_margin=10.0,  # %
        funding_raised=50.0,  # EUR millions
    )
    defaults.update(overrides)
    return FinancialMetric(**defaults)


def make_company(**overrides) -> Company:
    """
    Build a Company with sensible defaults.

    All enum values use the proper enum types (not raw strings),
    so these objects are safe to pass through Pydantic/dataclass validation.

    Override any field with kwargs:
        make_company(name="Phoenix Inc", financials=FinancialMetric(growth_rate=45.0))
    """
    defaults = dict(
        id="test-company",
        name="Test Corp",
        industry="Technology",
        headquarters="New York, USA",
        tier=CompanyTier.TIER_1,
        threat_level=ThreatLevel.MEDIUM,
        ai_maturity=AIMaturity.STRONG,  # enum, NOT "Strong"
        saas_maturity=4,
        tech_stack=["React", "Python", "AWS"],
        geographic_presence=["US", "UK"],
        financials=make_financial_metric(),
    )
    defaults.update(overrides)
    return Company(**defaults)


def make_phoenix_company(**overrides) -> Company:
    """Build a high-growth 'Phoenix' company for scoring tests."""
    defaults = dict(
        id="phoenix-001",
        name="Phoenix Inc",
        ai_maturity=AIMaturity.STRONG,
        financials=FinancialMetric(
            revenue=500.0,
            growth_rate=45.0,  # +2.25 (45/20, capped at 4.0)
            profit_margin=15.0,  # +1.0 (hits margin_med_threshold=10.0)
        ),
    )
    defaults.update(overrides)
    return make_company(**defaults)


def make_lead_company(**overrides) -> Company:
    """Build a declining 'Lead' company for scoring tests."""
    defaults = dict(
        id="lead-001",
        name="Lead Corp",
        ai_maturity=AIMaturity.NONE,
        financials=FinancialMetric(
            revenue=10.0,
            growth_rate=-5.0,  # -0.25 (−5/20)
            profit_margin=-2.0,  # -1.0 penalty (negative margin)
        ),
    )
    defaults.update(overrides)
    return make_company(**defaults)
