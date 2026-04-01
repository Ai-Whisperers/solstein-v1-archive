"""Factory Boy factories for creating test data.

This module provides centralized factories for creating test data
without manual mock setup.

Usage:
    from tests.factories import CompanyFactory

    # Create a company with default values
    company = CompanyFactory()

    # Create a company with specific values
    company = CompanyFactory(name="Test Corp", tier=CompanyTier.TIER_1)

    # Create multiple companies
    companies = CompanyFactory.create_batch(10)
"""

from typing import TYPE_CHECKING, Any, Optional, cast  # noqa: F401
from uuid import uuid4

from factory.base import Factory

if TYPE_CHECKING:

    class _BaseFactoryMeta(Factory.Meta):
        pass
else:

    class _BaseFactoryMeta:
        pass


from factory.declarations import Iterator, List, Sequence, SubFactory
from factory.faker import Faker
from factory.helpers import post_generation
from sqlalchemy.ext.asyncio import AsyncSession

from solstein.domain.facts import Fact, FactSource, GatheringBatch
from solstein.domain.models import (
    AIMaturity,
    Company,
    CompanyTier,
    ConfidenceLevel,
    FinancialMetric,
    ThreatLevel,
)


class FinancialMetricFactory(Factory[FinancialMetric]):
    """Factory for creating FinancialMetric instances."""

    class Meta(_BaseFactoryMeta):
        model = FinancialMetric

    revenue = Faker("pydecimal", left_digits=6, right_digits=2, positive=True)
    revenue_confidence = ConfidenceLevel.CONFIRMED
    growth_rate = Faker("pydecimal", left_digits=2, right_digits=2, positive=True)
    growth_confidence = ConfidenceLevel.ESTIMATED
    employees = Faker("random_int", min=10, max=10000)
    employees_confidence = ConfidenceLevel.CONFIRMED


class CompanyFactory(Factory[Company]):
    """Factory for creating Company instances.

    Creates realistic company data with sensible defaults.
    All fields can be overridden.

    Examples:
        >>> # Default company
        >>> company = CompanyFactory()

        >>> # Company with specific tier
        >>> company = CompanyFactory(tier=CompanyTier.TIER_1)

        >>> # Create 10 companies
        >>> companies = CompanyFactory.create_batch(10)
    """

    class Meta(_BaseFactoryMeta):
        model = Company

    id = Sequence(lambda n: f"comp_{n:03d}")
    name = Faker("company")
    industry = Faker("bs")
    description = Faker("catch_phrase")
    website = Faker("url")
    headquarters = Faker("city")
    founded_year = Faker("year")

    tier = Iterator(CompanyTier)
    ai_maturity = Iterator(AIMaturity)
    threat_level = Iterator(ThreatLevel)

    financials = SubFactory(FinancialMetricFactory)
    composite_score: float | None = None

    geographic_presence = List([Faker("country") for _ in range(3)])

    @post_generation
    def set_composite_score(self, create, extracted, **kwargs):
        """Calculate composite score after creation."""
        growth_score = cast(float | None, getattr(self, "growth_score", None))
        financial_health_score = cast(float | None, getattr(self, "financial_health_score", None))
        competitive_position_score = cast(float | None, getattr(self, "competitive_position_score", None))
        if growth_score is not None and financial_health_score is not None and competitive_position_score is not None:
            composite_score = growth_score * 0.4 + financial_health_score * 0.3 + competitive_position_score * 0.3
            self.composite_score = composite_score


class CompanyFactoryHighGrowth(CompanyFactory):
    """Factory for high-growth companies (Phoenix type)."""

    growth_score = 8.5
    financial_health_score = 7.0
    tier = CompanyTier.TIER_1
    ai_maturity = AIMaturity.STRONG


class CompanyFactoryDistressed(CompanyFactory):
    """Factory for distressed companies."""

    growth_score = 2.0
    financial_health_score = 3.0
    tier = CompanyTier.TIER_4
    threat_level = ThreatLevel.HIGH


def make_company(**kwargs: object) -> Company:
    return CompanyFactory(**kwargs)


def make_financial_metric(**overrides: Any) -> FinancialMetric:
    defaults: dict[str, Any] = dict(
        revenue=100.0,
        growth_rate=15.0,
        profit_margin=10.0,
        funding_raised=50.0,
    )
    defaults.update(overrides)
    return FinancialMetric(**defaults)


def make_phoenix_company(**overrides: Any) -> Company:
    defaults: dict[str, Any] = dict(
        id="phoenix-001",
        name="Phoenix Inc",
        ai_maturity=AIMaturity.STRONG,
        financials=FinancialMetric(
            revenue=500.0,
            growth_rate=45.0,
            profit_margin=15.0,
        ),
    )
    defaults.update(overrides)
    return make_company(**defaults)


def make_lead_company(**overrides: Any) -> Company:
    defaults: dict[str, Any] = dict(
        id="lead-001",
        name="Lead Corp",
        ai_maturity=AIMaturity.NONE,
        financials=FinancialMetric(
            revenue=10.0,
            growth_rate=-5.0,
            profit_margin=-2.0,
        ),
    )
    defaults.update(overrides)
    return make_company(**defaults)


async def create_test_company(session: AsyncSession, **overrides: Any) -> str:
    company_id = overrides.get("company_id", f"test-company-{uuid4()}")
    return str(company_id)


async def create_test_batch(
    session: AsyncSession,
    company_id: str,
    **overrides: Any,
) -> GatheringBatch:
    batch_data: dict[str, Any] = {
        "company_id": company_id,
        "status": "completed",
    }
    batch_data.update(overrides)
    batch = GatheringBatch(**batch_data)
    session.add(batch)
    await session.commit()
    await session.refresh(batch)
    return batch


async def create_test_fact(
    session: AsyncSession,
    batch_id: str,
    company_id: str,
    **overrides: Any,
) -> Fact:
    fact_data: dict[str, Any] = {
        "batch_id": batch_id,
        "company_id": company_id,
        "fact_type": "test_fact",
        "value": 1000000.0,
        "confidence": 0.85,
    }
    fact_data.update(overrides)
    fact = Fact(**fact_data)
    session.add(fact)
    await session.commit()
    await session.refresh(fact)
    return fact


async def create_test_fact_source(
    session: AsyncSession,
    fact_id: str,
    **overrides: Any,
) -> FactSource:
    source_data: dict[str, Any] = {
        "fact_id": fact_id,
        "source_type": "test",
        "url": "https://example.com/test",
    }
    source_data.update(overrides)
    source = FactSource(**source_data)
    session.add(source)
    await session.commit()
    await session.refresh(source)
    return source


__all__ = [
    "CompanyFactory",
    "CompanyFactoryHighGrowth",
    "CompanyFactoryDistressed",
    "FinancialMetricFactory",
    "make_financial_metric",
    "make_company",
    "make_phoenix_company",
    "make_lead_company",
    "create_test_company",
    "create_test_batch",
    "create_test_fact",
    "create_test_fact_source",
]
