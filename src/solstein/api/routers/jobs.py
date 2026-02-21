"""
Job status router — queries Temporal workflow execution status.

NOTE: Temporal integration currently disabled (temporalio dependency removed).
Plan to reimplement with asyncio-based task queue in Phase 2.
"""

from typing import Any

from fastapi import APIRouter, HTTPException, status
from loguru import logger

# from temporalio.client import Client as TemporalClient
from ...config import get_settings

router = APIRouter(tags=["Jobs"])


@router.get("/{workflow_id}")
async def get_job_status(workflow_id: str) -> dict[str, Any]:
    """Get the status of a job (currently unavailable - Temporal disabled)."""
    logger.warning("Job status endpoint called but Temporal is disabled")
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Job status service currently unavailable. Temporal integration will be reimplemented in Phase 2.",
    )
