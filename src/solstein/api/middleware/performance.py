"""API performance monitoring middleware for EPIC-023.

EPIC-023 Story 1: Timing middleware for API endpoints
"""

from __future__ import annotations

import time
from typing import Any

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware to monitor API endpoint performance.

    Logs timing information for all requests and identifies slow endpoints.
    """

    def __init__(self, app: Any, slow_threshold_ms: float = 100.0):
        super().__init__(app)
        self.slow_threshold_ms = slow_threshold_ms

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process request and log performance metrics."""
        start_time = time.perf_counter()

        # Get request info
        method = request.method
        path = request.url.path

        try:
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log based on duration
            log_data = {
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
            }

            if duration_ms > self.slow_threshold_ms:
                logger.warning(f"Slow request: {method} {path}", **log_data)
            else:
                logger.debug(f"Request completed: {method} {path}", **log_data)

            # Add timing header in development
            response.headers["X-Response-Time-Ms"] = str(round(duration_ms, 2))

            return response

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"Request failed: {method} {path}",
                method=method,
                path=path,
                duration_ms=round(duration_ms, 2),
                error=str(e),
            )
            raise


class QueryCountMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track database query counts per request.

    Helps identify N+1 query problems.
    """

    def __init__(self, app: Any, warn_threshold: int = 10):
        super().__init__(app)
        self.warn_threshold = warn_threshold

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Track database queries during request."""
        # Note: This requires SQLAlchemy event listeners to be set up
        # For now, just a placeholder for the pattern

        start_time = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Add header with query count if available
        response.headers["X-Response-Time-Ms"] = str(round(duration_ms, 2))

        return response


def setup_performance_middleware(app: Any, enable_timing: bool = True) -> None:
    """
    Set up performance monitoring middleware on FastAPI app.

    Args:
        app: FastAPI application
        enable_timing: Whether to enable timing middleware
    """
    if enable_timing:
        app.add_middleware(PerformanceMonitoringMiddleware)
        logger.info("Performance monitoring middleware enabled")


__all__ = [
    "PerformanceMonitoringMiddleware",
    "QueryCountMiddleware",
    "setup_performance_middleware",
]
