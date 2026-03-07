"""Error classification for LLM providers."""

from __future__ import annotations

from typing import Any

from .models import ProviderError, ProviderErrorType


class ErrorClassifier:
    """Classifies provider errors into structured types."""

    # Error detection patterns
    RATE_LIMIT_PATTERNS = [
        "rate limit",
        "too many requests",
        "rate_limit",
        "429",
        "throttled",
        "quota exceeded",
    ]

    AUTH_PATTERNS = [
        "unauthorized",
        "invalid api key",
        "authentication",
        "auth",
        "401",
        "forbidden",
        "403",
    ]

    QUOTA_PATTERNS = [
        "quota",
        "credits exhausted",
        "out of credits",
        "billing",
        "payment",
        "402",
        "limit exceeded",
    ]

    TIMEOUT_PATTERNS = [
        "timeout",
        "timed out",
        "connection timeout",
    ]

    NETWORK_PATTERNS = [
        "connection error",
        "network",
        "unreachable",
        "refused",
        "dns",
        "ssl",
    ]

    def classify(self, error: Exception, provider: str) -> ProviderError:
        """Classify an exception into a structured error type."""
        error_str, message, status_code, retry_after = self._extract_details(error)

        # Check each error type in order of specificity
        checks = [
            (self._check_rate_limit, error_str, message, status_code, retry_after, provider),
            (self._check_authentication, error_str, message, status_code, provider),
            (self._check_quota, error_str, message, status_code, provider),
            (self._check_timeout, error_str, message, provider),
            (self._check_network, error_str, message, provider),
        ]

        for check_func, *args in checks:
            result = check_func(*args)
            if result:
                return result

        # Unknown error type
        return ProviderError(
            error_type=ProviderErrorType.UNKNOWN,
            message=message,
            status_code=status_code,
            provider=provider,
        )

    def _extract_details(self, error: Exception) -> tuple[str, str, int | None, str | None]:
        """Extract message, status code, and retry-after from exception."""
        error_str = str(error).lower()
        message = str(error)
        status_code = None
        retry_after = None

        # Try to extract status code from common exception types
        if hasattr(error, "status_code"):
            status_code = error.status_code
        elif hasattr(error, "code"):
            status_code = error.code

        # Try to extract retry-after
        if hasattr(error, "retry_after"):
            retry_after = error.retry_after
        elif hasattr(error, "headers"):
            retry_after = error.headers.get("retry-after")

        return error_str, message, status_code, retry_after

    def _check_rate_limit(
        self,
        error_str: str,
        message: str,
        status_code: int | None,
        retry_after: str | None,
        provider: str,
    ) -> ProviderError | None:
        """Check if error is a rate limit."""
        if status_code == 429 or any(p in error_str for p in self.RATE_LIMIT_PATTERNS):
            return ProviderError(
                error_type=ProviderErrorType.RATE_LIMIT,
                message=message,
                status_code=429,
                retry_after_seconds=int(retry_after) if retry_after else 60,
                provider=provider,
            )
        return None

    def _check_authentication(
        self,
        error_str: str,
        message: str,
        status_code: int | None,
        provider: str,
    ) -> ProviderError | None:
        """Check if error is an authentication failure."""
        if status_code == 401 or any(p in error_str for p in self.AUTH_PATTERNS):
            return ProviderError(
                error_type=ProviderErrorType.AUTHENTICATION,
                message=message,
                status_code=401,
                provider=provider,
            )
        return None

    def _check_quota(
        self,
        error_str: str,
        message: str,
        status_code: int | None,
        provider: str,
    ) -> ProviderError | None:
        """Check if error is quota exhaustion."""
        if status_code == 402 or any(p in error_str for p in self.QUOTA_PATTERNS):
            return ProviderError(
                error_type=ProviderErrorType.QUOTA_EXHAUSTED,
                message=message,
                status_code=status_code or 402,
                provider=provider,
            )
        return None

    def _check_timeout(self, error_str: str, message: str, provider: str) -> ProviderError | None:
        """Check if error is a timeout."""
        if any(p in error_str for p in self.TIMEOUT_PATTERNS):
            return ProviderError(
                error_type=ProviderErrorType.TIMEOUT,
                message=message,
                provider=provider,
            )
        return None

    def _check_network(self, error_str: str, message: str, provider: str) -> ProviderError | None:
        """Check if error is a network error."""
        if any(p in error_str for p in self.NETWORK_PATTERNS):
            return ProviderError(
                error_type=ProviderErrorType.NETWORK_ERROR,
                message=message,
                provider=provider,
            )
        return None
