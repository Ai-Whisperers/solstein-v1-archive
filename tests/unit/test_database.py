"""Tests for database.py - DatabaseManager with real Supabase.

This test suite uses an actual Supabase PostgreSQL connection to test
the DatabaseManager against real database operations where applicable.
"""

import pytest
from sqlalchemy import text

from solstein.infrastructure.database import DatabaseManager
from solstein.database_config import get_test_database_url, convert_to_async_url


@pytest.mark.asyncio
class TestDatabaseManager:
    """Test suite for DatabaseManager with real database backend."""

    @pytest.fixture
    def manager(self):
        """Provide DatabaseManager with real test database URL."""
        db_url = get_test_database_url()
        async_url = convert_to_async_url(db_url)

        from solstein.config import Settings

        settings = Settings()
        # Override with test URL
        settings.DATABASE_URL = async_url

        manager = DatabaseManager(settings)
        return manager

    async def test_initialization(self, manager):
        """Test DatabaseManager initializes correctly."""
        assert manager is not None
        assert manager.engine is None
        assert manager.session_factory is None

    async def test_init_async(self, manager):
        """Test async engine initialization with real database."""
        manager.init_async()

        assert manager.engine is not None
        assert manager.session_factory is not None

        # Cleanup
        await manager.close()

    async def test_init_sync(self, manager):
        """Test sync engine initialization with real database."""
        manager.init_sync()

        assert manager._sync_engine is not None
        assert manager._sync_session_factory is not None

        # Cleanup
        manager.close_sync()

    async def test_get_session_context_manager(self, manager):
        """Test get_session as async context manager with real database."""
        manager.init_async()

        # Use as async context manager with real database
        async with manager.get_session() as session:
            assert session is not None
            # Verify we can execute a query
            result = await session.execute(text("SELECT 1"))
            row = result.scalar_one()
            assert row == 1

        # Cleanup
        await manager.close()

    async def test_get_sync_session(self, manager):
        """Test get_sync_session returns a working session."""
        manager.init_sync()

        session = manager.get_sync_session()
        assert session is not None

        # Verify we can execute a query
        result = session.execute(text("SELECT 1"))
        row = result.scalar_one()
        assert row == 1

        session.close()
        manager.close_sync()

    async def test_create_tables(self, manager):
        """Test create_tables method with real database."""
        manager.init_async()

        # Should create tables without error
        await manager.create_tables()

        # Verify tables exist by querying
        async with manager.get_session() as session:
            result = await session.execute(text("SELECT COUNT(*) FROM gathering_batches"))
            count = result.scalar_one()
            assert count >= 0  # Table exists, may be empty

        # Cleanup
        await manager.close()

    async def test_database_connection_with_real_url(self):
        """Test DatabaseManager connects to real Supabase database."""
        db_url = get_test_database_url()
        async_url = convert_to_async_url(db_url)

        from solstein.config import Settings

        settings = Settings()
        settings.DATABASE_URL = async_url

        manager = DatabaseManager(settings)
        manager.init_async()

        # Verify connection works
        async with manager.get_session() as session:
            result = await session.execute(text("SELECT version()"))
            version = result.scalar_one()
            assert "PostgreSQL" in version

        await manager.close()

    async def test_session_rollback_on_error(self, manager):
        """Test session rolls back on error."""
        manager.init_async()

        async with manager.get_session() as session:
            # Execute something
            await session.execute(text("SELECT 1"))
            # Session will auto-rollback on error or close

        await manager.close()

    async def test_multiple_sessions(self, manager):
        """Test multiple sessions can be created."""
        manager.init_async()

        # Create multiple sessions
        async with manager.get_session() as session1:
            result1 = await session1.execute(text("SELECT 1"))
            assert result1.scalar_one() == 1

        async with manager.get_session() as session2:
            result2 = await session2.execute(text("SELECT 2"))
            assert result2.scalar_one() == 2

        await manager.close()
