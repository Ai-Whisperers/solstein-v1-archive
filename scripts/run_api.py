#!/usr/bin/env python3
"""
Run SolStein FastAPI server.

Production-ready API server with:
- Auto-reload in development
- Structured logging
- Environment-based configuration
- Health checks
"""

import sys
from pathlib import Path

import uvicorn
from loguru import logger

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from solstein.config import Settings  # noqa: E402


def configure_logging():
    """Configure structured logging."""
    logger.remove()  # Remove default handler

    # Add console handler
    logger.add(
        sys.stderr,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        level="INFO",
    )

    # Add file handler
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    logger.add(
        log_dir / "solstein_api_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="30 days",
        format=("{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"),
        level="DEBUG",
    )


def main():
    """Main entry point."""
    # Configure logging
    configure_logging()

    # Load settings
    settings = Settings()

    logger.info("=" * 60)
    logger.info("SolStein Competitive Intelligence API")
    logger.info("=" * 60)
    logger.info("Version: 1.0.0")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Host: {settings.api.host}")
    logger.info(f"Port: {settings.api.port}")
    logger.info(f"Debug: {settings.api.debug}")
    logger.info(f"Data directory: {settings.data.data_dir}")
    logger.info("=" * 60)

    # Create necessary directories
    Path("data/output/exports/excel").mkdir(parents=True, exist_ok=True)
    Path("data/output/exports/json").mkdir(parents=True, exist_ok=True)

    # Run server
    uvicorn.run(
        "solstein.api.main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.environment == "development",
        log_level="info",
        access_log=True,
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)
