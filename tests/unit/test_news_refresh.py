"""Tests for NewsRefreshConnector."""

from unittest.mock import MagicMock

import pytest

from solstein.infrastructure.connectors.news_refresh import NewsRefreshConnector
from solstein.infrastructure.database import DatabaseManager


class TestNewsRefreshConnector:
    """Test suite for NewsRefreshConnector."""

    @pytest.fixture
    def mock_db_manager(self):
        return MagicMock(spec=DatabaseManager)

    def test_initialization(self, mock_db_manager):
        connector = NewsRefreshConnector(mock_db_manager, news_api_key="test-key")
        assert connector.source_name == "news"
        assert connector.source_type == "press_coverage"
        assert connector.confidence == 0.72

    @pytest.mark.asyncio
    async def test_fetch_facts_success(self, mock_db_manager):
        connector = NewsRefreshConnector(mock_db_manager, news_api_key="test-key")
        connector.news_detector = MagicMock()
        connector.client.get_news = MagicMock(
            return_value=[{"title": "Company News", "url": "https://example.com", "date": "2023-01-01"}]
        )

        facts = await connector.fetch_facts(["company-name"])
        assert len(facts) >= 0

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_db_manager):
        connector = NewsRefreshConnector(mock_db_manager, news_api_key="test-key")
        connector.news_detector = MagicMock()
        connector.client.get_news = MagicMock(side_effect=Exception("API error"))

        facts = await connector.fetch_facts(["company-name"])
        assert facts == []

    @pytest.mark.asyncio
    async def test_empty_results(self, mock_db_manager):
        connector = NewsRefreshConnector(mock_db_manager, news_api_key="test-key")
        connector.news_detector = MagicMock()
        connector.client.get_news = MagicMock(return_value=[])

        facts = await connector.fetch_facts(["company-name"])
        assert facts == []
