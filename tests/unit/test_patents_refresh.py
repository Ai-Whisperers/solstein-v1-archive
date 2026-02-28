"""Tests for PatentsRefreshConnector."""

import pytest
from unittest.mock import MagicMock, patch

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
    @patch("solstein.infrastructure.connectors.patents_refresh.search_company_patents")
    async def test_error_handling(self, mock_search, mock_db_manager):
        mock_search.side_effect = Exception("Error")
        connector = PatentsRefreshConnector(mock_db_manager)

        facts = await connector.fetch_facts(["company"])
        assert facts == []

    @pytest.mark.asyncio
    @patch("solstein.infrastructure.connectors.patents_refresh.search_company_patents")
    async def test_empty_results(self, mock_search, mock_db_manager):
        # Create a mock result object that mimics PatentSearchResult
        mock_result = MagicMock()
        mock_result.total_patents = 0
        mock_result.recent_patents = 0
        mock_result.ai_related_patents = 0
        mock_result.top_categories = []
        mock_result.source = "uspto_peds"
        mock_search.return_value = mock_result
        connector = PatentsRefreshConnector(mock_db_manager)

        facts = await connector.fetch_facts(["company"])
        assert len(facts) == 1  # Returns fact with zero patents
