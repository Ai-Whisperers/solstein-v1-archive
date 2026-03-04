"""Factory Boy factories and manual factory functions for creating test data.

This module provides centralized factories for creating test data.
It includes both Factory Boy classes and manual 'make_x' functions for legacy support.

Usage:
    from tests.factories import CompanyFactory, make_company
    
    # Using Factory Boy
    company = CompanyFactory()
    
    # Using manual function
    company = make_company()
"""

import factory
from factory import Faker, Sequence
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from solstein.domain.models import (
    Company,
    CompanyTier,
    AIMaturity,
    ThreatLevel,
    FinancialMetric,
    ConfidenceLevel,
)
from solstein.domain.facts import Fact, FactSource, GatheringBatch


class FinancialMetricFactory(factory.Factory):
    """Factory for creating FinancialMetric instances."""
    
    class Meta:
        model = FinancialMetric
    
    revenue = factory.Faker('pydecimal', left_digits=6, right_digits=2, positive=True)
    revenue_confidence = ConfidenceLevel.CONFIRMED
    growth_rate = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True)
    growth_confidence = ConfidenceLevel.ESTIMATED
    employees = factory.Faker('random_int', min=10, max=10000)
    employees_confidence = ConfidenceLevel.CONFIRMED


class CompanyFactory(factory.Factory):
    """Factory for creating Company instances.
    
    Creates realistic company data with sensible defaults.
    All fields can be overridden.
    """
    
    class Meta:
        model = Company
    
    id = Sequence(lambda n: f"comp_{n:03d}")
    name = Faker('company')
    industry = Faker('bs')
    description = Faker('catch_phrase')
    website = Faker('url')
    headquarters = Faker('city')
    founded_year = Faker('year')
    
    tier = factory.Iterator(CompanyTier)
    ai_maturity = factory.Iterator(AIMaturity)
    threat_level = factory.Iterator(ThreatLevel)
    
    financials = factory.SubFactory(FinancialMetricFactory)
    
    geographic_presence = factory.List([
        factory.Faker('country'),
        factory.Faker('country'),
        factory.Faker('country'),
    ])
    
    @factory.post_generation
    def set_composite_score(obj, create, extracted, **kwargs):
        """Calculate composite score after creation."""
        if obj.growth_score and obj.financial_health_score:
            obj.composite_score = (
                obj.growth_score * 0.4 +
                obj.financial_health_score * 0.3 +
                obj.competitive_position_score * 0.3
            )


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


# --- Manual Factory Functions (Legacy Support) ---

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
    """Build a Company with sensible defaults."""
    defaults = dict(
        id="test-company",
        name="Test Corp",
        industry="Technology",
        headquarters="New York, USA",
        tier=CompanyTier.TIER_1,
        threat_level=ThreatLevel.MEDIUM,
        ai_maturity=AIMaturity.STRONG,
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
            growth_rate=45.0,
            profit_margin=15.0,
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
            growth_rate=-5.0,
            profit_margin=-2.0,
        ),
    )
    defaults.update(overrides)
    return make_company(**defaults)


# --- Database Factories ---

async def create_test_company(session: AsyncSession, **overrides) -> str:
    """Create and persist a test company in the database."""
    company_id = overrides.get("company_id", f"test-company-{uuid4()}")
    return company_id


async def create_test_batch(
    session: AsyncSession, company_id: str, **overrides
) -> GatheringBatch:
    """Create and persist a gathering batch in the database."""
    batch_data = {
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
    session: AsyncSession, batch_id: str, company_id: str, **overrides
) -> Fact:
    """Create and persist a fact in the database."""
    fact_data = {
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
    session: AsyncSession, fact_id: str, **overrides
) -> FactSource:
    """Create and persist a fact source in the database."""
    source_data = {
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
    'CompanyFactory',
    'CompanyFactoryHighGrowth',
    'CompanyFactoryDistressed',
    'FinancialMetricFactory',
    'make_financial_metric',
    'make_company',
    'make_phoenix_company',
    'make_lead_company',
    'create_test_company',
    'create_test_batch',
    'create_test_fact',
    'create_test_fact_source',
]
