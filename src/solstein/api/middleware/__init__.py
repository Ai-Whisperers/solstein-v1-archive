"""API Middleware for SolStein platform."""

from .logging import (
    setup_logging_middleware,
    ContextMiddleware,
    RequestIDMiddleware,
    RequestLoggingMiddleware,
    ErrorLoggingMiddleware,
)
from .rate_limit import (
    RateLimitConfig,
    RateLimitMiddleware,
    UserRateLimitMiddleware,
    setup_rate_limiting,
)
from .security import (
    AuthenticationMiddleware,
    setup_security_middleware,
)
from .tracing import (
    PerformanceMetricsMiddleware,
    RequestTracingMiddleware,
    get_correlation_id,
)

__all__ = [
    # Logging
    "setup_logging_middleware",
    "ContextMiddleware",
    "RequestIDMiddleware",
    "RequestLoggingMiddleware",
    "ErrorLoggingMiddleware",
    # Security
    "setup_security_middleware",
    "AuthenticationMiddleware",
    # Rate limiting
    "RateLimitMiddleware",
    "UserRateLimitMiddleware",
    "RateLimitConfig",
    "setup_rate_limiting",
    # Tracing
    "RequestTracingMiddleware",
    "PerformanceMetricsMiddleware",
    "get_correlation_id",
]
