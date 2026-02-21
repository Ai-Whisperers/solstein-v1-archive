"""Database configuration and session management.

Provides SQLAlchemy engine, session factory, and async context management
for PostgreSQL persistence of scoring results and market analysis data.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.pool import NullPool, QueuePool

from ..config import Settings

Base = declarative_base()


class DatabaseManager:
    """Manages database engine and session lifecycle."""

    def __init__(self, settings: Settings):
        """Initialize database manager.

        Args:
            settings: Application settings with database configuration
        """
        self.settings = settings
        self.engine = None
        self.session_factory = None
        self._sync_engine = None
        self._sync_session_factory = None

    def init_async(self):
        """Initialize async engine and session factory."""
        url = self.settings.database.url
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

        self.engine = create_async_engine(
            url,
            pool_size=self.settings.database.pool_size,
            max_overflow=10,
            echo=self.settings.database.echo,
            poolclass=QueuePool,
        )

        self.session_factory = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    def init_sync(self):
        """Initialize sync engine and session factory for Alembic migrations."""
        self._sync_engine = create_engine(
            self.settings.database.url,
            pool_size=self.settings.database.pool_size,
            max_overflow=10,
            echo=self.settings.database.echo,
            poolclass=QueuePool,
        )

        self._sync_session_factory = lambda: Session(self._sync_engine)

    async def get_session(self) -> AsyncSession:
        """Get an async database session.

        Yields:
            AsyncSession: Database session for queries

        Raises:
            RuntimeError: If async engine not initialized
        """
        if not self.engine:
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
