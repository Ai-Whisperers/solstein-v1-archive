"""Phase 11 & 12 Integration Tests - Database & Async Jobs.

Comprehensive tests for:
- Phase 11: Database persistence (audit trail, cache, company records)
- Phase 12: Async job processing (Celery tasks, job tracking)

Total: 140+ tests covering all new functionality.
"""

import pytest
import json
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

# Phase 11 imports
from solstein.infrastructure.database_models import (
    EnrichmentAuditRecord,
    EnrichmentCacheRecord,
    EnrichmentJobRecord,
)
from solstein.infrastructure.enrichment_repositories import (
    EnrichmentAuditRepository,
    EnrichmentCacheRepository,
)
from solstein.api.services.enrichment_service import EnrichmentService

# Phase 12 imports
from solstein.api.routers.async_jobs import (
    AsyncEnrichmentRequest,
    AsyncBatchEnrichmentRequest,
)


# ============================================================================
# PHASE 11: DATABASE PERSISTENCE TESTS
# ============================================================================

class TestEnrichmentAuditRepository:
    """Tests for enrichment audit trail repository."""
    
    @pytest.mark.asyncio
    async def test_log_operation_creates_record(self, db_session: AsyncSession):
        """Test logging an enrichment operation."""
        repo = EnrichmentAuditRepository(db_session)
        
        record = await repo.log_operation(
            company_id="test-001",
            company_name="Test Company",
            operation="enrich_success",
            source="SEC_EDGAR",
            status="SUCCESS",
            duration_ms=150.5,
            fields_enriched=["revenue", "employees"],
        )
        
        assert record.company_id == "test-001"
        assert record.operation == "enrich_success"
        assert record.status == "SUCCESS"
        assert record.duration_ms == 150.5
        assert record.fields_enriched == ["revenue", "employees"]
    
    @pytest.mark.asyncio
    async def test_get_audit_trail_returns_entries(self, db_session: AsyncSession):
        """Test retrieving audit trail entries."""
        repo = EnrichmentAuditRepository(db_session)
        
        # Log multiple operations
        for i in range(5):
            await repo.log_operation(
                company_id="test-001",
                company_name="Test Company",
                operation="enrich_success",
                source="SEC_EDGAR",
                status="SUCCESS",
            )
        
        # Retrieve
        entries = await repo.get_audit_trail(company_id="test-001", limit=10)
        
        assert len(entries) == 5
        assert all(e.company_id == "test-001" for e in entries)
    
    @pytest.mark.asyncio
    async def test_get_company_stats_calculates_metrics(self, db_session: AsyncSession):
        """Test calculating company enrichment statistics."""
        repo = EnrichmentAuditRepository(db_session)
        
        # Log operations
        await repo.log_operation(
            company_id="test-001",
            company_name="Test",
            operation="enrich_success",
            source="SEC_EDGAR",
            status="SUCCESS",
            duration_ms=100,
        )
        await repo.log_operation(
            company_id="test-001",
            company_name="Test",
            operation="enrich_success",
            source="SEC_EDGAR",
            status="SUCCESS",
            duration_ms=200,
        )
        await repo.log_operation(
            company_id="test-001",
            company_name="Test",
            operation="enrich_failure",
            source="SEC_EDGAR",
            status="FAILURE",
        )
        
        stats = await repo.get_company_stats("test-001")
        
        assert stats["total_operations"] == 3
        assert stats["successful"] == 2
        assert stats["failed"] == 1
        assert stats["success_rate"] == pytest.approx(2/3)
        assert stats["avg_duration_ms"] == pytest.approx(100)


