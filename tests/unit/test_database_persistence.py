"""Tests for database persistence layer.

Tests verify that scoring records, signals, and market snapshots
are correctly stored and retrieved from PostgreSQL.
"""


import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from solstein.infrastructure.database import Base
from solstein.infrastructure.database_service import DatabaseService


@pytest_asyncio.fixture
async def test_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    SessionLocal = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with SessionLocal() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def db_service(test_db):
    """Create a DatabaseService with test database."""
    return DatabaseService(test_db)


class TestScoringRecordPersistence:
    """Test suite for scoring record persistence."""

    @pytest.mark.asyncio
    async def test_save_and_retrieve_scoring_record(self, db_service):
        """Verify that a scoring record can be saved and retrieved."""
        record = await db_service.save_scoring_record(
            company_id="tech-corp-001",
            company_name="TechCorp Inc",
            growth_score=8.5,
            financial_health_score=7.2,
            competitive_position_score=8.1,
            overall_score=7.9,
            classification="Phoenix",
        )
        await db_service.commit()

        assert record.id is not None
        assert record.company_id == "tech-corp-001"
        assert record.company_name == "TechCorp Inc"
        assert record.overall_score == 7.9
        assert record.classification == "Phoenix"

    @pytest.mark.asyncio
    async def test_save_record_with_data_sources(self, db_service):
        """Verify that data sources are stored with the record."""
        data_sources = {
            "github": {"repos": 5, "stars": 1000},
            "web_search": {"mentions": 150},
        }

        record = await db_service.save_scoring_record(
            company_id="startup-002",
            company_name="Startup Labs",
            growth_score=7.5,
            financial_health_score=6.0,
            competitive_position_score=7.0,
            overall_score=6.8,
            classification="Salt",
            data_sources_used=data_sources,
        )
        await db_service.commit()

        assert record.data_sources_used == data_sources

    @pytest.mark.asyncio
    async def test_get_company_scores_returns_sorted_history(self, db_service):
        """Verify that company scores are returned most-recent first."""
        company_id = "acme-corp"

        await db_service.save_scoring_record(
            company_id=company_id,
            company_name="ACME Corp",
            growth_score=5.0,
            financial_health_score=5.0,
            competitive_position_score=5.0,
            overall_score=5.0,
            classification="Salt",
        )
        await db_service.commit()

        await db_service.save_scoring_record(
            company_id=company_id,
            company_name="ACME Corp",
            growth_score=6.0,
            financial_health_score=6.0,
            competitive_position_score=6.0,
            overall_score=6.0,
            classification="Salt",
        )
        await db_service.commit()

        scores = await db_service.get_company_scores(company_id)

        assert len(scores) == 2
        assert scores[0].overall_score == 6.0
        assert scores[1].overall_score == 5.0

    @pytest.mark.asyncio
    async def test_get_latest_score(self, db_service):
        """Verify that only the most recent score is returned."""
        company_id = "beta-inc"

        await db_service.save_scoring_record(
            company_id=company_id,
            company_name="Beta Inc",
            growth_score=3.0,
            financial_health_score=3.0,
            competitive_position_score=3.0,
            overall_score=3.0,
            classification="Lead",
        )
        await db_service.commit()

        await db_service.save_scoring_record(
            company_id=company_id,
            company_name="Beta Inc",
            growth_score=4.5,
            financial_health_score=4.5,
            competitive_position_score=4.5,
            overall_score=4.5,
            classification="Salt",
        )
        await db_service.commit()

        latest = await db_service.get_latest_score(company_id)

        assert latest is not None
        assert latest.overall_score == 4.5
        assert latest.classification == "Salt"

    @pytest.mark.asyncio
    async def test_get_company_scores_with_limit(self, db_service):
        """Verify that limit parameter restricts results."""
        company_id = "gamma-systems"

        for i in range(5):
            await db_service.save_scoring_record(
                company_id=company_id,
                company_name="Gamma Systems",
                growth_score=float(i),
                financial_health_score=float(i),
                competitive_position_score=float(i),
                overall_score=float(i),
                classification="Salt",
            )
            await db_service.commit()

        scores = await db_service.get_company_scores(company_id, limit=3)

        assert len(scores) == 3


class TestSignalPersistence:
    """Test suite for signal record persistence."""

    @pytest.mark.asyncio
    async def test_save_and_retrieve_signals(self, db_service):
        """Verify that signals can be saved and linked to scores."""
        record = await db_service.save_scoring_record(
            company_id="signal-test-001",
            company_name="Signal Test Co",
            growth_score=7.0,
            financial_health_score=7.0,
            competitive_position_score=7.0,
            overall_score=7.0,
            classification="Phoenix",
        )
        await db_service.commit()

        signal = await db_service.save_signal(
            scoring_record_id=record.id,
            signal_name="Revenue Growth",
            signal_category="financial",
            source_agent="GitHub",
            confidence=0.95,
            signal_value=150.0,
            signal_text="150% YoY revenue growth",
            evidence={"source": "Company blog", "date": "2024-Q4"},
        )
        await db_service.commit()

        assert signal.signal_name == "Revenue Growth"
        assert signal.source_agent == "GitHub"
        assert signal.confidence == 0.95

    @pytest.mark.asyncio
    async def test_get_signals_for_score(self, db_service):
        """Verify that all signals for a score are retrieved."""
        record = await db_service.save_scoring_record(
            company_id="multi-signal-test",
            company_name="Multi Signal Co",
            growth_score=7.5,
            financial_health_score=7.5,
            competitive_position_score=7.5,
            overall_score=7.5,
            classification="Phoenix",
        )
        await db_service.commit()

        for i in range(3):
            await db_service.save_signal(
                scoring_record_id=record.id,
                signal_name=f"Signal {i}",
                signal_category="test",
                source_agent="TestAgent",
                confidence=0.9,
            )
            await db_service.commit()

        signals = await db_service.get_signals_for_score(record.id)

        assert len(signals) == 3
        assert all(s.scoring_record_id == record.id for s in signals)

    @pytest.mark.asyncio
    async def test_signal_confidence_scores(self, db_service):
        """Verify that confidence scores are preserved correctly."""
        record = await db_service.save_scoring_record(
            company_id="confidence-test",
            company_name="Confidence Test Inc",
            growth_score=6.0,
            financial_health_score=6.0,
            competitive_position_score=6.0,
            overall_score=6.0,
            classification="Salt",
        )
        await db_service.commit()

        confidences = [0.5, 0.75, 0.95, 1.0]
        for i, conf in enumerate(confidences):
            await db_service.save_signal(
                scoring_record_id=record.id,
                signal_name=f"Signal {i}",
                signal_category="test",
                source_agent="TestAgent",
                confidence=conf,
            )
            await db_service.commit()

        signals = await db_service.get_signals_for_score(record.id)
        retrieved_confidences = [s.confidence for s in signals]

        assert set(retrieved_confidences) == set(confidences)


