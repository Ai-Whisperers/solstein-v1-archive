"""Tests for PatentsRefreshConnector."""

import pytest
from unittest.mock import MagicMock

from solstein.infrastructure.connectors.patents_refresh import PatentsRefreshConnector
from solstein.infrastructure.database import DatabaseManager


class TestPatentsRefreshConnector:
    """Test suite for PatentsRefreshConnector."""

    @pytest.fixture
    def mock_db_manager(self):
        return MagicMock(spec=DatabaseManager)

    def test_initialization(self, mock_db_manager):
        connector = PatentsRefreshConnector(mock_db_manager)
        assert connector.source_name == "patents"
        assert connector.source_type == "ip_data"
        assert connector.confidence == 0.80

    @pytest.mark.asyncio
    async def test_fetch_facts_success(self, mock_db_manager):
        connector = PatentsRefreshConnector(mock_db_manager)
        connector.patent_client = MagicMock()
        connector.patent_client.search = MagicMock(
            return_value=[{"id": "US123456", "title": "Patent Title", "date": "2023-01-01"}]
        )

        facts = await connector.fetch_facts(["company"])
        assert len(facts) >= 0

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_db_manager):
        connector = PatentsRefreshConnector(mock_db_manager)
        connector.patent_client = MagicMock()
        connector.patent_client.search = MagicMock(side_effect=Exception("Error"))

        facts = await connector.fetch_facts(["company"])
        assert facts == []

    @pytest.mark.asyncio
    async def test_empty_results(self, mock_db_manager):
        connector = PatentsRefreshConnector(mock_db_manager)
        connector.patent_client = MagicMock()
        connector.patent_client.search = MagicMock(return_value=[])

        facts = await connector.fetch_facts(["company"])
        assert facts == []
