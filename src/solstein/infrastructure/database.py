"""Database configuration and session management.

Provides SQLAlchemy engine, session factory, and async context management
for PostgreSQL persistence of scoring results and market analysis data.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable

    from sqlalchemy.engine import Engine

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeMeta, Session, declarative_base
from sqlalchemy.pool import QueuePool

from ..config import Settings

Base: DeclarativeMeta = declarative_base()


class DatabaseManager:
    """Manages database engine and session lifecycle."""

    settings: Settings

    def __init__(self, settings: Settings):
        """Initialize database manager.

        Args:
            settings: Application settings with database configuration
        """
        self.settings = settings
        self.engine: AsyncEngine | None = None
        self.session_factory: async_sessionmaker[AsyncSession] | None = None
        self._sync_engine: Engine | None = None
        self._sync_session_factory: Callable[[], Session] | None = None

    def init_async(self):
        """Initialize async engine and session factory."""
        url = self.settings.get_database_url()
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("sqlite://") and "+aiosqlite" not in url:
            url = url.replace("sqlite://", "sqlite+aiosqlite://", 1)

        self.engine = create_async_engine(
            url,
            pool_size=self.settings.database.pool_size,
            max_overflow=10,
            echo=self.settings.database.echo,
        )

        self.session_factory = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    def init_sync(self):
        """Initialize sync engine and session factory for Alembic migrations."""
        self._sync_engine = create_engine(
            self.settings.get_database_url(),
            pool_size=self.settings.database.pool_size,
            max_overflow=10,
            echo=self.settings.database.echo,
            poolclass=QueuePool,
        )

        def _factory() -> Session:
            if self._sync_engine is None:
                raise RuntimeError("Sync database engine not initialized")
            return Session(self._sync_engine)

        self._sync_session_factory = _factory

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session.

        Yields:
            AsyncSession: Database session for queries

        Raises:
            RuntimeError: If async engine not initialized
        """
        if self.engine is None or self.session_factory is None:
            raise RuntimeError("Database not initialized. Call init_async() first.")

        async with self.session_factory() as session:
            yield session

    def get_sync_session(self) -> Session:
        """Get a sync database session.

        Returns:
            Session: Synchronous database session

        Raises:
            RuntimeError: If sync engine not initialized
        """
        if not self._sync_session_factory:
            raise RuntimeError("Sync database not initialized. Call init_sync() first.")

        return self._sync_session_factory()

    async def create_tables(self):
        """Create all tables from Base metadata."""
        if not self.engine:
            raise RuntimeError("Database not initialized. Call init_async() first.")

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self):
        """Drop all tables from Base metadata."""
        if not self.engine:
            raise RuntimeError("Database not initialized. Call init_async() first.")

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def close(self):
        """Close database connection pool."""
        if self.engine:
            await self.engine.dispose()

    def close_sync(self):
        """Close synchronous database connection pool."""
        if self._sync_engine:
            self._sync_engine.dispose()


db_manager = DatabaseManager(Settings.load())


async def get_async_session():
    """FastAPI dependency that yields an async SQLAlchemy session.

    Usage::

        from fastapi import Depends
        from solstein.infrastructure.database import get_async_session
        from sqlalchemy.ext.asyncio import AsyncSession

        @router.get("/")
        async def my_route(session: AsyncSession = Depends(get_async_session)):
            ...
    """
    from sqlalchemy.ext.asyncio import AsyncSession

    engine = db_manager.engine
    if engine is None:
        # Initialise lazily in dev when DB is not yet connected
        db_manager.init_async()
        engine = db_manager.engine
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


def get_async_engine():
    """Return the shared async engine (initialised lazily)."""
    return db_manager.engine
