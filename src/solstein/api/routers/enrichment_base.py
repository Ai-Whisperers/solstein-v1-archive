"""Enrichment API router helpers and endpoints.

EPIC-021: Modularized from monolithic 801-line file.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, Request
from sqlalchemy import text

from solstein.api.schemas.enrichment import (
    AuditEntry,
    AuditTrailResponse,
    BatchEnrichmentRequest,
    BatchEnrichmentResponse,
    BatchEnrichmentResult,
    CacheCheckResponse,
    CacheClearResponse,
    EnrichmentRequest,
    EnrichmentResponse,
    EnrichmentResultData,
    HealthCheckResponse,
    MetricsResponse,
    ReadinessCheckResponse,
)
from solstein.data.security_hardening import audit_logger, input_validator, rate_limiter
from solstein.data.unified_loader import UnifiedCompany, unified_loader
from solstein.infrastructure.database import db_manager
from solstein.infrastructure.enrichment_repositories import EnrichmentAuditRepository, EnrichmentCacheRepository

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================================
# REPOSITORY HELPERS
# ============================================================================


async def get_audit_repo_if_available():
    """Get audit repository if database is initialized, else None."""
    try:
        if hasattr(db_manager, "initialized") and db_manager.initialized:
            async with db_manager.get_session() as session:
                return EnrichmentAuditRepository(session)
    except Exception as e:
        logger.debug(f"Could not initialize audit repository: {e}")
    return None


async def get_cache_repo_if_available():
    """Get cache repository if database is initialized, else None."""
    try:
        if hasattr(db_manager, "initialized") and db_manager.initialized:
            async with db_manager.get_session() as session:
                return EnrichmentCacheRepository(session)
    except Exception as e:
        logger.debug(f"Could not initialize cache repository: {e}")
    return None


# ============================================================================
# HEALTH CHECK HELPERS
# ============================================================================


async def check_database_health() -> tuple[str, bool]:
    """Check database connectivity."""
    try:
        if hasattr(db_manager, "initialized") and db_manager.initialized:
            async with db_manager.get_session() as session:
                await session.execute(text("SELECT 1"))
            return "operational", True
        else:
            return "not_initialized", False
    except Exception as e:
        logger.debug(f"Database health check failed: {e}")
        return "unavailable", False


async def check_sec_edgar_health() -> tuple[str, bool]:
    """Check SEC EDGAR connector health."""
    try:
        if hasattr(unified_loader, "sec_connector") and unified_loader.sec_connector:
            return "operational", True
        else:
            return "not_initialized", False
    except Exception as e:
        logger.debug(f"SEC EDGAR health check failed: {e}")
        return "unavailable", False


async def check_companies_house_health() -> tuple[str, bool]:
    """Check Companies House connector health."""
    try:
        if hasattr(unified_loader, "companies_house_connector") and unified_loader.companies_house_connector:
            return "operational", True
        else:
            return "not_initialized", False
    except Exception as e:
        logger.debug(f"Companies House health check failed: {e}")
        return "unavailable", False


async def check_news_signals_health() -> tuple[str, bool]:
    """Check News Signals connector health."""
    try:
        if hasattr(unified_loader, "news_detector") and unified_loader.news_detector:
            return "operational", True
        else:
            return "not_initialized", False
    except Exception as e:
        logger.debug(f"News Signals health check failed: {e}")
        return "unavailable", False


async def check_cache_health() -> tuple[str, bool]:
    """Check cache health (in-memory or Redis)."""
    try:
        cache_repo = await get_cache_repo_if_available()
        if cache_repo:
            return "operational", True
        elif hasattr(unified_loader, "cache") and unified_loader.cache:
            return "operational", True
        else:
            return "not_initialized", False
    except Exception as e:
        logger.debug(f"Cache health check failed: {e}")
        return "unavailable", False


# ============================================================================
# CLIENT ID HELPER
# ============================================================================


def get_client_id(request: Request) -> str:
    """Extract client ID for rate limiting."""
    client_id = request.headers.get("X-Client-ID")
    if client_id:
        return client_id
    if request.client:
        return request.client.host
    return "unknown"