class TestMarketSnapshotPersistence:
    """Test suite for market snapshot persistence."""

    @pytest.mark.asyncio
    async def test_save_and_retrieve_market_snapshot(self, db_service):
        """Verify that market snapshots can be saved and retrieved."""
        snapshot = await db_service.save_market_snapshot(
            total_companies_scored=100,
            average_growth_score=6.5,
            average_financial_score=6.0,
            average_competitive_score=6.3,
            phoenix_count=25,
            salt_count=50,
            lead_count=25,
        )
        await db_service.commit()

        assert snapshot.id is not None
        assert snapshot.total_companies_scored == 100
        assert snapshot.phoenix_count == 25

    @pytest.mark.asyncio
    async def test_market_snapshot_with_metadata(self, db_service):
        """Verify that metadata is stored with snapshots."""
        metadata = {
            "market": "European Energy Software",
            "analyst": "Analyst A",
            "notes": "Quarterly refresh",
        }

        snapshot = await db_service.save_market_snapshot(
            total_companies_scored=50,
            average_growth_score=7.0,
            average_financial_score=7.0,
            average_competitive_score=7.0,
            phoenix_count=15,
            salt_count=25,
            lead_count=10,
            market_metadata=metadata,
        )
        await db_service.commit()

        assert snapshot.market_metadata == metadata

    @pytest.mark.asyncio
    async def test_get_market_snapshots_ordered_by_date(self, db_service):
        """Verify that snapshots are returned most-recent first."""
        for i in range(3):
            await db_service.save_market_snapshot(
                total_companies_scored=100 + i,
                average_growth_score=6.0 + float(i) * 0.5,
                average_financial_score=6.0,
                average_competitive_score=6.0,
                phoenix_count=20,
                salt_count=50,
                lead_count=30,
            )
            await db_service.commit()

        snapshots = await db_service.get_market_snapshots()

        assert len(snapshots) == 3
        assert snapshots[0].total_companies_scored == 102
        assert snapshots[2].total_companies_scored == 100


class TestTransactionManagement:
    """Test suite for transaction handling."""

    @pytest.mark.asyncio
    async def test_commit_persists_data(self, db_service):
        """Verify that commit persists data to database."""
        record = await db_service.save_scoring_record(
            company_id="commit-test",
            company_name="Commit Test Corp",
            growth_score=5.0,
            financial_health_score=5.0,
            competitive_position_score=5.0,
            overall_score=5.0,
            classification="Salt",
        )
        await db_service.commit()

        retrieved = await db_service.get_latest_score("commit-test")
        assert retrieved is not None
        assert retrieved.company_name == "Commit Test Corp"

    @pytest.mark.asyncio
    async def test_rollback_discards_changes(self, db_service):
        """Verify that rollback discards uncommitted changes."""
        await db_service.save_scoring_record(
            company_id="rollback-test",
            company_name="Rollback Test",
            growth_score=5.0,
            financial_health_score=5.0,
            competitive_position_score=5.0,
            overall_score=5.0,
            classification="Salt",
        )
        await db_service.rollback()

        retrieved = await db_service.get_latest_score("rollback-test")
        assert retrieved is None


class TestDataIntegrity:
    """Test suite for data integrity and constraints."""

    @pytest.mark.asyncio
    async def test_classification_values_preserved(self, db_service):
        """Verify that classification values are correctly stored and retrieved."""
        classifications = ["Phoenix", "Salt", "Lead"]

        for i, classification in enumerate(classifications):
            await db_service.save_scoring_record(
                company_id=f"class-test-{i}",
                company_name=f"Classification Test {i}",
                growth_score=5.0,
                financial_health_score=5.0,
                competitive_position_score=5.0,
                overall_score=5.0,
                classification=classification,
            )
            await db_service.commit()

        for i, expected_class in enumerate(classifications):
            record = await db_service.get_latest_score(f"class-test-{i}")
            assert record.classification == expected_class

    @pytest.mark.asyncio
    async def test_score_boundaries(self, db_service):
        """Verify that score boundaries are handled correctly."""
        boundary_scores = [0.0, 5.0, 10.0]

        for i, score in enumerate(boundary_scores):
            await db_service.save_scoring_record(
                company_id=f"boundary-{i}",
                company_name=f"Boundary Test {i}",
                growth_score=score,
                financial_health_score=score,
                competitive_position_score=score,
                overall_score=score,
                classification="Salt",
            )
            await db_service.commit()

        for i, expected_score in enumerate(boundary_scores):
            record = await db_service.get_latest_score(f"boundary-{i}")
            assert record.overall_score == expected_score
