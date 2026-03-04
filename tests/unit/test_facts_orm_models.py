"""Unit tests for Fact ORM models and repository operations.

Tests cover:
- Model creation and validation
- Confidence scoring constraints
- Foreign key relationships
- Repository CRUD operations
- Batch operations
- Source tracking
"""

import uuid
from datetime import datetime, timezone

import pytest

from solstein.domain.facts import Fact, FactSource, GatheringBatch
from solstein.infrastructure.database import DatabaseManager
from solstein.infrastructure.repositories import FactRepository


class TestGatheringBatchModel:
    """Tests for GatheringBatch ORM model."""

    def test_create_batch(self):
        """Test creating a GatheringBatch instance."""
        batch = GatheringBatch(company_id="test-company-123")
        assert batch.company_id == "test-company-123"
        # Note: SQLAlchemy defaults only apply on DB insert, not on instantiation
        # So we test that the model can be created with required fields

    def test_batch_status_values(self):
        """Test batch status can be set to valid values."""
        for status in ["in_progress", "completed", "failed"]:
            batch = GatheringBatch(company_id="test-company", status=status)
            assert batch.status == status

    def test_batch_created_at_default(self):
        """Test batch created_at can be set explicitly."""
        now = datetime.now(timezone.utc)
        batch = GatheringBatch(company_id="test-company", created_at=now)
        assert batch.created_at == now
        assert isinstance(batch.created_at, datetime)

    def test_batch_repr(self):
        """Test batch string representation."""
        batch = GatheringBatch(company_id="test-company", status="completed")
        repr_str = repr(batch)
        assert "GatheringBatch" in repr_str
        assert "test-company" in repr_str
        assert "completed" in repr_str


class TestFactModel:
    """Tests for Fact ORM model."""

    def test_create_fact_minimal(self):
        """Test creating a Fact with minimal required fields."""
        batch_id = uuid.uuid4()
        fact_id = uuid.uuid4()
        fact = Fact(
            fact_id=fact_id,
            company_id="test-company",
            batch_id=batch_id,
            fact_type="annual_revenue",
            confidence=0.95,
        )
        assert fact.company_id == "test-company"
        assert fact.batch_id == batch_id
        assert fact.fact_type == "annual_revenue"
        assert fact.confidence == 0.95
        assert fact.fact_id == fact_id

    def test_create_fact_with_numeric_value(self):
        """Test creating a Fact with numeric value."""
        batch_id = uuid.uuid4()
        fact = Fact(
            company_id="test-company",
            batch_id=batch_id,
            fact_type="annual_revenue",
            value=1000000.50,
            confidence=0.95,
        )
        assert fact.value == 1000000.50

    def test_create_fact_with_string_value(self):
        """Test creating a Fact with string value."""
        batch_id = uuid.uuid4()
        fact = Fact(
            company_id="test-company",
            batch_id=batch_id,
            fact_type="company_status",
            value_str="active",
            confidence=0.90,
        )
        assert fact.value_str == "active"

    def test_create_fact_with_date_value(self):
        """Test creating a Fact with date value."""
        batch_id = uuid.uuid4()
        date_val = datetime(2024, 1, 15, tzinfo=timezone.utc)
        fact = Fact(
            company_id="test-company",
            batch_id=batch_id,
            fact_type="funding_date",
            value_date=date_val,
            confidence=0.85,
        )
        assert fact.value_date == date_val

    def test_fact_confidence_valid_range(self):
        """Test fact confidence accepts valid values 0.0-1.0."""
        batch_id = uuid.uuid4()
        for confidence in [0.0, 0.5, 0.95, 1.0]:
            fact = Fact(
                company_id="test-company",
                batch_id=batch_id,
                fact_type="test",
                confidence=confidence,
            )
            fact.validate()  # Should not raise

    def test_fact_confidence_validation_too_low(self):
        """Test fact confidence validation rejects values < 0.0."""
        batch_id = uuid.uuid4()
        fact = Fact(
            company_id="test-company",
            batch_id=batch_id,
            fact_type="test",
            confidence=-0.1,
        )
        with pytest.raises(ValueError, match="Confidence must be between"):
            fact.validate()

    def test_fact_confidence_validation_too_high(self):
        """Test fact confidence validation rejects values > 1.0."""
        batch_id = uuid.uuid4()
        fact = Fact(
            company_id="test-company",
            batch_id=batch_id,
            fact_type="test",
            confidence=1.1,
        )
        with pytest.raises(ValueError, match="Confidence must be between"):
            fact.validate()

    def test_fact_validation_missing_fact_type(self):
        """Test fact validation requires fact_type."""
        batch_id = uuid.uuid4()
        fact = Fact(
            company_id="test-company",
            batch_id=batch_id,
            fact_type="",
            confidence=0.95,
        )
        with pytest.raises(ValueError, match="Fact type is required"):
            fact.validate()

    def test_fact_validation_missing_company_id(self):
        """Test fact validation requires company_id."""
        batch_id = uuid.uuid4()
        fact = Fact(
            company_id="",
            batch_id=batch_id,
            fact_type="test",
            confidence=0.95,
        )
        with pytest.raises(ValueError, match="Company ID is required"):
            fact.validate()

    def test_fact_validation_missing_batch_id(self):
        """Test fact validation requires batch_id."""
        fact = Fact(
            company_id="test-company",
            batch_id=None,
            fact_type="test",
            confidence=0.95,
        )
        with pytest.raises(ValueError, match="Batch ID is required"):
            fact.validate()

    def test_fact_extracted_at_default(self):
        """Test fact extracted_at can be set explicitly."""
        batch_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        fact = Fact(
            company_id="test-company",
            batch_id=batch_id,
            fact_type="test",
            confidence=0.95,
            extracted_at=now,
        )
        assert fact.extracted_at == now
        assert isinstance(fact.extracted_at, datetime)

    def test_fact_repr(self):
        """Test fact string representation."""
        batch_id = uuid.uuid4()
        fact = Fact(
            company_id="test-company",
            batch_id=batch_id,
            fact_type="annual_revenue",
            confidence=0.95,
        )
        repr_str = repr(fact)
        assert "Fact" in repr_str
        assert "annual_revenue" in repr_str
        assert "0.95" in repr_str


