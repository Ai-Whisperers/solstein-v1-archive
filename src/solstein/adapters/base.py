"""Abstract base class for all Solstein data source adapters.

Bridges three connector hierarchies under a unified interface that
satisfies the ``UnifiedDataSource`` protocol:

- ``data/connectors/``        — original fetch connectors
- ``infrastructure/connectors/`` — refresh connectors (delta detection)
- ``adapters/enrichment/``    — unified enrichment adapters

All concrete adapters should inherit from ``BaseDataSourceAdapter`` so
they are registered, typed, and interchangeable across the pipeline.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from solstein.domain.models import DataSourceType, RawDataSource
from solstein.infrastructure.conflict_resolution import SourceAuthority
from solstein.research.discovery import DiscoveryCandidate


class BaseDataSourceAdapter(ABC):
    """Abstract base for all data source adapters.

    Satisfies the ``UnifiedDataSource`` protocol from ``adapters.protocols``.
    Subclasses must implement all abstract methods/properties to be
    structurally compatible with the protocol and usable in the registry.

    **Hierarchy mapping**:

    .. code-block:: text

        BaseDataSourceAdapter (adapters/base.py)
        ├── Original connectors  (data/connectors/)
        │     Uses: enrich() + discover() — no refresh
        ├── Refresh connectors   (infrastructure/connectors/)
        │     Uses: refresh() — wraps BaseRefreshConnector.fetch_facts()
        └── Enrichment adapters  (adapters/enrichment/*_unified.py)
              Uses: enrich() + optional discover() + optional refresh()
    """

    # ------------------------------------------------------------------
    # Identity (required by UnifiedDataSource protocol)
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Human-readable name (e.g. ``'yahoo_finance'``)."""

    @property
    @abstractmethod
    def source_type(self) -> DataSourceType:
        """DataSourceType enum value for this adapter."""

    # ------------------------------------------------------------------
    # Core data operations (required by UnifiedDataSource protocol)
    # ------------------------------------------------------------------

    @abstractmethod
    def discover(
        self,
        market: str,
        seed_company: str,
        max_results: int = 50,
        extra_keywords: list[str] | None = None,
    ) -> list[DiscoveryCandidate]:
        """Return candidate companies for the target market.

        Sources that do not support discovery should return ``[]``.
        """

    @abstractmethod
    def enrich(
        self,
        company_id: str,
        company_name: str,
        ticker: str | None = None,
        website: str | None = None,
    ) -> RawDataSource:
        """Fetch raw data for a single company from this source."""

    @abstractmethod
    def refresh(
        self,
        company_ids: list[str],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Refresh facts for multiple companies (incremental update).

        Sources that do not support incremental refresh should return ``[]``.
        """

    # ------------------------------------------------------------------
    # Quality metadata (required by UnifiedDataSource protocol)
    # ------------------------------------------------------------------

    @abstractmethod
    def get_confidence(self) -> float:
        """Base confidence score for data from this source (0.0–1.0)."""

    @abstractmethod
    def get_authority(self) -> SourceAuthority:
        """Authority level used for conflict resolution."""

    @abstractmethod
    def supports_incremental(self) -> bool:
        """Return ``True`` if this adapter supports incremental refresh."""

    # ------------------------------------------------------------------
    # Convenience helpers (optional to override)
    # ------------------------------------------------------------------

    def is_healthy(self) -> bool:
        """Return ``True`` if the underlying data source is reachable."""
        return True

    def __repr__(self) -> str:
        return f"<{type(self).__name__} source={self.source_name!r}>"
