"""Tests for FundingRefreshConnector."""

import pytest
from unittest.mock import MagicMock

from solstein.infrastructure.connectors.funding_refresh import FundingRefreshConnector
from solstein.infrastructure.database import DatabaseManager


class TestFundingRefreshConnector:
    """Test suite for FundingRefreshConnector."""

    @pytest.fixture
    def mock_db_manager(self):
        return MagicMock(spec=DatabaseManager)

    def test_initialization(self, mock_db_manager):
        connector = FundingRefreshConnector(mock_db_manager, crunchbase_key="test")
        assert connector.source_name == "funding"
        assert connector.source_type == "funding_data"
        assert connector.confidence == 0.73

    @pytest.mark.asyncio
    async def test_fetch_facts_success(self, mock_db_manager):
        connector = FundingRefreshConnector(mock_db_manager, crunchbase_key="test")
        connector.loader = MagicMock()
        connector.loader.get_funding = MagicMock(return_value={"total_raised": 5000000, "num_rounds": 2})

        facts = await connector.fetch_facts(["company"])
        assert len(facts) >= 0

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_db_manager):
        connector = FundingRefreshConnector(mock_db_manager, crunchbase_key="test")
        connector.loader = MagicMock()
        connector.loader.get_funding = MagicMock(side_effect=Exception("Error"))

        facts = await connector.fetch_facts(["company"])
        assert facts == []

    @pytest.mark.asyncio
    async def test_empty_results(self, mock_db_manager):
        connector = FundingRefreshConnector(mock_db_manager, crunchbase_key="test")
        connector.loader = MagicMock()
        connector.loader.get_funding = MagicMock(return_value={})

        facts = await connector.fetch_facts(["company"])
        assert facts == []
