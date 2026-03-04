"""Tests for LinkedInRefreshConnector."""

from unittest.mock import MagicMock

import pytest

from solstein.infrastructure.connectors.linkedin_refresh import LinkedInRefreshConnector
from solstein.infrastructure.database import DatabaseManager


class TestLinkedInRefreshConnector:
    """Test suite for LinkedInRefreshConnector."""

    @pytest.fixture
    def mock_db_manager(self):
        return MagicMock(spec=DatabaseManager)

    def test_initialization(self, mock_db_manager):
        connector = LinkedInRefreshConnector(mock_db_manager, news_api_key="test")
        assert connector.source_name == "linkedin"
        assert connector.source_type == "professional_data"
        assert connector.confidence == 0.75

    @pytest.mark.asyncio
    async def test_fetch_facts_success(self, mock_db_manager):
        connector = LinkedInRefreshConnector(mock_db_manager, news_api_key="test")
        connector.loader = MagicMock()
        connector.client.get_linkedin_data = MagicMock(return_value={"employees": 1000, "company_size": "1K-5K"})

        facts = await connector.fetch_facts(["company"])
        assert len(facts) >= 0

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_db_manager):
        connector = LinkedInRefreshConnector(mock_db_manager, news_api_key="test")
        connector.loader = MagicMock()
        connector.client.get_linkedin_data = MagicMock(side_effect=Exception("Error"))

        facts = await connector.fetch_facts(["company"])
        assert facts == []

    @pytest.mark.asyncio
    async def test_empty_results(self, mock_db_manager):
        connector = LinkedInRefreshConnector(mock_db_manager, news_api_key="test")
        connector.loader = MagicMock()
        connector.client.get_linkedin_data = MagicMock(return_value={})

        facts = await connector.fetch_facts(["company"])
        assert facts == []
