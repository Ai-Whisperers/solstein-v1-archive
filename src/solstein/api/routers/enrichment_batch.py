"""Batch enrichment endpoint.

EPIC-021: Modularized from enrichment.py.
"""

from __future__ import annotations

import time
from datetime import datetime

from fastapi import HTTPException, Request

from solstein.api.schemas.enrichment import (
    BatchEnrichmentMetrics,
    BatchEnrichmentRequest,
    BatchEnrichmentResponse,
    BatchEnrichmentResult,
)
from solstein.data.security_hardening import input_validator, rate_limiter
from solstein.data.unified.batch_outcomes import BatchEnrichmentOutcome
from solstein.data.unified_loader import UnifiedCompany

from .enrichment_base import get_client_id, logger, router, unified_loader


@router.post("/companies/enrich/batch", response_model=BatchEnrichmentResponse)
async def enrich_batch(request_data: BatchEnrichmentRequest, request: Request) -> BatchEnrichmentResponse:
    """Batch enrich multiple companies with caching and optimization."""
    client_id = get_client_id(request)
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    for company_id in request_data.company_ids:
        is_valid, _ = input_validator.validate_company_id(company_id)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid company ID: {company_id}")

    logger.info(f"📦 Batch enriching {len(request_data.company_ids)} companies")

    try:
        start_time = time.time()
        companies = [UnifiedCompany(id=cid, name=cid) for cid in request_data.company_ids]
        enriched_companies: list[BatchEnrichmentOutcome] = unified_loader.enrich_batch(
            companies, batch_size=request_data.batch_size
        )
        total_duration_ms = int((time.time() - start_time) * 1000)

        results: list[BatchEnrichmentResult] = []
        failed_count = 0
        cache_hits = 0
        per_company_ms = total_duration_ms // len(enriched_companies) if enriched_companies else 0
        for outcome in enriched_companies:
            if outcome.status != "success":
                failed_count += 1
            if outcome.from_cache:
                cache_hits += 1

            errors = list(getattr(outcome, "errors", []))
            results.append(
                BatchEnrichmentResult(
                    company_id=outcome.company.id,
                    company_name=getattr(outcome.company, "name", None),
                    status=outcome.status,
                    duration_ms=per_company_ms,
                    source="batch_enrichment_cache" if outcome.from_cache else "batch_enrichment",
                    error="; ".join(errors)[:1000] if errors else None,
                    errors=errors,
                    from_cache=outcome.from_cache,
                )
            )

        enriched_count = len(results) - failed_count
        cache_misses = len(results) - cache_hits
        success_rate = (enriched_count / len(results) * 100.0) if results else 0.0

        return BatchEnrichmentResponse(
            status="partial" if failed_count else "success",
            batch_id=f"batch_{datetime.now().timestamp()}",
            total_companies=len(request_data.company_ids),
            enriched_count=enriched_count,
            failed_count=failed_count,
            results=results,
            metrics=BatchEnrichmentMetrics(
                total_duration_ms=total_duration_ms,
                avg_duration_ms=total_duration_ms // len(request_data.company_ids) if request_data.company_ids else 0,
                cache_hits=cache_hits,
                cache_misses=cache_misses,
                success_rate=round(success_rate, 1),
            ),
        )

    except Exception as e:
        logger.error(f"Batch enrichment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
