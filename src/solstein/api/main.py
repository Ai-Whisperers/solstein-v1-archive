"""
SolStein FastAPI Backend - Competitive Intelligence Platform

Production-ready REST API following clean architecture patterns:
- Clean architecture with clear separation of concerns
- Type-safe Pydantic models for request/response validation
- OpenAPI/Swagger auto-documentation
- JWT authentication (optional)
- PostgreSQL with async support
- Comprehensive error handling
- Performance monitoring (EPIC-023)
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from loguru import logger

from solstein.config import ConfigurationError, Settings
from solstein.core.production_hardening import (
    FeatureFlagManager,
    GracefulDegradation,
    GracefulShutdown,
    ResponseCache,
)
from solstein.infrastructure.cache_warming import warm_cache

from .exceptions import setup_exception_handlers
from .middleware import (
    setup_logging_middleware,
    setup_rate_limiting,
    setup_security_middleware,
)
from .middleware.performance import setup_performance_middleware
from .middleware.tenant import TenantMiddleware
from .routers import (
    async_jobs,
    auth,
    companies,
    drill_down,
    enrichment,
    export,
    health,
    jobs,
    market,
    research_jobs,
    review,
    scoring,
    semantic_search,
    simulation,
)

settings = Settings()

feature_flags: FeatureFlagManager | None = None
response_cache: ResponseCache | None = None
graceful_degradation: GracefulDegradation | None = None
graceful_shutdown: GracefulShutdown | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifecycle manager for startup and shutdown events."""
    global feature_flags, response_cache, graceful_degradation, graceful_shutdown

    logger.info("Starting SolStein API server")

    try:
        settings.check_configuration()
    except ConfigurationError as e:
        logger.error(f"Configuration validation failed: {e}")
        raise

    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Data directory: {settings.data.data_dir}")

    settings.data.ensure_dirs()
    if settings.logging.file_path:
        settings.logging.file_path.parent.mkdir(parents=True, exist_ok=True)

    feature_flags = FeatureFlagManager()
    response_cache = ResponseCache()
    graceful_degradation = GracefulDegradation()
    graceful_shutdown = GracefulShutdown()

    logger.info("Production hardening components initialized")

    # STORY-050: Initialize OpenTelemetry distributed tracing
    try:
        from solstein.observability.tracing import init_tracing, instrument_fastapi

        tracing_enabled = init_tracing(
            service_name="solstein",
            otlp_endpoint=settings.otlp_endpoint,
        )
        if tracing_enabled:
            instrument_fastapi(app)
            logger.info("OpenTelemetry tracing active")
    except Exception as _otel_exc:  # noqa: BLE001 — tracing is non-critical
        logger.warning("OpenTelemetry init failed — tracing disabled", error=str(_otel_exc))

    # EPIC-023: Enable performance profiling if configured
    if settings.environment == "development":
        from solstein.monitoring.profiler import enable_profiling

        enable_profiling()
        logger.info("Performance profiling enabled")

    # EPIC-018: Warm cache in background
    try:
        import asyncio as _asyncio

        from solstein.infrastructure.cache import CacheManager as _CacheManager

        _cache = _CacheManager()
        _asyncio.create_task(warm_cache(_cache))
        logger.info("Cache warming task scheduled")
    except Exception as _exc:
        logger.warning("Cache warming could not start", error=str(_exc))

    # EPIC-024 / STORY-084: Start Supabase Realtime listener
    try:
        from solstein.api.websocket.realtime_listener import start_realtime_listener

        await start_realtime_listener()
        logger.info("Supabase Realtime listener started")
    except (ImportError, ConnectionError, OSError) as _rt_exc:
        logger.warning(
            "Supabase Realtime listener could not start",
            error=str(_rt_exc),
        )

    yield

    # EPIC-024: Stop Realtime listener before shutdown
    try:
        from solstein.api.websocket.realtime_listener import stop_realtime_listener

        await stop_realtime_listener()
    except (ImportError, RuntimeError) as _rt_exc:
        logger.warning("Realtime listener stop error", error=str(_rt_exc))

    logger.info("Executing graceful shutdown sequence")
    await graceful_shutdown.shutdown()
    logger.info("Shutting down SolStein API server")


# Initialize FastAPI app
app = FastAPI(
    title="SolStein Competitive Intelligence API",
    description="AI-powered competitive intelligence platform for VC/PE firms",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.cors_origins,
    allow_credentials=True,
    allow_methods=settings.api.cors_methods,
    allow_headers=settings.api.cors_headers,
    max_age=600,
)

# Setup middleware (order matters)
setup_exception_handlers(app)
setup_logging_middleware(app)
setup_rate_limiting(app)
setup_security_middleware(app)

# EPIC-023: Performance monitoring middleware
setup_performance_middleware(app, enable_timing=True)

# EPIC-023: Profiling dashboard
from solstein.monitoring.profiling.dashboard import router as profiling_router

app.include_router(profiling_router, prefix="/admin")

# STORY-086: Data access audit trail (must be added BEFORE TenantMiddleware
# so it executes AFTER tenant_id is set on request.state)
from .middleware.audit import AuditMiddleware  # noqa: E402

app.add_middleware(AuditMiddleware)

# Multi-tenancy
app.add_middleware(TenantMiddleware)

# Include Routers
app.include_router(auth.router)
app.include_router(enrichment.router)
app.include_router(health.router)
app.include_router(health.metrics_router)
app.include_router(companies.router)
app.include_router(scoring.router, prefix="/scoring")
app.include_router(market.router, prefix="/market")
app.include_router(export.router, prefix="/export")
app.include_router(jobs.router, prefix="/jobs")
app.include_router(drill_down.router)
app.include_router(simulation.router, prefix="/simulation")
app.include_router(async_jobs.router)
app.include_router(research_jobs.router, prefix="/jobs")
app.include_router(semantic_search.router)
app.include_router(review.router, prefix="/api/v1")

# STORY-088: Admin DLQ endpoint — list, inspect, resolve, re-queue failed tasks
from .routers.admin_dlq import router as admin_dlq_router  # noqa: E402

app.include_router(admin_dlq_router)

# WebSocket realtime endpoints (EPIC-024)
from .websocket.routes import router as ws_router

app.include_router(ws_router)

# Dashboard API
from .routers.dashboard import router as dashboard_router

app.include_router(dashboard_router)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html() -> Any:
    """Custom Swagger UI with SolStein branding."""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="SolStein API Documentation",
        swagger_favicon_url="https://solstein.ai/favicon.ico",
    )


@app.get("/healthz", tags=["Health"], include_in_schema=False)
async def health_check_alias() -> dict[str, Any]:
    """Health check alias for K8s."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    uvicorn.run(
        "solstein.api.main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.environment == "development",
        log_level="info",
    )
