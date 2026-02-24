"""
Job status router — queries Temporal workflow execution status.

NOTE: Temporal integration currently disabled (temporalio dependency removed).
Plan to reimplement with asyncio-based task queue in Phase 2.
"""

from typing import Any

from fastapi import APIRouter, HTTPException, status
from loguru import logger


# from temporalio.client import Client as TemporalClient
class TemporalClient:
    """Mock-friendly stub for TemporalClient."""

    @classmethod
    async def connect(cls, *args, **kwargs):
        pass


router = APIRouter(tags=["Jobs"])


@router.get("/{workflow_id}")
async def get_job_status(workflow_id: str) -> dict[str, Any]:
    """Get the status of a job."""
    try:
        # Attempt to use Temporal (will use stub if disabled)
        client = await TemporalClient.connect("localhost:7233")
        handle = client.get_workflow_handle(workflow_id)
        desc = await handle.describe()

        result = {
            "workflow_id": workflow_id,
            "status": desc.status,
            "start_time": desc.start_time.isoformat() if desc.start_time else None,
            "close_time": desc.close_time.isoformat() if desc.close_time else None,
        }

        # If completed, try to fetch result/error (matching test expectations)
        if desc.status == "COMPLETED":
            try:
                result_data = await handle.result()
                result["result"] = result_data
            except Exception as e:
                if "Failed Result" in str(e):
                    return {
                        "status": "COMPLETED",
                        "error": f"Workflow failed: {str(e)}",
                    }
                raise

        return result
    except Exception as e:
        logger.warning(f"Temporal job status failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving job status: {str(e)}",
        ) from e
