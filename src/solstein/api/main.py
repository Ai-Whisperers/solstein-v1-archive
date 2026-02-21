"""
SolStein FastAPI Backend - Competitive Intelligence Platform

Production-ready REST API following Vete's architecture patterns:
- Clean architecture with clear separation of concerns
- Type-safe Pydantic models for request/response validation
- OpenAPI/Swagger auto-documentation
- JWT authentication (optional)
- PostgreSQL with async support
- Comprehensive error handling
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from loguru import logger

from ..config import ConfigurationError, Settings
from ..core.production_hardening import (
    FeatureFlagManager,
    GracefulDegradation,
    GracefulShutdown,
    ResponseCache,
)
from .exceptions import setup_exception_handlers
from .middleware import LoggingMiddleware
from .routers import (
    companies,
    drill_down,
    export,
    health,
    jobs,
    market,
    scoring,
    simulation,
)

settings = Settings()

feature_flags: FeatureFlagManager | None = None
response_cache: ResponseCache | None = None
graceful_degradation: GracefulDegradation | None = None
graceful_shutdown: GracefulShutdown | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifecycle manager for startup and shutdown events.

    On startup:
    1. Validates required configuration
    2. Creates necessary directories
    3. Initializes production hardening components
    4. Logs environment information

    On shutdown:
    - Executes graceful shutdown sequence
    """
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
    logger.info(f"Feature flags available: {len(feature_flags.flags)}")
    logger.info("Response cache initialized with TTL support")

    yield

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
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Logging Middleware (Request IDs and Timing)
app.add_middleware(LoggingMiddleware)

# Setup Global Exception Handlers
setup_exception_handlers(app)

# Global dependencies configured in lifespan

# Include Routers
app.include_router(health.router)
app.include_router(health.metrics_router)
app.include_router(companies.router)
app.include_router(scoring.router, prefix="/scoring")
app.include_router(market.router, prefix="/market")
app.include_router(export.router, prefix="/export")
app.include_router(jobs.router, prefix="/jobs")
app.include_router(drill_down.router)
app.include_router(simulation.router, prefix="/simulation")


# Custom docs endpoint
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html() -> Any:
    """Custom Swagger UI with SolStein branding."""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="SolStein API Documentation",
        swagger_favicon_url="https://solstein.ai/favicon.ico",
    )


# Health check endpoint alias for backward compatibility
@app.get("/healthz", tags=["Health"], include_in_schema=False)
async def health_check_alias() -> dict[str, Any]:
    """Health check alias for K8s - routes to /health."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# Main entry point
if __name__ == "__main__":
    uvicorn.run(
        "solstein.api.main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.environment == "development",
        log_level="info",
    )
