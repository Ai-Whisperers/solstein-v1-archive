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


# ============================================================================
# DATABASE FACTORIES FOR REAL SUPABASE TESTING (Wave 2, Task 8)
# ============================================================================

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from solstein.domain.facts import Fact, FactSource, GatheringBatch


async def create_test_company(session: AsyncSession, **overrides) -> str:
    """Create and persist a test company in the database.

    Args:
        session: AsyncSession for database operations
        **overrides: Override default company values

    Returns:
        company_id of the created company

    Note:
        This function assumes the companies table already has test data.
        For now, it returns a test company ID. In future, it will create
        actual company records via a Company ORM model.
    """
    # For now, return a test company ID
    # TODO: Implement when Company ORM model is available
    company_id = overrides.get("company_id", f"test-company-{uuid4()}")
    return company_id


async def create_test_batch(
    session: AsyncSession, company_id: str, **overrides
) -> GatheringBatch:
    """Create and persist a gathering batch in the database.

    Args:
        session: AsyncSession for database operations
        company_id: ID of the company this batch belongs to
        **overrides: Override default batch values

    Returns:
        GatheringBatch ORM instance (persisted)

    Example:
        batch = await create_test_batch(session, "company-123")
        assert batch.batch_id is not None
    """
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
    """Create and persist a fact in the database.

    Args:
        session: AsyncSession for database operations
        batch_id: ID of the gathering batch this fact belongs to
        company_id: ID of the company this fact is about
        **overrides: Override default fact values

    Returns:
        Fact ORM instance (persisted)

    Example:
        fact = await create_test_fact(
            session,
            batch_id="batch-123",
            company_id="company-123",
            fact_type="annual_revenue",
            value=5000000.0,
            confidence=0.95
        )
        assert fact.fact_id is not None
    """
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
    """Create and persist a fact source in the database.

    Args:
        session: AsyncSession for database operations
        fact_id: ID of the fact this source belongs to
        **overrides: Override default source values

    Returns:
        FactSource ORM instance (persisted)

    Example:
        source = await create_test_fact_source(
            session,
            fact_id="fact-123",
            source_type="sec_filing",
            url="https://sec.gov/..."
        )
        assert source.source_id is not None
    """
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
    "make_financial_metric",
    "make_company",
    "make_phoenix_company",
    "make_lead_company",
    "create_test_company",
    "create_test_batch",
    "create_test_fact",
    "create_test_fact_source",
]
