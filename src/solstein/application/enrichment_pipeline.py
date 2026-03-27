"""Enrichment pipeline — orchestrates all data source adapters.

The ``EnrichmentPipeline`` calls every registered enrichment adapter in
parallel for a given company and merges the results into a single
``AggregatedDataRecord``.  Errors in individual adapters are isolated so
one failing source never blocks the rest.

Usage::

    from solstein.application.enrichment_pipeline import EnrichmentPipeline
    from solstein.adapters.registry import build_default_registry
    from solstein.config import get_settings

    registry = build_default_registry(get_settings())
    pipeline = EnrichmentPipeline(registry)

    record = await pipeline.enrich("stripe-inc", "Stripe")
    logger.info(f"Confidence score: {record.confidence_score}")
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Any

from loguru import logger

from solstein.adapters.registry import SourceRegistry
from solstein.domain.models import AggregatedDataRecord, AggregatedFact, RawDataSource


class EnrichmentPipeline:
    """Parallel enrichment orchestrator.

    Runs all registered enrichment adapters concurrently and returns a
    merged ``AggregatedDataRecord`` with quality metrics.

    Args:
        registry: Source registry providing ``all_enrichment_sources``.
        timeout_s: Per-adapter timeout in seconds (default: 30).
        max_concurrent: Max parallel adapter calls (semaphore limit).
    """

    def __init__(
        self,
        registry: SourceRegistry,
        timeout_s: float = 30.0,
        max_concurrent: int = 8,
    ) -> None:
        self._registry = registry
        self._timeout_s = timeout_s
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def enrich(
        self,
        company_id: str,
        company_name: str,
        ticker: str | None = None,
        website: str | None = None,
    ) -> AggregatedDataRecord:
        """Enrich a single company using all registered adapters.

        Args:
            company_id: Internal company identifier.
            company_name: Human-readable company name.
            ticker: Optional stock ticker symbol.
            website: Optional company website URL.

        Returns:
            Merged ``AggregatedDataRecord`` with results from all adapters
            and quality metrics (confidence, completeness, source count).
        """
        sources = self._registry.all_enrichment_sources
        if not sources:
            logger.warning("No enrichment sources registered, returning empty record")
            return AggregatedDataRecord(
                company_id=company_id,
                gathering_batch_id=str(uuid.uuid4()),
                facts=[],
            )

        logger.info(
            "Enrichment pipeline started",
            company_id=company_id,
            sources=len(sources),
        )

        # Run all adapters in parallel under a concurrency semaphore
        tasks = [
            self._call_adapter(
                source=source,
                company_id=company_id,
                company_name=company_name,
                ticker=ticker,
                website=website,
            )
            for source in sources
        ]
        raw_sources: list[RawDataSource | None] = await asyncio.gather(*tasks, return_exceptions=False)

        # Merge successful results
        successful = [r for r in raw_sources if r is not None]
        logger.info(
            "Enrichment pipeline complete",
            company_id=company_id,
            success=len(successful),
            failed=len(raw_sources) - len(successful),
        )

        return self._merge(company_id, company_name, successful)

    async def _call_adapter(
        self,
        source: Any,
        company_id: str,
        company_name: str,
        ticker: str | None,
        website: str | None,
    ) -> RawDataSource | None:
        """Call a single adapter with timeout and error isolation."""
        adapter_name = getattr(source, "source_name", type(source).__name__)
        async with self._semaphore:
            try:
                enrich_fn = getattr(source, "enrich", None)
                if enrich_fn is None:
                    logger.debug("Adapter has no enrich() method, skipping", adapter=adapter_name)
                    return None

                # Support both sync and async adapters
                if asyncio.iscoroutinefunction(enrich_fn):
                    result = await asyncio.wait_for(
                        enrich_fn(
                            company_id=company_id,
                            company_name=company_name,
                            ticker=ticker,
                            website=website,
                        ),
                        timeout=self._timeout_s,
                    )
                else:
                    result = await asyncio.wait_for(
                        asyncio.to_thread(
                            enrich_fn,
                            company_id=company_id,
                            company_name=company_name,
                            ticker=ticker,
                            website=website,
                        ),
                        timeout=self._timeout_s,
                    )

                logger.debug("Adapter succeeded", adapter=adapter_name)
                return result if isinstance(result, RawDataSource) else None
            except TimeoutError:
                logger.warning("Adapter timed out", adapter=adapter_name, timeout_s=self._timeout_s)
                return None
            except Exception as exc:
                logger.error("Adapter failed", adapter=adapter_name, error=str(exc))
                return None

    def _merge(
        self,
        company_id: str,
        company_name: str,
        sources: list[RawDataSource],
    ) -> AggregatedDataRecord:
        """Merge multiple RawDataSource results into a single AggregatedDataRecord.

        Each RawDataSource is converted to an AggregatedFact with source
        attribution and metadata preserved.  Quality metrics (total_facts,
        verified_facts, average_confidence, data_completeness_percentage) are
        computed after all facts are assembled.
        """
        total_registered = len(self._registry.all_enrichment_sources)
        facts: list[AggregatedFact] = []
        for src in sources:
            source_id = src.url or src.source_name
            fact = AggregatedFact(
                fact_type=src.source_type.value if hasattr(src.source_type, "value") else str(src.source_type),
                value=src.raw_content,
                confidence=src.confidence,
                sources_used=[source_id] if source_id else [src.source_name],
            )
            facts.append(fact)

        record = AggregatedDataRecord(
            company_id=company_id,
            gathering_batch_id=str(uuid.uuid4()),
            facts=facts,
        )
        record.update_quality_metrics()
        # Compute data completeness as the fraction of registered sources that
        # returned usable data.
        if total_registered > 0:
            record.data_completeness_percentage = (len(sources) / total_registered) * 100.0
        return record
