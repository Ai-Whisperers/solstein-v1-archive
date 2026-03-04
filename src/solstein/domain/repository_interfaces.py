"""Abstract repository interfaces for the domain layer.

These interfaces define the *what* of data access without coupling to any
persistence technology.  Infrastructure implementations (PostgreSQL,
in-memory, etc.) live in ``solstein.infrastructure`` and satisfy these
interfaces via duck-typing or explicit inheritance.

All methods are async-first to align with the FastAPI + asyncpg stack.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from solstein.domain.models import Company, RawDataSource
from solstein.domain.value_objects import CompanyId, DateRange

# ---------------------------------------------------------------------------
# Query filter / sort helpers
# ---------------------------------------------------------------------------


@dataclass
class CompanyQuery:
    """Structured query parameters for company listing.

    Attributes:
        tier: Filter by classification tier (``'Phoenix'``, ``'Salt'``, ``'Lead'``).
        industry: Exact-match industry filter.
        min_revenue: Minimum annual revenue in EUR.
        min_score: Minimum composite score (0–10).
        search: Full-text keyword search against name + description.
        limit: Maximum number of results to return.
        offset: Pagination offset.
        order_by: Field name to sort by (default: ``composite_score``).
        descending: Sort direction (``True`` = highest first).
    """

    tier: str | None = None
    industry: str | None = None
    min_revenue: float | None = None
    min_score: float | None = None
    search: str | None = None
    limit: int = 50
    offset: int = 0
    order_by: str = "composite_score"
    descending: bool = True


@dataclass
class Page:
    """A paginated result set.

    Attributes:
        items: The result items for this page.
        total: Total number of matching items across all pages.
        limit: Page size used for this query.
        offset: Offset used for this query.
    """

    items: list[Any]
    total: int
    limit: int
    offset: int

    @property
    def has_next(self) -> bool:
        return self.offset + self.limit < self.total

    @property
    def has_prev(self) -> bool:
        return self.offset > 0


# ---------------------------------------------------------------------------
# Company repository
# ---------------------------------------------------------------------------


class ICompanyRepository(ABC):
    """Abstract async repository for Company entities."""

    @abstractmethod
    async def get_by_id(self, company_id: CompanyId | str) -> Company | None:
        """Return a Company by its ID, or ``None`` if not found."""

    @abstractmethod
    async def get_all(self, query: CompanyQuery | None = None) -> Page:
        """Return a paginated list of companies matching *query*."""

    @abstractmethod
    async def save(self, company: Company) -> Company:
        """Persist *company* and return the saved entity (with any DB-assigned fields)."""

    @abstractmethod
    async def delete(self, company_id: CompanyId | str) -> bool:
        """Delete a company.  Return ``True`` if deleted, ``False`` if not found."""

    @abstractmethod
    async def search(self, query: str, limit: int = 20) -> list[Company]:
        """Full-text search against company name and description."""

    @abstractmethod
    async def count(self, query: CompanyQuery | None = None) -> int:
        """Return total number of companies matching *query*."""

    @abstractmethod
    async def bulk_upsert(self, companies: list[Company]) -> list[Company]:
        """Insert or update multiple companies in a single transaction."""


# ---------------------------------------------------------------------------
# Enrichment / raw-data repository
# ---------------------------------------------------------------------------


class IEnrichmentRepository(ABC):
    """Abstract async repository for raw enrichment data."""

    @abstractmethod
    async def save_raw_source(self, source: RawDataSource) -> RawDataSource:
        """Persist a raw data source record."""

    @abstractmethod
    async def get_raw_sources(
        self,
        company_id: CompanyId | str,
        since: datetime | None = None,
    ) -> list[RawDataSource]:
        """Return raw data sources for a company, optionally filtered by recency."""

    @abstractmethod
    async def delete_old_sources(
        self,
        company_id: CompanyId | str,
        older_than: datetime,
    ) -> int:
        """Delete stale raw sources.  Return number of rows deleted."""


# ---------------------------------------------------------------------------
# Analysis / insights repository
# ---------------------------------------------------------------------------


@dataclass
class AnalysisRecord:
    """A stored analysis result for a company.

    Attributes:
        company_id: The analysed company.
        analysis_type: E.g. ``'competitive'``, ``'financial'``, ``'market'``.
        period: Date range covered by the analysis.
        payload: Arbitrary JSON-serialisable result dict.
        created_at: Creation timestamp.
    """

    company_id: CompanyId
    analysis_type: str
    period: DateRange
    payload: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None


class IAnalysisRepository(ABC):
    """Abstract async repository for analysis results."""

    @abstractmethod
    async def save(self, record: AnalysisRecord) -> AnalysisRecord:
        """Persist an analysis record."""

    @abstractmethod
    async def get_latest(
        self,
        company_id: CompanyId | str,
        analysis_type: str,
    ) -> AnalysisRecord | None:
        """Return the most recent analysis of *analysis_type* for a company."""

    @abstractmethod
    async def list_for_company(
        self,
        company_id: CompanyId | str,
    ) -> list[AnalysisRecord]:
        """Return all analysis records for a company, newest first."""


__all__ = [
    "CompanyQuery",
    "Page",
    "ICompanyRepository",
    "IEnrichmentRepository",
    "IAnalysisRepository",
    "AnalysisRecord",
]
