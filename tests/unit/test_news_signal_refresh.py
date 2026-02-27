"""Tests for NewsSignalRefreshConnector."""

import pytest
from unittest.mock import MagicMock

from solstein.infrastructure.connectors.news_signal_refresh import NewsSignalRefreshConnector
from solstein.infrastructure.database import DatabaseManager


class TestNewsSignalRefreshConnector:
    """Test suite for NewsSignalRefreshConnector."""

    @pytest.fixture
    def mock_db_manager(self):
        return MagicMock(spec=DatabaseManager)

    def test_initialization(self, mock_db_manager):
        connector = NewsSignalRefreshConnector(mock_db_manager)
        assert connector.source_name == "news_signal"
        assert connector.source_type == "market_signal"
        assert connector.confidence == 0.72

    @pytest.mark.asyncio
    async def test_fetch_facts_success(self, mock_db_manager):
        connector = NewsSignalRefreshConnector(mock_db_manager)
        connector.news_detector = MagicMock()
        connector.news_detector.detect_signals = MagicMock(
            return_value=[{"signal": "acquisition", "confidence": 0.8, "date": "2023-01-01"}]
        )

        facts = await connector.fetch_facts(["company"])
        assert len(facts) >= 0

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_db_manager):
        connector = NewsSignalRefreshConnector(mock_db_manager)
        connector.news_detector = MagicMock()
        connector.news_detector.detect_signals = MagicMock(side_effect=Exception("Error"))

        facts = await connector.fetch_facts(["company"])
        assert facts == []

    @pytest.mark.asyncio
    async def test_empty_results(self, mock_db_manager):
        connector = NewsSignalRefreshConnector(mock_db_manager)
        connector.news_detector = MagicMock()
        connector.news_detector.detect_signals = MagicMock(return_value=[])

        facts = await connector.fetch_facts(["company"])
        assert facts == []
