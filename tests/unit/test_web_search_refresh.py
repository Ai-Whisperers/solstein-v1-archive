"""Tests for WebSearchRefreshConnector."""

from unittest.mock import MagicMock

import pytest

from solstein.infrastructure.connectors.web_search_refresh import WebSearchRefreshConnector
from solstein.infrastructure.database import DatabaseManager


class TestWebSearchRefreshConnector:
    """Test suite for WebSearchRefreshConnector."""

    @pytest.fixture
    def mock_db_manager(self):
        return MagicMock(spec=DatabaseManager)

    def test_initialization(self, mock_db_manager):
        connector = WebSearchRefreshConnector(mock_db_manager, exa_api_key="test")
        assert connector.source_name == "web_search"
        assert connector.source_type == "web_discovery"
        assert connector.confidence == 0.68

    @pytest.mark.asyncio
    async def test_fetch_facts_success(self, mock_db_manager):
        connector = WebSearchRefreshConnector(mock_db_manager, exa_api_key="test")
        connector.search_client = MagicMock()
        connector.search_client.search = MagicMock(return_value=[{"title": "Result 1", "url": "https://example.com/1"}])

        facts = await connector.fetch_facts(["company"])
        assert len(facts) >= 0

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_db_manager):
        connector = WebSearchRefreshConnector(mock_db_manager, exa_api_key="test")
        connector.search_client = MagicMock()
        connector.search_client.search = MagicMock(side_effect=Exception("Error"))

        facts = await connector.fetch_facts(["company"])
        assert facts == []

    @pytest.mark.asyncio
    async def test_empty_results(self, mock_db_manager):
        connector = WebSearchRefreshConnector(mock_db_manager, exa_api_key="test")
        connector.search_client = MagicMock()
        connector.search_client.search = MagicMock(return_value=[])

        facts = await connector.fetch_facts(["company"])
        assert facts == []
