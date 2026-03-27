"""Test fixtures for EPIC-012: Testing Strategy

Provides comprehensive test fixtures for different company scenarios.
"""

import pytest

from solstein.domain.models import (
    AIMaturity,
    Company,
    CompanyClassification,
    CompanyTier,
    FinancialMetric,
)


@pytest.fixture
def small_startup() -> Company:
    """Small startup fixture (€500K revenue, 10 employees)."""
    return Company(
        id="small-startup",
        name="Small Startup Inc",
        industry="Energy Software",
        tier=CompanyTier.TIER_4,
        ai_maturity=AIMaturity.LOW,
        saas_maturity=2,
        financials=FinancialMetric(
            revenue=0.5,
            growth_rate=50.0,
            employees=10,
            funding_raised=1.0,
        ),
        founded_year=2022,
        headquarters="Berlin, Germany",
        website="https://smallstartup.example.com",
    )


@pytest.fixture
def growth_company() -> Company:
    """Growth stage company fixture (€5M revenue, 50 employees)."""
    return Company(
        id="growth-co",
        name="Growth Company",
        industry="Energy Software",
        tier=CompanyTier.TIER_3,
        ai_maturity=AIMaturity.MODERATE,
        saas_maturity=5,
        financials=FinancialMetric(
            revenue=5.0,
            growth_rate=35.0,
            employees=50,
            funding_raised=10.0,
            valuation=50.0,
        ),
        founded_year=2018,
        headquarters="Copenhagen, Denmark",
        website="https://growth.example.com",
    )


@pytest.fixture
def enterprise_company() -> Company:
    """Enterprise company fixture (€100M revenue, 1000 employees)."""
    return Company(
        id="enterprise-co",
        name="Enterprise Solutions",
        industry="Energy Software",
        tier=CompanyTier.TIER_1,
        ai_maturity=AIMaturity.STRONG,
        saas_maturity=9,
        financials=FinancialMetric(
            revenue=100.0,
            growth_rate=15.0,
            employees=1000,
            funding_raised=0.0,
            valuation=500.0,
        ),
        founded_year=2005,
        headquarters="Munich, Germany",
        website="https://enterprise.example.com",
    )


@pytest.fixture
def phoenix_company() -> Company:
    """Phoenix classification fixture (high growth, strong position)."""
    return Company(
        id="phoenix-co",
        name="Phoenix Energy",
        industry="Energy Software",
        tier=CompanyTier.TIER_1,
        ai_maturity=AIMaturity.STRONG,
        saas_maturity=9,
        financials=FinancialMetric(
            revenue=50.0,
            growth_rate=80.0,
            employees=200,
            funding_raised=100.0,
            valuation=400.0,
        ),
        founded_year=2015,
        headquarters="Oslo, Norway",
        website="https://phoenix.example.com",
        classification=CompanyClassification.PHOENIX,
    )


@pytest.fixture
def salt_company() -> Company:
    """Salt classification fixture (moderate growth)."""
    return Company(
        id="salt-co",
        name="Salt Systems",
        industry="Energy Software",
        tier=CompanyTier.TIER_2,
        ai_maturity=AIMaturity.MODERATE,
        saas_maturity=6,
        financials=FinancialMetric(
            revenue=20.0,
            growth_rate=25.0,
            employees=150,
            funding_raised=30.0,
            valuation=120.0,
        ),
        founded_year=2012,
        headquarters="Stockholm, Sweden",
        website="https://salt.example.com",
        classification=CompanyClassification.SALT,
    )


@pytest.fixture
def lead_company() -> Company:
    """Lead classification fixture (low growth)."""
    return Company(
        id="lead-co",
        name="Legacy Systems",
        industry="Energy Software",
        tier=CompanyTier.TIER_4,
        ai_maturity=AIMaturity.LOW,
        saas_maturity=2,
        financials=FinancialMetric(
            revenue=2.0,
            growth_rate=-10.0,
            employees=100,
            funding_raised=0.5,
            valuation=2.0,
        ),
        founded_year=2000,
        headquarters="Hamburg, Germany",
        website="https://legacy.example.com",
        classification=CompanyClassification.LEAD,
    )


@pytest.fixture
def missing_data_company() -> Company:
    """Company with missing data fixture."""
    return Company(
        id="missing-data-co",
        name="Unknown Corp",
        industry="Energy Software",
        tier=CompanyTier.TIER_3,
        ai_maturity=AIMaturity.UNKNOWN,
        saas_maturity=1,
        financials=FinancialMetric(allow_empty_primary=True),
        founded_year=None,
        headquarters=None,
        website=None,
    )


@pytest.fixture
def edge_case_company() -> Company:
    """Edge case fixture (zero revenue, extreme values)."""
    return Company(
        id="edge-case-co",
        name="Edge Case Ltd",
        industry="Energy Software",
        tier=CompanyTier.TIER_4,
        ai_maturity=AIMaturity.NONE,
        saas_maturity=1,
        financials=FinancialMetric(
            revenue=0.0,
            growth_rate=0.0,
            employees=1,
            funding_raised=0.0,
            valuation=0.0,
            profit_margin=0.0,
        ),
        founded_year=2024,
        headquarters="Remote",
        website=None,
    )
