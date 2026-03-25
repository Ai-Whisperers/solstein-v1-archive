"""Redis health check strategy.

Checks Redis connectivity with real probe.
"""

from datetime import datetime, timezone

from loguru import logger

from .base import HealthCheck, HealthCheckStrategy, HealthStatus


class RedisHealthCheck(HealthCheckStrategy):
    """Check Redis connectivity with real probe."""

    @property
    def name(self) -> str:
        return "redis"

    async def check(self) -> HealthCheck:
        """Check Redis connectivity with real probe.

        Returns:
            HealthCheck result
        """
        start = datetime.now(timezone.utc)
        try:
            import redis.asyncio as redis

            from ...config import Settings

            settings = Settings.load()

            # Settings may expose redis_url directly or via celery_broker_url
            redis_url = getattr(settings, "redis_url", None) or settings.celery_broker_url
            if not redis_url:
                return HealthCheck(
                    name="redis",
                    status=HealthStatus.HEALTHY,
                    message="Redis not configured (optional)",
                    duration_ms=(datetime.now(timezone.utc) - start).total_seconds() * 1000,
                    details={"configured": False},
                )

            r = redis.from_url(redis_url)
            await r.ping()
            await r.close()

            return HealthCheck(
                name="redis",
                status=HealthStatus.HEALTHY,
                message="Redis connection successful",
                duration_ms=(datetime.now(timezone.utc) - start).total_seconds() * 1000,
                details={"configured": True, "url": redis_url},
            )
        except Exception as e:
            # Redis is optional, so degraded status
            check = HealthCheck(
                name="redis",
                status=HealthStatus.DEGRADED,
                message=f"Redis connection failed (optional service): {str(e)}",
                duration_ms=(datetime.now(timezone.utc) - start).total_seconds() * 1000,
                details={"error": str(e), "optional": True},
            )
            logger.warning("Redis health check failed (optional service)", error=str(e))
            return check