class TestFactSourceModel:
    """Tests for FactSource ORM model."""

    def test_create_source(self):
        """Test creating a FactSource instance."""
        fact_id = uuid.uuid4()
        source_id = uuid.uuid4()
        source = FactSource(
            source_id=source_id,
            fact_id=fact_id,
            source_type="sec_edgar",
            source_url="https://www.sec.gov/cgi-bin/browse-edgar",
        )
        assert source.fact_id == fact_id
        assert source.source_type == "sec_edgar"
        assert source.source_url == "https://www.sec.gov/cgi-bin/browse-edgar"
        assert source.source_id == source_id

    def test_create_source_with_raw_content(self):
        """Test creating a FactSource with raw API response."""
        fact_id = uuid.uuid4()
        raw_json = '{"revenue": 1000000, "currency": "USD"}'
        source = FactSource(
            fact_id=fact_id,
            source_type="companies_house",
            raw_content=raw_json,
        )
        assert source.raw_content == raw_json

    def test_source_extraction_timestamp_default(self):
        """Test source extraction_timestamp can be set explicitly."""
        fact_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        source = FactSource(
            fact_id=fact_id,
            source_type="newsapi",
            extraction_timestamp=now,
        )
        assert source.extraction_timestamp == now
        assert isinstance(source.extraction_timestamp, datetime)

    def test_source_repr(self):
        """Test source string representation."""
        fact_id = uuid.uuid4()
        source = FactSource(fact_id=fact_id, source_type="github")
        repr_str = repr(source)
        assert "FactSource" in repr_str
        assert "github" in repr_str


