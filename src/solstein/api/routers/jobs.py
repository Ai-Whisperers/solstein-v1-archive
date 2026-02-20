from typing import Any

from fastapi import APIRouter, HTTPException, status
from celery.result import AsyncResult
from loguru import logger

from ..worker import celery_app

router = APIRouter(tags=["Jobs"])


@router.get("/{task_id}")
async def get_job_status(task_id: str) -> dict[str, Any]:
    """
    Get the status and result of a background task.
    """
    try:
        result = AsyncResult(task_id, app=celery_app)
        
        response = {
            "task_id": task_id,
            "status": result.status,
            "ready": result.ready(),
        }

        if result.ready():
            if result.successful():
                response["result"] = result.result
            else:
                response["error"] = str(result.result)
                response["traceback"] = result.traceback

        return response
    except Exception as e:
        logger.error(f"Error checking job status for {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking job status: {str(e)}",
        ) from e
