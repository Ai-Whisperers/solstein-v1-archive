"""
Job status router — queries Temporal workflow execution status.
"""

from typing import Any

from fastapi import APIRouter, HTTPException, status
from loguru import logger
from temporalio.client import Client as TemporalClient

from ...config import get_settings

router = APIRouter(tags=["Jobs"])


async def _get_temporal_client() -> TemporalClient:
    """Create a Temporal client connection."""
    settings = get_settings()
    return await TemporalClient.connect(
        settings.temporal.host_url,
        namespace=settings.temporal.namespace,
        api_key=settings.temporal.api_key,
    )


@router.get("/{workflow_id}")
async def get_job_status(workflow_id: str) -> dict[str, Any]:
    """
    Get the status of a Temporal workflow execution.
    """
    try:
        client = await _get_temporal_client()
        handle = client.get_workflow_handle(workflow_id)
        desc = await handle.describe()

        response: dict[str, Any] = {
            "workflow_id": workflow_id,
            "status": str(desc.status),
            "start_time": desc.start_time.isoformat() if desc.start_time else None,
            "close_time": desc.close_time.isoformat() if desc.close_time else None,
        }

        # If the workflow is complete, fetch its result
        if desc.close_time:
            try:
                result = await handle.result()
                response["result"] = result
            except Exception:
                response["error"] = "Workflow failed or was cancelled."

        return response
    except Exception as e:
        logger.error(f"Error checking workflow status for {workflow_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking workflow status: {str(e)}",
        ) from e
