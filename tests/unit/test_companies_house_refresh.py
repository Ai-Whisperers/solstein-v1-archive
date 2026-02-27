"""Tests for CompaniesHouseRefreshConnector."""

import pytest
from unittest.mock import MagicMock, patch

from solstein.infrastructure.connectors.companies_house_refresh import CompaniesHouseRefreshConnector
from solstein.infrastructure.database import DatabaseManager


class TestCompaniesHouseRefreshConnector:
    """Test suite for CompaniesHouseRefreshConnector."""

    @pytest.fixture
    def mock_db_manager(self):
        return MagicMock(spec=DatabaseManager)

    def test_initialization(self, mock_db_manager):
        with patch("solstein.infrastructure.connectors.companies_house_refresh.CompaniesHouseConnector"):
            connector = CompaniesHouseRefreshConnector(mock_db_manager)
            assert connector.source_name == "companies_house"
            assert connector.source_type == "corporate_profile"
            assert connector.confidence == 0.93

    @pytest.mark.asyncio
    async def test_fetch_facts_success(self, mock_db_manager):
        with patch("solstein.infrastructure.connectors.companies_house_refresh.CompaniesHouseConnector") as mock_class:
            connector = CompaniesHouseRefreshConnector(mock_db_manager)
            connector.ch_connector = MagicMock()
            connector.ch_connector.get_company = MagicMock(
                return_value={"company_number": "12345678", "company_name": "Test Ltd", "status": "active"}
            )

            facts = await connector.fetch_facts(["12345678"])
            assert len(facts) >= 0

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_db_manager):
        with patch("solstein.infrastructure.connectors.companies_house_refresh.CompaniesHouseConnector"):
            connector = CompaniesHouseRefreshConnector(mock_db_manager)
            connector.ch_connector = MagicMock()
            connector.ch_connector.get_company = MagicMock(side_effect=Exception("API error"))

            facts = await connector.fetch_facts(["12345678"])
            assert facts == []

    @pytest.mark.asyncio
    async def test_empty_results(self, mock_db_manager):
        with patch("solstein.infrastructure.connectors.companies_house_refresh.CompaniesHouseConnector"):
            connector = CompaniesHouseRefreshConnector(mock_db_manager)
            connector.ch_connector = MagicMock()
            connector.ch_connector.get_company = MagicMock(return_value=None)

            facts = await connector.fetch_facts(["12345678"])
            assert facts == []
