"""
Security Middleware for Enrichment API (Phase 10)

Implements:
- CORS (Cross-Origin Resource Sharing)
- Security headers (XSS, Clickjacking, MIME sniffing)
- Bearer token authentication
- Input validation
"""

import logging
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response."""
        response = await call_next(request)

        for header, value in self.SECURITY_HEADERS.items():
            response.headers[header] = value

        logger.debug(f"Added security headers to {request.url.path}")
        return response


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Validate Bearer token authentication."""

    EXCLUDED_PATHS = {"/health", "/ready", "/docs", "/openapi.json", "/redoc", "/metrics"}

    def __init__(self, app, token_validator=None):
        """Initialize with optional token validator."""
        super().__init__(app)
        self.token_validator = token_validator

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Validate authentication on protected endpoints."""
        # Skip authentication for health checks and docs
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)

        # Skip authentication for public endpoints
        if request.url.path.startswith(("/companies", "/enrichment")):
            return await call_next(request)

        # For any other path, let it through to get a proper 404 from FastAPI
        # instead of blocking with 401
        if not request.url.path.startswith(("/api", "/admin")):
            return await call_next(request)

        # Get authorization header
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            logger.warning(f"Missing Authorization header for {request.url.path}")
            return JSONResponse(
                status_code=401,
                content={"error": "unauthorized", "message": "Missing Authorization header", "code": "AUTH_001"},
            )

        # Validate Bearer token format
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            logger.warning(f"Invalid Authorization header format for {request.url.path}")
            return JSONResponse(
                status_code=401,
                content={"error": "unauthorized", "message": "Invalid Authorization header format", "code": "AUTH_002"},
            )

        token = parts[1]

        # Validate token using provided validator or basic check
        if self.token_validator:
            is_valid = await self.token_validator(token)
            if not is_valid:
                logger.warning(f"Invalid token for {request.url.path}")
                return JSONResponse(
                    status_code=401,
                    content={"error": "unauthorized", "message": "Invalid or expired token", "code": "AUTH_003"},
                )
        elif not token or len(token) < 10:
            logger.warning(f"Invalid token format for {request.url.path}")
            return JSONResponse(
                status_code=401,
                content={"error": "unauthorized", "message": "Invalid or expired token", "code": "AUTH_003"},
            )

        logger.debug(f"Authenticated request to {request.url.path}")
        return await call_next(request)

class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """Sanitize and validate incoming requests."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Validate request size and content."""
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 1024 * 1024:  # 1MB limit
            logger.warning(f"Request too large: {content_length} bytes")
            return JSONResponse(
                status_code=413,
                content={
                    "error": "payload_too_large",
                    "message": "Request payload exceeds maximum size",
                    "code": "VAL_001",
                },
            )

        # Check for suspicious patterns in URL
        url_str = str(request.url)
        suspicious_patterns = ["'", '"', "--", "/*", "*/", "xp_", "sp_"]
        if any(pattern in url_str.lower() for pattern in suspicious_patterns):
            logger.warning(f"Suspicious URL pattern detected: {url_str}")
            return JSONResponse(
                status_code=400,
                content={"error": "invalid_request", "message": "Invalid characters in request", "code": "VAL_002"},
            )

        return await call_next(request)


def setup_security_middleware(app) -> None:
    """Setup all security middleware."""
    # CORS middleware is now configured in main.py with secure settings
    # DO NOT add CORS middleware here - it would override the secure configuration
    # See main.py lines 111-119 for the secure CORS configuration

    # Input sanitization (before auth, validate format)
    app.add_middleware(InputSanitizationMiddleware)

    # Authentication
    app.add_middleware(AuthenticationMiddleware)

    # Security headers (last, applied to all responses)
    app.add_middleware(SecurityHeadersMiddleware)

    logger.info("✅ Security middleware configured")
