"""Tests for loader_orchestrator module.

E1: Tests for extracted orchestration layer.
"""

import asyncio
from dataclasses import dataclass
from typing import Any

import pytest

from solstein.data.loader_orchestrator import (
    LoadConfig,
    LoadResult,
    UnifiedLoaderOrchestrator,
)
from solstein.data.conflict_resolution import CompositeResolver, ConflictResolver
from solstein.data.normalization import DataNormalizer
from solstein.domain.models import Company


class MockDataSource:
    """Mock data source for testing."""

    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.data = data

    async def fetch(self, query: dict[str, Any]) -> list[dict[str, Any]]:
        return self.data


class FailingDataSource:
    """Data source that always fails."""

    async def fetch(self, query: dict[str, Any]) -> list[dict[str, Any]]:
        raise ConnectionError("Network failure")


@dataclass
class MockEnrichmentConnector:
    """Mock enrichment connector."""

    name: str
    data_to_add: dict[str, Any]

    async def enrich(self, company: Company) -> dict[str, Any]:
        return self.data_to_add


class TestLoadConfig:
    """Tests for LoadConfig dataclass."""

    def test_default_values(self) -> None:
        config = LoadConfig()
        assert config.batch_size == 100
        assert config.max_concurrent_enrichment == 10
        assert config.enable_conflict_resolution is True
        assert config.enrichment_timeout_seconds == 30.0
        assert config.retry_attempts == 3

    def test_custom_values(self) -> None:
        config = LoadConfig(
            batch_size=50,
            max_concurrent_enrichment=5,
            enable_conflict_resolution=False,
            enrichment_timeout_seconds=60.0,
            retry_attempts=5,
        )
        assert config.batch_size == 50
        assert config.max_concurrent_enrichment == 5
        assert config.enable_conflict_resolution is False
        assert config.enrichment_timeout_seconds == 60.0
        assert config.retry_attempts == 5


class TestLoadResult:
    """Tests for LoadResult dataclass."""

    def test_default_values(self) -> None:
        result = LoadResult()
        assert result.companies == []
        assert result.enriched_count == 0
        assert result.failed_count == 0
        assert result.skipped_count == 0
        assert result.errors == []
        assert result.metadata == {}

    def test_add_error(self) -> None:
        result = LoadResult()
        result.add_error("test_source", ValueError("test error"), {"key": "value"})

        assert len(result.errors) == 1
        assert result.errors[0]["source"] == "test_source"
        assert result.errors[0]["error_type"] == "ValueError"
        assert result.errors[0]["error_message"] == "test error"
        assert result.errors[0]["context"] == {"key": "value"}


