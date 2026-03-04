"""Comprehensive unit tests for all repository classes.

This test suite validates all CRUD operations, batch operations, and data
integrity for CompanyRepository, FactRepository, EnrichmentAuditRepository,
and EnrichmentCacheRepository.
"""

from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from solstein.domain.facts import Fact
from solstein.infrastructure.company_repository import CompanyRepository
from solstein.infrastructure.database_models import (
    CompanyRecord,
)
from solstein.infrastructure.enrichment_repositories import (
    EnrichmentAuditRepository,
    EnrichmentCacheRepository,
)
from solstein.infrastructure.repositories import FactRepository

# ============================================================================
# COMPANY REPOSITORY TESTS
# ============================================================================


@pytest.mark.asyncio
class TestCompanyRepository:
    """Test suite for CompanyRepository CRUD operations."""

    async def test_get_all_companies(self, db_session: AsyncSession):
        """Test fetching all companies with pagination."""
        repo = CompanyRepository(db_session)

        # Create test companies
        company_data_1 = {
            "company_id": "comp-001",
            "name": "Company One",
            "industry": "Energy Software",
        }
        company_data_2 = {
            "company_id": "comp-002",
            "name": "Company Two",
            "industry": "Energy Software",
        }

        await repo.create(company_data_1)
        await repo.create(company_data_2)
        await db_session.commit()

        # Fetch all companies
        companies = await repo.get_all()

        assert len(companies) >= 2
        assert all(hasattr(c, "company_id") for c in companies)
        assert all(hasattr(c, "name") for c in companies)

    async def test_get_all_companies_with_pagination(self, db_session: AsyncSession):
        """Test fetching companies with skip and limit parameters."""
        repo = CompanyRepository(db_session)

        # Create multiple companies
        for i in range(5):
            company_data = {
                "company_id": f"comp-{i:03d}",
                "name": f"Company {i}",
                "industry": "Energy Software",
            }
            await repo.create(company_data)
        await db_session.commit()

        # Test pagination
        companies_page_1 = await repo.get_all(skip=0, limit=2)
        companies_page_2 = await repo.get_all(skip=2, limit=2)

        assert len(companies_page_1) == 2
        assert len(companies_page_2) == 2
        assert companies_page_1[0].company_id != companies_page_2[0].company_id

    async def test_get_company_by_id(self, db_session: AsyncSession):
        """Test fetching a single company by ID."""
        repo = CompanyRepository(db_session)

        company_data = {
            "company_id": "test-comp-001",
            "name": "Test Company",
            "industry": "Energy Software",
            "website": "https://testcompany.com",
        }

        await repo.create(company_data)
        await db_session.commit()

        # Fetch by ID
        fetched = await repo.get_by_id("test-comp-001")

        assert fetched is not None
        assert fetched.company_id == "test-comp-001"
        assert fetched.name == "Test Company"
        assert fetched.website == "https://testcompany.com"

    async def test_get_company_not_found(self, db_session: AsyncSession):
        """Test fetching a non-existent company returns None."""
        repo = CompanyRepository(db_session)

        result = await repo.get_by_id("non-existent-id")

        assert result is None

    async def test_create_company(self, db_session: AsyncSession):
        """Test creating a new company record."""
        repo = CompanyRepository(db_session)

        company_data = {
            "company_id": "new-comp-001",
            "name": "New Company",
            "industry": "Energy Software",
            "headquarters": "Berlin",
            "founded_year": 2015,
        }

        record = await repo.create(company_data)
        await db_session.commit()

        assert record is not None
        assert isinstance(record, CompanyRecord)
        assert record.company_id == "new-comp-001"
        assert record.name == "New Company"
        assert record.industry == "Energy Software"
        assert record.headquarters == "Berlin"
        assert record.founded_year == 2015

    async def test_create_company_missing_required_fields(self, db_session: AsyncSession):
        """Test creating a company without required fields raises ValueError."""
        repo = CompanyRepository(db_session)

        # Missing company_id
        with pytest.raises(ValueError, match="company_id and name are required"):
            await repo.create({"name": "Test Company"})

        # Missing name
        with pytest.raises(ValueError, match="company_id and name are required"):
            await repo.create({"company_id": "test-001"})

    async def test_update_company(self, db_session: AsyncSession):
        """Test updating an existing company record."""
        repo = CompanyRepository(db_session)

        # Create company
        company_data = {
            "company_id": "update-test-001",
            "name": "Original Name",
            "industry": "Energy Software",
        }
        await repo.create(company_data)
        await db_session.commit()

        # Update company
        update_data = {
            "name": "Updated Name",
            "industry": "Energy Analytics",
            "headquarters": "Munich",
        }
        updated = await repo.update("update-test-001", update_data)
        await db_session.commit()

        assert updated.name == "Updated Name"
        assert updated.industry == "Energy Analytics"
        assert updated.headquarters == "Munich"

        # Verify persistence
        fetched = await repo.get_by_id("update-test-001")
        assert fetched.name == "Updated Name"

    async def test_update_company_not_found(self, db_session: AsyncSession):
        """Test updating a non-existent company raises ValueError."""
        repo = CompanyRepository(db_session)

        with pytest.raises(ValueError, match="not found"):
            await repo.update("non-existent", {"name": "New Name"})

    async def test_delete_company(self, db_session: AsyncSession):
        """Test deleting a company record."""
        repo = CompanyRepository(db_session)

        # Create company
        company_data = {
            "company_id": "delete-test-001",
            "name": "To Delete",
            "industry": "Energy Software",
        }
        await repo.create(company_data)
        await db_session.commit()

        # Delete company
        result = await repo.delete("delete-test-001")
        await db_session.commit()

        assert result is True

        # Verify deletion
        fetched = await repo.get_by_id("delete-test-001")
        assert fetched is None

    async def test_delete_company_not_found(self, db_session: AsyncSession):
        """Test deleting a non-existent company returns False."""
        repo = CompanyRepository(db_session)

        result = await repo.delete("non-existent-id")

        assert result is False

    async def test_search_companies_by_name(self, db_session: AsyncSession):
        """Test searching companies by name."""
        repo = CompanyRepository(db_session)

        # Create test companies
        companies_data = [
            {"company_id": "search-001", "name": "Energy Solutions Inc", "industry": "Energy Software"},
            {"company_id": "search-002", "name": "Power Analytics Ltd", "industry": "Energy Software"},
            {"company_id": "search-003", "name": "Grid Optimization GmbH", "industry": "Energy Software"},
        ]

        for data in companies_data:
            await repo.create(data)
        await db_session.commit()

        # Search by name
        results = await repo.search("Energy", field="name")

        assert len(results) >= 1
        assert any("Energy" in c.name for c in results)

    async def test_search_companies_by_industry(self, db_session: AsyncSession):
        """Test searching companies by industry."""
        repo = CompanyRepository(db_session)

        # Create test companies
        companies_data = [
            {"company_id": "ind-001", "name": "Company A", "industry": "Energy Software"},
            {"company_id": "ind-002", "name": "Company B", "industry": "Energy Analytics"},
        ]

        for data in companies_data:
            await repo.create(data)
        await db_session.commit()

        # Search by industry
        results = await repo.search("Energy Software", field="industry")

        assert len(results) >= 1
        assert all(c.industry == "Energy Software" for c in results)

    async def test_search_companies_invalid_field(self, db_session: AsyncSession):
        """Test searching with invalid field raises ValueError."""
        repo = CompanyRepository(db_session)

        with pytest.raises(ValueError, match="not supported"):
            await repo.search("test", field="invalid_field")

    async def test_filter_by_single_criterion(self, db_session: AsyncSession):
        """Test filtering companies by single criterion."""
        repo = CompanyRepository(db_session)

        # Create test companies
        companies_data = [
            {"company_id": "filter-001", "name": "Company A", "industry": "Energy Software", "tier": "A"},
            {"company_id": "filter-002", "name": "Company B", "industry": "Energy Software", "tier": "B"},
        ]

        for data in companies_data:
            await repo.create(data)
        await db_session.commit()

        # Filter by tier
        results = await repo.filter_by(tier="A")

        assert len(results) >= 1
        assert all(c.tier == "A" for c in results)

    async def test_filter_by_multiple_criteria(self, db_session: AsyncSession):
        """Test filtering companies by multiple criteria."""
        repo = CompanyRepository(db_session)

        # Create test companies
        companies_data = [
            {
                "company_id": "multi-001",
                "name": "Company A",
                "industry": "Energy Software",
                "tier": "A",
            },
            {
                "company_id": "multi-002",
                "name": "Company B",
                "industry": "Energy Analytics",
                "tier": "A",
            },
        ]

        for data in companies_data:
            await repo.create(data)
        await db_session.commit()

        # Filter by multiple criteria
        results = await repo.filter_by(industry="Energy Software", tier="A")

        assert len(results) >= 1
        assert all(c.industry == "Energy Software" and c.tier == "A" for c in results)

    async def test_filter_by_no_criteria(self, db_session: AsyncSession):
        """Test filtering with no criteria raises ValueError."""
        repo = CompanyRepository(db_session)

        with pytest.raises(ValueError, match="At least one filter criterion"):
            await repo.filter_by()

    async def test_filter_by_invalid_attribute(self, db_session: AsyncSession):
        """Test filtering by invalid attribute raises ValueError."""
        repo = CompanyRepository(db_session)

        with pytest.raises(ValueError, match="has no attribute"):
            await repo.filter_by(invalid_attr="value")


