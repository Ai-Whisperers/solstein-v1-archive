"""Enrichment API Endpoints (Phase 10 - Core Implementation).

EPIC-021: Refactored from monolithic 801-line file to modular structure.
This module now serves as the orchestration layer, importing from specialized modules.

All 8 REST endpoints:
1. GET /health - Health check
2. GET /ready - Readiness probe
3. GET /metrics - Performance metrics
4. POST /companies/{id}/enrich - Single enrichment
5. POST /companies/enrich/batch - Batch enrichment
6. GET /companies/{id}/enrichment/audit - Audit trail
7. GET /companies/{id}/enrichment/cache - Cache check
8. POST /enrichment/cache/clear - Cache clear

Also includes:
- Rate limiting integration
- Audit logging integration
- Input validation integration
- Security headers
"""

from __future__ import annotations

from fastapi import APIRouter

# Import all endpoints from modular files
from .enrichment_base import router as base_router
from .enrichment_health import router as health_router
from .enrichment_metrics import router as metrics_router
from .enrichment_single import router as single_router
from .enrichment_batch import router as batch_router
from .enrichment_audit import router as audit_router
from .enrichment_cache import router as cache_router

# Create main router
router = APIRouter()

# Include all sub-routers
router.include_router(base_router)
router.include_router(health_router)
router.include_router(metrics_router)
router.include_router(single_router)
router.include_router(batch_router)
router.include_router(audit_router)
router.include_router(cache_router)

# Re-export for backward compatibility
from .enrichment_base import (
    get_audit_repo_if_available,
    get_cache_repo_if_available,
    check_database_health,
    check_sec_edgar_health,
    check_companies_house_health,
    check_news_signals_health,
    check_cache_health,
    get_client_id,
    logger,
)

from .enrichment_health import health_check, readiness_check
from .enrichment_metrics import get_metrics
from .enrichment_single import enrich_single_company
from .enrichment_batch import enrich_batch
from .enrichment_audit import get_audit_trail
from .enrichment_cache import check_cache, clear_all_cache, clear_company_cache

__all__ = [
    # Router
    "router",
    # Base utilities
    "get_audit_repo_if_available",
    "get_cache_repo_if_available",
    "check_database_health",
    "check_sec_edgar_health",
    "check_companies_house_health",
    "check_news_signals_health",
    "check_cache_health",
    "get_client_id",
    "logger",
    # Endpoints
    "health_check",
    "readiness_check",
    "get_metrics",
    "enrich_single_company",
    "enrich_batch",
    "get_audit_trail",
    "check_cache",
    "clear_all_cache",
    "clear_company_cache",
]