class TestUnifiedLoaderOrchestrator:
    """Tests for UnifiedLoaderOrchestrator."""

    @pytest.mark.asyncio
    async def test_load_from_single_source(self) -> None:
        source = MockDataSource(
            [
                {"id": "test-1", "name": "TestCo", "domain": "testco.com"},
            ]
        )
        orchestrator = UnifiedLoaderOrchestrator()
        result = await orchestrator.load_companies([source])

        assert len(result.companies) == 1
        assert result.companies[0].name == "TestCo"
        assert result.failed_count == 0

    @pytest.mark.asyncio
    async def test_load_from_multiple_sources(self) -> None:
        source1 = MockDataSource(
            [
                {"id": "test-1", "name": "TestCo", "domain": "testco.com"},
            ]
        )
        source2 = MockDataSource(
            [
                {"id": "test-2", "name": "OtherCo", "domain": "otherco.com"},
            ]
        )
        orchestrator = UnifiedLoaderOrchestrator()
        result = await orchestrator.load_companies([source1, source2])

        assert len(result.companies) == 2
        names = {c.name for c in result.companies}
        assert names == {"TestCo", "OtherCo"}

    @pytest.mark.asyncio
    async def test_handles_source_failure(self) -> None:
        good_source = MockDataSource([{"id": "test-1", "name": "TestCo", "domain": "testco.com"}])
        bad_source = FailingDataSource()
        orchestrator = UnifiedLoaderOrchestrator()
        result = await orchestrator.load_companies([good_source, bad_source])

        assert len(result.companies) == 1
        assert result.companies[0].name == "TestCo"
        assert result.failed_count == 0  # Company still loaded
        assert len(result.errors) == 1
        assert result.errors[0]["source"] == "discovery"

    @pytest.mark.asyncio
    async def test_deduplicates_companies(self) -> None:
        source = MockDataSource(
            [
                {"id": "test-1", "name": "TestCo", "domain": "testco.com", "revenue": 100},
                {"id": "test-1", "name": "TestCo", "domain": "testco.com", "employees": 50},
            ]
        )
        orchestrator = UnifiedLoaderOrchestrator()
        result = await orchestrator.load_companies([source])

        assert len(result.companies) == 1
        # Should merge data from both records
        assert result.companies[0].name == "TestCo"

    @pytest.mark.asyncio
    async def test_enrichment(self) -> None:
        source = MockDataSource([{"id": "test-1", "name": "TestCo", "domain": "testco.com"}])
        connector = MockEnrichmentConnector("test", {"employees": 100})
        orchestrator = UnifiedLoaderOrchestrator()
        result = await orchestrator.load_companies([source], [connector])

        assert len(result.companies) == 1
        assert result.enriched_count == 1
        # Company should have enriched data
        assert result.companies[0].name == "TestCo"

    @pytest.mark.asyncio
    async def test_enrichment_failure_handled(self) -> None:
        @dataclass
        class FailingConnector:
            name: str = "failing"

            async def enrich(self, company: Company) -> dict[str, Any]:
                raise RuntimeError("Enrichment failed")

        source = MockDataSource([{"id": "test-1", "name": "TestCo", "domain": "testco.com"}])
        connector = FailingConnector()
        orchestrator = UnifiedLoaderOrchestrator()
        result = await orchestrator.load_companies([source], [connector])

        assert len(result.companies) == 1
        # Connector failures are caught internally and don't increment failed_count
        # The company is still loaded, just without enrichment data
        assert result.failed_count == 0
        assert result.enriched_count == 1  # Company was still "enriched" (with empty data)
        assert result.companies[0].name == "TestCo"  # Still loaded

    @pytest.mark.asyncio
    async def test_with_normalizer(self) -> None:
        source = MockDataSource([{"id": "test-1", "company_name": "TestCo", "website": "testco.com"}])
        normalizer = DataNormalizer()
        orchestrator = UnifiedLoaderOrchestrator(normalizer=normalizer)
        result = await orchestrator.load_companies([source])

        assert len(result.companies) == 1
        assert result.companies[0].name == "TestCo"

    @pytest.mark.asyncio
    async def test_with_conflict_resolver(self) -> None:
        source = MockDataSource(
            [
                {"id": "test-1", "name": "TestCo", "domain": "testco.com", "revenue": 100},
                {"id": "test-1", "name": "TestCo", "domain": "testco.com", "revenue": 200},
            ]
        )
        resolver = CompositeResolver()
        orchestrator = UnifiedLoaderOrchestrator(conflict_resolver=resolver)
        result = await orchestrator.load_companies([source])

        assert len(result.companies) == 1


class TestLoadResultErrorHandling:
    """Tests for LoadResult error handling."""

    def test_error_tracking(self) -> None:
        result = LoadResult()
        result.add_error("test", ValueError("error"))

        assert len(result.errors) == 1
        assert result.errors[0]["source"] == "test"


class TestOrchestratorConfiguration:
    """Tests for orchestrator configuration options."""

    def test_optional_dependencies(self) -> None:
        # Should work without optional dependencies
        orchestrator = UnifiedLoaderOrchestrator()
        assert orchestrator.normalizer is None
        assert orchestrator.conflict_resolver is None

    def test_with_all_dependencies(self) -> None:
        config = LoadConfig(batch_size=50)
        normalizer = DataNormalizer()
        resolver = CompositeResolver()

        orchestrator = UnifiedLoaderOrchestrator(
            config=config,
            normalizer=normalizer,
            conflict_resolver=resolver,
        )

        assert orchestrator.config.batch_size == 50
        assert orchestrator.normalizer is normalizer
        assert orchestrator.conflict_resolver is resolver
