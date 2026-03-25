"""Request/Response Logging Middleware with unified Loguru logging.

Logs all API requests and responses with:
- Request method, path, status
- Request duration
- User information (if available)
- Error details (if failed)
- Automatic context propagation via contextvars
"""

import json
import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger

from ...utils.context import set_context, reset_context, generate_request_id, generate_correlation_id


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID for tracing."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add request ID to request scope."""
        request_id = str(uuid.uuid4())[:8]
        request.scope["request_id"] = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


class ContextMiddleware(BaseHTTPMiddleware):
    """Set request-scoped context for logging using contextvars.

    This middleware ensures request_id, correlation_id, tenant_id, and user_id
    are propagated to all logs throughout the request lifecycle.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract or generate IDs
        request_id = request.headers.get("X-Request-ID") or generate_request_id()
        correlation_id = request.headers.get("X-Correlation-ID") or generate_correlation_id()

        # Extract tenant/user from request state (set by auth middleware)
        tenant_id = getattr(request.state, "tenant_id", None)
        user_id = getattr(request.state, "user_id", None)

        # Set context for this request
        tokens = set_context(
            request_id=request_id,
            correlation_id=correlation_id,
            tenant_id=tenant_id,
            user_id=user_id,
            operation=f"{request.method}_{request.url.path}",
        )

        # Store in request for handlers
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id

        try:
            logger.debug("Request started", method=request.method, path=request.url.path)
            response = await call_next(request)

            # Add headers to response
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Correlation-ID"] = correlation_id

            logger.debug("Request completed", status_code=response.status_code)
            return response

        except Exception:
            logger.exception("Request failed")
            raise
        finally:
            # ALWAYS reset context to prevent leaks
            reset_context(tokens)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests and responses with context."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request/response details."""
        request_id = getattr(request.state, "request_id", "unknown")
        start_time = time.time()

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Get user info if authenticated
        user_id = self._get_user_id(request)

        # Log request
        logger.info(
            f"📨 REQUEST: {request.method} {request.url.path}",
            method=request.method,
            path=request.url.path,
            client_ip=client_ip,
            user_id=user_id,
            query_params=dict(request.query_params) or None,
        )

        try:
            response = await call_next(request)
        except Exception as e:
            duration = time.time() - start_time
            logger.exception(
                f"❌ REQUEST FAILED: {request.method} {request.url.path}",
                method=request.method,
                path=request.url.path,
                duration_ms=round(duration * 1000, 2),
                error=str(e),
                client_ip=client_ip,
                user_id=user_id,
            )
            raise

        duration = time.time() - start_time

        # Log response
        log_level = "info" if response.status_code < 400 else "warning"

        if response.status_code < 400:
            logger.info(
                f"📤 RESPONSE: {request.method} {request.url.path} → {response.status_code}",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2),
                client_ip=client_ip,
                user_id=user_id,
            )
        else:
            logger.warning(
                f"📤 RESPONSE: {request.method} {request.url.path} → {response.status_code}",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2),
                client_ip=client_ip,
                user_id=user_id,
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
    """Log errors with details for debugging. Never silently swallow exceptions."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log error responses with full context."""
        response = await call_next(request)

        # Log errors
        if response.status_code >= 400:
            response = await self._log_error_response(request, response)

        return response

    async def _log_error_response(self, request: Request, response: Response) -> Response:
        """Log error response details. All failures are logged, never silent.

        Returns a new Response with the body restored so the client receives it.
        """
        from starlette.responses import Response as StarletteResponse

        request_id = getattr(request.state, "request_id", "unknown")

        try:
            # Consume body iterator and immediately restore it so the client receives the body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk if isinstance(chunk, bytes) else chunk.encode("utf-8")
            # Rebuild response with consumed body
            response = StarletteResponse(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

            error_data = None
            error_message = "Unknown error"

            try:
                error_data = json.loads(body)
                error_message = error_data.get("error", error_data.get("message", "Unknown error"))
            except json.JSONDecodeError as e:
                # Log JSON parsing failure but don't fail the whole handler
                logger.warning(
                    "Error response body is not valid JSON",
                    request_id=request_id,
                    status_code=response.status_code,
                    body_preview=body[:200].decode("utf-8", errors="replace"),
                    json_error=str(e),
                )
                error_message = body.decode("utf-8", errors="replace")[:200]

            # Log the actual error
            log_level = "error" if response.status_code >= 500 else "warning"
            logger.log(
                log_level,
                f"⚠️  ERROR RESPONSE: {response.status_code}",
                request_id=request_id,
                path=request.url.path,
                method=request.method,
                status_code=response.status_code,
                error=error_message,
                error_details=error_data,
            )

        except Exception as e:
            # CRITICAL: Never silent. Log everything we know.
            logger.exception(
                "Failed to log error response details",
                request_id=request_id,
                path=request.url.path,
                method=request.method,
                status_code=response.status_code,
                error_type=type(e).__name__,
                error=str(e),
            )

        return response


def setup_logging_middleware(app) -> None:
    """Setup all logging middleware in correct order.

    Order matters:
    1. ContextMiddleware (sets up context first)
    2. RequestIDMiddleware (for backward compat)
    3. ErrorLoggingMiddleware (catches errors)
    4. RequestLoggingMiddleware (logs all requests)
    """
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(ErrorLoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(ContextMiddleware)

    logger.info("✅ Logging middleware configured")
