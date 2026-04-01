"""Research job status API endpoints (STORY-083, EPIC-024).

Provides endpoints for querying research job status. Job creation
happens through the worker task system; these endpoints are read-only
for clients to poll or display job status (until STORY-084 adds
Realtime subscriptions).

All endpoints are tenant-scoped via the tenant middleware.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from loguru import logger
from pydantic import BaseModel

from ...infrastructure.research_job_repository import ResearchJobRepository
from ..dependencies import get_current_tenant, get_db_session
from ..exceptions import APIError

router = APIRouter(tags=["Research Jobs"])


class ResearchJobResponse(BaseModel):
    """Response schema for a research job status record."""

    id: str
    tenant_id: str
    company_id: str
    company_name: str | None = None
    status: str
    progress_pct: int
    current_stage: str | None = None
    error_message: str | None = None
    created_at: str | None = None
    started_at: str | None = None
    completed_at: str | None = None

    model_config = {"from_attributes": True}


class ResearchJobListResponse(BaseModel):
    """Response schema for listing research jobs."""

    items: list[ResearchJobResponse]
    total: int


def _job_to_response(job: Any) -> ResearchJobResponse:
    """Convert a ResearchJobRecord to a response schema.

    Args:
        job: ResearchJobRecord ORM instance.

    Returns:
        ResearchJobResponse with serialized fields.
    """
    return ResearchJobResponse(
        id=str(job.id),
        tenant_id=job.tenant_id,
        company_id=job.company_id,
        company_name=job.company_name,
        status=job.status,
        progress_pct=job.progress_pct,
        current_stage=job.current_stage,
        error_message=job.error_message,
        created_at=job.created_at.isoformat() if job.created_at else None,
        started_at=job.started_at.isoformat() if job.started_at else None,
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
    )


@router.get(
    "/research-jobs",
    response_model=ResearchJobListResponse,
    summary="List research jobs for the current tenant",
)
async def list_research_jobs(
    status_filter: str | None = Query(
        None,
        alias="status",
        description="Filter by job status (queued/running/completed/failed/cancelled)",
    ),
    limit: int = Query(50, ge=1, le=200, description="Page size"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    tenant: dict[str, Any] = Depends(get_current_tenant),
    session: Any = Depends(get_db_session),
) -> ResearchJobListResponse:
    """List research jobs for the authenticated tenant.

    Returns jobs ordered by creation time (newest first).
    Optionally filter by status.
    """
    tenant_id = tenant.get("tenant_id", "")
    repo = ResearchJobRepository(session)

    try:
        jobs = await repo.get_jobs_for_tenant(
            tenant_id=tenant_id,
            status_filter=status_filter,
            limit=limit,
            offset=offset,
        )
        return ResearchJobListResponse(
            items=[_job_to_response(j) for j in jobs],
            total=len(jobs),
        )
    except (ValueError, TypeError, RuntimeError) as e:
        logger.error(f"[ResearchJobs] Error listing jobs: {type(e).__name__}: {e}")
        raise APIError(
            code="INTERNAL_ERROR",
            message="Error listing research jobs",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from e


@router.get(
    "/research-jobs/{job_id}",
    response_model=ResearchJobResponse,
    summary="Get a specific research job by ID",
)
async def get_research_job(
    job_id: str,
    tenant: dict[str, Any] = Depends(get_current_tenant),
    session: Any = Depends(get_db_session),
) -> ResearchJobResponse:
    """Get details for a specific research job.

    Returns 404 if the job doesn't exist or belongs to another tenant.
    """
    tenant_id = tenant.get("tenant_id", "")
    repo = ResearchJobRepository(session)

    try:
        parsed_id = uuid.UUID(job_id)
    except ValueError as e:
        raise APIError(
            code="INVALID_JOB_ID",
            message=f"Invalid job ID format: {job_id}",
            status_code=status.HTTP_400_BAD_REQUEST,
        ) from e

    try:
        job = await repo.get_job(parsed_id)
    except (ValueError, TypeError, RuntimeError) as e:
        logger.error(f"[ResearchJobs] Error fetching job {job_id}: {type(e).__name__}: {e}")
        raise APIError(
            code="INTERNAL_ERROR",
            message="Error fetching research job",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from e

    if job is None or job.tenant_id != tenant_id:
        raise APIError(
            code="NOT_FOUND",
            message=f"Research job {job_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return _job_to_response(job)
