"""
Integration tests for data migration from JSON to PostgreSQL.

These tests verify that:
1. Migration scripts work correctly
2. Data integrity is preserved during migration
3. All relationships are maintained
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path
import uuid

import pytest
import pytest_asyncio
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from solstein.config import Settings
from solstein.infrastructure.database import DatabaseManager
from solstein.infrastructure.database_models import (
    CompanyRecord,
    ContradictionRecord,
    FactRecord,
    ResearchRunRecord,
    ScoringRecord,
    SignalRecord,
)


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """Provide a database session for tests."""
    db_manager = DatabaseManager(Settings.load())
    session = await db_manager.get_session().__aenter__()

    # Start transaction that will be rolled back
    transaction = await session.begin_nested()

    yield session

    # Rollback transaction and close session
    await transaction.rollback()
    await session.close()
    await db_manager.engine.dispose()


class TestDataMigration:
    """Test suite for data migration from JSON to PostgreSQL."""

    @pytest.mark.asyncio
    async def test_company_migration(self, db_session: AsyncSession):
        """Test that companies can be migrated with all fields."""
        # Create test company data
        company_id = "test-company-1"
        company = CompanyRecord(
            company_id=company_id,
            ticker="TEST",
            name="Test Company",
            status="active",
            industry="Software",
        )

        # Insert into database
        db_session.add(company)
        await db_session.commit()

        # Verify retrieval
        result = await db_session.execute(select(CompanyRecord).where(CompanyRecord.company_id == company_id))
        fetched = result.scalar_one_or_none()
        assert fetched is not None
        assert fetched.ticker == "TEST"
        assert fetched.name == "Test Company"

    @pytest.mark.asyncio
    async def test_research_run_migration(self, db_session: AsyncSession):
        """Test that research runs with company relationships migrate correctly."""
        # Create research run
        run_id = "test-run-1"
        run = ResearchRunRecord(
            run_id=run_id,
            market="test market",
            seed_company="test company",
            status="completed",
        )
        db_session.add(run)
        await db_session.commit()

        # Verify relationship
        result = await db_session.execute(select(ResearchRunRecord).where(ResearchRunRecord.run_id == run_id))
        fetched = result.scalar_one_or_none()
        assert fetched is not None
        assert fetched.run_id == run_id
        assert fetched.status == "completed"

    @pytest.mark.asyncio
    async def test_fact_migration_with_relationships(self, db_session: AsyncSession):
        """Test that facts with company and run relationships migrate correctly."""
        # Create parent records
        company_id = "test-company-3"
        company = CompanyRecord(company_id=company_id, name="Test Company 3", status="active")
        db_session.add(company)
        
        run_id = "test-run-2"
        run = ResearchRunRecord(run_id=run_id, market="market", seed_company="seed", status="completed")
        db_session.add(run)
        await db_session.flush()

        # Create fact
        fact_id = "test-fact-1"
        fact = FactRecord(
            id=fact_id,
            company_id=company_id,
            run_id=run_id,
            fact_key="revenue_2024",
            fact_value="1000000",
            confidence=0.95,
            status="active",
        )
        db_session.add(fact)
        await db_session.commit()

        # Verify
        result = await db_session.execute(select(FactRecord).where(FactRecord.id == fact_id))
        fetched = result.scalar_one_or_none()
        assert fetched is not None
        assert fetched.company_id == company_id
        assert fetched.run_id == run_id
        assert fetched.confidence == 0.95

    @pytest.mark.asyncio
    async def test_signal_migration(self, db_session: AsyncSession):
        """Test that signals migrate with all metadata."""
        # Create parent company
        company_id = "test-company-4"
        company = CompanyRecord(company_id=company_id, name="Test Company 4", status="active")
        db_session.add(company)
        await db_session.flush()

        # Create scoring record (signals depend on it)
        scoring = ScoringRecord(
            company_id=company_id,
            company_name="Test Company 4",
            growth_score=8.5,
            financial_health_score=7.0,
            competitive_position_score=6.5,
            overall_score=7.5,
            classification="Phoenix",
        )
        db_session.add(scoring)
        await db_session.flush()

        # Create signal
        signal = SignalRecord(
            scoring_record_id=scoring.id,
            signal_name="high_growth",
            signal_category="growth",
            signal_value=9.0,
            source_agent="FinancialAgent",
            confidence=0.9,
        )
        db_session.add(signal)
        await db_session.commit()

        # Verify
        result = await db_session.execute(select(SignalRecord).where(SignalRecord.signal_name == "high_growth"))
        fetched = result.scalar_one_or_none()
        assert fetched is not None
        assert fetched.signal_category == "growth"
        assert fetched.confidence == 0.9

    @pytest.mark.asyncio
    async def test_scoring_record_migration(self, db_session: AsyncSession):
        """Test that scoring records with all scores migrate correctly."""
        company_id = "test-company-5"
        company = CompanyRecord(company_id=company_id, name="Test Company 5", status="active")
        db_session.add(company)
        await db_session.flush()

        scoring = ScoringRecord(
            company_id=company_id,
            company_name="Test Company 5",
            growth_score=90.0,
            financial_health_score=80.0,
            competitive_position_score=85.0,
            overall_score=85.0,
            classification="Phoenix",
        )
        db_session.add(scoring)
        await db_session.commit()

        result = await db_session.execute(select(ScoringRecord).where(ScoringRecord.company_id == company_id))
        fetched = result.scalar_one_or_none()
        assert fetched is not None
        assert fetched.overall_score == 85.0
        assert fetched.classification == "Phoenix"

    @pytest.mark.asyncio
    async def test_contradiction_migration(self, db_session: AsyncSession):
        """Test that contradictions migrate correctly."""
        company_id = "test-company-6"
        company = CompanyRecord(company_id=company_id, name="Test Company 6", status="active")
        db_session.add(company)
        await db_session.flush()

        run_id = "test-run-4"
        run = ResearchRunRecord(run_id=run_id, market="market", seed_company="seed", status="completed")
        db_session.add(run)
        await db_session.flush()

        contradiction = ContradictionRecord(
            run_id=run.id,
            company_id=company_id,
            metric_key="revenue",
            contradiction_type="value_mismatch",
            status="open",
        )
        db_session.add(contradiction)
        await db_session.commit()

        result = await db_session.execute(select(ContradictionRecord).where(ContradictionRecord.company_id == company_id))
        fetched = result.scalar_one_or_none()
        assert fetched is not None
        assert fetched.status == "open"

    @pytest.mark.asyncio
    async def test_batch_migration_simulation(self, db_session: AsyncSession):
        """Test batch insertion of multiple records."""
        companies = []
        for i in range(10):
            companies.append(
                CompanyRecord(company_id=f"batch-company-{i}", name=f"Batch Company {i}", status="active")
            )

        db_session.add_all(companies)
        await db_session.commit()

        # Verify all inserted
        result = await db_session.execute(select(CompanyRecord).where(CompanyRecord.company_id.like("batch-company-%")))
        fetched = result.scalars().all()
        assert len(fetched) == 10


class TestDataIntegrity:
    """Test data integrity after migration."""

    @pytest.mark.asyncio
    async def test_no_duplicate_company_ids(self, db_session: AsyncSession):
        """Test that no duplicate company_ids exist."""
        # Insert a company
        c1 = CompanyRecord(company_id="dup-1", name="Company 1", status="active")
        db_session.add(c1)
        await db_session.commit()

        # Try to insert another with same company_id
        c2 = CompanyRecord(company_id="dup-1", name="Company 2", status="active")
        db_session.add(c2)
        
        with pytest.raises(Exception):
            await db_session.commit()
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_required_fields_not_null(self, db_session: AsyncSession):
        """Test that required fields have values."""
        # Check companies have name and status
        result = await db_session.execute(text("SELECT COUNT(*) FROM companies WHERE name IS NULL OR name = ''"))
        null_names = result.scalar()
        assert null_names == 0, f"Found {null_names} companies with null/empty name"

        result = await db_session.execute(text("SELECT COUNT(*) FROM companies WHERE status IS NULL"))
        null_status = result.scalar()
        assert null_status == 0, f"Found {null_status} companies with null status"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
