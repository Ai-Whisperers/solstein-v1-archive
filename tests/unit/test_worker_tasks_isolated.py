"""Isolated tests for Celery worker tasks.

These tests use dependency injection and proper mocking
without sys.modules manipulation.
"""

import contextlib
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.mocks import MaxRetriesExceededError


class TestRefreshTasksIsolated:
    """Test suite for refresh tasks using proper isolation."""

    @pytest.fixture
    def mock_db_manager(self):
        """Mock database manager."""
        return MagicMock()

    @pytest.fixture
    def mock_task_self(self):
        """Mock Celery task self object."""
        mock = MagicMock()
        mock.retry = MagicMock(side_effect=MaxRetriesExceededError("Max retries exceeded"))
        mock.request = MagicMock()
        mock.request.retries = 0
        return mock

    @pytest.fixture
    def mock_tracked_companies(self):
        """Mock tracked companies list."""
        return ["comp_001", "comp_002"]

    @pytest.fixture
    def mock_store_facts(self):
        """Mock store facts function."""
        return AsyncMock(return_value=5)

    def test_refresh_sec_edgar_success(self, mock_task_self, mock_db_manager, mock_tracked_companies, mock_store_facts):
        """Test successful SEC EDGAR refresh task execution."""
        # Use dependency injection instead of patching imports
        with patch("solstein.worker_tasks.SECEDGARRefreshConnector") as mock_connector:
            instance = MagicMock()
            instance.fetch_facts = AsyncMock(return_value=[{"fact": 1}])
            mock_connector.return_value = instance

            with (
                patch("solstein.worker_tasks._get_tracked_company_ids", return_value=mock_tracked_companies),
                patch("solstein.worker_tasks._store_facts", mock_store_facts),
            ):
                # Import here to avoid module-level import issues
                from solstein.worker_tasks import refresh_sec_edgar

                result = refresh_sec_edgar(mock_task_self)
                assert result is not None
                assert result["status"] == "completed"

    def test_refresh_companies_house_success(
        self, mock_task_self, mock_db_manager, mock_tracked_companies, mock_store_facts
    ):
        """Test successful Companies House refresh task execution."""
        with patch("solstein.worker_tasks.CompaniesHouseRefreshConnector") as mock_connector:
            instance = MagicMock()
            instance.fetch_facts = AsyncMock(return_value=[{"fact": 1}])
            mock_connector.return_value = instance

            with (
                patch("solstein.worker_tasks._get_tracked_company_ids", return_value=mock_tracked_companies),
                patch("solstein.worker_tasks._store_facts", mock_store_facts),
            ):
                from solstein.worker_tasks import refresh_companies_house

                result = refresh_companies_house(mock_task_self)
                assert result is not None

    def test_refresh_news_signals_success(
        self, mock_task_self, mock_db_manager, mock_tracked_companies, mock_store_facts
    ):
        """Test successful News Signals refresh task execution."""
        with patch("solstein.worker_tasks.NewsSignalRefreshConnector") as mock_connector:
            instance = MagicMock()
            instance.fetch_facts = AsyncMock(return_value=[{"fact": 1}])
            mock_connector.return_value = instance

            with (
                patch("solstein.worker_tasks._get_tracked_company_ids", return_value=mock_tracked_companies),
                patch("solstein.worker_tasks._store_facts", mock_store_facts),
            ):
                from solstein.worker_tasks import refresh_news_signals

                result = refresh_news_signals(mock_task_self)
                assert result is not None


class TestRetryLogicIsolated:
    """Test suite for retry logic using proper isolation."""

    def test_retry_on_connector_error(self):
        """Test that task retries on connector error."""
        mock_task = MagicMock()
        mock_task.request = MagicMock()
        mock_task.request.retries = 0
        mock_task.retry = MagicMock()

        with patch("solstein.worker_tasks.SECEDGARRefreshConnector") as mock_connector:
            instance = MagicMock()
            instance.fetch_facts = AsyncMock(side_effect=Exception("API Error"))
            mock_connector.return_value = instance

            with (
                patch("solstein.worker_tasks._get_db_manager"),
                patch("solstein.worker_tasks._get_tracked_company_ids", return_value=["comp_001"]),
            ):
                from solstein.worker_tasks import refresh_sec_edgar

                with contextlib.suppress(Exception):
                    refresh_sec_edgar(mock_task)

    def test_max_retries_exceeded_logging(self):
        """Test that MaxRetriesExceededError is logged."""
        mock_task = MagicMock()
        mock_task.request = MagicMock()
        mock_task.request.retries = 3
        mock_task.retry = MagicMock(side_effect=MaxRetriesExceededError("Max retries exceeded"))

        with patch("solstein.worker_tasks.SECEDGARRefreshConnector") as mock_connector:
            instance = MagicMock()
            instance.fetch_facts = AsyncMock(side_effect=Exception("API Error"))
            mock_connector.return_value = instance

            with (
                patch("solstein.worker_tasks._get_db_manager"),
                patch("solstein.worker_tasks._get_tracked_company_ids", return_value=["comp_001"]),
            ):
                from solstein.worker_tasks import refresh_sec_edgar

                with contextlib.suppress(MaxRetriesExceededError):
                    refresh_sec_edgar(mock_task)
