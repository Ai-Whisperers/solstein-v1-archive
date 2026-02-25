"""Tests for adapter protocols."""

import pytest

from solstein.adapters.protocols import (
    DiscoverySource,
    EnrichmentSource,
    FactAggregator,
    UnifiedDataSource,
)
from solstein.domain.models import DataSourceType, RawDataSource
from solstein.infrastructure.conflict_resolution import SourceAuthority
from solstein.research.discovery import DiscoveryCandidate


class MockDiscoverySource:
    """Mock implementation of DiscoverySource protocol."""

    @property
    def source_name(self) -> str:
        return "mock_discovery"

    def discover(
        self,
        market: str,
        seed_company: str,
        max_results: int = 50,
        extra_keywords: list[str] | None = None,
    ) -> list[DiscoveryCandidate]:
        return []


class MockEnrichmentSource:
    """Mock implementation of EnrichmentSource protocol."""

    @property
    def source_name(self) -> str:
        return "mock_enrichment"

    @property
    def source_type(self) -> DataSourceType:
        return DataSourceType.YAHOO_FINANCE

    def enrich(
        self,
        company_id: str,
        company_name: str,
        ticker: str | None = None,
        website: str | None = None,
    ) -> RawDataSource:
        return RawDataSource(
            source_type=DataSourceType.YAHOO_FINANCE,
            source_name="mock",
            raw_content={},
        )

class TestDiscoverySourceProtocol:
    """Test DiscoverySource protocol runtime checkability."""

    def test_isinstance_check_passes(self):
        """Mock implementing DiscoverySource passes isinstance check."""
        mock = MockDiscoverySource()
        assert isinstance(mock, DiscoverySource)

    def test_missing_method_fails_isinstance(self):
        """Class missing required method fails isinstance check."""

        class Incomplete:
            @property
            def source_name(self):
                return "incomplete"

        incomplete = Incomplete()
        assert not isinstance(incomplete, DiscoverySource)


class TestEnrichmentSourceProtocol:
    """Test EnrichmentSource protocol (original interface)."""

    def test_isinstance_check_passes(self):
        """Mock implementing EnrichmentSource passes isinstance check."""
        mock = MockEnrichmentSource()
        assert isinstance(mock, EnrichmentSource)

    def test_missing_method_fails_isinstance(self):
        """Class missing enrich method fails isinstance check."""

        class IncompleteEnrichment:
            @property
            def source_name(self):
                return "incomplete"

            @property
            def source_type(self):
                return DataSourceType.YAHOO_FINANCE

        incomplete = IncompleteEnrichment()
        assert not isinstance(incomplete, EnrichmentSource)

class TestUnifiedDataSourceProtocol:
    """Test UnifiedDataSource protocol."""

    def test_unified_protocol_includes_all_methods(self):
        """Unified protocol has discovery, enrichment, and refresh methods."""
        # MockEnrichmentSource doesn't have discover, so it shouldn't match
        mock = MockEnrichmentSource()
        assert not isinstance(mock, UnifiedDataSource)

    def test_full_implementation_passes_check(self):
        """Class with all methods passes UnifiedDataSource check."""

        class FullImplementation:
            @property
            def source_name(self):
                return "full"

            @property
            def source_type(self):
                return DataSourceType.YAHOO_FINANCE

            def discover(self, market, seed_company, max_results=50, extra_keywords=None):
                return []

            def enrich(self, company_id, company_name, ticker=None, website=None):
                return RawDataSource(
                    source_type=DataSourceType.YAHOO_FINANCE,
                    source_name="full",
                    raw_content={},
                )

            def refresh(self, company_ids, start_date=None, end_date=None):
                return []

            def get_confidence(self):
                return 0.9

            def get_authority(self):
                return SourceAuthority.SEC_EDGAR

            def supports_incremental(self):
                return True

            def supports_discovery(self):
                return True

        full = FullImplementation()
        assert isinstance(full, UnifiedDataSource)
