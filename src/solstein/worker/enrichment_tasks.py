"""Enrichment async tasks for company data.

Extracted from worker_tasks.py as part of EPIC-021 file splitting.
Provides Celery tasks for enriching company data from external sources.
"""

from __future__ import annotations

import traceback
from datetime import datetime, timezone

from celery import Task
from celery.exceptions import MaxRetriesExceededError
from loguru import logger

from solstein.celery_config import celery_app

from .base import dead_letter_queue


class EnrichmentTask(Task):
    """Base task class for enrichment operations with result tracking."""

    def on_success(self, result, task_id, args, kwargs):
        """Called on task success - log completion."""
        company_id = args[0] if args else kwargs.get("company_id", "unknown")
        logger.info(f"[EnrichmentTask] Task {task_id} succeeded for company {company_id}")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called on task failure - log with full traceback."""
        company_id = args[0] if args else kwargs.get("company_id", "unknown")
        logger.error(
            f"[EnrichmentTask] Task {task_id} failed for company {company_id}: {exc}\n{einfo}"
        )


@celery_app.task(base=EnrichmentTask, bind=True, max_retries=3)
def enrich_company_async(
    self, company_id: str, company_name: str | None = None, sources: list[str] | None = None, user_id: str | None = None
):
    """Asynchronously enrich a single company (Phase 12).

    Phase 13.4: Implements exponential backoff retry logic

    Args:
        company_id: Company identifier
        company_name: Company name (optional)
        sources: List of enrichment sources (default: ['SEC_EDGAR'])
        user_id: User who requested enrichment (optional)

    Returns:
        Dict with enrichment results
    """
    try:
        import time

        from solstein.data.unified_loader import UnifiedCompany, unified_loader

        sources = sources or ["SEC_EDGAR"]
        start_time = time.time()

        # Perform enrichment
        company = UnifiedCompany(id=company_id, name=company_name or company_id)
        enriched = unified_loader.enrich_from_connectors(company)

        duration_ms = (time.time() - start_time) * 1000

        # Track enriched fields
        fields_enriched = []
        if enriched.financials and enriched.financials.revenue:
            fields_enriched.append("revenue")
        if enriched.financials and enriched.financials.employees:
            fields_enriched.append("employees")
        if enriched.financials and enriched.financials.growth_rate:
            fields_enriched.append("growth_rate")

        return {
            "task_id": self.request.id,
            "company_id": company_id,
            "company_name": enriched.name or company_name or company_id,
            "status": "SUCCESS",
            "sources_used": sources,
            "fields_enriched": fields_enriched,
            "duration_ms": duration_ms,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "enriched_data": {
                "revenue": enriched.financials.revenue if enriched.financials else None,
                "employees": enriched.financials.employees if enriched.financials else None,
                "growth_rate": enriched.financials.growth_rate if enriched.financials else None,
                "profit_margin": enriched.financials.profit_margin if enriched.financials else None,
            },
        }

    except Exception as exc:
        # Phase 13.4: Exponential backoff retry
        countdown = 5 * (2**self.request.retries)
        logger.info(
            f"[RETRY-ATTEMPT-{self.request.retries + 1}] Enrichment for {company_id} will retry in {countdown}s"
        )

        try:
            self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            dead_letter_queue.record_failure(
                "enrich_company_async", self.request.id, f"{exc}\n{tb}", self.request.retries + 1
            )
            return {
                "task_id": self.request.id,
                "company_id": company_id,
                "company_name": company_name,
                "status": "FAILED",
                "error": str(exc),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }


@celery_app.task(bind=True, max_retries=3)
def enrich_companies_batch_async(
    self, companies: list[dict], sources: list[str] | None = None, batch_size: int = 10, user_id: str | None = None
):
    """Asynchronously enrich multiple companies in batches (Phase 12).

    Phase 13.4: Implements exponential backoff retry logic

    Args:
        companies: List of company dicts with 'id' and 'name' keys
        sources: List of enrichment sources
        batch_size: Number of companies per batch
        user_id: User who requested enrichment

    Returns:
        Dict with batch enrichment results
    """
    try:
        import time

        from solstein.data.unified_loader import UnifiedCompany, unified_loader

        sources = sources or ["SEC_EDGAR"]
        start_time = time.time()
        batch_results = []
        failed_count = 0

        # Process companies
        for i, company_data in enumerate(companies):
            try:
                company_id = company_data.get("id")
                company_name = company_data.get("name", company_id)

                company = UnifiedCompany(id=company_id, name=company_name)
                enriched = unified_loader.enrich_from_connectors(company)

                batch_results.append(
                    {
                        "company_id": company_id,
                        "company_name": enriched.name or company_name,
                        "status": "SUCCESS",
                    }
                )

            except Exception as e:
                failed_count += 1
                batch_results.append(
                    {
                        "company_id": company_data.get("id"),
                        "company_name": company_data.get("name"),
                        "status": "FAILED",
                        "error": str(e),
                    }
                )

        duration_ms = (time.time() - start_time) * 1000

        return {
            "task_id": self.request.id,
            "total": len(companies),
            "successful": len(companies) - failed_count,
            "failed": failed_count,
            "results": batch_results,
            "duration_ms": duration_ms,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as exc:
        # Phase 13.4: Exponential backoff retry
        countdown = 5 * (2**self.request.retries)
        logger.info(f"[RETRY-ATTEMPT-{self.request.retries + 1}] Batch enrichment will retry in {countdown}s")

        try:
            self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            dead_letter_queue.record_failure(
                "enrich_companies_batch_async", self.request.id, f"{exc}\n{tb}", self.request.retries + 1
            )
            return {
                "task_id": self.request.id,
                "status": "FAILED",
                "error": str(exc),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
