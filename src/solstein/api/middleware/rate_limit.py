"""Rate limiting middleware for API protection.

Provides configurable rate limiting with multiple strategies:
- IP-based limiting
- User-based limiting
- Endpoint-specific limits with per-route configuration
"""

from __future__ import annotations

import os
import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

# Route-specific rate limits: requests per minute
ROUTE_LIMITS = {
    # Expensive analysis routes: 10/minute
    "/api/v1/companies/analyze": 10,
    "/api/v1/research/": 10,
    "/api/v1/export/": 10,
    "/scoring/": 10,
    "/market/analysis": 10,
    "/export/": 10,
    # General routes: 60/minute (default)
}


def get_rate_limit_for_path(path: str) -> int:
    """Determine rate limit for a given path.

    Args:
        path: Request path

    Returns:
        Requests per minute limit
    """
    # Check for exact matches first
    if path in ROUTE_LIMITS:
        return ROUTE_LIMITS[path]

    # Check for prefix matches
    for route_pattern, limit in ROUTE_LIMITS.items():
        if (route_pattern.endswith("/")) and (path.startswith(route_pattern)):
            return limit

    # Default: 60 requests per minute
    return 60


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""

    requests_per_minute: int = 60
    burst_size: int = 10
    window_seconds: int = 60


@dataclass
class RateLimitEntry:
    """Tracks rate limit usage for a client."""

    requests: list[float] = field(default_factory=list)
    blocked_until: float | None = None

    def is_blocked(self) -> bool:
        """Check if client is currently blocked."""
        if self.blocked_until is None:
            return False
        return time.time() < self.blocked_until

    def clean_old_requests(self, window_seconds: int) -> None:
        """Remove requests outside the time window."""
        cutoff = time.time() - window_seconds
        self.requests = [t for t in self.requests if t > cutoff]

    def add_request(self) -> None:
        """Record a new request."""
        self.requests.append(time.time())

    def get_request_count(self, window_seconds: int) -> int:
        """Get count of requests in the time window."""
        self.clean_old_requests(window_seconds)
        return len(self.requests)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with configurable strategies.

    Uses sliding window algorithm for accurate rate limiting.
    Supports IP-based and user-based limiting.
    Supports per-route rate limit configuration.

    Example:
        >>> from fastapi import FastAPI
        >>> app = FastAPI()
        >>> app.add_middleware(
        ...     RateLimitMiddleware,
        ...     config=RateLimitConfig(requests_per_minute=100)
        ... )
    """

    # Paths excluded from rate limiting
    EXCLUDED_PATHS = {
        "/health",
        "/ready",
        "/metrics",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/healthz",
    }

    def __init__(
        self,
        app,
        config: RateLimitConfig | None = None,
        key_func: Callable[[Request], str] | None = None,
    ):
        """Initialize rate limiting middleware.

        Args:
            app: FastAPI application
            config: Rate limiting configuration
            key_func: Function to extract client key from request
                     (defaults to IP address)
        """
        super().__init__(app)
        self.config = config or RateLimitConfig()
        self.key_func = key_func or self._get_client_key
        self._storage: dict[str, RateLimitEntry] = defaultdict(RateLimitEntry)

    def _get_client_key(self, request: Request) -> str:
        """Extract client identifier from request.

        Uses X-Forwarded-For header if present, otherwise REMOTE_ADDR.
        Falls back to "unknown" if neither is available.
        """
        # Check for forwarded IP (behind proxy/load balancer)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Use direct client IP
        client_ip = request.client.host if request.client else "unknown"
        return client_ip

    def _is_excluded(self, request: Request) -> bool:
        """Check if path is excluded from rate limiting."""
        # Check environment first
        if os.getenv("SOLSTEIN_DISABLE_RATE_LIMIT") == "true":
            return True

        path = request.url.path
        return path in self.EXCLUDED_PATHS

    def _check_rate_limit(self, key: str, requests_per_minute: int) -> tuple[bool, dict]:
        """Check if request should be rate limited.

        Args:
            key: Client identifier
            requests_per_minute: Rate limit for this request

        Returns:
            Tuple of (allowed: bool, headers: dict)
        """
        # Check environment first
        if os.getenv("SOLSTEIN_DISABLE_RATE_LIMIT") == "true":
            return True, {}

        entry = self._storage[key]
        now = time.time()

        # Check if currently blocked
        if entry.is_blocked():
            remaining_time = int(entry.blocked_until - now)
            return False, {
                "X-RateLimit-Limit": str(requests_per_minute),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(remaining_time),
                "Retry-After": str(remaining_time),
            }

        # Clean old requests and count current
        entry.clean_old_requests(self.config.window_seconds)
        current_count = len(entry.requests)

        # Check if over limit
        if current_count >= requests_per_minute:
            # Block client
            block_duration = self.config.window_seconds
            entry.blocked_until = now + block_duration
            logger.warning(f"Rate limit exceeded for client: {key} (limit: {requests_per_minute}/min)")
            return False, {
                "X-RateLimit-Limit": str(requests_per_minute),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(block_duration),
                "Retry-After": str(block_duration),
            }

        # Allow request
        entry.add_request()
        remaining = requests_per_minute - current_count - 1
        reset_time = int(now + self.config.window_seconds)

        return True, {
            "X-RateLimit-Limit": str(requests_per_minute),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_time),
        }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting."""
        # Skip rate limiting for excluded paths
        if self._is_excluded(request):
            return await call_next(request)

        # Get client identifier
        key = self.key_func(request)

        # Get per-route limit if configured, otherwise use default config
        route_limit = get_rate_limit_for_path(request.url.path)

        # Check rate limit
        allowed, headers = self._check_rate_limit(key, route_limit)

        if not allowed:
            # Get request_id from state if available
            request_id = getattr(request.state, "request_id", None) or "unknown"

            # Return 429 Too Many Requests with standardized error format
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests",
                        "details": None,
                    },
                    "request_id": request_id,
                },
            )
            for header, value in headers.items():
                response.headers[header] = value
            return response

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        for header, value in headers.items():
            response.headers[header] = value

        return response


class UserRateLimitMiddleware(RateLimitMiddleware):
    """Rate limiting based on authenticated user.

    Falls back to IP-based limiting for unauthenticated requests.
    """

    def _get_client_key(self, request: Request) -> str:
        """Extract user ID from request, fall back to IP."""
        # Try to get user from request state (set by auth middleware)
        user = getattr(request.state, "user", None)
        if user and hasattr(user, "id"):
            return f"user:{user.id}"

        # Fall back to IP-based
        return super()._get_client_key(request)


# Convenience function for setting up rate limiting
def setup_rate_limiting(app, requests_per_minute: int = 60) -> None:
    """Add rate limiting middleware to FastAPI app.

    Args:
        app: FastAPI application
        requests_per_minute: Default rate limit per client
    """
    config = RateLimitConfig(requests_per_minute=requests_per_minute)
    app.add_middleware(RateLimitMiddleware, config=config)
    logger.info(f"Rate limiting enabled: {requests_per_minute} requests/minute (with per-route overrides)")
