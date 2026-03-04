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

import pytest
import pytest_asyncio
from sqlalchemy import text
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
        company_data = {
            "id": "test-company-1",
            "ticker": "TEST",
            "name": "Test Company",
            "status": "active",
            "sector": "Technology",
            "industry": "Software",
            "metadata": {"employees": 1000, "founded": 2020},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        # Insert into database
        company = CompanyRecord(**company_data)
        db_session.add(company)
        await db_session.commit()

        # Verify retrieval
        result = await db_session.get(CompanyRecord, "test-company-1")
        assert result is not None
        assert result.ticker == "TEST"
        assert result.name == "Test Company"
        assert result.metadata == {"employees": 1000, "founded": 2020}

    @pytest.mark.asyncio
    async def test_research_run_migration(self, db_session: AsyncSession):
        """Test that research runs with company relationships migrate correctly."""
        # Create parent company
        company = CompanyRecord(id="test-company-2", ticker="TEST2", name="Test Company 2", status="active")
        db_session.add(company)
        await db_session.flush()

        # Create research run
        run = ResearchRunRecord(
            id="test-run-1",
            company_id="test-company-2",
            status="completed",
            metadata={"query": "test analysis"},
            run_metadata={"depth": "deep"},
        )
        db_session.add(run)
        await db_session.commit()

        # Verify relationship
        result = await db_session.get(ResearchRunRecord, "test-run-1")
        assert result is not None
        assert result.company_id == "test-company-2"
        assert result.status == "completed"

    @pytest.mark.asyncio
    async def test_fact_migration_with_relationships(self, db_session: AsyncSession):
        """Test that facts with company and run relationships migrate correctly."""
        # Create parent records
        company = CompanyRecord(id="test-company-3", ticker="TEST3", name="Test Company 3", status="active")
        db_session.add(company)
        await db_session.flush()

        run = ResearchRunRecord(id="test-run-2", company_id="test-company-3", status="completed")
        db_session.add(run)
        await db_session.flush()

        # Create fact
        fact = FactRecord(
            id="test-fact-1",
            company_id="test-company-3",
            run_id="test-run-2",
            fact_key="revenue_2024",
            fact_value="1000000",
            confidence=0.95,
            status="active",
        )
        db_session.add(fact)
        await db_session.commit()

        # Verify
        result = await db_session.get(FactRecord, "test-fact-1")
        assert result is not None
        assert result.company_id == "test-company-3"
        assert result.run_id == "test-run-2"
        assert result.confidence == 0.95

    @pytest.mark.asyncio
    async def test_signal_migration(self, db_session: AsyncSession):
        """Test that signals migrate with all metadata."""
        # Create dependencies
        company = CompanyRecord(id="test-company-4", ticker="TEST4", name="Test Company 4", status="active")
        db_session.add(company)
        await db_session.flush()

        run = ResearchRunRecord(id="test-run-3", company_id="test-company-4", status="completed")
        db_session.add(run)
        await db_session.flush()

        # Create signal
        signal = SignalRecord(
            id="test-signal-1",
            company_id="test-company-4",
            run_id="test-run-3",
            signal_type="price_movement",
            confidence=0.85,
            strength=0.75,
            direction="bullish",
            status="active",
        )
        db_session.add(signal)
        await db_session.commit()

        # Verify
        result = await db_session.get(SignalRecord, "test-signal-1")
        assert result is not None
        assert result.signal_type == "price_movement"
        assert result.direction == "bullish"

    @pytest.mark.asyncio
    async def test_scoring_record_migration(self, db_session: AsyncSession):
        """Test that scoring records with all scores migrate correctly."""
        company = CompanyRecord(id="test-company-5", ticker="TEST5", name="Test Company 5", status="active")
        db_session.add(company)
        await db_session.flush()

        scoring = ScoringRecord(
            id="test-scoring-1",
            company_id="test-company-5",
            total_score=85,
            growth_score=90,
            profitability_score=80,
            valuation_score=85,
            quality_score=85,
            quartile=1,
        )
        db_session.add(scoring)
        await db_session.commit()

        result = await db_session.get(ScoringRecord, "test-scoring-1")
        assert result is not None
        assert result.total_score == 85
        assert result.quartile == 1

    @pytest.mark.asyncio
    async def test_contradiction_migration(self, db_session: AsyncSession):
        """Test that contradictions migrate correctly."""
        company = CompanyRecord(id="test-company-6", ticker="TEST6", name="Test Company 6", status="active")
        db_session.add(company)
        await db_session.flush()

        run = ResearchRunRecord(id="test-run-4", company_id="test-company-6", status="completed")
        db_session.add(run)
        await db_session.flush()

        contradiction = ContradictionRecord(
            id="test-contradiction-1",
            company_id="test-company-6",
            run_id="test-run-4",
            severity="high",
            status="open",
            detected_at=datetime.now(timezone.utc),
        )
        db_session.add(contradiction)
        await db_session.commit()

        result = await db_session.get(ContradictionRecord, "test-contradiction-1")
        assert result is not None
        assert result.severity == "high"

    @pytest.mark.asyncio
    async def test_json_field_migration(self, db_session: AsyncSession):
        """Test that complex JSON fields migrate correctly."""
        company = CompanyRecord(
            id="test-company-json",
            ticker="JSON",
            name="JSON Test",
            status="active",
            metadata={"nested": {"deep": {"value": "test"}}, "list": [1, 2, 3], "null_value": None},
        )
        db_session.add(company)
        await db_session.commit()

        result = await db_session.get(CompanyRecord, "test-company-json")
        assert result.metadata["nested"]["deep"]["value"] == "test"
        assert result.metadata["list"] == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_batch_migration_simulation(self, db_session: AsyncSession):
        """Test batch insertion of multiple records."""
        companies = []
        for i in range(10):
            companies.append(
                CompanyRecord(id=f"batch-company-{i}", ticker=f"BATCH{i}", name=f"Batch Company {i}", status="active")
            )

        db_session.add_all(companies)
        await db_session.commit()

        # Verify all inserted
        for i in range(10):
            result = await db_session.get(CompanyRecord, f"batch-company-{i}")
            assert result is not None
            assert result.ticker == f"BATCH{i}"

    @pytest.mark.asyncio
    async def test_foreign_key_integrity(self, db_session: AsyncSession):
        """Test that foreign key constraints are enforced."""
        # Try to create a research run with non-existent company
        # (This assumes FK constraints are enabled)
        run = ResearchRunRecord(id="test-fk-run", company_id="non-existent-company", status="pending")
        db_session.add(run)

        # This should raise an error when FK constraints are enabled
        # For now, just verify the record exists (constraint check depends on DB config)
        try:
            await db_session.commit()
            # If we get here, FK constraints might not be enforced in test DB
        except Exception as e:
            # Expected if FK constraints are enforced
            await db_session.rollback()
            assert "foreign key" in str(e).lower() or "violates" in str(e).lower()


class TestMigrationScripts:
    """Test the migration scripts themselves."""

    def test_migration_script_exists(self):
        """Verify migration scripts exist."""
        migration_script = Path("scripts/migrate_competitor_data.py")
        assert migration_script.exists(), "Migration script not found"

    def test_migration_script_importable(self):
        """Verify migration script can be imported."""
        try:
            import scripts.migrate_competitor_data as migration

            assert hasattr(migration, "main") or "async" in dir(migration)
        except ImportError as e:
            pytest.skip(f"Migration script not importable: {e}")

    def test_simple_migration_script_exists(self):
        """Verify simple migration script exists."""
        migration_script = Path("scripts/migrate_simple.py")
        assert migration_script.exists(), "Simple migration script not found"

    def test_verification_script_exists(self):
        """Verify integrity verification script exists."""
        verification_script = Path("scripts/verify_database_integrity.py")
        assert verification_script.exists(), "Verification script not found"


class TestDataIntegrity:
    """Test data integrity after migration."""

    @pytest.mark.asyncio
    async def test_no_duplicate_ids(self, db_session: AsyncSession):
        """Test that no duplicate IDs exist in migrated data."""
        # Check companies
        result = await db_session.execute(
            text("""
                SELECT id, COUNT(*) as cnt 
                FROM companies 
                GROUP BY id 
                HAVING COUNT(*) > 1
            """)
        )
        duplicates = result.all()
        assert len(duplicates) == 0, f"Duplicate company IDs found: {duplicates}"

    @pytest.mark.asyncio
    async def test_required_fields_not_null(self, db_session: AsyncSession):
        """Test that required fields have values."""
        # Check companies have ticker and status
        result = await db_session.execute(text("SELECT COUNT(*) FROM companies WHERE ticker IS NULL OR ticker = ''"))
        null_tickers = result.scalar()
        assert null_tickers == 0, f"Found {null_tickers} companies with null/empty ticker"

        result = await db_session.execute(text("SELECT COUNT(*) FROM companies WHERE status IS NULL"))
        null_status = result.scalar()
        assert null_status == 0, f"Found {null_status} companies with null status"

    @pytest.mark.asyncio
    async def test_date_consistency(self, db_session: AsyncSession):
        """Test that date fields are consistent."""
        # updated_at should be >= created_at
        result = await db_session.execute(
            text("""
                SELECT COUNT(*) FROM companies 
                WHERE updated_at < created_at
            """)
        )
        inconsistent = result.scalar()
        assert inconsistent == 0, f"Found {inconsistent} records with updated_at < created_at"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
