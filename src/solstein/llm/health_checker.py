"""LLM Provider health checking with credit and rate limit detection.

Provides proactive health monitoring for LLM providers, detecting:
- Rate limits (429)
- Authentication errors (401)
- Quota exhaustion (402/429)
- Network failures

Supports automatic provider rotation on failures.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

from loguru import logger


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


class ProviderHealthChecker:
    """Proactive health checker for LLM providers.

    Tracks provider health status and detects common failure modes:
    - Rate limiting (429)
    - Authentication failures (401)
    - Quota exhaustion (402/429)
    - Network issues

    Example:
        >>> checker = ProviderHealthChecker()
        >>> await checker.check_all_providers()
        >>> health = checker.get_health("openai")
        >>> if health.is_available:
        ...     result = await call_openai()
        ... else:
        ...     result = await checker.try_alternative("openai")
    """

    # Provider priority order (highest priority first)
    PROVIDER_PRIORITY = ["ollama", "fireworks", "openai", "groq"]

    # Error patterns for classification
    RATE_LIMIT_PATTERNS = [
        "rate limit",
        "too many requests",
        "429",
        "throttled",
        "retry-after",
    ]
    AUTH_PATTERNS = [
        "authentication",
        "unauthorized",
        "invalid api key",
        "401",
    ]
    QUOTA_PATTERNS = [
        "quota",
        "exceeded",
        "insufficient quota",
        "credits",
        "billing",
        "402",
    ]
    TIMEOUT_PATTERNS = [
        "timeout",
        "timed out",
        "deadline exceeded",
    ]
    NETWORK_PATTERNS = [
        "connection",
        "network",
        "unreachable",
        "dns",
        "refused",
    ]

    def __init__(self):
        """Initialize health checker."""
        self._health: dict[str, ProviderHealth] = {}
        self._settings = None
        self._clients: dict[str, Any] = {}

    def _get_settings(self):
        """Lazy load settings."""
        if self._settings is None:
            from ..config import get_settings

            self._settings = get_settings()
        return self._settings

    def _get_client(self, provider: str) -> Any | None:
        """Get or create API client for provider."""
        if provider in self._clients:
            return self._clients[provider]

        settings = self._get_settings()

        try:
            if provider == "openai":
                from openai import AsyncOpenAI

                if not settings.openai_api_key:
                    return None
                client = AsyncOpenAI(api_key=settings.openai_api_key)
                self._clients[provider] = client
                return client

            if provider == "groq":
                import importlib

                if not settings.groq_api_key:
                    return None
                groq_mod = importlib.import_module("groq")
                client = groq_mod.AsyncGroq(api_key=settings.groq_api_key)
                self._clients[provider] = client
                return client

            if provider == "fireworks":
                from openai import AsyncOpenAI

                if not settings.fireworks_api_key:
                    return None
                client = AsyncOpenAI(
                    api_key=settings.fireworks_api_key,
                    base_url="https://api.fireworks.ai/inference/v1",
                )
                self._clients[provider] = client
                return client

        except Exception as e:
            logger.warning(f"Failed to initialize {provider} client: {e}")
            return None

        return None

    def _classify_error(self, error: Exception, provider: str) -> ProviderError:
        """Classify an exception into a structured error type."""
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

        # Classify based on patterns and status codes
        if status_code == 429 or any(p in error_str for p in self.RATE_LIMIT_PATTERNS):
            return ProviderError(
                error_type=ProviderErrorType.RATE_LIMIT,
                message=message,
                status_code=429,
                retry_after_seconds=int(retry_after) if retry_after else 60,
                provider=provider,
            )

        if status_code == 401 or any(p in error_str for p in self.AUTH_PATTERNS):
            return ProviderError(
                error_type=ProviderErrorType.AUTHENTICATION,
                message=message,
                status_code=401,
                provider=provider,
            )

        if status_code == 402 or any(p in error_str for p in self.QUOTA_PATTERNS):
            return ProviderError(
                error_type=ProviderErrorType.QUOTA_EXHAUSTED,
                message=message,
                status_code=status_code or 402,
                provider=provider,
            )

        if any(p in error_str for p in self.TIMEOUT_PATTERNS):
            return ProviderError(
                error_type=ProviderErrorType.TIMEOUT,
                message=message,
                provider=provider,
            )

        if any(p in error_str for p in self.NETWORK_PATTERNS):
            return ProviderError(
                error_type=ProviderErrorType.NETWORK_ERROR,
                message=message,
                provider=provider,
            )

        return ProviderError(
            error_type=ProviderErrorType.UNKNOWN,
            message=message,
            status_code=status_code,
            provider=provider,
        )

    def _update_health_on_error(self, provider: str, error: ProviderError) -> ProviderHealth:
        """Update provider health status after an error."""
        now = datetime.now(timezone.utc)

        if provider not in self._health:
            self._health[provider] = ProviderHealth(provider=provider, status=ProviderStatus.HEALTHY)

        health = self._health[provider]
        health.last_error = error.error_type
        health.error_message = error.message
        health.last_checked = now
        health.consecutive_failures += 1
        health.total_failures += 1

        # Determine new status based on error type
        if error.error_type == ProviderErrorType.RATE_LIMIT:
            health.status = ProviderStatus.RATE_LIMITED
            if error.retry_after_seconds:
                health.retry_after = now + timedelta(seconds=error.retry_after_seconds)
            else:
                health.retry_after = now + timedelta(seconds=60)
            logger.warning(f"{provider} rate limited, retry after {health.retry_after}")

        elif error.error_type == ProviderErrorType.QUOTA_EXHAUSTED:
            health.status = ProviderStatus.EXHAUSTED
            health.estimated_credits_remaining = False
            logger.error(f"{provider} quota exhausted: {error.message}")

        elif error.error_type == ProviderErrorType.AUTHENTICATION:
            health.status = ProviderStatus.UNHEALTHY
            logger.error(f"{provider} authentication failed: {error.message}")

        elif health.consecutive_failures >= 3:
            health.status = ProviderStatus.DEGRADED
            logger.warning(f"{provider} marked degraded after {health.consecutive_failures} consecutive failures")

        return health

    def _update_health_on_success(self, provider: str) -> ProviderHealth:
        """Update provider health status after successful call."""
        now = datetime.now(timezone.utc)

        if provider not in self._health:
            self._health[provider] = ProviderHealth(provider=provider, status=ProviderStatus.HEALTHY)

        health = self._health[provider]

        # Reset failure counters
        was_healthy = health.status == ProviderStatus.HEALTHY
        health.consecutive_failures = 0
        health.total_successes += 1
        health.last_checked = now

        # If we were rate limited, check if we can mark healthy again
        if health.status == ProviderStatus.RATE_LIMITED and health.retry_after:
            if now >= health.retry_after:
                health.status = ProviderStatus.HEALTHY
                health.retry_after = None
                health.last_error = None
                logger.info(f"{provider} recovered from rate limit")

        # Mark healthy if we had failures but now working
        if health.status in {ProviderStatus.DEGRADED, ProviderStatus.UNHEALTHY}:
            health.status = ProviderStatus.HEALTHY
            health.last_error = None
            logger.info(f"{provider} recovered and marked healthy")

        return health

    async def check_ollama(self, url: str = "http://localhost:11434") -> ProviderHealth:
        """Check Ollama health via HTTP."""
        import aiohttp

        provider = "ollama"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{url}/api/version", timeout=aiohttp.ClientTimeout(total=2)) as response:
                    if response.status == 200:
                        return self._update_health_on_success(provider)
                    else:
                        error = ProviderError(
                            error_type=ProviderErrorType.NETWORK_ERROR,
                            message=f"Ollama returned {response.status}",
                            status_code=response.status,
                            provider=provider,
                        )
                        return self._update_health_on_error(provider, error)
        except asyncio.TimeoutError:
            error = ProviderError(
                error_type=ProviderErrorType.TIMEOUT,
                message="Ollama connection timeout",
                provider=provider,
            )
            return self._update_health_on_error(provider, error)
        except Exception as e:
            error = ProviderError(
                error_type=ProviderErrorType.NETWORK_ERROR,
                message=str(e),
                provider=provider,
            )
            return self._update_health_on_error(provider, error)

    async def check_provider(self, provider: str) -> ProviderHealth:
        """Check a cloud provider's health with a minimal test call."""
        if provider == "ollama":
            settings = self._get_settings()
            return await self.check_ollama(settings.ollama_url)

        client = self._get_client(provider)
        if not client:
            # No API key configured
            return ProviderHealth(
                provider=provider,
                status=ProviderStatus.UNHEALTHY,
                last_error=ProviderErrorType.AUTHENTICATION,
                error_message="No API key configured",
            )

        settings = self._get_settings()

        # Get the appropriate model for this provider
        if provider == "fireworks":
            model = settings.fireworks_model
        elif provider == "openai":
            model = settings.openai_model
        else:
            model = settings.groq_model

        try:
            # Make minimal test call (1 token)
            if hasattr(client, "chat") and hasattr(client.chat, "completions"):
                response = await client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "hi"}],
                    max_tokens=1,
                    temperature=0,
                )
                # Success!
                return self._update_health_on_success(provider)
            else:
                # Unknown client type, skip detailed check
                return ProviderHealth(
                    provider=provider,
                    status=ProviderStatus.HEALTHY,
                    last_checked=datetime.now(timezone.utc),
                )

        except Exception as e:
            error = self._classify_error(e, provider)
            return self._update_health_on_error(provider, error)

    async def check_all_providers(self) -> dict[str, ProviderHealth]:
        """Check health of all configured providers."""
        settings = self._get_settings()
        providers_to_check = []

        # Always check Ollama if in auto mode or explicitly set
        if settings.llm_provider in ("auto", "ollama"):
            providers_to_check.append("ollama")

        # Check configured cloud providers
        if settings.fireworks_api_key and settings.llm_provider in ("auto", "fireworks"):
            providers_to_check.append("fireworks")
        if settings.openai_api_key and settings.llm_provider in ("auto", "openai"):
            providers_to_check.append("openai")
        if settings.groq_api_key and settings.llm_provider in ("auto", "groq"):
            providers_to_check.append("groq")

        # Run checks in parallel
        results = await asyncio.gather(
            *[self.check_provider(p) for p in providers_to_check],
            return_exceptions=True,
        )

        for provider, result in zip(providers_to_check, results):
            if isinstance(result, Exception):
                # Check failed with exception
                error = ProviderError(
                    error_type=ProviderErrorType.UNKNOWN,
                    message=str(result),
                    provider=provider,
                )
                self._update_health_on_error(provider, error)
            else:
                self._health[provider] = result

        return self._health

    def get_health(self, provider: str) -> ProviderHealth | None:
        """Get current health status for a provider."""
        return self._health.get(provider)

    def get_available_providers(self) -> list[str]:
        """Get list of currently available providers."""
        available = []
        for provider in self.PROVIDER_PRIORITY:
            health = self._health.get(provider)
            if health and health.is_available:
                available.append(provider)
        return available

    def get_best_provider(self, exclude: list[str] | None = None) -> str | None:
        """Get the best available provider based on priority."""
        exclude = exclude or []
        for provider in self.PROVIDER_PRIORITY:
            if provider in exclude:
                continue
            health = self._health.get(provider)
            if health and health.is_available:
                return provider
        return None

    async def try_alternative(self, failed_provider: str, exclude: list[str] | None = None) -> str | None:
        """Get an alternative provider when one fails."""
        exclude = exclude or []
        exclude.append(failed_provider)

        # Mark the failed provider
        await self.check_provider(failed_provider)

        # Find alternative
        alternative = self.get_best_provider(exclude=exclude)
        if alternative:
            logger.info(f"Switching from {failed_provider} to {alternative}")
        else:
            logger.warning(f"No alternative provider available (tried: {exclude})")

        return alternative

    def report_error(self, provider: str, error: Exception) -> ProviderHealth:
        """Report an error that occurred during API usage."""
        structured_error = self._classify_error(error, provider)
        return self._update_health_on_error(provider, structured_error)

    def report_success(self, provider: str) -> ProviderHealth:
        """Report a successful API call."""
        return self._update_health_on_success(provider)

    def get_all_health(self) -> dict[str, ProviderHealth]:
        """Get health status for all known providers."""
        return self._health.copy()

    def should_retry(self, provider: str) -> bool:
        """Check if a failed request to this provider should be retried."""
        health = self._health.get(provider)
        if not health:
            return True  # Unknown provider, allow retry
        return health.should_retry

    def get_retry_delay(self, provider: str) -> float:
        """Get recommended retry delay for a provider."""
        health = self._health.get(provider)
        if not health:
            return 1.0

        if health.status == ProviderStatus.RATE_LIMITED and health.retry_after:
            now = datetime.now(timezone.utc)
            if health.retry_after > now:
                return (health.retry_after - now).total_seconds()

        # Exponential backoff based on consecutive failures
        base_delay = 1.0
        return min(base_delay * (2**health.consecutive_failures), 60.0)


# Global health checker instance
_health_checker: ProviderHealthChecker | None = None


def get_health_checker() -> ProviderHealthChecker:
    """Get the global health checker instance."""
    global _health_checker
    if _health_checker is None:
        _health_checker = ProviderHealthChecker()
    return _health_checker


def reset_health_checker() -> None:
    """Reset the global health checker (useful for testing)."""
    global _health_checker
    _health_checker = None
