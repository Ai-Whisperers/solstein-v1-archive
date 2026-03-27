"""Security Middleware for Solstein API.

STORY-068: Supabase JWT Authentication Middleware

Implements:
- CORS (Cross-Origin Resource Sharing) — configured in main.py
- Security headers (XSS, Clickjacking, MIME sniffing)
- Supabase JWT authentication via get_user API
- Input validation and sanitization

Middleware ordering (REQ-4):
  RateLimitMiddleware -> SupabaseJWTMiddleware -> SanitizationMiddleware -> LoggingMiddleware
"""

from collections.abc import Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger
from supabase_auth.errors import AuthApiError


class SecurityHeadersMiddleware:
    """Add security headers to all responses.

    Uses raw ASGI interface for better performance (avoids Starlette's base middleware overhead).
    """

    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    }

    def __init__(self, app: Callable) -> None:
        self.app = app

    async def __call__(self, scope: dict, receive: Callable, send: Callable) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message: dict) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                for header, value in self.SECURITY_HEADERS.items():
                    headers.append((header.lower().encode(), value.encode()))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_with_headers)


class SupabaseJWTMiddleware:
    """Validate Bearer tokens via Supabase Auth for all protected routes.

    STORY-068: Replaces the old AuthenticationMiddleware that had bypass entries
    for /companies and /enrichment. The bypass allowlist now only contains
    genuinely public routes.

    On successful verification, sets request.state.supabase_user with
    the verified user object including tenant_id (from app_metadata or user_metadata).
    """

    # REQ-1: Only genuinely public routes are excluded from authentication.
    PUBLIC_PATHS = frozenset(
        {
            "/health",
            "/healthz",
            "/ready",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/auth/login",
            "/auth/signup",
            "/auth/refresh",
        }
    )

    # Path prefixes that are always public
    PUBLIC_PREFIXES = (
        "/docs",
        "/redoc",
    )

    def __init__(self, app: Callable) -> None:
        self.app = app

    def _is_public_path(self, path: str) -> bool:
        """Check if path is in the public allowlist."""
        if path in self.PUBLIC_PATHS:
            return True
        return any(path.startswith(prefix + "/") or path == prefix for prefix in self.PUBLIC_PREFIXES)

    async def __call__(self, scope: dict, receive: Callable, send: Callable) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        path = request.url.path

        # Skip auth for public paths
        if self._is_public_path(path):
            await self.app(scope, receive, send)
            return

        # Extract Authorization header
        auth_header = request.headers.get("authorization", "")
        if not auth_header:
            response = JSONResponse(
                status_code=401,
                content={
                    "error": {
                        "code": "AUTH_MISSING",
                        "message": "Authorization header required",
                    }
                },
            )
            await response(scope, receive, send)
            return

        # Validate Bearer token format
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            response = JSONResponse(
                status_code=401,
                content={
                    "error": {
                        "code": "AUTH_FORMAT",
                        "message": "Authorization header must be: Bearer <token>",
                    }
                },
            )
            await response(scope, receive, send)
            return

        token = parts[1]

        # Verify token via Supabase Auth (REQ-2)
        try:
            from solstein.core.supabase_client import get_supabase

            client = get_supabase()
            user_response = client.auth.get_user(token)
        except AuthApiError as e:
            logger.warning(f"JWT verification failed for {path}: {e.message}")
            response = JSONResponse(
                status_code=401,
                content={
                    "error": {
                        "code": "AUTH_INVALID",
                        "message": "Invalid or expired token",
                    }
                },
            )
            await response(scope, receive, send)
            return
        except (ValueError, ImportError) as e:
            logger.error(f"Supabase unavailable for JWT verification: {e}")
            response = JSONResponse(
                status_code=503,
                content={
                    "error": {
                        "code": "AUTH_UNAVAILABLE",
                        "message": "Authentication service unavailable",
                    }
                },
            )
            await response(scope, receive, send)
            return

        if not user_response or not user_response.user:
            response = JSONResponse(
                status_code=401,
                content={
                    "error": {
                        "code": "AUTH_INVALID",
                        "message": "Invalid or expired token",
                    }
                },
            )
            await response(scope, receive, send)
            return

        # REQ-3: Extract tenant_id and make available downstream
        user = user_response.user
        tenant_id = None
        if user.app_metadata:
            tenant_id = user.app_metadata.get("tenant_id")
        if not tenant_id and user.user_metadata:
            tenant_id = user.user_metadata.get("tenant_id")

        # Set user info on request state for downstream handlers
        scope.setdefault("state", {})
        scope["state"]["supabase_user"] = user
        scope["state"]["tenant_id"] = tenant_id
        scope["state"]["user_id"] = user.id
        scope["state"]["user_email"] = user.email

        logger.debug(f"Authenticated request to {path} by user {user.email}")
        await self.app(scope, receive, send)


class InputSanitizationMiddleware:
    """Sanitize and validate incoming requests.

    Uses raw ASGI interface for better performance (avoids Starlette's base middleware overhead).
    """

    def __init__(self, app: Callable) -> None:
        self.app = app

    async def __call__(self, scope: dict, receive: Callable, send: Callable) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)

        # Check content length
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 1024 * 1024:  # 1MB limit
            logger.warning(f"Request too large: {content_length} bytes")
            response = JSONResponse(
                status_code=413,
                content={
                    "error": {
                        "code": "VAL_001",
                        "message": "Request payload exceeds maximum size",
                    }
                },
            )
            await response(scope, receive, send)
            return

        # Check for suspicious patterns in URL
        url_str = str(request.url)
        suspicious_patterns = ["'", '"', "--", "/*", "*/", "xp_", "sp_"]
        if any(pattern in url_str.lower() for pattern in suspicious_patterns):
            logger.warning(f"Suspicious URL pattern detected: {url_str}")
            response = JSONResponse(
                status_code=400,
                content={
                    "error": {
                        "code": "VAL_002",
                        "message": "Invalid characters in request",
                    }
                },
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)


def setup_security_middleware(app: object) -> None:
    """Setup all security middleware.

    STORY-068 REQ-4: Middleware ordering is:
      RateLimitMiddleware -> SupabaseJWTMiddleware -> SanitizationMiddleware -> LoggingMiddleware

    Note: In Starlette/FastAPI, middleware is applied in LIFO order.
    The last middleware added is the first to process the request.
    So we add in reverse order.
    """
    # CORS middleware is configured in main.py — DO NOT add here.

    # Added first = processed last (innermost):
    # Input sanitization (validates format after auth)
    app.add_middleware(InputSanitizationMiddleware)  # type: ignore[attr-defined]

    # Supabase JWT Authentication (REQ-2)
    app.add_middleware(SupabaseJWTMiddleware)  # type: ignore[attr-defined]

    # Security headers (outermost, applied to all responses)
    app.add_middleware(SecurityHeadersMiddleware)  # type: ignore[attr-defined]

    logger.info("Security middleware configured: SecurityHeaders -> SupabaseJWT -> InputSanitization")
