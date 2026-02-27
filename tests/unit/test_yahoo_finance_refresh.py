"""Tests for YahooFinanceRefreshConnector."""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from solstein.infrastructure.connectors.yahoo_finance_refresh import YahooFinanceRefreshConnector
from solstein.infrastructure.database import DatabaseManager


class TestYahooFinanceRefreshConnector:
    """Test suite for YahooFinanceRefreshConnector."""

    @pytest.fixture
    def mock_db_manager(self):
        """Provide a mocked DatabaseManager."""
        return MagicMock(spec=DatabaseManager)

    @pytest.fixture
    def connector(self, mock_db_manager):
        """Provide a YahooFinanceRefreshConnector instance."""
        with patch("solstein.infrastructure.connectors.yahoo_finance_refresh.CompanyResearcher"):
            connector = YahooFinanceRefreshConnector(mock_db_manager)
            return connector

    def test_initialization(self, mock_db_manager):
        """Test connector initializes with valid config."""
        with patch("solstein.infrastructure.connectors.yahoo_finance_refresh.CompanyResearcher"):
            connector = YahooFinanceRefreshConnector(mock_db_manager)

            assert connector is not None
            assert connector.db_manager == mock_db_manager
            assert connector.source_name == "yahoo_finance"
            assert connector.source_type == "market_data"
            assert connector.confidence == 0.88

    @pytest.mark.asyncio
    async def test_fetch_facts_success(self, connector):
        """Test successful fact fetching with mocked market data."""
        mock_profile = MagicMock()
        # Set all required attributes
        for attr in [
            "market_cap",
            "enterprise_value",
            "pe_ratio",
            "forward_pe",
            "peg_ratio",
            "price_to_book",
            "price_to_sales",
            "revenue",
            "revenue_growth",
            "profit_margin",
            "operating_margin",
            "ebitda",
            "net_income",
            "eps",
            "earnings_growth",
            "earnings_quarterly_growth",
            "revenue_quarterly_growth",
            "name",
            "industry",
            "sector",
            "employees",
            "website",
            "country",
            "currency",
            "exchange",
            "fiscal_year",
        ]:
            setattr(mock_profile, attr, None)

        connector.researcher = MagicMock()
        connector.researcher.research = MagicMock(return_value=mock_profile)

        facts = await connector.fetch_facts(["AAPL"])

        # Should return 4 facts: market_metrics, financial_metrics, growth_metrics, company_profile
        assert len(facts) == 4
        assert all(f["source"] == "yahoo_finance" for f in facts)
        assert all(f["confidence"] == 0.88 for f in facts)

    @pytest.mark.asyncio
    async def test_fetch_facts_error_handling(self, connector):
        """Test error handling for API failures."""
        connector.researcher = MagicMock()
        connector.researcher.research = MagicMock(side_effect=Exception("API error"))

        facts = await connector.fetch_facts(["INVALID"])
        assert facts == []

    @pytest.mark.asyncio
    async def test_empty_results_handling(self, connector):
        """Test handling of empty results."""
        mock_profile = MagicMock()
        for attr in [
            "market_cap",
            "enterprise_value",
            "pe_ratio",
            "forward_pe",
            "peg_ratio",
            "price_to_book",
            "price_to_sales",
            "revenue",
            "revenue_growth",
            "profit_margin",
            "operating_margin",
            "ebitda",
            "net_income",
            "eps",
            "earnings_growth",
            "earnings_quarterly_growth",
            "revenue_quarterly_growth",
            "name",
            "industry",
            "sector",
            "employees",
            "website",
            "country",
            "currency",
            "exchange",
            "fiscal_year",
        ]:
            setattr(mock_profile, attr, None)

        connector.researcher = MagicMock()
        connector.researcher.research = MagicMock(return_value=mock_profile)

        facts = await connector.fetch_facts(["UNKNOWN"])
        assert len(facts) == 4  # Still returns 4 fact types, just with empty values

    @pytest.mark.asyncio
    async def test_multiple_companies(self, connector):
        """Test fetching facts for multiple companies."""
        mock_profile = MagicMock()
        for attr in [
            "market_cap",
            "enterprise_value",
            "pe_ratio",
            "forward_pe",
            "peg_ratio",
            "price_to_book",
            "price_to_sales",
            "revenue",
            "revenue_growth",
            "profit_margin",
            "operating_margin",
            "ebitda",
            "net_income",
            "eps",
            "earnings_growth",
            "earnings_quarterly_growth",
            "revenue_quarterly_growth",
            "name",
            "industry",
            "sector",
            "employees",
            "website",
            "country",
            "currency",
            "exchange",
            "fiscal_year",
        ]:
            setattr(mock_profile, attr, None)

        connector.researcher = MagicMock()
        connector.researcher.research = MagicMock(return_value=mock_profile)

        facts = await connector.fetch_facts(["AAPL", "MSFT", "GOOGL"])

        # 3 companies × 4 facts each
        assert len(facts) == 12
        assert connector.researcher.research.call_count == 3

    @pytest.mark.asyncio
    async def test_confidence_and_source_attribution(self, connector):
        """Test confidence and source are correctly set."""
        mock_profile = MagicMock()
        for attr in [
            "market_cap",
            "enterprise_value",
            "pe_ratio",
            "forward_pe",
            "peg_ratio",
            "price_to_book",
            "price_to_sales",
            "revenue",
            "revenue_growth",
            "profit_margin",
            "operating_margin",
            "ebitda",
            "net_income",
            "eps",
            "earnings_growth",
            "earnings_quarterly_growth",
            "revenue_quarterly_growth",
            "name",
            "industry",
            "sector",
            "employees",
            "website",
            "country",
            "currency",
            "exchange",
            "fiscal_year",
        ]:
            setattr(mock_profile, attr, None)

        connector.researcher = MagicMock()
        connector.researcher.research = MagicMock(return_value=mock_profile)

        facts = await connector.fetch_facts(["TEST"])

        for fact in facts:
            assert fact["source"] == "yahoo_finance"
            assert fact["confidence"] == 0.88
            assert "extracted_at" in fact
            assert "metadata" in fact
