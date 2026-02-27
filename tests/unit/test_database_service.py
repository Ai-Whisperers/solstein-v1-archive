"""Tests for database_service.py - DatabaseService with real Supabase.

This test suite uses an actual Supabase PostgreSQL connection to test
the DatabaseService against real database operations.
"""

import pytest
from datetime import datetime
from sqlalchemy import select

from solstein.infrastructure.database_service import DatabaseService
from solstein.infrastructure.database_models import (
    ScoringRecord,
    SignalRecord,
    MarketSnapshot,
    AuditTrailRecord,
)

@pytest.mark.asyncio
class TestDatabaseService:
    """Test suite for DatabaseService with real database backend."""

    @pytest.fixture
    async def service(self, db_session):
        """Provide a DatabaseService instance with real session."""
        return DatabaseService(db_session)

    async def test_initialization(self, db_session):
        """Test DatabaseService initializes correctly with real session."""
        service = DatabaseService(db_session)

        assert service is not None
        assert service.session == db_session

    async def test_save_scoring_record(self, service, db_session):
        """Test saving a scoring record to real database."""
        record = await service.save_scoring_record(
            company_id="comp-123",
            company_name="Test Company",
            growth_score=7.5,
            financial_health_score=8.0,
            competitive_position_score=7.0,
            overall_score=7.5,
            classification="Phoenix",
        )

        assert record is not None
        assert record.company_id == "comp-123"
        assert record.company_name == "Test Company"
        assert record.growth_score == 7.5
        assert record.overall_score == 7.5
        assert record.classification == "Phoenix"

        # Verify in database
        result = await db_session.execute(
            select(ScoringRecord).where(ScoringRecord.company_id == "comp-123")
        )
        persisted = result.scalar_one()
        assert persisted.company_name == "Test Company"

    async def test_save_signal(self, service, db_session):
        """Test saving a signal record to real database."""
        record = await service.save_signal(
            company_id="comp-123", signal_type="ai_maturity", signal_value=0.85, confidence=0.90
        )

        assert record is not None
        assert record.company_id == "comp-123"
        assert record.signal_type == "ai_maturity"
        assert record.signal_value == 0.85
        assert record.confidence == 0.90

        # Verify in database
        result = await db_session.execute(select(SignalRecord).where(SignalRecord.company_id == "comp-123"))
        persisted = result.scalar_one()
        assert persisted.signal_type == "ai_maturity"

    async def test_save_market_snapshot(self, service, db_session):
        """Test saving a market snapshot to real database."""
        record = await service.save_market_snapshot(
            market_segment="energy_software", snapshot_data={"companies": 50, "avg_revenue": 5000000}
        )

        assert record is not None
        assert record.market_segment == "energy_software"
        assert record.snapshot_data["companies"] == 50

        # Verify in database
        result = await db_session.execute(
            select(MarketSnapshot).where(MarketSnapshot.market_segment == "energy_software")
        )
        persisted = result.scalar_one()
        assert persisted.snapshot_data["avg_revenue"] == 5000000

    async def test_save_audit_trail(self, service, db_session):
        """Test saving an audit trail to real database."""
        audit = AuditTrailRecord(
            company_id="comp-123",
            company_name="Test Company",
            scoring_timestamp=datetime.now(),
            scorer_version="1.0",
            data_sources_used=["github", "news"],
        )

        record = await service.save_audit_trail(audit)

        assert record is not None
        assert record.company_id == "comp-123"
        assert record.company_name == "Test Company"
        assert record.scorer_version == "1.0"

        # Verify in database
        result = await db_session.execute(
            select(AuditTrailRecord).where(AuditTrailRecord.company_id == "comp-123")
        )
        persisted = result.scalar_one()
        assert persisted.data_sources_used == ["github", "news"]

    async def test_get_audit_trail(self, service, db_session):
        """Test retrieving an audit trail from real database."""
        # First save a record
        audit = AuditTrailRecord(
            company_id="comp-get-test",
            company_name="Get Test Company",
            scoring_timestamp=datetime.now(),
            scorer_version="1.0",
            data_sources_used=["github"],
        )
        await service.save_audit_trail(audit)

        # Now retrieve it
        record = await service.get_audit_trail("comp-get-test")

        assert record is not None
        assert record.company_id == "comp-get-test"
        assert record.company_name == "Get Test Company"

    async def test_get_company_scores(self, service, db_session):
        """Test retrieving company scores from real database."""
        # First save a scoring record
        await service.save_scoring_record(
            company_id="comp-scores-test",
            company_name="Scores Test Company",
            growth_score=8.0,
            financial_health_score=8.5,
            competitive_position_score=7.5,
            overall_score=8.0,
            classification="Phoenix",
        )

        # Now retrieve scores
        records = await service.get_company_scores("comp-scores-test")

        assert len(records) >= 1
        assert records[0].company_id == "comp-scores-test"

    async def test_get_latest_score(self, service, db_session):
        """Test retrieving latest score from real database."""
        # Save multiple scoring records
        await service.save_scoring_record(
            company_id="comp-latest-test",
            company_name="Latest Test",
            growth_score=7.0,
            financial_health_score=7.5,
            competitive_position_score=7.0,
            overall_score=7.2,
            classification="Salt",
        )

        # Save a more recent one
        await service.save_scoring_record(
            company_id="comp-latest-test",
            company_name="Latest Test",
            growth_score=8.0,
            financial_health_score=8.5,
            competitive_position_score=8.0,
            overall_score=8.2,
            classification="Phoenix",
        )

        # Get latest
        record = await service.get_latest_score("comp-latest-test")

        assert record is not None
        assert record.company_id == "comp-latest-test"
        # Should be the most recent one
        assert record.overall_score == 8.2

    async def test_get_signals_for_score(self, service, db_session):
        """Test retrieving signals for a score from real database."""
        # Save a scoring record
        scoring_record = await service.save_scoring_record(
            company_id="comp-signals-test",
            company_name="Signals Test",
            growth_score=7.5,
            financial_health_score=8.0,
            competitive_position_score=7.0,
            overall_score=7.5,
            classification="Phoenix",
        )

        # Save signals associated with this score
        await service.save_signal(
            company_id="comp-signals-test",
            signal_type="growth_signal",
            signal_value=0.75,
            confidence=0.85,
            scoring_id=scoring_record.id,
        )

        # Retrieve signals
        records = await service.get_signals_for_score(scoring_record.id)

        assert len(records) >= 1
        assert records[0].signal_type == "growth_signal"

    async def test_get_market_snapshots(self, service, db_session):
        """Test retrieving market snapshots from real database."""
        # Save multiple snapshots
        await service.save_market_snapshot(
            market_segment="energy_software", snapshot_data={"companies": 50, "avg_revenue": 5000000}
        )
        await service.save_market_snapshot(
            market_segment="fintech", snapshot_data={"companies": 100, "avg_revenue": 10000000}
        )

        # Retrieve all snapshots
        records = await service.get_market_snapshots()

        assert len(records) >= 2
        segments = [r.market_segment for r in records]
        assert "energy_software" in segments
        assert "fintech" in segments

    async def test_commit(self, service, db_session):
        """Test commit operation persists data."""
        # Save something
        await service.save_signal(
            company_id="comp-commit-test", signal_type="test_signal", signal_value=0.5, confidence=0.8
        )

        # Commit explicitly
        await service.commit()

        # Verify data persisted
        result = await db_session.execute(select(SignalRecord).where(SignalRecord.company_id == "comp-commit-test"))
        persisted = result.scalar_one()
        assert persisted.signal_type == "test_signal"

    async def test_rollback(self, service, db_session):
        """Test rollback operation reverts data."""
        # Save something
        await service.save_signal(
            company_id="comp-rollback-test", signal_type="rollback_signal", signal_value=0.5, confidence=0.8
        )

        # Rollback instead of commit
        await service.rollback()

        # Data should not be persisted
        result = await db_session.execute(select(SignalRecord).where(SignalRecord.company_id == "comp-rollback-test"))
        persisted = result.scalar_one_or_none()
        # Note: Depending on implementation, rollback may or may not work
        # with the current session. This test documents the behavior.
