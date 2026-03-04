"""Request tracing and observability middleware.

Provides:
- Correlation IDs for request tracing
- Request timing and logging
- Performance metrics collection
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class RequestTracingMiddleware(BaseHTTPMiddleware):
    """Add correlation IDs and request tracing to all requests.

    Adds X-Correlation-ID header to track requests across services.
    Logs request timing and performance metrics.

    Example:
        >>> from fastapi import FastAPI
        >>> app = FastAPI()
        >>> app.add_middleware(RequestTracingMiddleware)
    """

    def __init__(self, app, header_name: str = "X-Correlation-ID"):
        """Initialize tracing middleware.

        Args:
            app: FastAPI application
            header_name: Header name for correlation ID
        """
        super().__init__(app)
        self.header_name = header_name

    def _get_correlation_id(self, request: Request) -> str:
        """Get or generate correlation ID."""
        # Check for existing correlation ID from upstream
        existing = request.headers.get(self.header_name)
        if existing:
            return existing

        # Generate new correlation ID
        return str(uuid.uuid4())

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with tracing."""
        # Get correlation ID
        correlation_id = self._get_correlation_id(request)

        # Store in request state for access in routes
        request.state.correlation_id = correlation_id

        # Bind correlation ID to logger context
        with logger.contextualize(correlation_id=correlation_id):
            # Log request start
            start_time = time.time()
            logger.info(
                f"Request started: {request.method} {request.url.path}",
                method=request.method,
                path=request.url.path,
                query=str(request.query_params),
                client=request.client.host if request.client else "unknown",
            )

            try:
                # Process request
                response = await call_next(request)

                # Calculate duration
                duration_ms = (time.time() - start_time) * 1000

                # Add correlation ID to response headers
                response.headers[self.header_name] = correlation_id

                # Log request completion
                logger.info(
                    f"Request completed: {request.method} {request.url.path} - {response.status_code} ({duration_ms:.2f}ms)",
                    method=request.method,
                    path=request.url.path,
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                )

                return response

            except Exception as e:
                # Calculate duration even on error
                duration_ms = (time.time() - start_time) * 1000

                # Log error
                logger.error(
                    f"Request failed: {request.method} {request.url.path} - {type(e).__name__} ({duration_ms:.2f}ms)",
                    method=request.method,
                    path=request.url.path,
                    error_type=type(e).__name__,
                    error=str(e),
                    duration_ms=duration_ms,
                )
                raise


class PerformanceMetricsMiddleware(BaseHTTPMiddleware):
    """Collect performance metrics for API requests.

    Tracks:
    - Request counts by endpoint and status
    - Response times (p50, p95, p99)
    - Error rates
    """

    def __init__(self, app):
        """Initialize metrics middleware."""
        super().__init__(app)
        self._metrics: dict = {
            "requests_total": 0,
            "requests_by_path": {},
            "requests_by_status": {},
            "response_times": [],
            "errors_total": 0,
        }

    def _record_request(self, path: str, status_code: int, duration_ms: float) -> None:
        """Record request metrics."""
        self._metrics["requests_total"] += 1

        # By path
        if path not in self._metrics["requests_by_path"]:
            self._metrics["requests_by_path"][path] = {"count": 0, "total_time": 0}
        self._metrics["requests_by_path"][path]["count"] += 1
        self._metrics["requests_by_path"][path]["total_time"] += duration_ms

        # By status
        status = str(status_code)
        self._metrics["requests_by_status"][status] = self._metrics["requests_by_status"].get(status, 0) + 1

        # Response times (keep last 1000)
        self._metrics["response_times"].append(duration_ms)
        if len(self._metrics["response_times"]) > 1000:
            self._metrics["response_times"] = self._metrics["response_times"][-1000:]

        # Error count
        if status_code >= 400:
            self._metrics["errors_total"] += 1

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics."""
        start_time = time.time()

        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000

            self._record_request(
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
            )

            # Add metrics headers
            response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

            return response

        except Exception:
            duration_ms = (time.time() - start_time) * 1000
            self._record_request(
                path=request.url.path,
                status_code=500,
                duration_ms=duration_ms,
            )
            raise

    def get_metrics(self) -> dict:
        """Get current metrics snapshot."""
        import statistics

        metrics = self._metrics.copy()

        # Calculate percentiles
        if metrics["response_times"]:
            times = sorted(metrics["response_times"])
            n = len(times)
            metrics["response_time_p50"] = times[int(n * 0.5)]
            metrics["response_time_p95"] = times[int(n * 0.95)]
            metrics["response_time_p99"] = times[int(n * 0.99)]
            metrics["response_time_avg"] = statistics.mean(times)
        else:
            metrics["response_time_p50"] = 0
            metrics["response_time_p95"] = 0
            metrics["response_time_p99"] = 0
            metrics["response_time_avg"] = 0

        return metrics


def get_correlation_id(request: Request) -> str | None:
    """Get correlation ID from request.

    Use in route handlers to access the correlation ID.

    Example:
        >>> @router.get("/data")
        ... async def get_data(request: Request):
        ...     correlation_id = get_correlation_id(request)
        ...     logger.info("Processing", correlation_id=correlation_id)
    """
    return getattr(request.state, "correlation_id", None)
