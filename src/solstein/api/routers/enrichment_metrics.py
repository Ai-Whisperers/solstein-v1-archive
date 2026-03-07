"""Metrics endpoint for enrichment API.

EPIC-021: Modularized from enrichment.py.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, Request

from solstein.api.schemas.enrichment import MetricsResponse
from solstein.data.security_hardening import rate_limiter

from .enrichment_base import get_client_id, logger, router, unified_loader


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(request: Request) -> MetricsResponse:
    """Get enrichment performance metrics."""
    client_id = get_client_id(request)
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    logger.info(f"📊 Metrics request from {client_id}")

    enrichment_metrics = unified_loader.get_enrichment_metrics()
    rate_limit_remaining = rate_limiter.get_remaining(client_id)

    enrichment_data = {
        "total": enrichment_metrics.get("total_enrichments", 0),
        "successful": enrichment_metrics.get("successful", 0),
        "failed": enrichment_metrics.get("failed", 0),
        "success_rate": enrichment_metrics.get("success_rate", 0),
        "avg_duration_ms": enrichment_metrics.get("avg_duration_ms", 0),
        "total_duration_ms": enrichment_metrics.get("total_duration_ms", 0),
    }

    return MetricsResponse(
        timestamp=datetime.now(timezone.utc),
        enrichment=enrichment_data,
        cache={
            "size": 0,
            "ttl_hours": 24,
            "hits": enrichment_metrics.get("cache_hits", 0),
            "misses": enrichment_metrics.get("cache_misses", 0),
            "hit_rate": 0.0,
        },
        rate_limiting={
            "requests_per_minute": 100,
            "current_requests": 100 - rate_limit_remaining,
            "remaining": rate_limit_remaining,
        },
    )
