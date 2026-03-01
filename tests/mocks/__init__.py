"""Mock utilities for testing.

This module provides centralized mocking utilities to avoid
duplicating mock setup across test files.
"""

from unittest.mock import MagicMock, AsyncMock
import pytest


class CeleryMockFactory:
    """Factory for creating Celery-related mocks without sys.modules manipulation."""
    
    @staticmethod
    def create_celery_app():
        """Create a mock Celery application."""
        app = MagicMock()
        app.Task = MagicMock()
        return app
    
    @staticmethod
    def create_task_mock():
        """Create a mock Celery task."""
        task = MagicMock()
        task.apply = MagicMock(return_value=MagicMock(successful=True))
        task.apply_async = MagicMock(return_value=MagicMock(id="task-123"))
        return task
    
    @staticmethod
    def shared_task_decorator(*args, **kwargs):
        """Mock @shared_task decorator that returns the function unchanged."""
        def decorator(func):
            return func
        return decorator


class MaxRetriesExceededError(Exception):
    """Mock exception for testing retry logic."""
    pass


class SoftTimeLimitExceeded(Exception):
    """Mock exception for testing time limits."""
    pass


@pytest.fixture
def celery_app():
    """Provide a mock Celery application.
    
    Usage:
        def test_task(celery_app):
            task = MyTask.bind(celery_app)
            result = task.apply()
            assert result.successful()
    """
    return CeleryMockFactory.create_celery_app()


@pytest.fixture
def mock_celery_task():
    """Provide a mock Celery task.
    
    Usage:
        def test_async_task(mock_celery_task):
            mock_celery_task.apply_async.return_value.id = "task-123"
            result = my_task.delay()
            assert result.id == "task-123"
    """
    return CeleryMockFactory.create_task_mock()


@pytest.fixture
def mock_retry_exception():
    """Provide MaxRetriesExceededError for testing retry logic.
    
    Usage:
        def test_retry_logic(mock_retry_exception):
            with pytest.raises(mock_retry_exception):
                task_that_fails()
    """
    return MaxRetriesExceededError
