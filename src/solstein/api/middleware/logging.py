"""
Request/Response Logging Middleware (Phase 10)

Logs all API requests and responses with:
- Request method, path, status
- Request duration
- User information (if available)
- Error details (if failed)
"""

import logging
import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import json

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID for tracing."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add request ID to request scope."""
        request_id = str(uuid.uuid4())[:8]
        request.scope["request_id"] = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request/response details."""
        request_id = request.scope.get("request_id", "unknown")
        start_time = time.time()

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Get user info if authenticated
        user_id = self._get_user_id(request)

        # Log request
        logger.info(
            f"📨 REQUEST: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client_ip": client_ip,
                "user_id": user_id,
                "query_params": dict(request.query_params) or None,
            },
        )

        try:
            response = await call_next(request)
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"❌ REQUEST FAILED: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": duration * 1000,
                    "error": str(e),
                    "client_ip": client_ip,
                    "user_id": user_id,
                },
                exc_info=True,
            )
            raise

        duration = time.time() - start_time

        # Log response
        log_level = "info" if response.status_code < 400 else "warning"
        log_func = getattr(logger, log_level)

        log_func(
            f"📤 RESPONSE: {request.method} {request.url.path} → {response.status_code}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration * 1000,
                "client_ip": client_ip,
                "user_id": user_id,
            },
        )

        # Add timing headers
        response.headers["X-Response-Time"] = f"{duration * 1000:.2f}ms"

        return response

    @staticmethod
    def _get_user_id(request: Request) -> str:
        """Extract user ID from Authorization header."""
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            return token[:8] + "..."  # Redact token
        return "anonymous"


class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """Log errors with details for debugging."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log error responses."""
        response = await call_next(request)

        # Log errors
        if response.status_code >= 400:
            try:
                body = await response.body()
                if body:
                    try:
                        error_data = json.loads(body)
                        logger.warning(
                            f"⚠️  ERROR RESPONSE: {response.status_code}",
                            extra={
                                "path": request.url.path,
                                "status_code": response.status_code,
                                "error": error_data.get("error"),
                                "message": error_data.get("message"),
                            },
                        )
                    except json.JSONDecodeError:
                        logger.warning(
                            f"⚠️  ERROR RESPONSE: {response.status_code}",
                            extra={"path": request.url.path, "status_code": response.status_code},
                        )
            except Exception:
                pass

        return response


def setup_logging_middleware(app) -> None:
    """Setup all logging middleware."""
    app.add_middleware(ErrorLoggingMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)

    logger.info("✅ Logging middleware configured")
