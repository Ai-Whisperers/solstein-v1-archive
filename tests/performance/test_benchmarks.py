"""Performance benchmarks for EPIC-023 Story 6.

Usage:
    pytest tests/performance/test_benchmarks.py -v
"""

from __future__ import annotations

import asyncio
import time

import pytest

from solstein.monitoring.profiler import get_profiler


class TestAPIPerformance:
    """API endpoint performance tests."""

    @pytest.mark.asyncio
    async def test_health_endpoint_latency(self, client):
        """Health endpoint should respond in <100ms."""
        start = time.perf_counter()
        response = await client.get("/health")
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert response.status_code == 200
        assert elapsed_ms < 100, f"Health endpoint took {elapsed_ms:.2f}ms"

    @pytest.mark.asyncio
    async def test_company_list_latency(self, client):
        """Company list should respond in <200ms."""
        start = time.perf_counter()
        response = await client.get("/api/v1/companies")
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert response.status_code == 200
        assert elapsed_ms < 200, f"Company list took {elapsed_ms:.2f}ms"


class TestResearchPipelinePerformance:
    """Research pipeline performance tests."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_discovery_stage_timing(self):
        """Discovery stage should complete in <10s."""
        from solstein.research.discovery import discover_companies
        from solstein.research.sources import SourceRegistry

        registry = SourceRegistry()

        start = time.perf_counter()
        candidates = discover_companies(
            seed_company="OpenAI",
            market="AI/ML",
            max_companies=10,
            registry=registry,
        )
        elapsed = time.perf_counter() - start

        assert len(candidates) > 0
        assert elapsed < 10, f"Discovery took {elapsed:.2f}s"

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_concurrent_enrichment_timing(self):
        """Concurrent enrichment should be faster than sequential."""
        from solstein.research.discovery import discover_companies
        from solstein.research.gather import enrich_company, enrich_company_async
        from solstein.research.sources import SourceRegistry

        registry = SourceRegistry()
        candidates = discover_companies(
            seed_company="OpenAI",
            market="AI/ML",
            max_companies=5,
            registry=registry,
        )[:3]  # Test with 3 companies

        # Sequential timing
        start = time.perf_counter()
        for candidate in candidates:
            enrich_company(candidate, registry, "test-batch")
        sequential_time = time.perf_counter() - start

        # Concurrent timing
        start = time.perf_counter()
        await asyncio.gather(*[enrich_company_async(candidate, registry, "test-batch") for candidate in candidates])
        concurrent_time = time.perf_counter() - start

        # Concurrent should be significantly faster
        assert concurrent_time < sequential_time * 0.8, (
            f"Concurrent ({concurrent_time:.2f}s) not faster than sequential ({sequential_time:.2f}s)"
        )


class TestDatabasePerformance:
    """Database performance tests."""

    @pytest.mark.asyncio
    async def test_company_query_performance(self, db_session):
        """Company queries should complete in <50ms."""
        from solstein.infrastructure.repositories import CompanyRepository

        repo = CompanyRepository(db_session)

        start = time.perf_counter()
        await repo.get_all()
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert elapsed_ms < 50, f"Company query took {elapsed_ms:.2f}ms"


class TestCachePerformance:
    """Cache performance tests."""

    @pytest.mark.asyncio
    async def test_cache_read_latency(self):
        """Cache read should be <5ms."""
        from solstein.infrastructure.cache import cache_manager

        # Warm cache
        await cache_manager.set("test-key", {"data": "value"}, ttl=60)

        start = time.perf_counter()
        result = await cache_manager.get("test-key")
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert result is not None
        assert elapsed_ms < 5, f"Cache read took {elapsed_ms:.2f}ms"


@pytest.fixture(scope="session")
def benchmark_report():
    """Generate benchmark report after all tests."""
    profiler = get_profiler()
    profiler.enable()

    yield

    # Print summary after tests
    summary = profiler.get_summary()
    print("\n" + "=" * 70)
    print("PERFORMANCE BENCHMARK SUMMARY")
    print("=" * 70)
    print(f"Total operations profiled: {summary.get('count', 0)}")
    print(f"Average duration: {summary.get('avg_duration_ms', 0):.2f}ms")
    print(f"Max duration: {summary.get('max_duration_ms', 0):.2f}ms")
    print("=" * 70)
