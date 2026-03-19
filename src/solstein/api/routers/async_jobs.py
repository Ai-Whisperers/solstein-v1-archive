"""Async job management endpoints (Phase 12).

Provides API for submitting and tracking async enrichment jobs.

Note: This router requires Celery and Redis to be installed and configured.
If Celery is not available, this router will not be functional.
"""

import asyncio
import logging
import uuid

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/async", tags=["async-jobs"])

# Try to import Celery, but don't fail if it's not available
try:
    from solstein.celery_config import celery_app

    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    celery_app = None
    logger.warning("Celery not installed - async job endpoints will return 503 Service Unavailable")

from solstein.data.security_hardening import input_validator, rate_limiter

from ..exceptions import APIError

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class AsyncEnrichmentRequest(BaseModel):
    """Request to enrich a company asynchronously."""

    company_id: str
    company_name: str | None = None
    sources: list[str] | None = None
    use_cache: bool = True


class AsyncBatchEnrichmentRequest(BaseModel):
    """Request to enrich multiple companies asynchronously."""

    companies: list[dict]  # List of {id, name} dicts
    sources: list[str] | None = None
    batch_size: int = 10


class JobStatusResponse(BaseModel):
    """Response with job status."""

    job_id: str
    company_id: str
    company_name: str | None
    job_type: str
    status: str
    progress: int
    created_at: str
    started_at: str | None
    completed_at: str | None
    duration_ms: float | None
    result_data: dict | None
    error_message: str | None


class JobResultResponse(BaseModel):
    """Response with job result."""

    job_id: str
    status: str
    result_data: dict
    error_message: str | None


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _get_client_id(request: Request) -> str:
    """Extract client ID from request headers."""
    return (
        request.headers.get("X-Client-ID")
        or request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        or request.client.host
        or "unknown"
    )


def _check_celery_available():
    """Check if Celery is available."""
    if not CELERY_AVAILABLE or celery_app is None:
        raise APIError(
            code="SERVICE_UNAVAILABLE",
            message="Async enrichment service unavailable. Celery/Redis not configured.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.post("/enrich/single")
async def enrich_single_async(request_data: AsyncEnrichmentRequest, request: Request):
    """Submit async single company enrichment job.

    Returns:
        Dict with job_id and status
    """
    _check_celery_available()

    # Rate limiting
    client_id = _get_client_id(request)
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Validation
    is_valid, error = input_validator.validate_company_id(request_data.company_id)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    # Submit async task (send_task blocks on broker I/O; run in thread pool)
    task_id = str(uuid.uuid4())
    task = await asyncio.to_thread(
        celery_app.send_task,
        "solstein.worker_tasks.enrich_company_async",
        args=[
            request_data.company_id,
            request_data.company_name,
            request_data.sources,
            None,  # user_id
        ],
        task_id=task_id,
    )

    logger.info(f"📨 Submitted async enrichment job {task.id} for {request_data.company_id}")

    return {
        "job_id": task.id,
        "company_id": request_data.company_id,
        "status": "SUBMITTED",
        "message": "Enrichment job submitted successfully",
    }


@router.post("/enrich/batch")
async def enrich_batch_async(request_data: AsyncBatchEnrichmentRequest, request: Request):
    """Submit async batch company enrichment job.

    Returns:
        Dict with job_id and status
    """
    _check_celery_available()

    # Rate limiting
    client_id = _get_client_id(request)
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Validation
    if not request_data.companies:
        raise HTTPException(status_code=400, detail="Companies list cannot be empty")

    if len(request_data.companies) > 1000:
        raise HTTPException(status_code=400, detail="Batch size limited to 1000 companies")

    # Submit async task (send_task blocks on broker I/O; run in thread pool)
    batch_task_id = str(uuid.uuid4())
    task = await asyncio.to_thread(
        celery_app.send_task,
        "solstein.worker_tasks.enrich_companies_batch_async",
        args=[
            request_data.companies,
            request_data.sources,
            request_data.batch_size,
            None,  # user_id
        ],
        task_id=batch_task_id,
    )

    logger.info(f"📨 Submitted async batch enrichment job {task.id} for {len(request_data.companies)} companies")

    return {
        "job_id": task.id,
        "total_companies": len(request_data.companies),
        "status": "SUBMITTED",
        "message": f"Batch enrichment job submitted for {len(request_data.companies)} companies",
    }


@router.get("/jobs/{job_id}/status")
async def get_job_status(job_id: str, request: Request):
    """Get status of an async job.

    Args:
        job_id: Celery task ID

    Returns:
        Dict with job status and progress
    """
    _check_celery_available()

    # Rate limiting
    client_id = _get_client_id(request)
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Get task
    task = celery_app.AsyncResult(job_id)

    if task.state == "PENDING":
        response = {
            "job_id": job_id,
            "status": "PENDING",
            "progress": 0,
        }
    elif task.state == "RUNNING":
        response = {
            "job_id": job_id,
            "status": "RUNNING",
            "progress": task.info.get("progress", 0) if isinstance(task.info, dict) else 0,
        }
    elif task.state == "SUCCESS":
        response = {
            "job_id": job_id,
            "status": "SUCCESS",
            "progress": 100,
            "result": task.result,
        }
    elif task.state == "FAILURE":
        response = {
            "job_id": job_id,
            "status": "FAILED",
            "progress": 0,
            "error": str(task.info),
        }
    else:
        response = {
            "job_id": job_id,
            "status": task.state,
            "progress": 0,
        }

    return response


@router.get("/jobs/{job_id}/result")
async def get_job_result(job_id: str, request: Request):
    """Get result of a completed async job.

    Args:
        job_id: Celery task ID

    Returns:
        Dict with job result and enrichment data
    """
    _check_celery_available()

    # Rate limiting
    client_id = _get_client_id(request)
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Get task
    task = celery_app.AsyncResult(job_id)

    if task.state == "PENDING":
        raise HTTPException(status_code=202, detail="Job still pending")
    elif task.state == "RUNNING":
        raise HTTPException(status_code=202, detail="Job still running")
    elif task.state == "SUCCESS":
        return {
            "job_id": job_id,
            "status": "SUCCESS",
            "result": task.result,
        }
    elif task.state == "FAILURE":
        return {
            "job_id": job_id,
            "status": "FAILED",
            "error": str(task.info),
        }
    else:
        raise HTTPException(status_code=400, detail=f"Unknown job state: {task.state}")
