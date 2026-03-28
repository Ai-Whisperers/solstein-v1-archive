"""Instrumented adapter wrappers for health telemetry.

Transparent decorators around DiscoverySource and EnrichmentSource
that record per-call timing, success/failure, and data shape without
modifying any adapter implementation or ``enrich_company()`` logic.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from solstein.adapters.logging import log_adapter_error
from solstein.adapters.protocols import DiscoverySource, EnrichmentSource
from solstein.domain.models import DataSourceType, RawDataSource
from solstein.research.discovery import DiscoveryCandidate


@dataclass
class AdapterHealthRecord:
    """Per-invocation health record for one adapter call."""

    adapter_name: str
    adapter_type: str  # "enrichment" | "discovery"
    status: str  # "success" | "error"
    response_time_ms: float
    error_message: str | None = None
    data_item_count: int = 0
    confidence: float = 0.0
    company_id: str | None = None
    company_name: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class InstrumentedEnrichmentSource:
    """Transparent wrapper that records timing and health for an EnrichmentSource."""

    def __init__(self, inner: EnrichmentSource) -> None:
        self._inner = inner
        self._records: list[AdapterHealthRecord] = []

    @property
    def source_name(self) -> str:
        return self._inner.source_name

    @property
    def source_type(self) -> DataSourceType:
        return self._inner.source_type

    @property
    def health_records(self) -> list[AdapterHealthRecord]:
        return list(self._records)

    def enrich(
        self,
        company_id: str,
        company_name: str,
        ticker: str | None = None,
        website: str | None = None,
    ) -> RawDataSource:
        start = time.perf_counter()
        try:
            result = self._inner.enrich(company_id, company_name, ticker, website)
            elapsed_ms = (time.perf_counter() - start) * 1000
            content = result.raw_content
            item_count = len(content) if isinstance(content, (dict, list)) else 1
            self._records.append(
                AdapterHealthRecord(
                    adapter_name=self._inner.source_name,
                    adapter_type="enrichment",
                    status="success",
                    response_time_ms=round(elapsed_ms, 1),
                    data_item_count=item_count,
                    confidence=result.confidence,
                    company_id=company_id,
                    company_name=company_name,
                )
            )
            return result
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start) * 1000
            self._records.append(
                AdapterHealthRecord(
                    adapter_name=self._inner.source_name,
                    adapter_type="enrichment",
                    status="error",
                    response_time_ms=round(elapsed_ms, 1),
                    error_message=str(exc),
                    company_id=company_id,
                    company_name=company_name,
                )
            )
            log_adapter_error(
                component=f"Instrumented:{self._inner.source_name}",
                operation="enrich",
                error=exc,
                entity_id=company_id,
                entity_name=company_name,
            )
            raise


class InstrumentedDiscoverySource:
    """Transparent wrapper that records timing and health for a DiscoverySource."""

    def __init__(self, inner: DiscoverySource) -> None:
        self._inner = inner
        self._records: list[AdapterHealthRecord] = []

    @property
    def source_name(self) -> str:
        return self._inner.source_name

    @property
    def health_records(self) -> list[AdapterHealthRecord]:
        return list(self._records)

    def discover(
        self,
        market: str,
        seed_company: str,
        max_results: int = 50,
        extra_keywords: list[str] | None = None,
    ) -> list[DiscoveryCandidate]:
        start = time.perf_counter()
        try:
            results = self._inner.discover(market, seed_company, max_results, extra_keywords)
            elapsed_ms = (time.perf_counter() - start) * 1000
            self._records.append(
                AdapterHealthRecord(
                    adapter_name=self._inner.source_name,
                    adapter_type="discovery",
                    status="success",
                    response_time_ms=round(elapsed_ms, 1),
                    data_item_count=len(results),
                    confidence=1.0,
                )
            )
            return results
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start) * 1000
            self._records.append(
                AdapterHealthRecord(
                    adapter_name=self._inner.source_name,
                    adapter_type="discovery",
                    status="error",
                    response_time_ms=round(elapsed_ms, 1),
                    error_message=str(exc),
                )
            )
            log_adapter_error(
                component=f"Instrumented:{self._inner.source_name}",
                operation="discover",
                error=exc,
                entity_name=seed_company,
            )
            raise


def build_instrumented_registry(
    settings: Any,
) -> tuple[Any, list[InstrumentedEnrichmentSource], list[InstrumentedDiscoverySource]]:
    """Build a registry where all adapters are wrapped with instrumentation.

    Returns (registry, enrichment_wrappers, discovery_wrappers) so callers
    can inspect health_records after the pipeline run.
    """
    from solstein.adapters.registry import SourceRegistry, build_default_registry

    base_registry = build_default_registry(settings)
    instrumented = SourceRegistry()
    enrichment_wrappers: list[InstrumentedEnrichmentSource] = []
    discovery_wrappers: list[InstrumentedDiscoverySource] = []

    for source in base_registry.discovery_sources:
        wrapper = InstrumentedDiscoverySource(source)
        instrumented.register_discovery(wrapper)
        discovery_wrappers.append(wrapper)

    for source in base_registry.enrichment_sources:
        wrapper = InstrumentedEnrichmentSource(source)
        instrumented.register_enrichment(wrapper)
        enrichment_wrappers.append(wrapper)

    return instrumented, enrichment_wrappers, discovery_wrappers
