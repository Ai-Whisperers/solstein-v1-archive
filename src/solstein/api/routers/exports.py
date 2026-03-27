"""Async export API endpoints.

STORY-111: POST /api/v1/exports returns 202 Accepted with a job_id
immediately. The actual export runs as a Celery task on the ``export``
queue.

STORY-113: Added GET /api/v1/exports (list with pagination/filtering),
DELETE /api/v1/exports/{job_id} (cancel with Celery revoke), and
expiry-aware status responses.

Supported formats: excel, csv, json, markdown, llm, pdf
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import BaseModel, Field

from ..dependencies import get_current_tenant
from .exports_helpers import (
    cancel_job,
    create_job_record,
    dispatch_export_task,
    get_job_record,
    list_job_records,
    mark_job_error,
)

router = APIRouter(prefix="/api/v1/exports", tags=["Exports"])

# Valid export formats
_VALID_FORMATS = frozenset({
    "excel", "csv", "json", "markdown", "llm", "pdf",
})

# Valid status values for filtering
_VALID_STATUSES = frozenset({
    "queued", "processing", "completed", "failed", "cancelled", "expired",
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
    file_size_bytes: int | None = None
    error_message: str | None = None
    progress_pct: int = 0
    created_at: str | None = None
    completed_at: str | None = None
    expires_at: str | None = None


class ExportListResponse(BaseModel):
    """Paginated list of export jobs."""

    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int
    has_more: bool


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

    job_id = str(uuid.uuid4())
    try:
        await create_job_record(
            job_id=job_id,
            tenant_id=tenant_id,
            user_id=tenant.get("user_id"),
            export_format=body.format,
            company_id=body.company_id,
        )
    except (ConnectionError, OSError, RuntimeError) as exc:
        logger.error("[ExportAPI] Failed to create job record: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Export service temporarily unavailable"},
        )

    filters: dict[str, Any] = {"tenant_id": tenant_id}
    if body.company_id:
        filters["company_id"] = body.company_id
    if body.industry:
        filters["industry"] = body.industry

    try:
        dispatch_export_task(
            job_id=job_id,
            tenant_id=tenant_id,
            export_format=body.format,
            filters=filters,
        )
    except (ConnectionError, OSError, RuntimeError) as exc:
        logger.error("[ExportAPI] Failed to dispatch Celery task: %s", exc)
        await mark_job_error(job_id, "Task dispatch failed")
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
            "file_size_bytes": None,
            "error_message": None,
            "progress_pct": 0,
            "created_at": None,
            "completed_at": None,
            "expires_at": None,
        },
    )


@router.get("", response_model=ExportListResponse)
async def list_exports(
    tenant: dict[str, Any] = Depends(get_current_tenant),
    status_filter: str | None = Query(
        None,
        alias="status",
        description="Filter by status",
    ),
    format_filter: str | None = Query(
        None,
        alias="format",
        description="Filter by export format",
    ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> JSONResponse:
    """List export jobs for the current tenant.

    STORY-113: Paginated, filterable by status and format.
    Ordered by created_at descending (most recent first).
    """
    tenant_id = tenant.get("tenant_id", "")

    if status_filter and status_filter not in _VALID_STATUSES:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": f"Invalid status '{status_filter}'. "
                f"Valid: {', '.join(sorted(_VALID_STATUSES))}",
            },
        )

    try:
        items, total = await list_job_records(
            tenant_id=tenant_id,
            status_filter=status_filter,
            format_filter=format_filter,
            page=page,
            page_size=page_size,
        )
    except (ConnectionError, OSError, RuntimeError) as exc:
        logger.error("[ExportAPI] Failed to list jobs: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Export service temporarily unavailable"},
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_more": (page * page_size) < total,
        },
    )


@router.get("/{job_id}", response_model=ExportJobResponse)
async def get_export_status(
    job_id: str,
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> JSONResponse:
    """Get the status of an export job.

    STORY-113: Returns signed URL when status=completed and not expired.
    Expired exports return status='expired' with no file_url.
    """
    tenant_id = tenant.get("tenant_id", "")

    try:
        job = await get_job_record(job_id, tenant_id)
    except (ConnectionError, OSError, RuntimeError) as exc:
        logger.error("[ExportAPI] Failed to fetch job %s: %s", job_id, exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Export service temporarily unavailable"},
        )

    if job is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"Export job {job_id} not found"},
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content=job)


@router.delete("/{job_id}", status_code=status.HTTP_200_OK)
async def cancel_export(
    job_id: str,
    tenant: dict[str, Any] = Depends(get_current_tenant),
) -> JSONResponse:
    """Cancel a queued or running export job.

    STORY-113: Cancels queued exports immediately and revokes running
    Celery tasks. Completed/failed/cancelled exports cannot be cancelled.
    """
    tenant_id = tenant.get("tenant_id", "")

    try:
        result = await cancel_job(job_id, tenant_id)
    except (ConnectionError, OSError, RuntimeError) as exc:
        logger.error("[ExportAPI] Failed to cancel job %s: %s", job_id, exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Export service temporarily unavailable"},
        )

    if result is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"Export job {job_id} not found"},
        )

    if result == "already_terminal":
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "detail": f"Export job {job_id} is already in a terminal state",
            },
        )

    logger.info("[ExportAPI] Cancelled export job_id=%s", job_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"job_id": job_id, "status": "cancelled"},
    )
