"""Unified loader orchestration layer.

E1: Extract orchestration layer from unified_loader.py
Orchestrates the data loading pipeline: discovery, enrichment, merging, and persistence.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Protocol

from loguru import logger

from solstein.data.conflict_resolution import FieldConflict
from solstein.domain.models import Company


class DataSourceAdapter(Protocol):
    """Protocol for data source adapters."""

    async def fetch(self, query: dict[str, Any]) -> list[dict[str, Any]]:
        """Fetch data from the source."""
        ...


class EnrichmentConnector(Protocol):
    """Protocol for enrichment connectors."""

    name: str

    async def enrich(self, company: Company) -> dict[str, Any]:
        """Enrich a company with additional data."""
        ...


class Normalizer(Protocol):
    """Protocol for data normalizers."""

    def normalize(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """Normalize raw data to standard format."""
        ...


class ConflictResolver(Protocol):
    """Protocol for conflict resolution strategies."""

    def resolve(self, existing: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
        """Resolve conflicts between existing and incoming data."""
        ...


@dataclass(frozen=True)
class LoadConfig:
    """Configuration for the loading pipeline."""

    batch_size: int = 100
    max_concurrent_enrichment: int = 10
    enable_conflict_resolution: bool = True
    enrichment_timeout_seconds: float = 30.0
    retry_attempts: int = 3


@dataclass
class LoadResult:
    """Result of a loading operation."""

    companies: list[Company] = field(default_factory=list)
    enriched_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0
    errors: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_error(self, source: str, error: Exception, context: dict[str, Any] | None = None) -> None:
        """Add an error to the result."""
        self.errors.append(
            {
                "source": source,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context or {},
            }
        )


class UnifiedLoaderOrchestrator:
    """Orchestrates the unified data loading pipeline.

    E1: Extracted from unified_loader.py to separate orchestration concerns.
    """

    def __init__(
        self,
        config: LoadConfig | None = None,
        normalizer: Normalizer | None = None,
        conflict_resolver: ConflictResolver | None = None,
    ) -> None:
        self.config = config or LoadConfig()
        self.normalizer = normalizer
        self.conflict_resolver = conflict_resolver
        self._enrichment_semaphore: asyncio.Semaphore | None = None

    async def load_companies(
        self,
        sources: list[DataSourceAdapter],
        connectors: list[EnrichmentConnector] | None = None,
    ) -> LoadResult:
        """Load companies from multiple sources with optional enrichment.

        Args:
            sources: Data source adapters to fetch from
            connectors: Optional enrichment connectors

        Returns:
            LoadResult with loaded companies and metadata
        """
        result = LoadResult()
        all_raw_data: list[dict[str, Any]] = []

        # Phase 1: Discovery - fetch from all sources
        logger.info("Starting discovery phase", source_count=len(sources))
        for source in sources:
            try:
                raw = await source.fetch({})
                all_raw_data.extend(raw)
                logger.debug("Fetched from source", count=len(raw))
            except Exception as e:
                logger.error("Source fetch failed", source=type(source).__name__, error=str(e))
                result.add_error("discovery", e, {"source_type": type(source).__name__})

        # Phase 2: Normalization
        logger.info("Starting normalization phase", record_count=len(all_raw_data))
        normalized: list[dict[str, Any]] = []
        for record in all_raw_data:
            try:
                if self.normalizer:
                    normalized.append(self.normalizer.normalize(record))
                else:
                    normalized.append(record)
            except Exception as e:
                logger.warning("Normalization failed", error=str(e))
                result.add_error("normalization", e, {"record_preview": str(record)[:100]})

        # Phase 3: Merge and deduplicate
        logger.info("Starting merge phase", record_count=len(normalized))
        merged = self._merge_records(normalized)

        # Phase 4: Enrichment (if connectors provided)
        if connectors:
            logger.info("Starting enrichment phase", connector_count=len(connectors))
            companies = await self._enrich_companies(merged, connectors, result)
        else:
            companies = [Company(**record) for record in merged]

        result.companies = companies
        logger.info(
            "Load complete",
            total=len(companies),
            enriched=result.enriched_count,
            failed=result.failed_count,
        )
        return result

    def _merge_records(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Merge and deduplicate records.

        Groups records by company identifier and merges conflicting data.
        """
        if not records:
            return []

        # Group by identifier (name + domain as fallback)
        groups: dict[str, list[dict[str, Any]]] = {}
        for record in records:
            key = self._get_company_key(record)
            groups.setdefault(key, []).append(record)

        # Merge each group
        merged: list[dict[str, Any]] = []
        for key, group in groups.items():
            if len(group) == 1:
                merged.append(group[0])
            else:
                merged_record = self._merge_group(group)
                merged.append(merged_record)

        return merged

    def _get_company_key(self, record: dict[str, Any]) -> str:
        """Generate a unique key for deduplication."""
        name = record.get("name", "").lower().strip()
        domain = record.get("domain", "").lower().strip()
        return f"{name}:{domain}" if domain else name

    def _merge_group(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        """Merge multiple records for the same company."""
        if not records:
            return {}

        # Start with the most complete record
        base = max(records, key=lambda r: len([v for v in r.values() if v is not None]))
        merged = dict(base)

        # Merge in data from other records
        for record in records:
            if record is base:
                continue
            for key, value in record.items():
                if value is None:
                    continue
                if key not in merged or merged[key] is None:
                    merged[key] = value
                elif self.conflict_resolver and merged[key] != value:
                    conflict = FieldConflict(
                        field_name=key,
                        existing_value=merged[key],
                        incoming_value=value,
                    )
                    resolution = self.conflict_resolver.resolve(conflict)
                    merged[key] = resolution.resolved_value

        return merged

    async def _enrich_companies(
        self,
        records: list[dict[str, Any]],
        connectors: list[EnrichmentConnector],
        result: LoadResult,
    ) -> list[Company]:
        """Enrich records with data from connectors."""
        if self._enrichment_semaphore is None:
            self._enrichment_semaphore = asyncio.Semaphore(self.config.max_concurrent_enrichment)

        companies: list[Company] = []

        for record in records:
            try:
                company = await self._enrich_single(record, connectors)
                companies.append(company)
                result.enriched_count += 1
            except Exception as e:
                logger.error("Enrichment failed", company=record.get("name"), error=str(e))
                result.failed_count += 1
                result.add_error("enrichment", e, {"company": record.get("name")})
                # Still include the company without enrichment
                companies.append(Company(**record))

        return companies

    async def _enrich_single(
        self,
        record: dict[str, Any],
        connectors: list[EnrichmentConnector],
    ) -> Company:
        """Enrich a single company with all connectors."""
        enriched_data = dict(record)

        async def enrich_with_connector(conn: EnrichmentConnector) -> dict[str, Any]:
            async with self._enrichment_semaphore:  # type: ignore
                try:
                    return await asyncio.wait_for(
                        conn.enrich(Company(**record)),
                        timeout=self.config.enrichment_timeout_seconds,
                    )
                except asyncio.TimeoutError:
                    logger.warning(
                        "Enrichment timeout",
                        connector=conn.name,
                        company=record.get("name"),
                    )
                    return {}
                except Exception as e:
                    logger.error(
                        "Enrichment error",
                        connector=conn.name,
                        company=record.get("name"),
                        error=str(e),
                    )
                    return {}

        # Run all connectors concurrently
        tasks = [enrich_with_connector(conn) for conn in connectors]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Merge enrichment results
        for conn, res in zip(connectors, results):
            if isinstance(res, Exception):
                continue
            if isinstance(res, dict):
                for key, value in res.items():
                    if value is not None and (key not in enriched_data or enriched_data[key] is None):
                        enriched_data[key] = value

        return Company(**enriched_data)
