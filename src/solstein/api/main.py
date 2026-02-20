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

from datetime import datetime
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from loguru import logger

from ..config import Settings

# Import Routers
from .routers import companies, export, jobs, market, scoring, simulation

# Initialize FastAPI app
app = FastAPI(
    title="SolStein Competitive Intelligence API",
    description="AI-powered competitive intelligence platform for VC/PE firms",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances (for startup logging)
settings = Settings()


# Include Routers
app.include_router(companies.router)
app.include_router(scoring.router, prefix="/scoring")
app.include_router(market.router, prefix="/market")
app.include_router(export.router, prefix="/export")
app.include_router(simulation.router, prefix="/simulation")
app.include_router(jobs.router, prefix="/jobs")


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "environment": settings.environment,
    }


# Custom docs endpoint
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html() -> Any:
    """Custom Swagger UI with SolStein branding."""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="SolStein API Documentation",
        swagger_favicon_url="https://solstein.ai/favicon.ico",
    )


# Startup event
@app.on_event("startup")
async def startup_event() -> None:
    """Initialize application on startup."""
    logger.info("Starting SolStein API server")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Data directory: {settings.data.data_dir}")

    # Create necessary directories
    settings.data.ensure_dirs()
    if settings.logging.file_path:
        settings.logging.file_path.parent.mkdir(parents=True, exist_ok=True)


# Health check endpoint alias
@app.get("/healthz", tags=["Health"], include_in_schema=False)
async def health_check_alias() -> dict[str, Any]:
    """Health check alias for K8s."""
    return await health_check()


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Cleanup on shutdown."""
    logger.info("Shutting down SolStein API server")


# Main entry point
if __name__ == "__main__":
    uvicorn.run(
        "solstein.api.main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.environment == "development",
        log_level="info",
    )
