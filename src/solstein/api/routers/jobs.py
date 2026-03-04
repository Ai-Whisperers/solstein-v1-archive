"""Job status router — queries workflow execution status.

NOTE: Temporal integration currently disabled (temporalio dependency removed).
Plan to reimplement with asyncio-based task queue in Phase 2.
"""

from typing import Any

from fastapi import APIRouter, status
from loguru import logger

router = APIRouter(tags=["Jobs"])
from ..exceptions import APIError

router = APIRouter(tags=["Jobs"])


@router.get("/{workflow_id}")
async def get_job_status(workflow_id: str) -> dict[str, Any]:
    """Get the status of a job."""
    try:
        raise APIError(
            code="NOT_IMPLEMENTED",
            message="Job status endpoint disabled - Temporal integration removed",
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )
    except APIError:
        raise
    except Exception as e:
        logger.warning(f"Job status failed: {e}")
        raise APIError(
            code="INTERNAL_ERROR",
            message="Error retrieving job status",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=str(e),
        ) from e