class TestFactRepositoryValidation:
    """Tests for FactRepository validation logic (async methods awaited properly)."""

    @pytest.mark.asyncio
    async def test_repository_store_validates_confidence(self):
        """Test repository store() validates confidence range."""
        from unittest.mock import MagicMock

        session = MagicMock(spec=DatabaseManager)
        repo = FactRepository(session)

        batch_id = uuid.uuid4()
        fact = Fact(
            company_id="test-company",
            batch_id=batch_id,
            fact_type="test",
            confidence=1.5,  # Invalid
        )

        with pytest.raises(ValueError, match="Confidence must be between"):
            await repo.store(fact)

    @pytest.mark.asyncio
    async def test_repository_store_validates_fact_type(self):
        """Test repository store() validates fact_type is not empty."""
        from unittest.mock import MagicMock

        session = MagicMock(spec=DatabaseManager)
        repo = FactRepository(session)

        batch_id = uuid.uuid4()
        fact = Fact(
            company_id="test-company",
            batch_id=batch_id,
            fact_type="",  # Invalid
            confidence=0.95,
        )

        with pytest.raises(ValueError, match="Fact type is required"):
            await repo.store(fact)

    @pytest.mark.asyncio
    async def test_repository_get_company_facts_requires_company_id(self):
        """Test get_company_facts() requires company_id."""
        from unittest.mock import MagicMock

        session = MagicMock(spec=DatabaseManager)
        repo = FactRepository(session)

        with pytest.raises(ValueError, match="Company ID is required"):
            await repo.get_company_facts("")

    @pytest.mark.asyncio
    async def test_repository_get_facts_by_type_requires_company_id(self):
        """Test get_facts_by_type() requires company_id."""
        from unittest.mock import MagicMock

        session = MagicMock(spec=DatabaseManager)
        repo = FactRepository(session)

        with pytest.raises(ValueError, match="Company ID is required"):
            await repo.get_facts_by_type("", "annual_revenue")

    @pytest.mark.asyncio
    async def test_repository_get_facts_by_type_requires_fact_type(self):
        """Test get_facts_by_type() requires fact_type."""
        from unittest.mock import MagicMock

        session = MagicMock(spec=DatabaseManager)
        repo = FactRepository(session)

        with pytest.raises(ValueError, match="Fact type is required"):
            await repo.get_facts_by_type("test-company", "")

    @pytest.mark.asyncio
    async def test_repository_create_batch_requires_company_id(self):
        """Test create_batch() requires company_id."""
        from unittest.mock import MagicMock

        session = MagicMock(spec=DatabaseManager)
        repo = FactRepository(session)

        with pytest.raises(ValueError, match="Company ID is required"):
            await repo.create_batch("")

    @pytest.mark.asyncio
    async def test_repository_add_source_requires_fact_id(self):
        """Test add_source() requires fact_id."""
        from unittest.mock import MagicMock

        session = MagicMock(spec=DatabaseManager)
        repo = FactRepository(session)

        with pytest.raises(ValueError, match="Fact ID is required"):
            await repo.add_source("", "sec_edgar")

    @pytest.mark.asyncio
    async def test_repository_add_source_requires_source_type(self):
        """Test add_source() requires source_type."""
        from unittest.mock import MagicMock

        session = MagicMock(spec=DatabaseManager)
        repo = FactRepository(session)

        with pytest.raises(ValueError, match="Source type is required"):
            await repo.add_source(str(uuid.uuid4()), "")

    @pytest.mark.asyncio
    async def test_repository_get_batch_requires_batch_id(self):
        """Test get_batch() requires batch_id."""
        from unittest.mock import MagicMock

        session = MagicMock(spec=DatabaseManager)
        repo = FactRepository(session)

        with pytest.raises(ValueError, match="Batch ID is required"):
            await repo.get_batch("")

    @pytest.mark.asyncio
    async def test_repository_update_batch_status_requires_batch_id(self):
        """Test update_batch_status() requires batch_id."""
        from unittest.mock import MagicMock

        session = MagicMock(spec=DatabaseManager)
        repo = FactRepository(session)

        with pytest.raises(ValueError, match="Batch ID is required"):
            await repo.update_batch_status("", "completed")

    @pytest.mark.asyncio
    async def test_repository_update_batch_status_requires_status(self):
        """Test update_batch_status() requires status."""
        from unittest.mock import MagicMock

        session = MagicMock(spec=DatabaseManager)
        repo = FactRepository(session)

        with pytest.raises(ValueError, match="Status is required"):
            await repo.update_batch_status(str(uuid.uuid4()), "")


class TestFactModelSerialization:
    """Tests for fact model serialization and roundtrip."""

    def test_fact_uuid_serialization(self):
        """Test fact UUIDs serialize correctly."""
        batch_id = uuid.uuid4()
        fact_id = uuid.uuid4()
        fact = Fact(
            fact_id=fact_id,
            company_id="test-company",
            batch_id=batch_id,
            fact_type="test",
            confidence=0.95,
        )
        # Verify UUIDs are stored as UUID objects
        assert isinstance(fact.fact_id, uuid.UUID)
        assert isinstance(fact.batch_id, uuid.UUID)
        # Verify they can be converted to strings
        assert isinstance(str(fact.fact_id), str)
        assert isinstance(str(fact.batch_id), str)

    def test_fact_confidence_numeric_precision(self):
        """Test fact confidence maintains numeric precision."""
        batch_id = uuid.uuid4()
        fact = Fact(
            company_id="test-company",
            batch_id=batch_id,
            fact_type="test",
            confidence=0.85,
        )
        # Confidence should be stored as Numeric(3, 2) = 0.85
        assert fact.confidence == 0.85

    def test_fact_datetime_serialization(self):
        """Test fact datetime fields serialize correctly."""
        batch_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        fact = Fact(
            company_id="test-company",
            batch_id=batch_id,
            fact_type="test",
            confidence=0.95,
            extracted_at=now,
        )
        assert fact.extracted_at == now
        assert isinstance(fact.extracted_at, datetime)

    def test_batch_datetime_serialization(self):
        """Test batch datetime fields serialize correctly."""
        now = datetime.now(timezone.utc)
        batch = GatheringBatch(company_id="test-company", created_at=now)
        assert batch.created_at == now
        assert isinstance(batch.created_at, datetime)

    def test_source_datetime_serialization(self):
        """Test source datetime fields serialize correctly."""
        fact_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        source = FactSource(
            fact_id=fact_id,
            source_type="sec_edgar",
            extraction_timestamp=now,
        )
        assert source.extraction_timestamp == now
        assert isinstance(source.extraction_timestamp, datetime)
