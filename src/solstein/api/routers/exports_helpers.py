"""Database helpers for async export endpoints.

STORY-113: Extracted from exports.py to keep file sizes under 500 lines.
All database operations for the export API live here.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from loguru import logger


async def create_job_record(
    job_id: str,
    tenant_id: str,
    export_format: str,
    company_id: str | None,
    user_id: str | None = None,
) -> None:
    """Insert an ExportJobRecord into the database."""
    from sqlalchemy.ext.asyncio import AsyncSession

    from solstein.infrastructure.database import get_async_engine
    from solstein.infrastructure.models.export import ExportJobRecord

    engine = get_async_engine()
    async with AsyncSession(engine, expire_on_commit=False) as session:
        record = ExportJobRecord(
            id=uuid.UUID(job_id),
            tenant_id=tenant_id,
            user_id=user_id,
            company_id=company_id,
            format=export_format,
            status="queued",
        )
        session.add(record)
        await session.commit()


def dispatch_export_task(
    job_id: str,
    tenant_id: str,
    export_format: str,
    filters: dict[str, Any],
) -> None:
    """Send the generate_export task to the Celery export queue."""
    from solstein.worker.export_tasks import generate_export

    generate_export.apply_async(
        args=[job_id, tenant_id, export_format],
        kwargs={"filters": filters},
        queue="export",
    )


async def get_job_record(
    job_id: str,
    tenant_id: str,
) -> dict[str, Any] | None:
    """Fetch an ExportJobRecord and return as dict with expiry check."""
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession

    from solstein.infrastructure.database import get_async_engine
    from solstein.infrastructure.models.export import ExportJobRecord

    engine = get_async_engine()
    async with AsyncSession(engine, expire_on_commit=False) as session:
        result = await session.execute(
            select(ExportJobRecord).where(
                ExportJobRecord.id == uuid.UUID(job_id),
                ExportJobRecord.tenant_id == tenant_id,
            )
        )
        job = result.scalar_one_or_none()
        if job is None:
            return None
        return job.to_dict(check_expiry=True)


async def list_job_records(
    tenant_id: str,
    status_filter: str | None = None,
    format_filter: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[dict[str, Any]], int]:
    """Fetch paginated export jobs for a tenant."""
    from sqlalchemy import func, select
    from sqlalchemy.ext.asyncio import AsyncSession

    from solstein.infrastructure.database import get_async_engine
    from solstein.infrastructure.models.export import ExportJobRecord

    engine = get_async_engine()
    async with AsyncSession(engine, expire_on_commit=False) as session:
        base_query = select(ExportJobRecord).where(
            ExportJobRecord.tenant_id == tenant_id,
        )

        if format_filter:
            base_query = base_query.where(
                ExportJobRecord.format == format_filter,
            )

        # Status filter: "expired" requires special handling
        if status_filter == "expired":
            base_query = base_query.where(
                ExportJobRecord.status == "completed",
                ExportJobRecord.expires_at < datetime.now(timezone.utc),
            )
        elif status_filter:
            base_query = base_query.where(
                ExportJobRecord.status == status_filter,
            )

        count_result = await session.execute(select(func.count()).select_from(base_query.subquery()))
        total = count_result.scalar_one()

        offset = (page - 1) * page_size
        result = await session.execute(
            base_query.order_by(ExportJobRecord.created_at.desc()).offset(offset).limit(page_size)
        )
        records = result.scalars().all()
        items = [r.to_dict(check_expiry=True) for r in records]

    return items, total


async def cancel_job(
    job_id: str,
    tenant_id: str,
) -> str | None:
    """Cancel an export job. Returns 'cancelled', 'already_terminal', or None."""
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession

    from solstein.infrastructure.database import get_async_engine
    from solstein.infrastructure.models.export import ExportJobRecord

    engine = get_async_engine()
    async with AsyncSession(engine, expire_on_commit=False) as session:
        result = await session.execute(
            select(ExportJobRecord).where(
                ExportJobRecord.id == uuid.UUID(job_id),
                ExportJobRecord.tenant_id == tenant_id,
            )
        )
        job = result.scalar_one_or_none()
        if job is None:
            return None

        if job.status in ("completed", "failed", "cancelled"):
            return "already_terminal"

        if job.status == "processing":
            _revoke_celery_task(job_id)

        job.mark_cancelled()
        await session.commit()
        return "cancelled"


def _revoke_celery_task(job_id: str) -> None:
    """Attempt to revoke a running Celery task for the given export job."""
    try:
        from solstein.celery_config import celery_app

        celery_app.control.revoke(job_id, terminate=True, signal="SIGTERM")
        logger.info("[ExportAPI] Revoked Celery task for job_id=%s", job_id)
    except Exception as exc:  # noqa: BLE001 -- best-effort revoke
        logger.warning(
            "[ExportAPI] Failed to revoke Celery task for job_id=%s: %s",
            job_id,
            exc,
        )


async def mark_job_error(
    job_id: str,
    error_message: str,
) -> None:
    """Mark a job as failed (used when Celery dispatch fails)."""
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession

    from solstein.infrastructure.database import get_async_engine
    from solstein.infrastructure.models.export import ExportJobRecord

    engine = get_async_engine()
    async with AsyncSession(engine, expire_on_commit=False) as session:
        result = await session.execute(
            select(ExportJobRecord).where(
                ExportJobRecord.id == uuid.UUID(job_id),
            )
        )
        job = result.scalar_one_or_none()
        if job is not None:
            job.status = "failed"
            job.error_message = error_message
            job.completed_at = datetime.now(timezone.utc)
            await session.commit()
