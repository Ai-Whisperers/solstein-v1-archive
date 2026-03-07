"""Configuration health check strategy.

Checks that configuration is valid.
"""

from datetime import datetime, timezone

from .base import HealthCheck, HealthCheckStrategy, HealthStatus


class ConfigurationHealthCheck(HealthCheckStrategy):
    """Check that configuration is valid."""

    @property
    def name(self) -> str:
        return "configuration"

    async def check(self) -> HealthCheck:
        """Check that configuration is valid.

        Returns:
            HealthCheck result
        """
        start = datetime.now(timezone.utc)
        try:
            from ...config import Settings

            settings = Settings.load()

            return HealthCheck(
                name="configuration",
                status=HealthStatus.HEALTHY,
                message="Configuration is valid",
                duration_ms=(datetime.now(timezone.utc) - start).total_seconds() * 1000,
                details={
                    "environment": settings.environment,
                    "debug": settings.debug,
                },
            )
        except Exception as e:
            return HealthCheck(
                name="configuration",
                status=HealthStatus.UNHEALTHY,
                message=f"Configuration check failed: {str(e)}",
                duration_ms=(datetime.now(timezone.utc) - start).total_seconds() * 1000,
                details={"error": str(e)},
            )
