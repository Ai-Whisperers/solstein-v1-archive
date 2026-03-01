"""Shared pytest fixtures for all tests.

This module provides centralized fixtures that can be used across
the entire test suite. Import these in your conftest.py or test files.

Usage:
    from tests.fixtures import db_session, company_factory
    
    def test_company(db_session, company_factory):
        company = company_factory()
        db_session.add(company)
        db_session.commit()
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from typing import Generator


@pytest.fixture
def mock_db_manager():
    """Provide a mock DatabaseManager.
    
    Returns:
        MagicMock configured as DatabaseManager spec
    
    Example:
        def test_with_db(mock_db_manager):
            mock_db_manager.get_session.return_value = mock_session
            result = service.get_company(db=mock_db_manager)
            assert result is not None
    """
    from solstein.infrastructure.database import DatabaseManager
    
    mock = MagicMock(spec=DatabaseManager)
    mock.get_session = MagicMock()
    mock.get_session.return_value.__aenter__ = AsyncMock(return_value=MagicMock())
    mock.get_session.return_value.__aexit__ = AsyncMock(return_value=False)
    return mock


@pytest.fixture
def mock_celery_task():
    """Provide a mock Celery task.
    
    Returns:
        MagicMock configured as Celery task
    
    Example:
        def test_task(mock_celery_task):
            mock_celery_task.request.retries = 0
            result = my_task(mock_celery_task)
            assert result.successful()
    """
    task = MagicMock()
    task.request = MagicMock()
    task.request.retries = 0
    task.request.max_retries = 3
    task.apply = MagicMock(return_value=MagicMock(successful=True))
    task.apply_async = MagicMock(return_value=MagicMock(id="task-123"))
    return task


@pytest.fixture
def company_factory():
    """Provide CompanyFactory for creating test companies.
    
    Returns:
        CompanyFactory class
    
    Example:
        def test_company(company_factory):
            company = company_factory(name="Test Corp")
            assert company.name == "Test Corp"
    """
    from tests.factories import CompanyFactory
    return CompanyFactory


@pytest.fixture
def mock_connector():
    """Provide a mock DataConnector.
    
    Returns:
        MagicMock configured as DataConnector
    
    Example:
        async def test_connector(mock_connector):
            mock_connector.fetch_facts = AsyncMock(return_value=[])
            result = await service.fetch(mock_connector)
            assert result == []
    """
    from solstein.core.ports import DataConnector
    
    mock = MagicMock(spec=DataConnector)
    mock.fetch_facts = AsyncMock(return_value=[])
    return mock


__all__ = [
    'mock_db_manager',
    'mock_celery_task',
    'company_factory',
    'mock_connector',
]
