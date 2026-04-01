"""Enrichment async tasks for company data.

Extracted from worker_tasks.py as part of EPIC-021 file splitting.
Provides Celery tasks for enriching company data from external sources.
"""

from __future__ import annotations

import traceback
from datetime import datetime, timezone
from typing import Any, NoReturn, cast

from celery import Task
from celery.exceptions import MaxRetriesExceededError
from loguru import logger

from solstein.celery_config import celery_app

from .base import dead_letter_queue
from .tenant_isolation import (
    task_tenant_context,
    validate_task_tenant_id,
)


def _build_failure_result(
    task_id: str | None,
    *,
    status: str,
    error: Exception,
    timestamp: str,
    extra: dict[str, str | None] | None = None,
) -> dict[str, str | None]:
    """Build a structured terminal task failure payload.

    Args:
        task_id: Celery task ID.
        status: Terminal status string (e.g. "FAILED").
        error: The exception that caused the failure.
        timestamp: ISO-format timestamp.
        extra: Optional additional fields (company_id, company_name, traceback, etc.).
    """
    payload: dict[str, str | None] = {
        "task_id": task_id,
        "status": status,
        "error": str(error),
        "error_type": type(error).__name__,
        "timestamp": timestamp,
    }
    if extra:
        payload.update(extra)
    return payload


def _retry_task(task: Task, *, exc: Exception, countdown: int) -> NoReturn:
    """Invoke Celery retry through a typed boundary."""
    raise cast(Any, task).retry(exc=exc, countdown=countdown)


def _handle_task_retry(
    task: Task,
    exc: Exception,
    *,
    task_name: str,
    context: dict[str, Any],
) -> dict[str, str | None]:
    """Handle exponential backoff retry, DLQ recording on max retries.

    Args:
        task: Celery Task instance (bind=True).
        exc: The exception that caused the failure.
        task_name: Task name for DLQ recording.
        context: Additional context for DLQ.

    Returns:
        Failure result dict if max retries exceeded.
    """
    request = cast(Any, task).request
    retries = int(request.retries)
    countdown = 5 * (2**retries)
    logger.info(f"[RETRY-ATTEMPT-{retries + 1}] {task_name} will retry in {countdown}s")

    try:
        _retry_task(task, exc=exc, countdown=countdown)
    except MaxRetriesExceededError:
        tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        dead_letter_queue.record_failure(
            task_name,
            request.id,
            exc,
            retries + 1,
            traceback_text=tb,
            context=context,
        )
        return _build_failure_result(
            request.id,
            status="FAILED",
            error=exc,
            timestamp=datetime.now(timezone.utc).isoformat(),
            extra={"error_traceback": tb},
        )
    # _retry_task raises, so this is unreachable unless retry succeeds
    return {}  # pragma: no cover


class EnrichmentTask(Task):
    """Base task class for enrichment operations with result tracking."""

    def on_success(self, result: Any, task_id: str, args: tuple[Any, ...], kwargs: dict[str, Any]) -> None:
        """Called on task success - log completion."""
        company_id = args[0] if args else kwargs.get("company_id", "unknown")
        logger.info(f"[EnrichmentTask] Task {task_id} succeeded for company {company_id}")

    def on_failure(
        self,
        exc: Exception,
        task_id: str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        einfo: Any,
    ) -> None:
        """Called on task failure - log with full traceback."""
        company_id = args[0] if args else kwargs.get("company_id", "unknown")
        logger.error(f"[EnrichmentTask] Task {task_id} failed for company {company_id}: {exc}\n{einfo}")


@celery_app.task(base=EnrichmentTask, bind=True, max_retries=3)
def enrich_company_async(
    self: Task,
    tenant_id: str,
    company_id: str,
    company_name: str | None = None,
    sources: list[str] | None = None,
    user_id: str | None = None,
) -> dict[str, Any]:
    """Asynchronously enrich a single company (Phase 12).

    STORY-066: tenant_id is now a required parameter. Tasks with missing
    or invalid tenant_id are rejected at entry.

    Phase 13.4: Implements exponential backoff retry logic

    Args:
        tenant_id: Tenant identifier (required, validated at entry)
        company_id: Company identifier
        company_name: Company name (optional)
        sources: List of enrichment sources (default: ['SEC_EDGAR'])
        user_id: User who requested enrichment (optional)

    Returns:
        Dict with enrichment results

    Raises:
        TenantIsolationError: If tenant_id is missing or invalid
    """
    # STORY-066: Validate and enforce tenant isolation
    validated_tenant = validate_task_tenant_id(tenant_id, task_name="enrich_company_async")

    try:
        import time

        from solstein.data.unified_loader import UnifiedCompany, unified_loader

        sources = sources or ["SEC_EDGAR"]
        start_time = time.time()

        with task_tenant_context(validated_tenant):
            # Perform enrichment — all downstream ops scoped to tenant
            company = UnifiedCompany(id=company_id, name=company_name or company_id)
            enriched = unified_loader.enrich_from_connectors(company)

            duration_ms = (time.time() - start_time) * 1000

            # Track enriched fields
            fields_enriched: list[str] = []
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
                "tenant_id": validated_tenant,
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
        return _handle_task_retry(
            self,
            exc,
            task_name="enrich_company_async",
            context={
                "company_id": company_id,
                "company_name": company_name,
                "user_id": user_id,
                "tenant_id": validated_tenant,
            },
        )


@celery_app.task(bind=True, max_retries=3)
def enrich_companies_batch_async(
    self: Task,
    tenant_id: str,
    companies: list[dict[str, Any]],
    sources: list[str] | None = None,
    batch_size: int = 10,
    user_id: str | None = None,
) -> dict[str, Any]:
    """Asynchronously enrich multiple companies in batches (Phase 12).

    STORY-066: tenant_id is now a required parameter. Tasks with missing
    or invalid tenant_id are rejected at entry.

    Phase 13.4: Implements exponential backoff retry logic

    Args:
        tenant_id: Tenant identifier (required, validated at entry)
        companies: List of company dicts with 'id' and 'name' keys
        sources: List of enrichment sources
        batch_size: Number of companies per batch
        user_id: User who requested enrichment

    Returns:
        Dict with batch enrichment results

    Raises:
        TenantIsolationError: If tenant_id is missing or invalid
    """
    # STORY-066: Validate and enforce tenant isolation
    validated_tenant = validate_task_tenant_id(tenant_id, task_name="enrich_companies_batch_async")

    try:
        import time

        from solstein.data.unified_loader import UnifiedCompany, unified_loader

        sources = sources or ["SEC_EDGAR"]
        start_time = time.time()
        batch_results: list[dict[str, Any]] = []
        failed_count = 0

        with task_tenant_context(validated_tenant):
            # Process companies — all ops scoped to tenant
            for _idx, company_data in enumerate(companies):
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

                except Exception as e:  # noqa: BLE001 — per-company isolation; log and continue
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
                "tenant_id": validated_tenant,
                "total": len(companies),
                "successful": len(companies) - failed_count,
                "failed": failed_count,
                "results": batch_results,
                "duration_ms": duration_ms,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    except Exception as exc:
        return _handle_task_retry(
            self,
            exc,
            task_name="enrich_companies_batch_async",
            context={
                "company_count": len(companies),
                "batch_size": batch_size,
                "user_id": user_id,
                "tenant_id": validated_tenant,
            },
        )
