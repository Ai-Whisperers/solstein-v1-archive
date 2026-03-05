"""FastAPI routes for manual data refresh and webhook triggers."""

import importlib
from typing import Protocol, cast

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from solstein.infrastructure.database import db_manager
from solstein.infrastructure.refresh import get_refresh_statuses
from solstein.worker_tasks import (
    refresh_all_sources,
    refresh_companies_house,
    refresh_github,
    refresh_news_signals,
    refresh_sec_edgar,
)


class AsyncResult(Protocol):
    id: str


class CeleryTask(Protocol):
    def apply_async(self) -> AsyncResult: ...


def _queue_task(task: CeleryTask) -> str:
    result = task.apply_async()
    return result.id


def _as_task(task: object) -> CeleryTask:
    return cast(CeleryTask, task)


router = APIRouter(prefix="/api/refresh", tags=["refresh"])

SUPPORTED_SOURCES: dict[str, CeleryTask | None] = {
    "sec_edgar": _as_task(refresh_sec_edgar),
    "companies_house": _as_task(refresh_companies_house),
    "news_signals": _as_task(refresh_news_signals),
    "github": _as_task(refresh_github),
    "all": None,
}


class RefreshRequest(BaseModel):
    company_ids: list[str] | None = None
    incremental: bool = True


class RefreshResponse(BaseModel):
    job_id: str
    source: str
    status: str


class RefreshStatusResponse(BaseModel):
    source_name: str
    source_type: str
    last_refresh_time: str | None
    next_scheduled_time: str | None
    refresh_interval_seconds: int
    stale: bool
    stale_reason: str | None
    freshness_window_hours: float


class WebhookPayload(BaseModel):
    source: str
    action: str = "refresh"
    company_ids: list[str] | None = None


@router.post("/{source_name}", response_model=RefreshResponse)
async def trigger_refresh(source_name: str, request: RefreshRequest | None = None):
    """Manually trigger a refresh for a specific data source.

    Args:
        source_name: Name of the data source (sec_edgar, companies_house, news_signals, github)
        request: Optional request body with company_ids and incremental flag

    Returns:
        Job ID and status information
    """
    if source_name not in SUPPORTED_SOURCES:
        raise HTTPException(
            status_code=404,
            detail=f"Source '{source_name}' not supported. Supported: {list(SUPPORTED_SOURCES.keys())}",
        )

    if source_name == "all":
        if request is not None:
            _ = request.company_ids
            _ = request.incremental
        return RefreshResponse(job_id=_queue_task(_as_task(refresh_all_sources)), source="all", status="queued")

    task = SUPPORTED_SOURCES[source_name]
    if task is None:
        raise HTTPException(status_code=500, detail="Refresh task not configured")
    return RefreshResponse(job_id=_queue_task(task), source=source_name, status="queued")


@router.get("/status/{job_id}")
async def get_refresh_status(job_id: str):
    """Get the status of a refresh job.

    Args:
        job_id: The Celery task ID

    Returns:
        Job status information
    """
    try:
        module = importlib.import_module("celery.result")
    except ImportError as exc:
        raise HTTPException(status_code=500, detail="Celery is not installed") from exc

    AsyncResult = getattr(module, "AsyncResult")
    result = AsyncResult(job_id)
    return {
        "job_id": job_id,
        "status": result.state,
        "result": result.result if result.ready() else None,
    }


@router.get("/status")
async def list_refresh_statuses(source_name: str | None = None):
    statuses = await get_refresh_statuses(db_manager=db_manager, source_name=source_name)
    return {
        "statuses": [
            RefreshStatusResponse(
                source_name=status.source_name,
                source_type=status.source_type,
                last_refresh_time=status.last_refresh_time.isoformat() if status.last_refresh_time else None,
                next_scheduled_time=status.next_scheduled_time.isoformat() if status.next_scheduled_time else None,
                refresh_interval_seconds=status.refresh_interval_seconds,
                stale=status.stale,
                stale_reason=status.stale_reason,
                freshness_window_hours=status.freshness_window_hours,
            )
            for status in statuses
        ]
    }


@router.post("/webhook")
async def webhook_trigger(payload: WebhookPayload):
    """Webhook endpoint for external systems to trigger refresh.

    Args:
        payload: Webhook payload with source and action

    Returns:
        Job ID and status
    """
    if payload.source not in SUPPORTED_SOURCES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid source '{payload.source}'. Supported: {list(SUPPORTED_SOURCES.keys())}",
        )

    if payload.action != "refresh":
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action '{payload.action}'. Only 'refresh' is supported.",
        )

    if payload.source == "all":
        job_id = _queue_task(_as_task(refresh_all_sources))
    else:
        task = SUPPORTED_SOURCES[payload.source]
        if task is None:
            raise HTTPException(status_code=500, detail="Refresh task not configured")
        job_id = _queue_task(task)

    return {
        "job_id": job_id,
        "source": payload.source,
        "status": "queued",
        "message": "Refresh triggered via webhook",
    }


@router.get("/sources")
async def list_sources():
    """List all available data sources for refresh.

    Returns:
        List of supported sources
    """
    return {
        "sources": [
            {"name": "sec_edgar", "description": "SEC EDGAR financial data", "schedule": "daily"},
            {
                "name": "companies_house",
                "description": "UK Companies House data",
                "schedule": "daily",
            },
            {
                "name": "news_signals",
                "description": "News API signal detection",
                "schedule": "hourly",
            },
            {"name": "github", "description": "GitHub repository data", "schedule": "every 6 hours"},
            {"name": "all", "description": "Refresh all sources", "schedule": "manual"},
        ]
    }
