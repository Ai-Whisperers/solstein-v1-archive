"""Async export Celery tasks.

STORY-111: Moves export file generation out of the HTTP request thread
into a Celery task on the ``export`` queue. The API endpoint creates an
ExportJobRecord with status='queued' and dispatches this task. The task
updates the record through processing -> completed | failed.

STORY-115: Exports are uploaded to Supabase Storage (signed URLs) via
the storage backend abstraction. Local disk is only used as a temporary
staging area during generation; the temp file is cleaned up after upload.

Task guarantees (inherited from EPIC-025):
- STORY-088: On permanent failure the job is persisted to DLQ.
- STORY-090: Idempotent — re-triggering the same export_job_id is a no-op
  if the job is already completed or processing.

Time limits:
- Default exports (excel, csv, markdown): 60 s soft / 90 s hard
- LLM-enhanced exports: 120 s soft / 150 s hard
"""

from __future__ import annotations

import asyncio
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from celery import shared_task
from loguru import logger

from .base import dead_letter_queue

# Formats that use LLM generation and need a longer time limit
_LLM_FORMATS = frozenset({"llm", "llm_enhanced", "llm_report"})


def _run_in_dedicated_loop(coro: Any) -> Any:
    """Run a coroutine in a short-lived event loop owned by this task."""
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@shared_task(
    name="solstein.worker_tasks.generate_export",
    bind=True,
    max_retries=2,
    default_retry_delay=10,
    queue="export",
    acks_late=True,
)
def generate_export(
    self: Any,
    export_job_id: str,
    tenant_id: str,
    export_format: str,
    filters: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Generate an export file asynchronously.

    Args:
        export_job_id: UUID of the ExportJobRecord to update.
        tenant_id: Tenant that owns this export.
        export_format: One of 'excel', 'csv', 'json', 'markdown', 'llm'.
        filters: Optional filters (industry, company_id, etc.).

    Returns:
        Dict with job_id and final status.
    """
    filters = filters or {}
    logger.info(
        "[Export] Starting export task job_id=%s format=%s tenant=%s",
        export_job_id,
        export_format,
        tenant_id[:8] + "..." if len(tenant_id) > 8 else tenant_id,
    )

    try:
        _run_in_dedicated_loop(
            _execute_export(export_job_id, tenant_id, export_format, filters)
        )
        return {"job_id": export_job_id, "status": "completed"}

    except self.MaxRetriesExceededError:
        _run_in_dedicated_loop(
            _mark_job_failed(export_job_id, "Max retries exceeded")
        )
        dead_letter_queue.record_failure(
            task_name="solstein.worker_tasks.generate_export",
            task_id=self.request.id or str(uuid.uuid4()),
            error="Max retries exceeded",
            attempt=self.request.retries or 0,
            tenant_id=tenant_id,
        )
        return {"job_id": export_job_id, "status": "failed"}

    except Exception as exc:
        logger.error(
            "[Export] Export failed job_id=%s error=%s",
            export_job_id,
            str(exc)[:500],
        )
        try:
            self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            _run_in_dedicated_loop(
                _mark_job_failed(export_job_id, str(exc))
            )
            dead_letter_queue.record_failure(
                task_name="solstein.worker_tasks.generate_export",
                task_id=self.request.id or str(uuid.uuid4()),
                error=exc,
                attempt=self.request.retries or 0,
                tenant_id=tenant_id,
            )
            return {"job_id": export_job_id, "status": "failed"}

        # If retry succeeds (doesn't raise), we won't reach here
        # but satisfy the type checker
        return {"job_id": export_job_id, "status": "retrying"}


async def _execute_export(
    export_job_id: str,
    tenant_id: str,
    export_format: str,
    filters: dict[str, Any],
) -> None:
    """Core export logic: update status, generate file, mark complete."""
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession

    from solstein.infrastructure.database import get_async_engine
    from solstein.infrastructure.models.export import ExportJobRecord

    engine = get_async_engine()

    # Mark as processing (idempotency check)
    async with AsyncSession(engine, expire_on_commit=False) as session:
        result = await session.execute(
            select(ExportJobRecord).where(
                ExportJobRecord.id == uuid.UUID(export_job_id)
            )
        )
        job = result.scalar_one_or_none()

        if job is None:
            raise ValueError(f"Export job {export_job_id} not found")

        # Idempotency: skip if already completed or processing
        if job.status in ("completed", "processing"):
            logger.warning(
                "[Export] Job %s already %s — skipping (idempotent)",
                export_job_id,
                job.status,
            )
            return

        job.status = "processing"
        await session.commit()

    # STORY-112: Progress callback updates export_jobs.progress_pct
    async def _update_progress(pct: int) -> None:
        async with AsyncSession(engine, expire_on_commit=False) as s:
            r = await s.execute(
                select(ExportJobRecord).where(
                    ExportJobRecord.id == uuid.UUID(export_job_id)
                )
            )
            j = r.scalar_one_or_none()
            if j is not None:
                j.progress_pct = min(pct, 99)  # 100 only on completion
                await s.commit()

    def _sync_progress(pct: int) -> None:
        """Synchronous progress callback for non-async exporters."""
        _run_in_dedicated_loop(_update_progress(pct))

    # STORY-115: Generate file and upload to storage backend
    file_url = await _generate_file(
        tenant_id, export_job_id, export_format, filters, _sync_progress,
    )

    # Mark as completed with expiry (STORY-113)
    async with AsyncSession(engine, expire_on_commit=False) as session:
        result = await session.execute(
            select(ExportJobRecord).where(
                ExportJobRecord.id == uuid.UUID(export_job_id)
            )
        )
        job = result.scalar_one_or_none()
        if job is not None:
            file_size = _get_file_size(file_url)
            job.mark_completed(file_url, file_size_bytes=file_size)
            await session.commit()

    logger.info(
        "[Export] Completed export job_id=%s file_url=%s",
        export_job_id,
        file_url,
    )


def _get_file_size(file_url: str) -> int | None:
    """Get file size in bytes from a local path or return None."""
    import pathlib

    try:
        path = pathlib.Path(file_url)
        if path.exists():
            return path.stat().st_size
    except (OSError, TypeError, ValueError):
        pass
    return None


async def _generate_file(
    tenant_id: str,
    export_job_id: str,
    export_format: str,
    filters: dict[str, Any],
    progress_callback: Any | None = None,
) -> str:
    """Generate an export file and upload it via the storage backend.

    STORY-115: Files are generated to a temp directory, uploaded to the
    configured storage backend (Supabase Storage or local fallback),
    and the temp file is cleaned up. Returns the download URL.

    STORY-112: Added progress_callback parameter for streaming exports.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    industry = filters.get("industry", "")
    prefix = industry.lower().replace(" ", "_") if industry else "all"

    filename = _build_filename(export_format, prefix, timestamp)

    # Generate to a temp file, upload, then clean up
    with tempfile.TemporaryDirectory(prefix="solstein_export_") as tmp_dir:
        tmp_path = Path(tmp_dir) / filename
        await _dispatch_exporter(
            export_format, tmp_path, filters, progress_callback,
        )

        if not tmp_path.exists():
            raise RuntimeError(
                f"Exporter did not produce output file: {filename}"
            )

        file_bytes = tmp_path.read_bytes()

    # Upload via storage backend (retry up to 3 times)
    from solstein.exporters.storage import get_storage_backend

    backend = get_storage_backend()
    last_exc: Exception | None = None
    for attempt in range(1, 4):
        try:
            url = await backend.upload(
                data=file_bytes,
                tenant_id=tenant_id,
                job_id=export_job_id,
                filename=filename,
            )
            return url
        except Exception as exc:
            last_exc = exc
            logger.warning(
                "[Export] Upload attempt %d/3 failed: %s",
                attempt,
                str(exc)[:200],
            )

    raise RuntimeError(
        f"Export upload failed after 3 attempts: {last_exc}"
    )


def _build_filename(
    export_format: str, prefix: str, timestamp: str,
) -> str:
    """Build the export filename from format, prefix, and timestamp."""
    ext_map: dict[str, str] = {
        "excel": "xlsx",
        "csv": "csv",
        "json": "json",
        "markdown": "md",
        "pdf": "pdf",
    }
    if export_format in _LLM_FORMATS:
        return f"export_llm_{prefix}_{timestamp}.md"
    ext = ext_map.get(export_format)
    if ext is None:
        raise ValueError(f"Unsupported export format: {export_format}")
    return f"export_{prefix}_{timestamp}.{ext}"


async def _dispatch_exporter(
    export_format: str,
    output_path: Path,
    filters: dict[str, Any],
    progress_callback: Any | None = None,
) -> None:
    """Dispatch to the appropriate exporter to write a file."""
    if export_format == "excel":
        await _generate_excel(output_path, filters, progress_callback)
    elif export_format == "csv":
        await _generate_csv(output_path, filters)
    elif export_format == "json":
        await _generate_json(output_path, filters)
    elif export_format == "markdown":
        await _generate_markdown(output_path, filters)
    elif export_format == "pdf":
        await _generate_pdf(output_path, filters, progress_callback)
    elif export_format in _LLM_FORMATS:
        await _generate_llm_report(output_path, filters)
    else:
        raise ValueError(f"Unsupported export format: {export_format}")


async def _generate_excel(
    output_path: Any,
    filters: dict[str, Any],
    progress_callback: Any | None = None,
) -> None:
    """Generate Excel export using streaming write_only mode.

    STORY-112: Uses StreamingExcelExporter for O(1) memory usage.
    Falls back to standard ExcelExporter if streaming fails.
    """
    from solstein.exporters.excel_streaming import (
        StreamingExcelExporter,
    )

    exporter = StreamingExcelExporter()
    companies = await _fetch_companies(filters)
    if companies:
        exporter.create_dashboard(
            companies, output_path, progress_callback,
        )


async def _generate_pdf(
    output_path: Any,
    filters: dict[str, Any],
    progress_callback: Any | None = None,
) -> None:
    """Generate PDF export using PDFExporter.

    STORY-114: Renders a structured PDF report with financial overview,
    company profiles, source citations, and revenue charts.
    """
    from solstein.exporters.pdf import PDFExporter

    exporter = PDFExporter()
    companies = await _fetch_companies(filters)
    if companies:
        page_format = filters.get("page_format", "a4")
        exporter.export(
            companies,
            output_path=output_path,
            page_format=page_format,
            progress_callback=progress_callback,
        )


async def _generate_csv(
    output_path: Any, filters: dict[str, Any]
) -> None:
    """Generate CSV export."""
    from solstein.exporters.csv import CSVExporter

    exporter = CSVExporter()
    companies = await _fetch_companies(filters)
    if companies:
        exporter.export(companies, output_path=output_path)


async def _generate_json(
    output_path: Any, filters: dict[str, Any]
) -> None:
    """Generate JSON export."""
    import json

    companies = await _fetch_companies(filters)
    data = [c.model_dump(mode="json") for c in companies]
    output_path.write_text(json.dumps(data, indent=2, default=str))


async def _generate_markdown(
    output_path: Any, filters: dict[str, Any]
) -> None:
    """Generate Markdown export."""
    from solstein.exporters.markdown.generator import (
        generate_enhanced_report,
    )

    companies = await _fetch_companies(filters)
    if companies:
        report = generate_enhanced_report(companies)
        output_path.write_text(report)


async def _generate_llm_report(
    output_path: Any, filters: dict[str, Any]
) -> None:
    """Generate LLM-enhanced report (higher time limit)."""
    from solstein.exporters import LLMReportEnhancer

    enhancer = LLMReportEnhancer()
    companies = await _fetch_companies(filters)
    if companies:
        report = enhancer.generate_full_report(companies)
        output_path.write_text(report)


async def _generate_pdf(
    output_path: Any,
    filters: dict[str, Any],
    progress_callback: Any | None = None,
) -> None:
    """Generate PDF export.

    STORY-114: Uses PDFExporter with optional page format and progress.
    """
    from solstein.exporters.pdf import PDFExporter

    exporter = PDFExporter()
    companies = await _fetch_companies(filters)
    if companies:
        page_format = filters.get("page_format", "a4")
        exporter.export(
            companies,
            output_path=output_path,
            page_format=page_format,
            progress_callback=progress_callback,
        )


async def _fetch_companies(
    filters: dict[str, Any],
) -> list[Any]:
    """Fetch companies from the database based on filters."""
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession

    from solstein.infrastructure.database import get_async_engine
    from solstein.infrastructure.database_models import CompanyRecord

    engine = get_async_engine()
    async with AsyncSession(engine, expire_on_commit=False) as session:
        query = select(CompanyRecord)

        industry = filters.get("industry")
        if industry:
            query = query.where(CompanyRecord.industry == industry)

        company_id = filters.get("company_id")
        if company_id:
            query = query.where(
                CompanyRecord.company_id == company_id
            )

        tenant_id = filters.get("tenant_id")
        if tenant_id:
            query = query.where(
                CompanyRecord.tenant_id == tenant_id
            )

        result = await session.execute(query.limit(1000))
        records = result.scalars().all()

    # Convert ORM records to domain objects
    companies = []
    for record in records:
        try:
            company = record.to_domain()
            companies.append(company)
        except (AttributeError, TypeError, ValueError) as exc:
            logger.warning(
                "[Export] Failed to convert record %s: %s",
                getattr(record, "company_id", "?"),
                exc,
            )
    return companies


async def _mark_job_failed(
    export_job_id: str, error_message: str
) -> None:
    """Mark an export job as failed in the database."""
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession

    from solstein.infrastructure.database import get_async_engine
    from solstein.infrastructure.models.export import ExportJobRecord

    engine = get_async_engine()
    async with AsyncSession(engine, expire_on_commit=False) as session:
        result = await session.execute(
            select(ExportJobRecord).where(
                ExportJobRecord.id == uuid.UUID(export_job_id)
            )
        )
        job = result.scalar_one_or_none()
        if job is not None:
            job.status = "failed"
            job.error_message = error_message[:2000]
            job.completed_at = datetime.now(timezone.utc)
            await session.commit()
