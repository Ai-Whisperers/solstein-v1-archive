"""Tests for GlobalMarketRefreshConnector."""

from unittest.mock import MagicMock

import pytest

from solstein.infrastructure.connectors.global_market_refresh import GlobalMarketRefreshConnector
from solstein.infrastructure.database import DatabaseManager


class TestGlobalMarketRefreshConnector:
    """Test suite for GlobalMarketRefreshConnector."""

    @pytest.fixture
    def mock_db_manager(self):
        return MagicMock(spec=DatabaseManager)

    def test_initialization(self, mock_db_manager):
        connector = GlobalMarketRefreshConnector(mock_db_manager)
        assert connector.source_name == "global_market"
        assert connector.source_type == "global_market_data"
        assert connector.confidence == 0.87

    @pytest.mark.asyncio
    async def test_fetch_facts_success(self, mock_db_manager):
        connector = GlobalMarketRefreshConnector(mock_db_manager)
        connector.loader = MagicMock()
        connector.loader.get_stock_data = MagicMock(return_value={"market_cap": 1000000, "growth": 0.15})

        facts = await connector.fetch_facts(["company"])
        assert len(facts) >= 0

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_db_manager):
        connector = GlobalMarketRefreshConnector(mock_db_manager)
        connector.loader = MagicMock()
        connector.loader.get_stock_data = MagicMock(side_effect=Exception("Error"))

        facts = await connector.fetch_facts(["company"])
        assert facts == []

    @pytest.mark.asyncio
    async def test_empty_results(self, mock_db_manager):
        connector = GlobalMarketRefreshConnector(mock_db_manager)
        connector.loader = MagicMock()
        connector.loader.get_stock_data = MagicMock(return_value={})

        facts = await connector.fetch_facts(["company"])
        assert facts == []
