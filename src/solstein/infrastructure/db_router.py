"""Read replica configuration and query routing.

EPIC-025 Story 8: Implements read replica support for load distribution.
Routes read queries to replicas and write queries to primary.

Note: This is a foundation implementation. Actual replica setup requires:
- PostgreSQL streaming replication configured
- Separate database URLs for primary and replicas
- Load balancer or connection routing
"""

import random
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine


class DatabaseRouter:
    """Route queries between primary and read replicas.

    Automatically routes read operations to replicas and write
    operations to the primary database for load distribution.

    Usage:
        router = DatabaseRouter(primary_url, [replica1_url, replica2_url])

        # Read query - goes to replica
        async with router.get_read_session() as session:
            result = await session.execute(select(CompanyRecord))

        # Write query - goes to primary
        async with router.get_write_session() as session:
            session.add(new_company)
    """

    def __init__(
        self,
        primary_url: str,
        replica_urls: list[str],
        pool_size: int = 20,
        max_overflow: int = 30,
    ):
        """Initialize database router.

        Args:
            primary_url: Primary database URL (writes).
            replica_urls: List of replica database URLs (reads).
            pool_size: Connection pool size per engine.
            max_overflow: Max overflow connections per engine.
        """
        self.primary_url = primary_url
        self.replica_urls = replica_urls
        self.pool_size = pool_size
        self.max_overflow = max_overflow

        self._primary_engine: AsyncEngine | None = None
        self._replica_engines: list[AsyncEngine] = []
        self._replica_index = 0

    def initialize(self):
        """Initialize all database engines."""
        # Convert URL to asyncpg format
        primary = self._to_asyncpg_url(self.primary_url)

        self._primary_engine = create_async_engine(
            primary,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            pool_pre_ping=True,
            pool_recycle=1800,
        )

        for url in self.replica_urls:
            replica_url = self._to_asyncpg_url(url)
            engine = create_async_engine(
                replica_url,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_pre_ping=True,
                pool_recycle=1800,
            )
            self._replica_engines.append(engine)

    def _to_asyncpg_url(self, url: str) -> str:
        """Convert PostgreSQL URL to asyncpg format.

        Args:
            url: Database URL.

        Returns:
            URL with asyncpg driver.
        """
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    def _get_replica_engine(self) -> AsyncEngine:
        """Get next replica engine using round-robin.

        Returns:
            AsyncEngine for a read replica.
        """
        if not self._replica_engines:
            # Fallback to primary if no replicas
            return self._primary_engine

        # Round-robin selection
        engine = self._replica_engines[self._replica_index]
        self._replica_index = (self._replica_index + 1) % len(self._replica_engines)
        return engine

    def _get_random_replica(self) -> AsyncEngine:
        """Get random replica engine.

        Returns:
            Randomly selected replica engine.
        """
        if not self._replica_engines:
            return self._primary_engine
        return random.choice(self._replica_engines)

    @asynccontextmanager
    async def get_read_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get session for read operations (uses replica).

        Yields:
            AsyncSession connected to a read replica.
        """
        engine = self._get_replica_engine()
        if engine is None:
            raise RuntimeError("DatabaseRouter not initialized — call initialize() first")
        session = AsyncSession(engine, expire_on_commit=False)
        try:
            yield session
        finally:
            await session.close()

    @asynccontextmanager
    async def get_write_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get session for write operations (uses primary).

        Yields:
            AsyncSession connected to primary database.
        """
        if self._primary_engine is None:
            raise RuntimeError("DatabaseRouter not initialized — call initialize() first")
        session = AsyncSession(self._primary_engine, expire_on_commit=False)
        try:
            yield session
        finally:
            await session.close()

    @asynccontextmanager
    async def get_session(self, read_only: bool = False) -> AsyncGenerator[AsyncSession, None]:
        """Get session with automatic routing.

        Args:
            read_only: If True, use replica. If False, use primary.

        Yields:
            AsyncSession for database operations.
        """
        if read_only:
            async with self.get_read_session() as session:
                yield session
        else:
            async with self.get_write_session() as session:
                yield session

    async def close(self):
        """Close all database engines."""
        if self._primary_engine:
            await self._primary_engine.dispose()

        for engine in self._replica_engines:
            await engine.dispose()

        self._replica_engines = []
        self._primary_engine = None

    def get_pool_status(self) -> dict:
        """Get connection pool status for all engines.

        Returns:
            Dictionary with pool status for primary and replicas.
        """
        status = {
            "primary": self._get_engine_pool_status(self._primary_engine),
            "replicas": [],
        }

        for i, engine in enumerate(self._replica_engines):
            status["replicas"].append(
                {
                    "index": i,
                    **self._get_engine_pool_status(engine),
                }
            )

        return status

    def _get_engine_pool_status(self, engine: AsyncEngine | None) -> dict:
        """Get pool status for a single engine.

        Args:
            engine: AsyncEngine to check.

        Returns:
            Pool status dictionary.
        """
        if not engine or not hasattr(engine, "pool"):
            return {"status": "not_initialized"}

        pool = engine.pool
        return {
            "status": "active",
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": getattr(pool, "overflow", lambda: 0)(),
        }


class ReadReplicaManager:
    """Manage read replica configuration and health.

    Handles replica discovery, health checking, and failover.
    """

    def __init__(self, replica_urls: list[str]):
        """Initialize replica manager.

        Args:
            replica_urls: List of replica database URLs.
        """
        self.replica_urls = replica_urls
        self.healthy_replicas: set[str] = set()
        self.unhealthy_replicas: set[str] = set()

    async def health_check(self) -> dict[str, bool]:
        """Check health of all replicas.

        Returns:
            Dictionary mapping replica URL to health status.
        """
        results = {}

        for url in self.replica_urls:
            try:
                engine = create_async_engine(
                    self._to_asyncpg_url(url),
                    pool_size=1,
                    max_overflow=0,
                )

                from sqlalchemy import text

                async with AsyncSession(engine) as session:
                    await session.execute(text("SELECT 1"))

                results[url] = True
                self.healthy_replicas.add(url)
                self.unhealthy_replicas.discard(url)

                await engine.dispose()

            except Exception:
                results[url] = False
                self.healthy_replicas.discard(url)
                self.unhealthy_replicas.add(url)

        return results

    def _to_asyncpg_url(self, url: str) -> str:
        """Convert URL to asyncpg format."""
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    def get_healthy_replicas(self) -> list[str]:
        """Get list of currently healthy replicas.

        Returns:
            List of healthy replica URLs.
        """
        return list(self.healthy_replicas)


# Convenience functions for common patterns
def create_router_from_config(config: dict) -> DatabaseRouter:
    """Create database router from configuration dictionary.

    Args:
        config: Configuration with keys:
            - primary_url: Primary database URL
            - replica_urls: List of replica URLs
            - pool_size: (optional) Pool size
            - max_overflow: (optional) Max overflow

    Returns:
        Configured DatabaseRouter.
    """
    router = DatabaseRouter(
        primary_url=config["primary_url"],
        replica_urls=config.get("replica_urls", []),
        pool_size=config.get("pool_size", 20),
        max_overflow=config.get("max_overflow", 30),
    )
    router.initialize()
    return router
