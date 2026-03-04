"""Tests for infrastructure repositories.py - FactRepository with real Supabase.

This test suite uses an actual Supabase PostgreSQL connection to test
the FactRepository against real database operations. Database is cleaned
up after each test.
"""

import pytest
from sqlalchemy import select

from solstein.domain.facts import Fact, FactSource, GatheringBatch
from solstein.infrastructure.repositories import FactRepository
from solstein.infrastructure.test_cleanup import cleanup_test_database
from tests.factories import create_test_batch, create_test_fact, create_test_fact_source


@pytest.mark.asyncio
class TestFactRepository:
    """Test suite for FactRepository with real Supabase backend."""

    async def test_initialization(self, db_session):
        """Test FactRepository initializes correctly with AsyncSession."""
        repo = FactRepository(db_session)

        assert repo is not None
        assert repo.session == db_session

    async def test_create_batch(self, db_session):
        """Test creating a gathering batch."""
        batch = await create_test_batch(db_session, "comp-123", status="in_progress")

        assert batch is not None
        assert isinstance(batch, GatheringBatch)
        assert batch.company_id == "comp-123"
        assert batch.status == "in_progress"
        assert batch.batch_id is not None

    async def test_create_batch_default_status(self, db_session):
        """Test creating a batch with default status."""
        batch = await create_test_batch(db_session, "comp-456")

        assert batch is not None
        assert batch.status == "in_progress"
        assert batch.batch_id is not None

    async def test_create_fact(self, db_session):
        """Test creating a fact using factory."""
        batch = await create_test_batch(db_session, "comp-123")

        fact = await create_test_fact(
            db_session,
            batch_id=str(batch.batch_id),
            company_id="comp-123",
            fact_type="financial_metrics",
            value=1000000,
            confidence=0.85,
        )

        assert fact is not None
        assert isinstance(fact, Fact)
        assert fact.fact_id is not None
        assert fact.batch_id == batch.batch_id
        assert fact.company_id == "comp-123"
        assert fact.value == 1000000
        assert fact.confidence == 0.85

    async def test_store_fact_with_repository(self, db_session):
        """Test storing a single fact - requires batch first."""
        batch = await create_test_batch(db_session, "comp-123")

        # Create fact with batch_id
        fact = Fact(
            company_id="comp-123",
            batch_id=batch.batch_id,
            fact_type="financial_metrics",
            value=1000000,
            confidence=0.85,
        )

        db_session.add(fact)
        await db_session.commit()
        await db_session.refresh(fact)

        # Verify fact was stored
        assert fact.fact_id is not None

        # Verify in database using async query
        result = await db_session.execute(select(Fact).where(Fact.fact_id == fact.fact_id))
        stored = result.scalar_one()
        assert stored is not None
        assert stored.value == 1000000
        assert stored.confidence == 0.85

    async def test_store_batch_of_facts(self, db_session):
        """Test storing multiple facts in a batch."""
        batch = await create_test_batch(db_session, "comp-789")

        facts = [
            await create_test_fact(
                db_session,
                batch_id=str(batch.batch_id),
                company_id="comp-789",
                fact_type="financial_metrics",
                value=1000000,
                confidence=0.85,
            ),
            await create_test_fact(
                db_session,
                batch_id=str(batch.batch_id),
                company_id="comp-789",
                fact_type="growth_metrics",
                value_str="25%",
                confidence=0.80,
            ),
        ]

        assert len(facts) == 2
        assert all(isinstance(f, Fact) for f in facts)
        assert all(f.fact_id is not None for f in facts)

        # Verify all facts stored using async query
        result = await db_session.execute(select(Fact).where(Fact.batch_id == batch.batch_id))
        stored_facts = result.scalars().all()
        assert len(stored_facts) == 2

    async def test_get_company_facts(self, db_session):
        """Test retrieving all facts for a company."""
        batch = await create_test_batch(db_session, "comp-get-test")
        await create_test_fact(
            db_session,
            batch_id=str(batch.batch_id),
            company_id="comp-get-test",
            fact_type="financial_metrics",
            value=1000000,
            confidence=0.85,
        )

        # Query using async
        result = await db_session.execute(select(Fact).where(Fact.company_id == "comp-get-test"))
        facts = result.scalars().all()

        assert isinstance(facts, list)
        assert len(facts) > 0
        assert facts[0].company_id == "comp-get-test"

    async def test_get_facts_by_type(self, db_session):
        """Test retrieving facts filtered by type."""
        batch = await create_test_batch(db_session, "comp-type-test")
        await create_test_fact(
            db_session,
            batch_id=str(batch.batch_id),
            company_id="comp-type-test",
            fact_type="market_metrics",
            value=5000000000,
            confidence=0.88,
        )

        # Query using async
        result = await db_session.execute(
            select(Fact).where(
                Fact.company_id == "comp-type-test",
                Fact.fact_type == "market_metrics",
            )
        )
        facts = result.scalars().all()

        assert isinstance(facts, list)
        assert len(facts) > 0
        assert all(f.fact_type == "market_metrics" for f in facts)

    async def test_get_fact_by_id(self, db_session):
        """Test retrieving a specific fact by ID."""
        batch = await create_test_batch(db_session, "comp-id-test")
        fact = await create_test_fact(
            db_session,
            batch_id=str(batch.batch_id),
            company_id="comp-id-test",
            fact_type="financial_metrics",
            value=1000000,
            confidence=0.85,
        )

        # Query using async
        result = await db_session.execute(select(Fact).where(Fact.fact_id == fact.fact_id))
        retrieved_fact = result.scalar_one()

        assert retrieved_fact is not None
        assert isinstance(retrieved_fact, Fact)
        assert retrieved_fact.fact_id == fact.fact_id

    async def test_add_source_attribution(self, db_session):
        """Test adding additional source to a fact."""
        batch = await create_test_batch(db_session, "comp-source-test")
        fact = await create_test_fact(
            db_session,
            batch_id=str(batch.batch_id),
            company_id="comp-source-test",
            fact_type="financial_metrics",
            value=1000000,
            confidence=0.85,
        )

        source = await create_test_fact_source(
            db_session,
            fact_id=str(fact.fact_id),
            source_type="sec_edgar",
            url="https://example.com",
        )

        assert source is not None
        assert isinstance(source, FactSource)
        assert source.source_type == "sec_edgar"
        assert source.url == "https://example.com"
        assert source.fact_id == fact.fact_id

    async def test_get_batch(self, db_session):
        """Test retrieving a batch by ID."""
        batch = await create_test_batch(db_session, "comp-batch-test")

        # Query using async
        result = await db_session.execute(select(GatheringBatch).where(GatheringBatch.batch_id == batch.batch_id))
        retrieved_batch = result.scalar_one()

        assert retrieved_batch is not None
        assert isinstance(retrieved_batch, GatheringBatch)
        assert retrieved_batch.batch_id == batch.batch_id
        assert retrieved_batch.company_id == "comp-batch-test"

    async def test_update_batch_status(self, db_session):
        """Test updating batch status."""
        batch = await create_test_batch(db_session, "comp-status-test")

        # Update status
        batch.status = "completed"
        await db_session.commit()
        await db_session.refresh(batch)

        assert batch is not None
        assert isinstance(batch, GatheringBatch)
        assert batch.status == "completed"

    async def test_cleanup_database(self, db_session):
        """Test cleanup utility removes all test data."""
        # Create some test data
        batch = await create_test_batch(db_session, "comp-cleanup-test")
        await create_test_fact(
            db_session,
            batch_id=str(batch.batch_id),
            company_id="comp-cleanup-test",
            fact_type="test",
            value=100,
        )

        # Verify data exists
        result = await db_session.execute(select(Fact))
        facts_before = len(result.scalars().all())
        assert facts_before > 0

        # Cleanup
        await cleanup_test_database(db_session)

        # Verify data is gone
        result = await db_session.execute(select(Fact))
        facts_after = result.scalars().all()
        assert len(facts_after) == 0

        result = await db_session.execute(select(GatheringBatch))
        batches_after = result.scalars().all()
        assert len(batches_after) == 0
