"""LLM services health check strategy.

Checks LLM service availability with detailed health status.
"""

from datetime import datetime, timezone

from loguru import logger

from .base import HealthCheck, HealthCheckStrategy, HealthStatus


class LLMHealthCheck(HealthCheckStrategy):
    """Check LLM service availability with detailed health status."""

    @property
    def name(self) -> str:
        return "llm_services"

    async def check(self) -> HealthCheck:
        """Check LLM service availability with detailed health status.

        Uses the enhanced health checker to provide detailed information about
        provider status, credits, and rate limits.

        Returns:
            HealthCheck result
        """
        start = datetime.now(timezone.utc)
        try:
            from ...llm.health_checker import ProviderStatus, get_health_checker

            health_checker = get_health_checker()
            health = await health_checker.check_all_providers()

            available_providers = health_checker.get_available_providers()

            if available_providers:
                # Collect detailed status for each provider
                provider_details = {}
                for name, h in health.items():
                    provider_details[name] = {
                        "status": h.status.value,
                        "is_available": h.is_available,
                        "last_error": h.last_error.value if h.last_error else None,
                        "consecutive_failures": h.consecutive_failures,
                        "total_successes": h.total_successes,
                    }

                return HealthCheck(
                    name="llm_services",
                    status=HealthStatus.HEALTHY,
                    message=f"LLM services available: {', '.join(available_providers)}",
                    duration_ms=(datetime.now(timezone.utc) - start).total_seconds() * 1000,
                    details={
                        "available_providers": available_providers,
                        "all_providers": provider_details,
                        "best_provider": health_checker.get_best_provider(),
                    },
                )
            else:
                # Check if any providers are exhausted or rate limited
                exhausted = [name for name, h in health.items() if h.status == ProviderStatus.EXHAUSTED]
                rate_limited = [name for name, h in health.items() if h.status == ProviderStatus.RATE_LIMITED]

                if exhausted or rate_limited:
                    status = HealthStatus.DEGRADED
                    message_parts = []
                    if exhausted:
                        message_parts.append(f"quota exhausted: {', '.join(exhausted)}")
                    if rate_limited:
                        message_parts.append(f"rate limited: {', '.join(rate_limited)}")
                    message = "LLM " + "; ".join(message_parts)
                else:
                    status = HealthStatus.DEGRADED
                    message = "No LLM backends configured or available"

                return HealthCheck(
                    name="llm_services",
                    status=status,
                    message=message,
                    duration_ms=(datetime.now(timezone.utc) - start).total_seconds() * 1000,
                    details={
                        "fallback": "keyword_and_template_based",
                        "exhausted_providers": exhausted,
                        "rate_limited_providers": rate_limited,
                        "all_statuses": {name: h.status.value for name, h in health.items()},
                    },
                )
        except Exception as e:
            logger.error(f"LLM health check failed: {str(e)}")
            return HealthCheck(
                name="llm_services",
                status=HealthStatus.DEGRADED,
                message=f"LLM health check failed: {str(e)}",
                duration_ms=(datetime.now(timezone.utc) - start).total_seconds() * 1000,
                details={"error": str(e), "fallback": "active"},
            )
