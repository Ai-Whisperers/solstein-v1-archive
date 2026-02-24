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
    """Mock implementation of EnrichmentSource protocol with refresh support."""

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

    def refresh(
        self,
        company_ids: list[str],
        start_date=None,
        end_date=None,
    ) -> list[dict]:
        return []

    def get_confidence(self) -> float:
        return 0.85

    def get_authority(self) -> SourceAuthority:
        return SourceAuthority.YAHOO_FINANCE

    def supports_incremental(self) -> bool:
        return True


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
    """Test EnrichmentSource protocol with refresh extensions."""

    def test_isinstance_check_passes(self):
        """Mock implementing full EnrichmentSource passes isinstance check."""
        mock = MockEnrichmentSource()
        assert isinstance(mock, EnrichmentSource)

    def test_refresh_method_exists(self):
        """EnrichmentSource protocol includes refresh method."""
        mock = MockEnrichmentSource()
        assert hasattr(mock, "refresh")
        assert callable(mock.refresh)

    def test_get_confidence_method_exists(self):
        """EnrichmentSource protocol includes get_confidence method."""
        mock = MockEnrichmentSource()
        assert hasattr(mock, "get_confidence")
        assert mock.get_confidence() == 0.85

    def test_get_authority_method_exists(self):
        """EnrichmentSource protocol includes get_authority method."""
        mock = MockEnrichmentSource()
        assert hasattr(mock, "get_authority")
        assert mock.get_authority() == SourceAuthority.YAHOO_FINANCE

    def test_supports_incremental_method_exists(self):
        """EnrichmentSource protocol includes supports_incremental method."""
        mock = MockEnrichmentSource()
        assert hasattr(mock, "supports_incremental")
        assert mock.supports_incremental() is True


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
