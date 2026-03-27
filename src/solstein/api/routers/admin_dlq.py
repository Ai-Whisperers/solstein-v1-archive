"""Admin API for Dead Letter Queue management.

STORY-088: Exposes the persistent DLQ (failed_tasks PostgreSQL table) through
an authenticated admin API. Supports listing, inspecting, and re-queuing failed
Celery tasks.

Endpoints:
    GET  /api/v1/admin/dlq          - List DLQ entries (filterable)
    GET  /api/v1/admin/dlq/{entry_id} - Inspect a single DLQ entry
    POST /api/v1/admin/dlq/{entry_id}/requeue - Re-queue a failed task
    POST /api/v1/admin/dlq/{entry_id}/resolve - Mark entry resolved without re-queue

Alerting note: callers should monitor unresolved count; raise an alert when
> 10 unresolved entries accumulate within any 1-hour window.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger
from pydantic import BaseModel

from solstein.api.dependencies import get_current_user
from solstein.worker.dlq import list_failed_tasks, mark_resolved

router = APIRouter(prefix="/api/v1/admin/dlq", tags=["Admin - DLQ"])


class DLQFilterParams:
    """Query parameter group for DLQ list endpoint (Depends-injected)."""

    def __init__(
        self,
        queue_name: str | None = Query(default=None, description="Filter by queue name"),
        task_name: str | None = Query(default=None, description="Filter by task name prefix"),
        resolved: bool | None = Query(
            default=False,
            description="None=all, True=resolved, False=unresolved (default)",
        ),
        limit: int = Query(default=50, ge=1, le=500, description="Max results per page"),
        offset: int = Query(default=0, ge=0, description="Pagination offset"),
    ) -> None:
        self.queue_name = queue_name
        self.task_name = task_name
        self.resolved = resolved
        self.limit = limit
        self.offset = offset


class DLQEntryResponse(BaseModel):
    """Schema for a single DLQ entry."""

    task_id: str
    task_name: str
    queue_name: str
    error_message: str
    traceback: str | None
    retry_count: int
    tenant_id: str | None
    created_at: str
    last_attempted_at: str
    resolved_at: str | None
    resolved_by: str | None


class DLQListResponse(BaseModel):
    """Paginated list of DLQ entries."""

    entries: list[DLQEntryResponse]
    total: int
    limit: int
    offset: int


class ResolveResponse(BaseModel):
    """Response for resolve/requeue operations."""

    task_id: str
    resolved: bool
    message: str


def _serialize_entry(row: dict[str, Any]) -> DLQEntryResponse:
    """Convert a DB row to the API response schema."""
    return DLQEntryResponse(
        task_id=str(row.get("task_id", "")),
        task_name=str(row.get("task_name", "")),
        queue_name=str(row.get("queue_name", "default")),
        error_message=str(row.get("error_message", "")),
        traceback=row.get("traceback"),
        retry_count=int(row.get("retry_count", 0)),
        tenant_id=row.get("tenant_id"),
        created_at=str(row.get("created_at", "")),
        last_attempted_at=str(row.get("last_attempted_at", "")),
        resolved_at=str(row["resolved_at"]) if row.get("resolved_at") else None,
        resolved_by=row.get("resolved_by"),
    )


@router.get("", response_model=DLQListResponse, summary="List DLQ entries")
async def list_dlq_entries(
    filters: DLQFilterParams = Depends(),
    _current_user: dict[str, Any] = Depends(get_current_user),
) -> DLQListResponse:
    """List Dead Letter Queue entries with optional filters.

    By default returns unresolved entries (resolved=false), newest first.
    Use resolved=null to see all entries regardless of status.
    """
    rows = list_failed_tasks(
        queue_name=filters.queue_name,
        task_name=filters.task_name,
        resolved=filters.resolved,
        limit=filters.limit,
        offset=filters.offset,
    )

    entries = [_serialize_entry(row) for row in rows]
    return DLQListResponse(
        entries=entries,
        total=len(entries),
        limit=filters.limit,
        offset=filters.offset,
    )


@router.get("/{entry_id}", response_model=DLQEntryResponse, summary="Get DLQ entry")
async def get_dlq_entry(
    entry_id: str,
    _current_user: dict[str, Any] = Depends(get_current_user),
) -> DLQEntryResponse:
    """Get a single DLQ entry by its UUID."""
    rows = list_failed_tasks(limit=1, offset=0)
    # Filter client-side (small result set for single-entry lookup)
    matching = [r for r in rows if str(r.get("task_id", "")) == entry_id]
    if not matching:
        # Try all (including resolved) entries
        all_rows = list_failed_tasks(resolved=None, limit=500, offset=0)
        matching = [r for r in all_rows if str(r.get("task_id", "")) == entry_id]
    if not matching:
        raise HTTPException(status_code=404, detail=f"DLQ entry {entry_id} not found")
    return _serialize_entry(matching[0])


@router.post(
    "/{entry_id}/resolve",
    response_model=ResolveResponse,
    summary="Resolve DLQ entry without re-queuing",
)
async def resolve_dlq_entry(
    entry_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> ResolveResponse:
    """Mark a DLQ entry as resolved without re-queuing the task.

    Use this when the issue has been fixed manually and re-execution is not needed.
    """
    resolved_by = current_user.get("email") or current_user.get("sub") or "admin"
    updated = mark_resolved(entry_id=entry_id, resolved_by=str(resolved_by))

    if not updated:
        raise HTTPException(
            status_code=404,
            detail=f"DLQ entry {entry_id} not found or already resolved",
        )

    logger.info("[DLQ Admin] Entry %s marked resolved by %s", entry_id, resolved_by)
    return ResolveResponse(
        task_id=entry_id,
        resolved=True,
        message=f"Entry {entry_id} marked as resolved by {resolved_by}",
    )


@router.post(
    "/{entry_id}/requeue",
    response_model=ResolveResponse,
    summary="Re-queue a failed task",
)
async def requeue_dlq_entry(
    entry_id: str,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> ResolveResponse:
    """Re-queue a failed task and mark the DLQ entry as resolved.

    Looks up the DLQ entry by ID, creates a new Celery task with the same
    task_name, then marks the original entry as resolved.
    """
    from solstein.celery_config import celery_app  # local import — avoids circular

    resolved_by = current_user.get("email") or current_user.get("sub") or "admin"

    # Find the entry
    all_rows = list_failed_tasks(resolved=False, limit=500, offset=0)
    matching = [r for r in all_rows if str(r.get("task_id", "")) == entry_id]
    if not matching:
        raise HTTPException(
            status_code=404,
            detail=f"DLQ entry {entry_id} not found or already resolved",
        )

    entry = matching[0]
    task_name = str(entry.get("task_name", ""))
    kwargs = entry.get("kwargs") or {}

    try:
        celery_app.send_task(task_name, kwargs=kwargs)
        logger.info(
            "[DLQ Admin] Re-queued task %s (entry %s) by %s",
            task_name,
            entry_id,
            resolved_by,
        )
    except Exception as exc:
        logger.error("[DLQ Admin] Failed to re-queue task %s: %s", task_name, exc)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to re-queue task: {exc}",
        ) from exc

    # Mark original entry resolved
    mark_resolved(entry_id=entry_id, resolved_by=str(resolved_by))

    return ResolveResponse(
        task_id=entry_id,
        resolved=True,
        message=f"Task {task_name} re-queued and entry {entry_id} resolved",
    )
