"""Production hardening features and graceful degradation.

Provides:
- Graceful shutdown hooks
- Dependency injection for testability
- Feature flags for gradual rollout
- Fallback strategies for agent failures
- Request timeout management
- Response caching
"""

import asyncio
import logging
from collections.abc import Callable
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class FeatureFlag(str, Enum):
    """Feature flags for gradual rollout."""

    ENABLE_LINKEDIN_AGENT = "enable_linkedin_agent"
    ENABLE_SEC_EDGAR_AGENT = "enable_sec_edgar_agent"
    ENABLE_PATENTS_AGENT = "enable_patents_agent"
    ENABLE_NEWS_AGENT = "enable_news_agent"
    ENABLE_JOBS_AGENT = "enable_jobs_agent"
    ENABLE_TECH_TRENDS_AGENT = "enable_tech_trends_agent"
    ENABLE_WEBSITE_AGENT = "enable_website_agent"
    ENABLE_RESPONSE_CACHING = "enable_response_caching"
    ENABLE_GRACEFUL_DEGRADATION = "enable_graceful_degradation"


class FeatureFlagManager:
    """Manages feature flags for gradual rollout."""

    def __init__(self):
        """Initialize feature flag manager."""
        self.flags: dict[FeatureFlag, bool] = {
            FeatureFlag.ENABLE_LINKEDIN_AGENT: True,
            FeatureFlag.ENABLE_SEC_EDGAR_AGENT: True,
            FeatureFlag.ENABLE_PATENTS_AGENT: True,
            FeatureFlag.ENABLE_NEWS_AGENT: True,
            FeatureFlag.ENABLE_JOBS_AGENT: True,
            FeatureFlag.ENABLE_TECH_TRENDS_AGENT: True,
            FeatureFlag.ENABLE_WEBSITE_AGENT: True,
            FeatureFlag.ENABLE_RESPONSE_CACHING: True,
            FeatureFlag.ENABLE_GRACEFUL_DEGRADATION: True,
        }

    def is_enabled(self, flag: FeatureFlag) -> bool:
        """Check if feature flag is enabled.

        Args:
            flag: Feature flag to check

        Returns:
            True if enabled, False otherwise
        """
        return self.flags.get(flag, False)

    def enable(self, flag: FeatureFlag) -> None:
        """Enable a feature flag.

        Args:
            flag: Feature flag to enable
        """
        self.flags[flag] = True
        logger.info(f"Feature flag enabled: {flag.value}")

    def disable(self, flag: FeatureFlag) -> None:
        """Disable a feature flag.

        Args:
            flag: Feature flag to disable
        """
        self.flags[flag] = False
        logger.info(f"Feature flag disabled: {flag.value}")

    def get_all(self) -> dict[str, bool]:
        """Get all feature flags.

        Returns:
            Dictionary of all flags and their status
        """
        return {flag.value: enabled for flag, enabled in self.flags.items()}


class ResponseCache:
    """Simple in-memory response cache with TTL."""

    def __init__(self):
        """Initialize response cache."""
        self.cache: dict[str, tuple[Any, datetime]] = {}

    def get(self, key: str) -> Any | None:
        """Get cached response if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if expired/not found
        """
        if key not in self.cache:
            return None

        value, expiry = self.cache[key]
        if datetime.utcnow() > expiry:
            del self.cache[key]
            return None

        return value

    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        """Set cached response with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds
        """
        expiry = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        self.cache[key] = (value, expiry)

    def clear(self) -> None:
        """Clear entire cache."""
        self.cache.clear()

    def size(self) -> int:
        """Get current cache size.

        Returns:
            Number of cached items
        """
        return len(self.cache)


class GracefulDegradation:
    """Handles graceful degradation when agents fail."""

    def __init__(self):
        """Initialize graceful degradation handler."""
        self.agent_failures: dict[str, int] = {}
        self.failure_threshold = 5

    async def wrap_agent_call(
        self,
        agent_name: str,
        agent_func: Callable,
        fallback_func: Callable | None = None,
    ) -> Any:
        """Wrap agent call with graceful degradation.

        Args:
            agent_name: Name of agent
            agent_func: Async function to call
            fallback_func: Optional fallback function

        Returns:
            Agent result or fallback result
        """
        try:
            result = await agent_func()
            self.agent_failures[agent_name] = 0
            return result
        except Exception as e:
            self.agent_failures[agent_name] = self.agent_failures.get(agent_name, 0) + 1
            logger.warning(f"Agent {agent_name} failed: {str(e)} (failure #{self.agent_failures[agent_name]})")

            if fallback_func:
                try:
                    return await fallback_func()
                except Exception as fallback_error:
                    logger.error(f"Fallback for {agent_name} also failed: {fallback_error}")
                    return {"error": f"Agent {agent_name} failed"}
            else:
                return {"error": f"Agent {agent_name} failed"}

    def is_agent_degraded(self, agent_name: str) -> bool:
        """Check if agent is degraded.

        Args:
            agent_name: Name of agent

        Returns:
            True if agent has exceeded failure threshold
        """
        failures = self.agent_failures.get(agent_name, 0)
        return failures >= self.failure_threshold

    def get_status(self) -> dict[str, Any]:
        """Get degradation status.

        Returns:
            Status of all agents
        """
        return {
            name: {
                "failures": failures,
                "degraded": failures >= self.failure_threshold,
            }
            for name, failures in self.agent_failures.items()
        }


class RequestTimeoutManager:
    """Manages request timeouts for different operations."""

    def __init__(self):
        """Initialize timeout manager."""
        self.timeouts = {
            "agent_call": 30.0,
            "database_query": 10.0,
            "cache_lookup": 5.0,
            "api_response": 60.0,
        }

    def get_timeout(self, operation: str) -> float:
        """Get timeout for operation.

        Args:
            operation: Type of operation

        Returns:
            Timeout in seconds
        """
        return self.timeouts.get(operation, 30.0)

    def set_timeout(self, operation: str, timeout_seconds: float) -> None:
        """Set timeout for operation.

        Args:
            operation: Type of operation
            timeout_seconds: Timeout duration
        """
        self.timeouts[operation] = timeout_seconds

    async def run_with_timeout(
        self,
        operation: str,
        coro,
    ) -> Any:
        """Run coroutine with timeout.

        Args:
            operation: Type of operation
            coro: Coroutine to run

        Returns:
            Coroutine result

        Raises:
            asyncio.TimeoutError: If timeout exceeded
        """
        timeout = self.get_timeout(operation)
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except TimeoutError:
            logger.error(f"Operation {operation} timed out after {timeout}s")
            raise


class GracefulShutdown:
    """Handles graceful shutdown of application."""

    def __init__(self):
        """Initialize graceful shutdown handler."""
        self.shutdown_handlers: list[Callable] = []
        self.is_shutting_down = False

    def register_shutdown_handler(self, handler: Callable) -> None:
        """Register a shutdown handler.

        Args:
            handler: Async function to call on shutdown
        """
        self.shutdown_handlers.append(handler)

    async def shutdown(self) -> None:
        """Execute all shutdown handlers.

        Runs handlers sequentially, logging any errors.
        """
        if self.is_shutting_down:
            return

        self.is_shutting_down = True
        logger.info("Starting graceful shutdown...")

        for handler in self.shutdown_handlers:
            try:
                await handler()
            except Exception as e:
                logger.error(f"Error during shutdown: {str(e)}")

        logger.info("Graceful shutdown complete")


feature_flags = FeatureFlagManager()
response_cache = ResponseCache()
degradation = GracefulDegradation()
timeout_manager = RequestTimeoutManager()
shutdown = GracefulShutdown()
