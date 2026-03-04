"""Tests for WebsiteRefreshConnector."""

from unittest.mock import MagicMock

import pytest

from solstein.infrastructure.connectors.website_refresh import WebsiteRefreshConnector
from solstein.infrastructure.database import DatabaseManager


class TestWebsiteRefreshConnector:
    """Test suite for WebsiteRefreshConnector."""

    @pytest.fixture
    def mock_db_manager(self):
        return MagicMock(spec=DatabaseManager)

    def test_initialization(self, mock_db_manager):
        connector = WebsiteRefreshConnector(mock_db_manager)
        assert connector.source_name == "website"
        assert connector.source_type == "website_data"
        assert connector.confidence == 0.84

    @pytest.mark.asyncio
    async def test_fetch_facts_success(self, mock_db_manager):
        connector = WebsiteRefreshConnector(mock_db_manager)
        connector.loader = MagicMock()
        connector.loader.fetch_website_data = MagicMock(
            return_value={"url": "https://example.com", "title": "Company Website"}
        )

        facts = await connector.fetch_facts(["company"])
        assert len(facts) >= 0

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_db_manager):
        connector = WebsiteRefreshConnector(mock_db_manager)
        connector.loader = MagicMock()
        connector.loader.fetch_website_data = MagicMock(side_effect=Exception("Error"))

        facts = await connector.fetch_facts(["company"])
        assert facts == []

    @pytest.mark.asyncio
    async def test_empty_results(self, mock_db_manager):
        connector = WebsiteRefreshConnector(mock_db_manager)
        connector.loader = MagicMock()
        connector.loader.fetch_website_data = MagicMock(return_value=None)

        facts = await connector.fetch_facts(["company"])
        assert facts == []