# ============================================================================
# FACT REPOSITORY TESTS
# ============================================================================


@pytest.mark.asyncio
class TestFactRepository:
    """Test suite for FactRepository operations."""

    async def test_create_batch(self, db_session: AsyncSession):
        """Test creating a gathering batch."""
        repo = FactRepository(db_session)

        batch = await repo.create_batch("comp-001", status="in_progress")
        await db_session.commit()

        assert batch is not None
        assert batch.company_id == "comp-001"
        assert batch.status == "in_progress"
        assert batch.batch_id is not None

    async def test_create_batch_invalid_company_id(self, db_session: AsyncSession):
        """Test creating batch with empty company_id raises ValueError."""
        repo = FactRepository(db_session)

        with pytest.raises(ValueError, match="Company ID is required"):
            await repo.create_batch("")

    async def test_store_fact(self, db_session: AsyncSession):
        """Test storing a single fact."""
        repo = FactRepository(db_session)

        # Create a fact
        fact = Fact(
            company_id="comp-001",
            fact_type="annual_revenue",
            value="1000000",
            confidence_score=0.95,
            extracted_at=datetime.now(timezone.utc),
        )

        fact_id = await repo.store(fact)
        await db_session.commit()

        assert fact_id is not None
        assert isinstance(fact_id, str)

    async def test_store_batch_facts(self, db_session: AsyncSession):
        """Test storing multiple facts in a batch."""
        repo = FactRepository(db_session)

        # Create batch
        batch = await repo.create_batch("comp-002", status="in_progress")
        await db_session.commit()

        # Create facts
        facts = [
            Fact(
                company_id="comp-002",
                fact_type="annual_revenue",
                value="1000000",
                confidence_score=0.95,
                extracted_at=datetime.now(timezone.utc),
            ),
            Fact(
                company_id="comp-002",
                fact_type="employee_count",
                value="150",
                confidence_score=0.90,
                extracted_at=datetime.now(timezone.utc),
            ),
        ]

        fact_ids = await repo.store_batch(facts, batch)
        await db_session.commit()

        assert len(fact_ids) == 2
        assert all(isinstance(fid, str) for fid in fact_ids)

    async def test_store_batch_empty_facts(self, db_session: AsyncSession):
        """Test storing empty batch returns empty list."""
        repo = FactRepository(db_session)

        batch = await repo.create_batch("comp-003", status="in_progress")
        await db_session.commit()

        fact_ids = await repo.store_batch([], batch)

        assert fact_ids == []

    async def test_get_facts_by_company(self, db_session: AsyncSession):
        """Test retrieving facts for a company."""
        repo = FactRepository(db_session)

        # Create batch and facts
        batch = await repo.create_batch("comp-004", status="in_progress")
        await db_session.commit()

        facts = [
            Fact(
                company_id="comp-004",
                fact_type="annual_revenue",
                value="1000000",
                confidence_score=0.95,
                extracted_at=datetime.now(timezone.utc),
            ),
            Fact(
                company_id="comp-004",
                fact_type="growth_rate",
                value="0.25",
                confidence_score=0.85,
                extracted_at=datetime.now(timezone.utc),
            ),
        ]

        await repo.store_batch(facts, batch)
        await db_session.commit()

        # Retrieve facts
        retrieved = await repo.get_company_facts("comp-004")

        assert len(retrieved) >= 2
        assert all(f.company_id == "comp-004" for f in retrieved)

    async def test_get_facts_by_company_empty(self, db_session: AsyncSession):
        """Test retrieving facts for company with no facts."""
        repo = FactRepository(db_session)

        facts = await repo.get_company_facts("non-existent-comp")

        assert facts == []

    async def test_get_facts_by_company_invalid_id(self, db_session: AsyncSession):
        """Test retrieving facts with empty company_id raises ValueError."""
        repo = FactRepository(db_session)

        with pytest.raises(ValueError, match="Company ID is required"):
            await repo.get_company_facts("")

    async def test_get_facts_by_type(self, db_session: AsyncSession):
        """Test retrieving facts of specific type."""
        repo = FactRepository(db_session)

        # Create batch and facts
        batch = await repo.create_batch("comp-005", status="in_progress")
        await db_session.commit()

        facts = [
            Fact(
                company_id="comp-005",
                fact_type="annual_revenue",
                value="1000000",
                confidence_score=0.95,
                extracted_at=datetime.now(timezone.utc),
            ),
            Fact(
                company_id="comp-005",
                fact_type="annual_revenue",
                value="1200000",
                confidence_score=0.90,
                extracted_at=datetime.now(timezone.utc),
            ),
            Fact(
                company_id="comp-005",
                fact_type="employee_count",
                value="150",
                confidence_score=0.85,
                extracted_at=datetime.now(timezone.utc),
            ),
        ]

        await repo.store_batch(facts, batch)
        await db_session.commit()

        # Retrieve by type
        revenue_facts = await repo.get_facts_by_type("comp-005", "annual_revenue")

        assert len(revenue_facts) >= 2
        assert all(f.fact_type == "annual_revenue" for f in revenue_facts)

    async def test_get_fact_by_id(self, db_session: AsyncSession):
        """Test retrieving a single fact by ID."""
        repo = FactRepository(db_session)

        # Create batch and fact
        await repo.create_batch("comp-006", status="in_progress")
        await db_session.commit()

        fact = Fact(
            company_id="comp-006",
            fact_type="annual_revenue",
            value="1000000",
            confidence_score=0.95,
            extracted_at=datetime.now(timezone.utc),
        )

        fact_id = await repo.store(fact)
        await db_session.commit()

        # Retrieve by ID
        retrieved = await repo.get_fact_by_id(fact_id)

        assert retrieved is not None
        assert retrieved.fact_id == fact.fact_id
        assert retrieved.company_id == "comp-006"

    async def test_get_fact_by_id_not_found(self, db_session: AsyncSession):
        """Test retrieving non-existent fact returns None."""
        repo = FactRepository(db_session)

        result = await repo.get_fact_by_id("non-existent-id")

        assert result is None

    async def test_add_source_to_fact(self, db_session: AsyncSession):
        """Test adding a source to a fact."""
        repo = FactRepository(db_session)

        # Create batch and fact
        await repo.create_batch("comp-007", status="in_progress")
        await db_session.commit()

        fact = Fact(
            company_id="comp-007",
            fact_type="annual_revenue",
            value="1000000",
            confidence_score=0.95,
            extracted_at=datetime.now(timezone.utc),
        )

        fact_id = await repo.store(fact)
        await db_session.commit()

        # Add source
        source = await repo.add_source(
            fact_id,
            source_type="sec_edgar",
            source_url="https://sec.gov/cgi-bin/browse-edgar",
            raw_content="SEC filing data",
        )
        await db_session.commit()

        assert source is not None
        assert source.fact_id == fact.fact_id
        assert source.source_type == "sec_edgar"
        assert source.source_url == "https://sec.gov/cgi-bin/browse-edgar"

    async def test_add_source_fact_not_found(self, db_session: AsyncSession):
        """Test adding source to non-existent fact raises RuntimeError."""
        repo = FactRepository(db_session)

        with pytest.raises(RuntimeError, match="not found"):
            await repo.add_source("non-existent-id", "sec_edgar")

    async def test_get_batch(self, db_session: AsyncSession):
        """Test retrieving a batch by ID."""
        repo = FactRepository(db_session)

        batch = await repo.create_batch("comp-008", status="in_progress")
        await db_session.commit()

        retrieved = await repo.get_batch(batch.batch_id)

        assert retrieved is not None
        assert retrieved.batch_id == batch.batch_id
        assert retrieved.company_id == "comp-008"

    async def test_get_batch_not_found(self, db_session: AsyncSession):
        """Test retrieving non-existent batch returns None."""
        repo = FactRepository(db_session)

        result = await repo.get_batch("non-existent-batch-id")

        assert result is None

    async def test_update_batch_status(self, db_session: AsyncSession):
        """Test updating batch status."""
        repo = FactRepository(db_session)

        batch = await repo.create_batch("comp-009", status="in_progress")
        await db_session.commit()

        updated = await repo.update_batch_status(batch.batch_id, "completed")
        await db_session.commit()

        assert updated.status == "completed"

        # Verify persistence
        retrieved = await repo.get_batch(batch.batch_id)
        assert retrieved.status == "completed"

    async def test_update_batch_status_not_found(self, db_session: AsyncSession):
        """Test updating non-existent batch raises RuntimeError."""
        repo = FactRepository(db_session)

        with pytest.raises(RuntimeError, match="not found"):
            await repo.update_batch_status("non-existent-id", "completed")