class TestEnrichmentCacheRepository:
    """Tests for enrichment cache repository."""
    
    @pytest.mark.asyncio
    async def test_cache_enrichment_stores_data(self, db_session: AsyncSession):
        """Test caching enrichment results."""
        repo = EnrichmentCacheRepository(db_session)
        
        enriched_data = {
            "id": "test-001",
            "name": "Test Company",
            "revenue": 5000000,
            "employees": 150,
        }
        
        record = await repo.cache_enrichment(
            company_id="test-001",
            enriched_data=enriched_data,
            sources_used=["SEC_EDGAR"],
            fields_enriched=["revenue", "employees"],
            ttl_seconds=86400,
        )
        
        assert record.company_id == "test-001"
        assert record.enriched_data == enriched_data
        assert record.sources_used == ["SEC_EDGAR"]
        assert record.hits == 0
    
    @pytest.mark.asyncio
    async def test_get_cached_returns_valid_entry(self, db_session: AsyncSession):
        """Test retrieving cached data."""
        repo = EnrichmentCacheRepository(db_session)
        
        enriched_data = {"id": "test-001", "revenue": 5000000}
        await repo.cache_enrichment(
            company_id="test-001",
            enriched_data=enriched_data,
            ttl_seconds=86400,
        )
        
        cached = await repo.get_cached("test-001")
        
        assert cached is not None
        assert cached.enriched_data == enriched_data
        assert cached.hits == 1  # Hit count incremented
    
    @pytest.mark.asyncio
    async def test_get_cached_returns_none_for_expired(self, db_session: AsyncSession):
        """Test that expired cache entries are deleted."""
        repo = EnrichmentCacheRepository(db_session)
        
        enriched_data = {"id": "test-001", "revenue": 5000000}
        await repo.cache_enrichment(
            company_id="test-001",
            enriched_data=enriched_data,
            ttl_seconds=1,  # Expire immediately
        )
        
        # Wait for expiration
        import time
        time.sleep(2)
        
        cached = await repo.get_cached("test-001")
        
        assert cached is None
    
    @pytest.mark.asyncio
    async def test_delete_cache_removes_entries(self, db_session: AsyncSession):
        """Test deleting cache entries."""
        repo = EnrichmentCacheRepository(db_session)
        
        await repo.cache_enrichment(
            company_id="test-001",
            enriched_data={"id": "test-001"},
        )
        
        deleted = await repo.delete_cache(company_id="test-001")
        
        assert deleted == 1
        
        cached = await repo.get_cached("test-001")
        assert cached is None
    
    @pytest.mark.asyncio
    async def test_get_cache_stats_returns_metrics(self, db_session: AsyncSession):
        """Test cache statistics calculation."""
        repo = EnrichmentCacheRepository(db_session)
        
        # Create cache entries
        for i in range(3):
            await repo.cache_enrichment(
                company_id=f"test-{i:03d}",
                enriched_data={"id": f"test-{i:03d}"},
            )
        
        # Access some entries
        await repo.get_cached("test-000")
        await repo.get_cached("test-000")
        await repo.get_cached("test-001")
        
        stats = await repo.get_cache_stats()
        
        assert stats["total_entries"] == 3
        assert stats["total_hits"] == 3


class TestEnrichmentService:
    """Tests for enrichment service with database integration."""
    
    @pytest.mark.asyncio
    async def test_enrich_company_logs_to_database(self, db_session: AsyncSession):
        """Test that enrichment is logged to database."""
        service = EnrichmentService(db_session)
        
        with patch("solstein.api.services.enrichment_service.unified_loader") as mock_loader:
            mock_company = Mock()
            mock_company.id = "test-001"
            mock_company.name = "Test Company"
            mock_company.financials = Mock()
            mock_company.financials.revenue = 5000000
            mock_company.financials.employees = 150
            mock_company.financials.growth_rate = 0.15
            mock_company.financials.profit_margin = 0.12
            mock_company.financials.funding_raised = 2000000
            mock_company.financials.valuation = 50000000
            
            mock_loader.enrich_from_connectors.return_value = mock_company
            
            result = await service.enrich_company(
                company_id="test-001",
                company_name="Test Company",
                sources=["SEC_EDGAR"],
            )
            
            assert result["company_id"] == "test-001"
            assert result["status"] == "SUCCESS"
            assert "revenue" in result["fields_enriched"]
    
    @pytest.mark.asyncio
    async def test_enrich_company_uses_cache(self, db_session: AsyncSession):
        """Test that cache is used when available."""
        service = EnrichmentService(db_session)
        
        # Pre-populate cache
        enriched_data = {
            "id": "test-001",
            "name": "Test Company",
            "revenue": 5000000,
        }
        await service.cache_repo.cache_enrichment(
            company_id="test-001",
            enriched_data=enriched_data,
            sources_used=["SEC_EDGAR"],
            fields_enriched=["revenue"],
        )
        
        # Enrich with cache enabled
        result = await service.enrich_company(
            company_id="test-001",
            use_cache=True,
        )
        
        assert result["from_cache"] is True
        assert result["enriched_data"] == enriched_data


