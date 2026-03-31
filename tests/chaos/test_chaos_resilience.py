"""Chaos engineering tests - EPIC-014.

Tests system resilience under failure conditions.
"""

import asyncio
import random
from unittest.mock import AsyncMock, Mock

import pytest

from solstein.application.enrichment_pipeline import EnrichmentPipeline
from solstein.infrastructure.circuit_breaker import CircuitBreaker, CircuitBreakerOpen


class TestCircuitBreakerResilience:
    """Test circuit breaker behavior under failure."""

    @pytest.mark.asyncio
    async def test_circuit_opens_after_failures(self):
        """Circuit should open after threshold failures."""
        breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=1.0)

        call_count = 0

        @breaker
        async def failing_function():
            nonlocal call_count
            call_count += 1
            raise Exception("Service unavailable")

        # First 3 calls should raise the original exception
        for _ in range(3):
            with pytest.raises(Exception, match="Service unavailable"):
                await failing_function()

        # 4th call should raise CircuitBreakerOpen
        with pytest.raises(CircuitBreakerOpen):
            await failing_function()

        assert call_count == 3  # Should not have been called after open

    @pytest.mark.asyncio
    async def test_circuit_closes_after_recovery(self):
        """Circuit should close after recovery timeout."""
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)

        @breaker
        async def flaky_function():
            raise Exception("Fail")

        # Trigger circuit open
        for _ in range(2):
            with pytest.raises(Exception):
                await flaky_function()

        # Circuit should be open
        with pytest.raises(CircuitBreakerOpen):
            await flaky_function()

        # Wait for recovery
        await asyncio.sleep(0.15)

        # Now it should try again (half-open)
        with pytest.raises(Exception):
            await flaky_function()

    @pytest.mark.asyncio
    async def test_success_resets_failure_count(self):
        """Successful calls should reset failure count."""
        breaker = CircuitBreaker(failure_threshold=3)

        call_count = 0

        @breaker
        async def sometimes_fails():
            nonlocal call_count
            call_count += 1
            if call_count % 2 == 0:
                return "success"
            raise Exception("Fail")

        # Alternate failures and successes
        with pytest.raises(Exception):
            await sometimes_fails()  # Fail 1

        result = await sometimes_fails()  # Success 1
        assert result == "success"

        with pytest.raises(Exception):
            await sometimes_fails()  # Fail 2

        result = await sometimes_fails()  # Success 2
        assert result == "success"

        # Circuit should still be closed (failures were reset)
        with pytest.raises(Exception):
            await sometimes_fails()  # Fail 3

        # This would be failure 4 if not reset, but it's only 3
        assert breaker.failure_count == 1  # Reset after success