# ============================================================================
# ENRICHMENT AUDIT REPOSITORY TESTS
# ============================================================================


@pytest.mark.asyncio
class TestEnrichmentAuditRepository:
    """Test suite for EnrichmentAuditRepository operations."""

    async def test_log_operation(self, db_session: AsyncSession):
        """Test logging an enrichment operation."""
        repo = EnrichmentAuditRepository(db_session)

        record = await repo.log_operation(
            company_id="comp-001",
            company_name="Test Company",
            operation="enrich_financials",
            source="sec_edgar",
            status="SUCCESS",
            duration_ms=1234.5,
            fields_enriched=["revenue", "growth_rate"],
        )
        await db_session.commit()

        assert record is not None
        assert record.company_id == "comp-001"
        assert record.company_name == "Test Company"
        assert record.operation == "enrich_financials"
        assert record.status == "SUCCESS"
        assert record.duration_ms == 1234.5

    async def test_log_operation_with_error(self, db_session: AsyncSession):
        """Test logging a failed enrichment operation."""
        repo = EnrichmentAuditRepository(db_session)

        record = await repo.log_operation(
            company_id="comp-002",
            company_name="Failed Company",
            operation="enrich_financials",
            source="sec_edgar",
            status="FAILURE",
            error_message="Connection timeout",
        )
        await db_session.commit()

        assert record.status == "FAILURE"
        assert record.error_message == "Connection timeout"

    async def test_get_audit_trail(self, db_session: AsyncSession):
        """Test retrieving audit trail entries."""
        repo = EnrichmentAuditRepository(db_session)

        # Log multiple operations
        for i in range(3):
            await repo.log_operation(
                company_id=f"comp-{i:03d}",
                company_name=f"Company {i}",
                operation="enrich_financials",
                source="sec_edgar",
                status="SUCCESS",
            )
        await db_session.commit()

        # Retrieve audit trail
        records = await repo.get_audit_trail(limit=10)

        assert len(records) >= 3

    async def test_get_audit_trail_by_company(self, db_session: AsyncSession):
        """Test retrieving audit trail for specific company."""
        repo = EnrichmentAuditRepository(db_session)

        # Log operations for different companies
        await repo.log_operation(
            company_id="comp-audit-001",
            company_name="Company A",
            operation="enrich_financials",
            source="sec_edgar",
            status="SUCCESS",
        )
        await repo.log_operation(
            company_id="comp-audit-002",
            company_name="Company B",
            operation="enrich_financials",
            source="sec_edgar",
            status="SUCCESS",
        )
        await db_session.commit()

        # Retrieve for specific company
        records = await repo.get_audit_trail(company_id="comp-audit-001")

        assert len(records) >= 1
        assert all(r.company_id == "comp-audit-001" for r in records)

    async def test_audit_timestamps(self, db_session: AsyncSession):
        """Test that audit records have correct timestamps."""
        repo = EnrichmentAuditRepository(db_session)

        before = datetime.now(timezone.utc)
        record = await repo.log_operation(
            company_id="comp-time-001",
            company_name="Time Test",
            operation="enrich_financials",
            source="sec_edgar",
            status="SUCCESS",
        )
        after = datetime.now(timezone.utc)
        await db_session.commit()

        assert record.timestamp is not None
        assert before <= record.timestamp <= after

    async def test_get_company_stats(self, db_session: AsyncSession):
        """Test retrieving company enrichment statistics."""
        repo = EnrichmentAuditRepository(db_session)

        # Log operations
        await repo.log_operation(
            company_id="comp-stats-001",
            company_name="Stats Company",
            operation="enrich_financials",
            source="sec_edgar",
            status="SUCCESS",
            duration_ms=100.0,
        )
        await repo.log_operation(
            company_id="comp-stats-001",
            company_name="Stats Company",
            operation="enrich_team",
            source="linkedin",
            status="SUCCESS",
            duration_ms=200.0,
        )
        await repo.log_operation(
            company_id="comp-stats-001",
            company_name="Stats Company",
            operation="enrich_tech",
            source="github",
            status="FAILURE",
        )
        await db_session.commit()

        stats = await repo.get_company_stats("comp-stats-001")

        assert stats["total_operations"] == 3
        assert stats["successful"] == 2
        assert stats["failed"] == 1
        assert stats["success_rate"] == pytest.approx(2 / 3, rel=0.01)
        assert stats["avg_duration_ms"] == pytest.approx(100.0, rel=0.01)