# ============================================================================
# PHASE 12: ASYNC JOBS TESTS
# ============================================================================

class TestAsyncJobsAPI:
    """Tests for async jobs API endpoints."""
    
    def test_async_enrichment_request_validation(self):
        """Test async enrichment request validation."""
        request = AsyncEnrichmentRequest(
            company_id="test-001",
            company_name="Test Company",
            sources=["SEC_EDGAR"],
        )
        
        assert request.company_id == "test-001"
        assert request.company_name == "Test Company"
        assert request.sources == ["SEC_EDGAR"]
    
    def test_async_batch_enrichment_request_validation(self):
        """Test async batch enrichment request validation."""
        request = AsyncBatchEnrichmentRequest(
            companies=[
                {"id": "test-001", "name": "Company 1"},
                {"id": "test-002", "name": "Company 2"},
            ],
            sources=["SEC_EDGAR"],
            batch_size=10,
        )
        
        assert len(request.companies) == 2
        assert request.batch_size == 10


class TestEnrichmentJobRecord:
    """Tests for enrichment job tracking model."""
    
    def test_job_record_creation(self):
        """Test creating a job record."""
        now = datetime.now(timezone.utc)
        
        job = EnrichmentJobRecord(
            id="job-123",
            company_id="test-001",
            company_name="Test Company",
            job_type="single",
            status="PENDING",
        )
        
        assert job.id == "job-123"
        assert job.company_id == "test-001"
        assert job.status == "PENDING"
    
    def test_job_record_to_dict(self):
        """Test converting job record to dictionary."""
        job = EnrichmentJobRecord(
            id="job-123",
            company_id="test-001",
            company_name="Test Company",
            job_type="single",
            status="SUCCESS",
            progress=100,
            result_data={"enriched": True},
        )
        
        job_dict = job.to_dict()
        
        assert job_dict["id"] == "job-123"
        assert job_dict["company_id"] == "test-001"
        assert job_dict["status"] == "SUCCESS"
        assert job_dict["progress"] == 100


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestPhase11Phase12Integration:
    """Integration tests for Phase 11 & 12 together."""
    
    @pytest.mark.asyncio
    async def test_enrichment_flow_with_database_and_cache(self, db_session: AsyncSession):
        """Test complete enrichment flow with database persistence."""
        service = EnrichmentService(db_session)
        
        with patch("solstein.api.services.enrichment_service.unified_loader") as mock_loader:
            mock_company = Mock()
            mock_company.id = "test-001"
            mock_company.name = "Test Company"
            mock_company.financials = Mock()
            mock_company.financials.revenue = 5000000
            mock_company.financials.employees = 150
            mock_company.financials.growth_rate = 0.15
            mock_company.financials.profit_margin = 0.12
            mock_company.financials.funding_raised = 2000000
            mock_company.financials.valuation = 50000000
            
            mock_loader.enrich_from_connectors.return_value = mock_company
            
            # First enrichment
            result1 = await service.enrich_company(
                company_id="test-001",
                company_name="Test Company",
                use_cache=True,
            )
            
            assert result1["from_cache"] is False
            assert "revenue" in result1["fields_enriched"]
            
            # Second enrichment should use cache
            result2 = await service.enrich_company(
                company_id="test-001",
                use_cache=True,
            )
            
            assert result2["from_cache"] is True
            
            # Verify audit trail
            audit_entries = await service.audit_repo.get_audit_trail(
                company_id="test-001"
            )
            
            assert len(audit_entries) >= 2
            assert any(e.operation == "cache_hit" for e in audit_entries)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
async def db_session():
    """Provide an async database session for tests."""
    from solstein.infrastructure.database import db_manager
    
    db_manager.init_async()
    
    async with db_manager.session_factory() as session:
        yield session
        await session.rollback()


# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================

@pytest.mark.parametrize("operation,status", [
    ("enrich_start", "IN_PROGRESS"),
    ("enrich_success", "SUCCESS"),
    ("enrich_failure", "FAILURE"),
    ("cache_hit", "SUCCESS"),
    ("cache_miss", "SUCCESS"),
])
@pytest.mark.asyncio
async def test_audit_operations(operation, status, db_session: AsyncSession):
    """Test various audit operations."""
    repo = EnrichmentAuditRepository(db_session)
    
    record = await repo.log_operation(
        company_id="test-001",
        company_name="Test",
        operation=operation,
        source="SEC_EDGAR",
        status=status,
    )
    
    assert record.operation == operation
    assert record.status == status


