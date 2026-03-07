"""Health checking models for LLM providers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ProviderErrorType(str, Enum):
    """Types of provider errors."""

    RATE_LIMIT = "rate_limit"
    AUTHENTICATION = "authentication"
    QUOTA_EXHAUSTED = "quota_exhausted"
    NETWORK_ERROR = "network_error"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"
    HEALTHY = "healthy"


class ProviderStatus(str, Enum):
    """Provider health status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    RATE_LIMITED = "rate_limited"
    EXHAUSTED = "exhausted"


@dataclass
class ProviderHealth:
    """Health status of an LLM provider."""

    provider: str
    status: ProviderStatus
    last_error: ProviderErrorType | None = None
    last_checked: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    error_message: str = ""
    retry_after: datetime | None = None
    consecutive_failures: int = 0
    total_failures: int = 0
    total_successes: int = 0
    estimated_credits_remaining: bool | None = None

    @property
    def is_available(self) -> bool:
        """Check if provider can be used."""
        if self.status == ProviderStatus.HEALTHY:
            return True
        if self.status == ProviderStatus.RATE_LIMITED and self.retry_after:
            return datetime.now(timezone.utc) >= self.retry_after
        return False

    @property
    def should_retry(self) -> bool:
        """Check if failed request should be retried."""
        if self.status == ProviderStatus.RATE_LIMITED:
            return True
        if self.consecutive_failures < 3:
            return True
        return False


@dataclass
class ProviderError:
    """Structured error information from provider."""

    error_type: ProviderErrorType
    message: str
    status_code: int | None = None
    retry_after_seconds: int | None = None
    provider: str | None = None
