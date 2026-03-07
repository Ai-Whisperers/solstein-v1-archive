"""Health and readiness endpoints for enrichment API.

EPIC-021: Modularized from enrichment.py.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, Request

from solstein.api.schemas.enrichment import HealthCheckResponse, ReadinessCheckResponse
from solstein.data.security_hardening import rate_limiter

from .enrichment_base import (
    check_cache_health,
    check_companies_house_health,
    check_database_health,
    check_news_signals_health,
    check_sec_edgar_health,
    get_client_id,
    logger,
    router,
)


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(request: Request) -> HealthCheckResponse:
    """Platform health check (liveness probe)."""
    logger.info(f"🏥 Health check from {request.client.host if request.client else 'unknown'}")

    db_status, db_healthy = await check_database_health()
    sec_status, sec_healthy = await check_sec_edgar_health()
    ch_status, ch_healthy = await check_companies_house_health()
    news_status, news_healthy = await check_news_signals_health()
    cache_status, cache_healthy = await check_cache_health()

    all_healthy = db_healthy and cache_healthy
    overall_status = "healthy" if all_healthy else "unhealthy"

    if not all_healthy:
        logger.warning(f"Health check failed: db={db_status}, cache={cache_status}")

    return HealthCheckResponse(
        status=overall_status,
        timestamp=datetime.now(timezone.utc),
        version="1.0",
        components={
            "database": db_status,
            "cache": cache_status,
            "sec_edgar": sec_status,
            "companies_house": ch_status,
            "news_signals": news_status,
        },
    )


@router.get("/ready", response_model=ReadinessCheckResponse)
async def readiness_check(request: Request) -> ReadinessCheckResponse:
    """Readiness probe for load balancers."""
    client_id = get_client_id(request)
    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    logger.info(f"📋 Readiness check from {client_id}")

    db_status, db_healthy = await check_database_health()
    sec_status, sec_healthy = await check_sec_edgar_health()
    ch_status, ch_healthy = await check_companies_house_health()
    news_status, news_healthy = await check_news_signals_health()
    cache_status, cache_healthy = await check_cache_health()

    system_ready = (db_status in ["operational", "not_initialized"]) and (
        cache_status in ["operational", "not_initialized"]
    )

    return ReadinessCheckResponse(
        ready=system_ready,
        timestamp=datetime.now(timezone.utc),
        checks={
            "configuration_loaded": True,
            "connectors_initialized": sec_healthy or ch_healthy or news_healthy,
            "cache_operational": cache_healthy,
            "enrichment_enabled": True,
            "database_ready": db_healthy,
        },
    )
