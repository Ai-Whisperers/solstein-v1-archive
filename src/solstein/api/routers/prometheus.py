"""Prometheus metrics scrape endpoint.

STORY-051: Exposes all application metrics in the standard Prometheus
text exposition format at ``/metrics/prometheus``.

Security note (REQ-3): This endpoint is deliberately unauthenticated
following the Prometheus scraping convention. Access should be restricted
at the network level (e.g., only reachable from the monitoring VPC).
"""

from __future__ import annotations

from fastapi import APIRouter
from starlette.responses import Response

from ...monitoring.metrics import CONTENT_TYPE_LATEST, generate_latest

router = APIRouter(tags=["metrics"])


@router.get(
    "/metrics/prometheus",
    response_class=Response,
    name="prometheus_metrics",
    summary="Prometheus scrape endpoint",
    description=(
        "Returns all application metrics in Prometheus text exposition format. "
        "Unauthenticated by design — restrict at network level."
    ),
)
async def prometheus_metrics() -> Response:
    """Return metrics in Prometheus text exposition format.

    This endpoint is unauthenticated by design (REQ-3) to follow the
    standard Prometheus scraping convention. Network-level access control
    should be used to restrict access to the monitoring infrastructure.

    Returns:
        Prometheus-formatted metrics response.
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
