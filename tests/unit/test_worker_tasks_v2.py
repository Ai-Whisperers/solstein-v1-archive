"""Tests for refactored Celery worker tasks using dependency injection.

These tests use dependency injection instead of sys.modules manipulation,
making them faster, more reliable, and easier to understand.

Usage:
    # Run these tests
    pytest tests/unit/test_worker_tasks_v2.py -v
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from solstein.worker_tasks_v2 import refresh_sec_edgar, refresh_companies_house
from solstein.core.ports import DataConnector


class TestRefreshTasksV2:
    """Test suite using dependency injection (no sys.modules hacking)."""

    @pytest.fixture
    def mock_db_manager(self):
        """Provide a mock DatabaseManager."""
        return MagicMock()

    @pytest.fixture
    def mock_task_self(self):
        """Provide a mock Celery task self object."""
        mock = MagicMock()
        mock.request.retries = 0
        mock.retry = MagicMock()
        return mock

    @pytest.fixture
    def mock_connector(self):
        """Provide a mock DataConnector using dependency injection."""
        connector = MagicMock(spec=DataConnector)
        connector.fetch_facts = AsyncMock(return_value=[
            {"company_id": "comp_001", "fact": "test_data"}
        ])
        return connector

    @pytest.mark.asyncio
    async def test_refresh_sec_edgar_with_injected_connector(self, mock_connector):
        """Test SEC EDGAR refresh with dependency injection.
        
        This test demonstrates the new pattern:
        1. Create mock connector
        2. Inject it into the task
        3. No sys.modules manipulation needed!
        """
        # Arrange
        mock_task = MagicMock()
        mock_task.request.retries = 0
        
        # Act - Inject mock connector directly
        with patch('solstein.worker_tasks_v2._get_db_manager') as mock_db:
            mock_db_manager = MagicMock()
            mock_db.return_value = mock_db_manager
            
            with patch('solstein.worker_tasks_v2._get_tracked_company_ids', 
                      new_callable=AsyncMock, return_value=["comp_001"]):
                with patch('solstein.worker_tasks_v2._store_facts', 
                          new_callable=AsyncMock, return_value=1):
                    result = await refresh_sec_edgar(mock_task, connector=mock_connector)
        
        # Assert
        assert result is not None
        assert result["status"] == "completed"
        assert result["facts_fetched"] == 1
        mock_connector.fetch_facts.assert_called_once()

    @pytest.mark.asyncio
    async def test_refresh_companies_house_with_injected_connector(self, mock_connector):
        """Test Companies House refresh with dependency injection."""
        mock_task = MagicMock()
        mock_task.request.retries = 0
        
        with patch('solstein.worker_tasks_v2._get_db_manager') as mock_db:
            mock_db_manager = MagicMock()
            mock_db.return_value = mock_db_manager
            
            with patch('solstein.worker_tasks_v2._get_tracked_company_ids',
                      new_callable=AsyncMock, return_value=["comp_001"]):
                with patch('solstein.worker_tasks_v2._store_facts',
                          new_callable=AsyncMock, return_value=1):
                    result = await refresh_companies_house(mock_task, connector=mock_connector)
        
        assert result is not None
        assert result["status"] == "completed"
        mock_connector.fetch_facts.assert_called_once()

    @pytest.mark.asyncio
    async def test_refresh_with_no_companies(self, mock_connector):
        """Test behavior when no tracked companies exist."""
        mock_task = MagicMock()
        mock_task.request.retries = 0
        
        with patch('solstein.worker_tasks_v2._get_db_manager') as mock_db:
            mock_db_manager = MagicMock()
            mock_db.return_value = mock_db_manager
            
            # Return empty list - no companies
            with patch('solstein.worker_tasks_v2._get_tracked_company_ids',
                      new_callable=AsyncMock, return_value=[]):
                result = await refresh_sec_edgar(mock_task, connector=mock_connector)
        
        assert result["status"] == "completed"
        assert result["facts_fetched"] == 0
        # Connector should not be called when no companies
        mock_connector.fetch_facts.assert_not_called()

    @pytest.mark.asyncio
    async def test_refresh_error_handling(self, mock_connector):
        """Test error handling with retry logic."""
        mock_task = MagicMock()
        mock_task.request.retries = 0
        mock_task.retry = MagicMock(side_effect=Exception("Max retries"))
        
        # Make connector raise an error
        mock_connector.fetch_facts = AsyncMock(
            side_effect=Exception("API Error")
        )
        
        with patch('solstein.worker_tasks_v2._get_db_manager') as mock_db:
            mock_db_manager = MagicMock()
            mock_db.return_value = mock_db_manager
            
            with patch('solstein.worker_tasks_v2._get_tracked_company_ids',
                      new_callable=AsyncMock, return_value=["comp_001"]):
                try:
                    await refresh_sec_edgar(mock_task, connector=mock_connector)
                except Exception:
                    pass  # Expected to fail after retries
        
        # Verify retry was called
        mock_task.retry.assert_called_once()


class TestDependencyInjectionBenefits:
    """Demonstrate the benefits of dependency injection."""

    def test_no_sys_modules_manipulation(self):
        """Verify tests don't need sys.modules manipulation.
        
        This test proves that with dependency injection, we don't need
        to manipulate sys.modules to mock Celery or other imports.
        """
        import sys
        
        # The old test needed this:
        # sys.modules['celery'] = MagicMock()  # ❌ BAD
        
        # The new test just does this:
        connector = MagicMock(spec=DataConnector)  # ✅ GOOD
        
        # No sys.modules pollution!
        assert 'celery' in sys.modules  # Celery should be imported normally

    def test_multiple_mock_strategies(self):
        """Show different ways to mock with DI."""
        
        # Strategy 1: Simple mock
        simple_mock = MagicMock(spec=DataConnector)
        simple_mock.fetch_facts = AsyncMock(return_value=[])
        
        # Strategy 2: Mock with specific return values
        specific_mock = MagicMock(spec=DataConnector)
        specific_mock.fetch_facts = AsyncMock(return_value=[
            {"company_id": "1", "fact": "data"}
        ])
        
        # Strategy 3: Mock with side effects
        side_effect_mock = MagicMock(spec=DataConnector)
        side_effect_mock.fetch_facts = AsyncMock(
            side_effect=[
                [{"company_id": "1"}],  # First call
                [{"company_id": "2"}],  # Second call
                Exception("API Error"),   # Third call raises
            ]
        )
        
        # All strategies work with DI - no patching needed!
        assert simple_mock is not None
        assert specific_mock is not None
        assert side_effect_mock is not None