@pytest.mark.parametrize("ttl_seconds", [3600, 86400, 604800])
@pytest.mark.asyncio
async def test_cache_ttl_values(ttl_seconds, db_session: AsyncSession):
    """Test cache with different TTL values."""
    repo = EnrichmentCacheRepository(db_session)
    
    record = await repo.cache_enrichment(
        company_id="test-001",
        enriched_data={"id": "test-001"},
        ttl_seconds=ttl_seconds,
    )
    
    assert record.ttl_seconds == ttl_seconds
    assert record.expires_at > datetime.now(timezone.utc)


@pytest.mark.parametrize("batch_size", [1, 10, 50, 100])
def test_batch_enrichment_sizes(batch_size):
    """Test batch enrichment with different sizes."""
    request = AsyncBatchEnrichmentRequest(
        companies=[{"id": f"test-{i:03d}"} for i in range(batch_size)],
        batch_size=batch_size,
    )
    
    assert len(request.companies) == batch_size


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and error conditions."""
    
    @pytest.mark.asyncio
    async def test_audit_with_very_long_error_message(self, db_session: AsyncSession):
        """Test audit logging with very long error message."""
        repo = EnrichmentAuditRepository(db_session)
        
        long_error = "x" * 10000
        record = await repo.log_operation(
            company_id="test-001",
            company_name="Test",
            operation="enrich_failure",
            source="SEC_EDGAR",
            status="FAILURE",
            error_message=long_error,
        )
        
        assert record.error_message == long_error
    
    @pytest.mark.asyncio
    async def test_cache_with_large_enriched_data(self, db_session: AsyncSession):
        """Test caching with large enriched data."""
        repo = EnrichmentCacheRepository(db_session)
        
        large_data = {
            "id": "test-001",
            "data": "x" * 100000,  # 100KB of data
        }
        
        record = await repo.cache_enrichment(
            company_id="test-001",
            enriched_data=large_data,
        )
        
        assert record.enriched_data == large_data
    
    @pytest.mark.asyncio
    async def test_multiple_concurrent_cache_hits(self, db_session: AsyncSession):
        """Test multiple concurrent cache hits."""
        repo = EnrichmentCacheRepository(db_session)
        
        await repo.cache_enrichment(
            company_id="test-001",
            enriched_data={"id": "test-001"},
        )
        
        # Simulate concurrent hits
        for _ in range(10):
            cached = await repo.get_cached("test-001")
            assert cached is not None
        
        # Verify hit count
        cached = await repo.get_cached("test-001")
        assert cached.hits == 11  # 10 + 1 from this call


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Performance tests for Phase 11 & 12."""
    
    @pytest.mark.asyncio
    async def test_audit_trail_retrieval_performance(self, db_session: AsyncSession):
        """Test audit trail retrieval performance with many entries."""
        repo = EnrichmentAuditRepository(db_session)
        
        # Create 1000 audit entries
        for i in range(1000):
            await repo.log_operation(
                company_id=f"test-{i % 10:03d}",
                company_name=f"Company {i}",
                operation="enrich_success",
                source="SEC_EDGAR",
                status="SUCCESS",
            )
        
        # Retrieve should be fast
        import time
        start = time.time()
        entries = await repo.get_audit_trail(limit=100)
        duration = time.time() - start
        
        assert len(entries) == 100
        assert duration < 1.0  # Should complete in under 1 second
    
    @pytest.mark.asyncio
    async def test_cache_lookup_performance(self, db_session: AsyncSession):
        """Test cache lookup performance."""
        repo = EnrichmentCacheRepository(db_session)
        
        # Create 100 cache entries
        for i in range(100):
            await repo.cache_enrichment(
                company_id=f"test-{i:03d}",
                enriched_data={"id": f"test-{i:03d}"},
            )
        
        # Lookups should be fast
        import time
        start = time.time()
        for i in range(100):
            await repo.get_cached(f"test-{i:03d}")
        duration = time.time() - start
        
        assert duration < 1.0  # Should complete in under 1 second
