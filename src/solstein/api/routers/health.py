"""Health check and monitoring endpoints.

Provides Kubernetes-compatible health checks:
- /health - Overall status
- /health/status - Full status with all checks
- /health/ready - Readiness probe
- /health/live - Liveness probe
- /metrics - Application metrics
- /metrics/data-quality - Data quality metrics
"""

from datetime import datetime

from fastapi import APIRouter, status

from ...core.monitoring import health_monitor
from ..exceptions import APIError

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", name="health_check")
async def health_check() -> dict:
    """Overall health status endpoint.

    Returns basic health indicator with HTTP 200 if healthy,
    503 if unhealthy (for load balancer compatibility).
    """
    await health_monitor.run_all_checks()
    status = health_monitor.get_overall_status()

    response = {
        "status": status.value,
        "timestamp": datetime.utcnow().isoformat(),
    }

    if status.value == "unhealthy":
        raise APIError(
            code="SERVICE_UNAVAILABLE",
            message="Service is unhealthy",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=response,
        )

    return response


@router.get("/status", name="full_health_status")
async def health_status() -> dict:
    """Full health status with all checks."""
    await health_monitor.run_all_checks()

    return health_monitor.to_dict()


@router.get("/ready", name="readiness_check")
async def readiness_check() -> dict:
    """Kubernetes readiness probe.

    Returns 200 if ready to serve requests, 503 if not.
    """
    await health_monitor.run_all_checks()
    is_ready = health_monitor.is_ready()

    response = {
        "ready": is_ready,
        "timestamp": datetime.utcnow().isoformat(),
    }

    if not is_ready:
        raise APIError(
            code="SERVICE_UNAVAILABLE",
            message="Application not ready",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=response,
        )

    return response


@router.get("/live", name="liveness_check")
async def liveness_check() -> dict:
    """Kubernetes liveness probe.

    Always returns 200 as long as process is running.
    """
    return {
        "alive": health_monitor.is_alive(),
        "timestamp": datetime.utcnow().isoformat(),
    }


metrics_router = APIRouter(prefix="/metrics", tags=["metrics"])


@metrics_router.get("", name="get_metrics")
async def get_metrics() -> dict:
    """Get application metrics snapshot."""
    await health_monitor.run_all_checks()
    metrics = health_monitor.get_metrics()

    return {
        "timestamp": metrics.timestamp.isoformat(),
        "requests": {
            "total": metrics.total_requests,
            "successful": metrics.successful_requests,
            "failed": metrics.failed_requests,
            "error_rate": round(metrics.error_rate, 4),
        },
        "performance": {
            "avg_response_time_ms": round(metrics.avg_response_time_ms, 2),
            "uptime_seconds": metrics.uptime_seconds,
        },
        "cache": {
            "hits": metrics.cache_hits,
            "misses": metrics.cache_misses,
        },
    }


@metrics_router.get("/data-quality", name="get_data_quality")
async def get_data_quality() -> dict:
    """Get data quality metrics."""
    dq = health_monitor.get_data_quality_metrics()

    return {
        "timestamp": dq.last_update.isoformat(),
        "companies_scored": dq.total_companies_scored,
        "companies_with_all_signals": dq.companies_with_all_signals,
        "companies_missing_critical_signals": dq.companies_missing_critical_signals,
        "signal_coverage": {
            "average_per_company": round(dq.average_signal_count_per_company, 2),
            "average_confidence": round(dq.average_confidence_score, 3),
        },
        "low_confidence_signals": dq.signals_with_low_confidence,
    }
