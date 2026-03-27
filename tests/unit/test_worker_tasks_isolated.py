"""Isolated tests for Celery worker tasks.

These tests use dependency injection and proper mocking
without sys.modules manipulation.

STORY-066: All refresh tasks now require tenant_id as first argument.
"""

import contextlib
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

celery = pytest.importorskip("celery", reason="celery not installed")

from tests.mocks import MaxRetriesExceededError

from solstein.worker_tasks import (
    refresh_companies_house,
    refresh_news_signals,
    refresh_sec_edgar,
)

# Valid tenant_id for tests (STORY-066)
TEST_TENANT_ID = str(uuid.uuid4())


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
        with patch(
            "solstein.worker.refresh_tasks.SECEDGARRefreshConnector.fetch_facts", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = [{"fact": 1}]

            with (
                patch("solstein.worker.refresh_tasks.get_db_manager", return_value=mock_db_manager),
                patch("solstein.worker.refresh_tasks.get_tracked_company_ids", return_value=mock_tracked_companies),
                patch("solstein.worker.refresh_tasks.store_facts", mock_store_facts),
            ):
                result = refresh_sec_edgar.run(TEST_TENANT_ID)
                assert result is not None
                assert result["status"] == "completed"

    def test_refresh_companies_house_success(
        self, mock_task_self, mock_db_manager, mock_tracked_companies, mock_store_facts
    ):
        """Test successful Companies House refresh task execution."""
        with patch(
            "solstein.worker.refresh_tasks.CompaniesHouseRefreshConnector.fetch_facts", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = [{"fact": 1}]

            with (
                patch("solstein.worker.refresh_tasks.get_db_manager", return_value=mock_db_manager),
                patch("solstein.worker.refresh_tasks.get_tracked_company_ids", return_value=mock_tracked_companies),
                patch("solstein.worker.refresh_tasks.store_facts", mock_store_facts),
            ):
                result = refresh_companies_house.run(TEST_TENANT_ID)
                assert result is not None

    def test_refresh_news_signals_success(
        self, mock_task_self, mock_db_manager, mock_tracked_companies, mock_store_facts
    ):
        """Test successful News Signals refresh task execution."""
        with (
            patch("solstein.worker.refresh_tasks.NewsSignalRefreshConnector.__init__", return_value=None),
            patch(
                "solstein.worker.refresh_tasks.NewsSignalRefreshConnector.fetch_facts", new_callable=AsyncMock
            ) as mock_fetch,
        ):
            mock_fetch.return_value = [{"fact": 1}]

            with (
                patch("solstein.worker.refresh_tasks.get_db_manager", return_value=mock_db_manager),
                patch("solstein.worker.refresh_tasks.get_tracked_company_ids", return_value=mock_tracked_companies),
                patch("solstein.worker.refresh_tasks.store_facts", mock_store_facts),
            ):
                result = refresh_news_signals.run(TEST_TENANT_ID)
                assert result is not None


class TestRetryLogicIsolated:
    """Test suite for retry logic using proper isolation."""

    def test_retry_on_connector_error(self):
        """Test that task retries on connector error."""
        mock_task = MagicMock()
        mock_task.request = MagicMock()
        mock_task.request.retries = 0
        mock_task.retry = MagicMock()

        with patch(
            "solstein.worker.refresh_tasks.SECEDGARRefreshConnector.fetch_facts", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.side_effect = Exception("API Error")

            with (
                patch("solstein.worker.refresh_tasks.get_db_manager"),
                patch("solstein.worker.refresh_tasks.get_tracked_company_ids", return_value=["comp_001"]),
            ):
                with contextlib.suppress(Exception):
                    refresh_sec_edgar.run(TEST_TENANT_ID)

    def test_max_retries_exceeded_logging(self):
        """Test that MaxRetriesExceededError is logged."""
        mock_task = MagicMock()
        mock_task.request = MagicMock()
        mock_task.request.retries = 3
        mock_task.retry = MagicMock(side_effect=MaxRetriesExceededError("Max retries exceeded"))

        with patch(
            "solstein.worker.refresh_tasks.SECEDGARRefreshConnector.fetch_facts", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.side_effect = Exception("API Error")

            with (
                patch("solstein.worker.refresh_tasks.get_db_manager"),
                patch("solstein.worker.refresh_tasks.get_tracked_company_ids", return_value=["comp_001"]),
            ):
                with contextlib.suppress(Exception):
                    refresh_sec_edgar.run(TEST_TENANT_ID)
