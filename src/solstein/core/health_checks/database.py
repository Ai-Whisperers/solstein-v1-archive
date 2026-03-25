"""Database health check strategy.

Checks database connectivity with real probe.
"""

from datetime import datetime, timezone

from loguru import logger

from .base import HealthCheck, HealthCheckStrategy, HealthStatus


class DatabaseHealthCheck(HealthCheckStrategy):
    """Check database connectivity with real probe."""

    @property
    def name(self) -> str:
        return "database"

    async def check(self) -> HealthCheck:
        """Check database connectivity with real probe.

        Returns:
            HealthCheck result
        """
        start = datetime.now(timezone.utc)
        try:
            from sqlalchemy import text

            from ...config import Settings
            from ...infrastructure.database import DatabaseManager

            settings = Settings.load()
            db_manager = DatabaseManager(settings)
            # init_async is synchronous (creates async engine config only)
            db_manager.init_async()

            if db_manager.engine is None:
                raise RuntimeError("Database engine not initialized after init_async()")

            async with db_manager.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))

            return HealthCheck(
                name="database",
                status=HealthStatus.HEALTHY,
                message="Database connection successful",
                duration_ms=(datetime.now(timezone.utc) - start).total_seconds() * 1000,
                details={"connection": "postgresql", "pool_size": settings.database.pool_size},
            )
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return HealthCheck(
                name="database",
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection failed: {str(e)}",
                duration_ms=(datetime.now(timezone.utc) - start).total_seconds() * 1000,
                details={"error": str(e)},
            )
