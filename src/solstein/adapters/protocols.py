"""Protocol definitions for pluggable data source adapters.

Three protocols cover all data source modules:

- DiscoverySource: produces company candidates for a given market
- EnrichmentSource: enriches a known company with factual data from one source
- FactAggregator: cross-references multiple RawDataSource objects into
  verified AggregatedFact objects

Extended with refresh support for unified data source architecture.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol, runtime_checkable

from solstein.domain.models import (
    AggregatedDataRecord,
    DataSourceType,
    RawDataRecord,
    RawDataSource,
)
from solstein.infrastructure.conflict_resolution import SourceAuthority
from solstein.research.discovery import DiscoveryCandidate


@runtime_checkable
class DiscoverySource(Protocol):
    """Provides company candidates for a given market.

    Implementations wrap specific data backends (static catalogs,
    web search APIs, competitor JSON files) and return a list of
    DiscoveryCandidate objects that the pipeline deduplicates and
    scores for relevance.
    """

    @property
    def source_name(self) -> str:
        """Human-readable name for this source (e.g. 'static_catalog')."""
        ...

    def discover(
        self,
        market: str,
        seed_company: str,
        max_results: int = 50,
        extra_keywords: list[str] | None = None,
    ) -> list[DiscoveryCandidate]:
        """Return candidate companies for the target market."""
        ...


@runtime_checkable
class EnrichmentSource(Protocol):
    """Enriches a company profile with data from one source.

    Each implementation wraps a single data backend (Yahoo Finance,
    NewsAPI, patent search, etc.) and returns a RawDataSource object
    containing the raw fetched data.  Multiple EnrichmentSource
    adapters are composed by the gather stage to build a RawDataRecord.

    Extended with refresh support for unified data source architecture.
    """

    @property
    def source_name(self) -> str:
        """Human-readable name for this source (e.g. 'yahoo_finance')."""
        ...

    @property
    def source_type(self) -> DataSourceType:
        """DataSourceType enum value for this source."""
        ...

    def enrich(
        self,
        company_id: str,
        company_name: str,
        ticker: str | None = None,
        website: str | None = None,
    ) -> RawDataSource:
        """Fetch raw data for a single company.

        Returns a RawDataSource containing the raw API response or
        scraped content.  Raises if the source is unavailable or
        returns no data.
        """
        ...

    def refresh(
        self,
        company_ids: list[str],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Refresh facts for multiple companies.

        Fetches updated data for the given company IDs and returns
        a list of fact dictionaries. Implementations should support
        incremental refresh (only returning changed data) when
        supports_incremental() returns True.

        Args:
            company_ids: List of company IDs to refresh
            start_date: Optional start date for data range
            end_date: Optional end date for data range

        Returns:
            List of fact dictionaries with updated data
        """
        ...

    def get_confidence(self) -> float:
        """Return the base confidence score for this source (0.0-1.0).

        This is the default confidence level for facts from this source
        before any calibration. Higher values indicate more trustworthy
        sources (e.g., SEC EDGAR = 0.95, News = 0.72).
        """
        ...

    def get_authority(self) -> SourceAuthority:
        """Return the authority level for this source.

        Authority determines priority when resolving conflicts between
        sources. Sources with higher authority win when facts disagree.
        """
        ...

    def supports_incremental(self) -> bool:
        """Return True if this source supports incremental refresh.

        Incremental refresh means the source can efficiently detect
        and return only changed data since a given timestamp, rather
        than fetching all data every time.
        """
        ...


@runtime_checkable
class FactAggregator(Protocol):
    """Aggregates raw data from multiple sources into verified facts.

    Takes a RawDataRecord (multiple RawDataSource objects for one
    company) and produces an AggregatedDataRecord with cross-referenced,
    deduplicated facts including agreement percentages and contradiction
    tracking.
    """

    def aggregate(
        self,
        company_id: str,
        raw_record: RawDataRecord,
    ) -> AggregatedDataRecord:
        """Cross-reference sources and return aggregated facts."""
        ...


@runtime_checkable
class UnifiedDataSource(Protocol):
    """Unified protocol for data sources supporting discovery, enrichment, and refresh.

    This protocol combines DiscoverySource and EnrichmentSource capabilities
    with refresh support for a complete data source interface. All data
    sources in the system should implement this protocol for consistency.

    Implementations include:
    - SEC EDGAR (financial filings)
    - Companies House (UK corporate data)
    - Yahoo Finance (market data)
    - News sources (market signals)
    - GitHub (technical metrics)
    - Patents (IP data)
    - Website scraping
    - LinkedIn (professional data)
    """

    @property
    def source_name(self) -> str:
        """Human-readable name for this source."""
        ...

    @property
    def source_type(self) -> DataSourceType:
        """DataSourceType enum value for this source."""
        ...

    def discover(
        self,
        market: str,
        seed_company: str,
        max_results: int = 50,
        extra_keywords: list[str] | None = None,
    ) -> list[DiscoveryCandidate]:
        """Return candidate companies for the target market (if supported)."""
        ...

    def enrich(
        self,
        company_id: str,
        company_name: str,
        ticker: str | None = None,
        website: str | None = None,
    ) -> RawDataSource:
        """Fetch raw data for a single company."""
        ...

    def refresh(
        self,
        company_ids: list[str],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Refresh facts for multiple companies."""
        ...

    def get_confidence(self) -> float:
        """Return the base confidence score (0.0-1.0)."""
        ...

    def get_authority(self) -> SourceAuthority:
        """Return the authority level for conflict resolution."""
        ...

    def supports_incremental(self) -> bool:
        """Return True if incremental refresh is supported."""
        ...

    def supports_discovery(self) -> bool:
        """Return True if this source supports company discovery."""
        ...
