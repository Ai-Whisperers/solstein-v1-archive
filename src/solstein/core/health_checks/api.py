"""API responsiveness health check strategy.

Checks API responsiveness (always healthy if process running).
"""

from datetime import datetime, timezone

from .base import HealthCheck, HealthCheckStrategy, HealthStatus


class ApiHealthCheck(HealthCheckStrategy):
    """Check API responsiveness (always healthy if process running)."""

    @property
    def name(self) -> str:
        return "api"

    async def check(self) -> HealthCheck:
        """Check API responsiveness.

        Returns:
            HealthCheck result
        """
        start = datetime.now(timezone.utc)
        try:
            # API responsiveness is implicit - if this code runs, API is responsive
            return HealthCheck(
                name="api",
                status=HealthStatus.HEALTHY,
                message="API is responsive",
                duration_ms=(datetime.now(timezone.utc) - start).total_seconds() * 1000,
                details={"endpoints_available": 14},
            )
        except Exception as e:
            return HealthCheck(
                name="api",
                status=HealthStatus.UNHEALTHY,
                message=f"API health check failed: {str(e)}",
                duration_ms=(datetime.now(timezone.utc) - start).total_seconds() * 1000,
                details={"error": str(e)},
            )
