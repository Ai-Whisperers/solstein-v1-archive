"""Async export API endpoints.

STORY-111: POST /api/v1/exports returns 202 Accepted with a job_id
immediately. The actual export runs as a Celery task on the ``export``
queue. GET /api/v1/exports/{job_id} returns the current status and a
download URL when complete.

Supported formats: excel, csv, json, markdown, llm, pdf
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import BaseModel, Field

from ..dependencies import get_current_tenant

router = APIRouter(prefix="/api/v1/exports", tags=["Exports"])

# Valid export formats
_VALID_FORMATS = frozenset({
    "excel", "csv", "json", "markdown", "llm", "pdf",
})


class ExportRequest(BaseModel):
    """Request body for creating an export job."""

    format: str = Field(
        ...,
        description="Export format: excel, csv, json, markdown, llm, pdf",
    )
    company_id: str | None = Field(
        None,
        description="Optional company ID to export",
    )
    industry: str | None = Field(
        None,
        description="Optional industry filter",
    )


class ExportJobResponse(BaseModel):
    """Response for export job creation and status."""

    job_id: str
    status: str
    format: str
    file_url: str | None = None
    error_message: str | None = None
    created_at: str | None = None
    completed_at: str | None = None


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ExportJobResponse,
)
async def create_export(
    body: ExportRequest,
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> JSONResponse:
    """Create an async export job.

    Returns 202 Accepted with a job_id. Poll GET /api/v1/exports/{job_id}
    for status and download URL.
    """
    tenant_id = tenant.get("tenant_id", "")
    if not tenant_id:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Tenant ID required"},
        )

    if body.format not in _VALID_FORMATS:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": f"Invalid format '{body.format}'. "
                f"Valid formats: {', '.join(sorted(_VALID_FORMATS))}",
            },
        )

    # Create the export job record
    job_id = str(uuid.uuid4())
    try:
        await _create_job_record(
            job_id=job_id,
            tenant_id=tenant_id,
            export_format=body.format,
            company_id=body.company_id,
        )
    except (ConnectionError, OSError, RuntimeError) as exc:
        logger.error(
            "[ExportAPI] Failed to create job record: %s", exc,
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Export service temporarily unavailable"},
        )

    # Dispatch Celery task
    filters: dict[str, Any] = {"tenant_id": tenant_id}
    if body.company_id:
        filters["company_id"] = body.company_id
    if body.industry:
        filters["industry"] = body.industry

    try:
        _dispatch_export_task(
            job_id=job_id,
            tenant_id=tenant_id,
            export_format=body.format,
            filters=filters,
        )
    except (ConnectionError, OSError, RuntimeError) as exc:
        logger.error(
            "[ExportAPI] Failed to dispatch Celery task: %s", exc,
        )
        # Job was created but task dispatch failed — mark as failed
        await _mark_job_error(job_id, "Task dispatch failed")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Export queue temporarily unavailable"},
        )

    logger.info(
        "[ExportAPI] Created export job_id=%s format=%s tenant=%s",
        job_id,
        body.format,
        tenant_id[:8] + "..." if len(tenant_id) > 8 else tenant_id,
    )

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "job_id": job_id,
            "status": "queued",
            "format": body.format,
            "file_url": None,
            "error_message": None,
            "created_at": None,
            "completed_at": None,
        },
    )


@router.get("/{job_id}", response_model=ExportJobResponse)
async def get_export_status(
    job_id: str,
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> JSONResponse:
    """Get the status of an export job.

    Returns the current status and download URL when complete.
    """
    tenant_id = tenant.get("tenant_id", "")

    try:
        job = await _get_job_record(job_id, tenant_id)
    except (ConnectionError, OSError, RuntimeError) as exc:
        logger.error(
            "[ExportAPI] Failed to fetch job %s: %s", job_id, exc,
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Export service temporarily unavailable"},
        )

    if job is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"Export job {job_id} not found"},
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=job,
    )


async def _create_job_record(
    job_id: str,
    tenant_id: str,
    export_format: str,
    company_id: str | None,
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
            company_id=company_id,
            format=export_format,
            status="queued",
        )
        session.add(record)
        await session.commit()


def _dispatch_export_task(
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


async def _get_job_record(
    job_id: str, tenant_id: str,
) -> dict[str, Any] | None:
    """Fetch an ExportJobRecord and return as dict."""
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
        return job.to_dict()


async def _mark_job_error(
    job_id: str, error_message: str,
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
            await session.commit()
