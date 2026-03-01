"""Rate limiting middleware for API protection.

Provides configurable rate limiting with multiple strategies:
- IP-based limiting
- User-based limiting
- Endpoint-specific limits
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


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
        """Check if client is currently blocked.""""
        if self.blocked_until is None:
            return False
        return time.time() < self.blocked_until

    def clean_old_requests(self, window_seconds: int) -> None:
        """Remove requests outside the time window.""""
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
        path = request.url.path
        return path in self.EXCLUDED_PATHS

    def _check_rate_limit(self, key: str) -> tuple[bool, dict]:
        """Check if request should be rate limited.

        Returns:
            Tuple of (allowed: bool, headers: dict)
        """
        entry = self._storage[key]
        now = time.time()

        # Check if currently blocked
        if entry.is_blocked():
            remaining_time = int(entry.blocked_until - now)
            return False, {
                "X-RateLimit-Limit": str(self.config.requests_per_minute),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(remaining_time),
                "Retry-After": str(remaining_time),
            }

        # Clean old requests and count current
        entry.clean_old_requests(self.config.window_seconds)
        current_count = len(entry.requests)

        # Check if over limit
        if current_count >= self.config.requests_per_minute:
            # Block client
            block_duration = self.config.window_seconds
            entry.blocked_until = now + block_duration
            logger.warning(f"Rate limit exceeded for client: {key}")
            return False, {
                "X-RateLimit-Limit": str(self.config.requests_per_minute),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(block_duration),
                "Retry-After": str(block_duration),
            }

        # Allow request
        entry.add_request()
        remaining = self.config.requests_per_minute - current_count - 1
        reset_time = int(now + self.config.window_seconds)

        return True, {
            "X-RateLimit-Limit": str(self.config.requests_per_minute),
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

        # Check rate limit
        allowed, headers = self._check_rate_limit(key)

        if not allowed:
            # Return 429 Too Many Requests
            response = JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": int(headers.get("Retry-After", 60)),
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
        requests_per_minute: Rate limit per client
    """
    config = RateLimitConfig(requests_per_minute=requests_per_minute)
    app.add_middleware(RateLimitMiddleware, config=config)
    logger.info(f"Rate limiting enabled: {requests_per_minute} requests/minute")
