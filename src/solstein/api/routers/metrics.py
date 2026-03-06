"""Metrics endpoint for dependency health monitoring.

Provides visibility into outbound dependency performance:
- Database query latencies
- LLM provider response times
- External API performance
- Error rates by service
"""

from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import require_admin
from ...utils.tracing import get_tracer

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/dependencies")
async def get_dependency_metrics(admin: bool = Depends(require_admin)):
    """Get aggregated metrics for all dependencies.

    Returns latency percentiles (p50, p95, p99), error rates,
    and call counts for each tracked dependency service.

    Requires: Admin authentication

    Example response:
    {
        "postgresql": {
            "total_calls": 1523,
            "error_count": 12,
            "error_rate": 0.0079,
            "latency_ms": {
                "p50": 15.2,
                "p95": 45.8,
                "p99": 89.3,
                "avg": 18.5,
                "max": 120.4
            }
        },
        "openai": {
            "total_calls": 456,
            "error_count": 3,
            "error_rate": 0.0066,
            "latency_ms": {
                "p50": 850.3,
                "p95": 2340.1,
                "p99": 4120.5,
                "avg": 923.7,
                "max": 5234.2
            }
        }
    }
    """
    tracer = get_tracer()
    return tracer.get_metrics()


@router.get("/dependencies/{service}")
async def get_service_metrics(service: str, admin: bool = Depends(require_admin)):
    """Get metrics for a specific service.

    Args:
        service: Service name (e.g., 'postgresql', 'openai', 'crunchbase')

    Returns: Metrics for the specified service

    Requires: Admin authentication
    """
    tracer = get_tracer()
    metrics = tracer.get_metrics(service=service)

    if not metrics:
        raise HTTPException(status_code=404, detail=f"No metrics found for service: {service}")

    return metrics


@router.post("/dependencies/reset")
async def reset_metrics(admin: bool = Depends(require_admin)):
    """Reset all dependency metrics counters.

    Use with caution - this clears all accumulated metrics history.

    Requires: Admin authentication
    """
    tracer = get_tracer()
    tracer._calls = []
    return {"status": "ok", "message": "Metrics reset successfully"}