# ============================================================================
# ENRICHMENT CACHE REPOSITORY TESTS
# ============================================================================


@pytest.mark.asyncio
class TestEnrichmentCacheRepository:
    """Test suite for EnrichmentCacheRepository operations."""

    async def test_cache_enrichment(self, db_session: AsyncSession):
        """Test caching enrichment results."""
        repo = EnrichmentCacheRepository(db_session)

        enriched_data = {
            "revenue": 1000000,
            "growth_rate": 0.25,
            "employee_count": 150,
        }

        record = await repo.cache_enrichment(
            company_id="comp-cache-001",
            enriched_data=enriched_data,
            sources_used=["sec_edgar", "linkedin"],
            fields_enriched=["revenue", "growth_rate", "employee_count"],
            ttl_seconds=3600,
        )
        await db_session.commit()

        assert record is not None
        assert record.company_id == "comp-cache-001"
        assert record.enriched_data == enriched_data
        assert record.sources_used == ["sec_edgar", "linkedin"]

    async def test_get_cached(self, db_session: AsyncSession):
        """Test retrieving cached enrichment data."""
        repo = EnrichmentCacheRepository(db_session)

        enriched_data = {"revenue": 1000000, "growth_rate": 0.25}

        await repo.cache_enrichment(
            company_id="comp-cache-002",
            enriched_data=enriched_data,
            ttl_seconds=3600,
        )
        await db_session.commit()

        # Retrieve cache
        cached = await repo.get_cached("comp-cache-002")

        assert cached is not None
        assert cached.company_id == "comp-cache-002"
        assert cached.enriched_data == enriched_data

    async def test_get_cached_not_found(self, db_session: AsyncSession):
        """Test retrieving non-existent cache returns None."""
        repo = EnrichmentCacheRepository(db_session)

        result = await repo.get_cached("non-existent-cache")

        assert result is None

    async def test_cache_expiration(self, db_session: AsyncSession):
        """Test that expired cache is not returned."""
        repo = EnrichmentCacheRepository(db_session)

        enriched_data = {"revenue": 1000000}

        # Create cache with very short TTL
        await repo.cache_enrichment(
            company_id="comp-cache-expired",
            enriched_data=enriched_data,
            ttl_seconds=0,  # Expires immediately
        )
        await db_session.commit()

        # Try to retrieve - should be expired
        cached = await repo.get_cached("comp-cache-expired")

        assert cached is None

    async def test_cache_hit_count(self, db_session: AsyncSession):
        """Test that cache hit count is incremented."""
        repo = EnrichmentCacheRepository(db_session)

        enriched_data = {"revenue": 1000000}

        await repo.cache_enrichment(
            company_id="comp-cache-hits",
            enriched_data=enriched_data,
            ttl_seconds=3600,
        )
        await db_session.commit()

        # Access cache multiple times
        cached1 = await repo.get_cached("comp-cache-hits")
        await db_session.commit()
        cached2 = await repo.get_cached("comp-cache-hits")
        await db_session.commit()

        assert cached1 is not None
        assert cached2 is not None
        assert cached2.hits >= 1

    async def test_delete_cache_by_company(self, db_session: AsyncSession):
        """Test deleting cache for specific company."""
        repo = EnrichmentCacheRepository(db_session)

        enriched_data = {"revenue": 1000000}

        await repo.cache_enrichment(
            company_id="comp-cache-delete",
            enriched_data=enriched_data,
            ttl_seconds=3600,
        )
        await db_session.commit()

        # Delete cache
        deleted_count = await repo.delete_cache("comp-cache-delete")
        await db_session.commit()

        assert deleted_count >= 1

        # Verify deletion
        cached = await repo.get_cached("comp-cache-delete")
        assert cached is None

    async def test_delete_expired_cache(self, db_session: AsyncSession):
        """Test deleting all expired cache entries."""
        repo = EnrichmentCacheRepository(db_session)

        # Create expired cache
        await repo.cache_enrichment(
            company_id="comp-cache-exp-1",
            enriched_data={"revenue": 1000000},
            ttl_seconds=0,
        )
        await db_session.commit()

        # Delete expired entries
        deleted_count = await repo.delete_cache()
        await db_session.commit()

        assert deleted_count >= 1

    async def test_get_cache_stats(self, db_session: AsyncSession):
        """Test retrieving cache statistics."""
        repo = EnrichmentCacheRepository(db_session)

        # Create multiple cache entries
        for i in range(3):
            await repo.cache_enrichment(
                company_id=f"comp-cache-stats-{i}",
                enriched_data={"revenue": 1000000 + i},
                ttl_seconds=3600,
            )
        await db_session.commit()

        # Access some caches
        await repo.get_cached("comp-cache-stats-0")
        await db_session.commit()
        await repo.get_cached("comp-cache-stats-0")
        await db_session.commit()

        stats = await repo.get_cache_stats()

        assert stats["total_entries"] >= 3
        assert stats["total_hits"] >= 2

    async def test_cache_update_overwrites_previous(self, db_session: AsyncSession):
        """Test that caching same company overwrites previous cache."""
        repo = EnrichmentCacheRepository(db_session)

        # Create initial cache
        await repo.cache_enrichment(
            company_id="comp-cache-overwrite",
            enriched_data={"revenue": 1000000},
            ttl_seconds=3600,
        )
        await db_session.commit()

        # Overwrite with new cache
        await repo.cache_enrichment(
            company_id="comp-cache-overwrite",
            enriched_data={"revenue": 2000000},
            ttl_seconds=3600,
        )
        await db_session.commit()

        # Retrieve and verify
        cached = await repo.get_cached("comp-cache-overwrite")

        assert cached is not None
        assert cached.enriched_data["revenue"] == 2000000