class TestEnrichmentPipelineResilience:
    """Test enrichment pipeline under various failure conditions."""

    @pytest.mark.asyncio
    async def test_partial_failure_continues(self):
        """Pipeline should continue if some sources fail."""
        pipeline = EnrichmentPipeline(registry=Mock())

        # Mock registry with some failing sources
        mock_sources = [
            Mock(enrich=AsyncMock(return_value={"source": "A", "data": "ok"})),
            Mock(enrich=AsyncMock(side_effect=Exception("API down"))),
            Mock(enrich=AsyncMock(return_value={"source": "C", "data": "ok"})),
        ]
        pipeline.registry.all_enrichment_sources = mock_sources

        result = await pipeline.enrich("test", "Test Company")

        # Should have data from successful sources
        assert result is not None
        # 2 sources should have succeeded
        assert mock_sources[0].enrich.called
        assert mock_sources[2].enrich.called

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Pipeline should handle slow sources."""
        pipeline = EnrichmentPipeline(registry=Mock())

        async def slow_enrich(*args, **kwargs):
            await asyncio.sleep(10)  # Very slow
            return {"data": "late"}

        mock_source = Mock(enrich=AsyncMock(side_effect=slow_enrich))
        pipeline.registry.all_enrichment_sources = [mock_source]

        # Should complete without waiting 10 seconds
        start = asyncio.get_event_loop().time()
        await pipeline.enrich("test", "Test Company")
        elapsed = asyncio.get_event_loop().time() - start

        assert elapsed < 5  # Should timeout much sooner


class TestDataLoaderResilience:
    """Test data loader resilience."""

    @pytest.mark.asyncio
    async def test_malformed_data_handling(self):
        """Loader should skip malformed data and continue."""
        from solstein.data.loaders import CompetitorDataLoader

        loader = CompetitorDataLoader()

        # Test with various malformed inputs
        malformed_data = [
            {"company_name": "Valid", "revenue": {"timeline": []}},
            None,  # Null entry
            {},  # Empty dict
            {"revenue": "invalid"},  # Wrong type
        ]

        # Should not crash
        results = []
        for data in malformed_data:
            try:
                result = loader._convert_to_domain_company(data, "test")
                if result:
                    results.append(result)
            except Exception:
                pass  # Expected for invalid data

        # Should have processed at least the valid one
        assert len(results) >= 1

    def test_invalid_json_handling(self, tmp_path):
        """Loader should handle invalid JSON gracefully."""
        from solstein.data.loaders import CompetitorDataLoader

        loader = CompetitorDataLoader(tmp_path)

        # Create invalid JSON file
        json_file = tmp_path / "competitor_data.json"
        json_file.write_text("not valid json")

        # Should return empty list, not crash
        companies = loader.load_companies()
        assert companies == []


class TestMemoryPressure:
    """Test behavior under memory pressure."""

    @pytest.mark.asyncio
    async def test_large_dataset_processing(self):
        """System should handle large datasets without OOM."""
        from solstein.infrastructure.batch_processor import BatchProcessor

        processor = BatchProcessor(batch_size=100, max_concurrency=5)

        # Simulate large dataset
        large_dataset = list(range(10000))

        async def process_item(item: int) -> int:
            await asyncio.sleep(0.001)  # Simulate work
            return item * 2

        result = await processor.process(large_dataset, process_item)

        assert result.processed_count == 10000
        assert len(result.results) == 10000


class TestConcurrentAccess:
    """Test concurrent access patterns."""

    @pytest.mark.asyncio
    async def test_concurrent_cache_access(self):
        """Cache should handle concurrent access safely."""
        from solstein.infrastructure.cache import get_cache

        cache = get_cache()

        async def write_and_read(key: str, value: int):
            await cache.set(key, value, ttl=60)
            return await cache.get(key)

        # Concurrent writes to same key
        tasks = [write_and_read("test_key", i) for i in range(100)]
        results = await asyncio.gather(*tasks)

        # All reads should return valid values
        assert all(r is not None for r in results)

    @pytest.mark.asyncio
    async def test_concurrent_enrichment(self):
        """Multiple concurrent enrichments should not conflict."""
        from solstein.data.eneve_enrichment_integration import EneveEnricher

        enricher = EneveEnricher()

        companies = [{"company_name": f"Company {i}", "website": f"https://company{i}.com"} for i in range(10)]

        # Enrich same companies concurrently
        tasks = [enricher.enrich_companies(companies) for _ in range(3)]

        results = await asyncio.gather(*tasks)

        # All should complete without error
        assert all(len(r) == 10 for r in results)


# Stress test markers
@pytest.mark.stress
@pytest.mark.slow
class TestStressConditions:
    """Long-running stress tests."""

    @pytest.mark.asyncio
    async def test_sustained_load(self):
        """System should handle sustained load."""
        from solstein.infrastructure.batch_processor import BatchProcessor

        processor = BatchProcessor(batch_size=50, max_concurrency=10)

        async def process_with_random_delay(item: int) -> int:
            await asyncio.sleep(random.uniform(0.001, 0.01))
            return item

        # Process 5000 items
        items = list(range(5000))
        result = await processor.process(items, process_with_random_delay)

        assert result.processed_count == 5000
        assert result.error_count == 0
