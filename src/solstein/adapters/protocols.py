"""Protocol definitions for pluggable data source adapters.

Three protocols cover all data source modules:

- DiscoverySource: produces company candidates for a given market
- EnrichmentSource: enriches a known company with factual data from one source
- FactAggregator: cross-references multiple RawDataSource objects into
  verified AggregatedFact objects
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from solstein.domain.models import (
    AggregatedDataRecord,
    DataSourceType,
    RawDataRecord,
    RawDataSource,
)
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
