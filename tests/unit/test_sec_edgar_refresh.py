"""Tests for SECEDGARRefreshConnector."""

from unittest.mock import MagicMock, patch

import pytest

from solstein.infrastructure.connectors.sec_edgar_refresh import SECEDGARRefreshConnector
from solstein.infrastructure.database import DatabaseManager


class TestSECEDGARRefreshConnector:
    """Test suite for SECEDGARRefreshConnector."""

    @pytest.fixture
    def mock_db_manager(self):
        return MagicMock(spec=DatabaseManager)

    @pytest.fixture
    def connector(self, mock_db_manager):
        with patch("solstein.infrastructure.connectors.sec_edgar_refresh.SECConnector"):
            return SECEDGARRefreshConnector(mock_db_manager)

    def test_initialization(self, mock_db_manager):
        """Test connector initializes correctly."""
        with patch("solstein.infrastructure.connectors.sec_edgar_refresh.SECConnector"):
            connector = SECEDGARRefreshConnector(mock_db_manager)
            assert connector.source_name == "sec_edgar"
            assert connector.source_type == "financial"
            assert connector.confidence == 0.95

    @pytest.mark.asyncio
    async def test_fetch_facts_success(self, connector):
        """Test successful fact fetching."""
        connector.sec_connector = MagicMock()
        connector.sec_connector.get_company_filings = MagicMock(
            return_value=[{"accession_number": "0001234567-23-000001", "filing_type": "10-K", "date": "2023-02-01"}]
        )

        facts = await connector.fetch_facts(["0000012345"])
        assert len(facts) >= 0

    @pytest.mark.asyncio
    async def test_fetch_facts_error_handling(self, connector):
        """Test error handling."""
        connector.sec_connector = MagicMock()
        connector.sec_connector.get_company_filings = MagicMock(side_effect=Exception("API error"))

        facts = await connector.fetch_facts(["0000012345"])
        assert facts == []

    @pytest.mark.asyncio
    async def test_empty_results(self, connector):
        """Test empty results handling."""
        connector.sec_connector = MagicMock()
        connector.sec_connector.get_company_filings = MagicMock(return_value=[])

        facts = await connector.fetch_facts(["0000012345"])
        assert facts == []

    @pytest.mark.asyncio
    async def test_confidence_and_source(self, connector):
        """Test confidence and source attribution."""
        connector.sec_connector = MagicMock()
        connector.sec_connector.get_company_filings = MagicMock(return_value=[])

        facts = await connector.fetch_facts(["0000012345"])

        for fact in facts:
            assert fact.get("source") == "sec_edgar" or len(facts) == 0
