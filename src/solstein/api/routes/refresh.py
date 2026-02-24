"""FastAPI routes for manual data refresh and webhook triggers."""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from solstein.worker_tasks import (
    refresh_all_sources,
    refresh_companies_house,
    refresh_github,
    refresh_news_signals,
    refresh_sec_edgar,
)

router = APIRouter(prefix="/api/refresh", tags=["refresh"])

SUPPORTED_SOURCES = {
    "sec_edgar": refresh_sec_edgar,
    "companies_house": refresh_companies_house,
    "news_signals": refresh_news_signals,
    "github": refresh_github,
    "all": None,
}


class RefreshRequest(BaseModel):
    company_ids: list[str] | None = None
    incremental: bool = True


class RefreshResponse(BaseModel):
    job_id: str
    source: str
    status: str


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
        result = refresh_all_sources.apply_async()
        return RefreshResponse(job_id=result.id, source="all", status="queued")

    task = SUPPORTED_SOURCES[source_name]
    result = task.apply_async()

    return RefreshResponse(job_id=result.id, source=source_name, status="queued")


@router.get("/status/{job_id}")
async def get_refresh_status(job_id: str):
    """Get the status of a refresh job.

    Args:
        job_id: The Celery task ID

    Returns:
        Job status information
    """
    from celery.result import AsyncResult

    result = AsyncResult(job_id)
    return {
        "job_id": job_id,
        "status": result.state,
        "result": result.result if result.ready() else None,
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
        result = refresh_all_sources.apply_async()
    else:
        task = SUPPORTED_SOURCES[payload.source]
        result = task.apply_async()

    return {
        "job_id": result.id,
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
