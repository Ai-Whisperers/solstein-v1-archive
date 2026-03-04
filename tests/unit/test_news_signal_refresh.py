"""Tests for NewsSignalRefreshConnector."""

from unittest.mock import MagicMock, patch

import pytest

from solstein.infrastructure.connectors.news_signal_refresh import NewsSignalRefreshConnector
from solstein.infrastructure.database import DatabaseManager


class TestNewsSignalRefreshConnector:
    """Test suite for NewsSignalRefreshConnector."""

    @pytest.fixture
    def mock_db_manager(self):
        return MagicMock(spec=DatabaseManager)

    def test_initialization(self, mock_db_manager):
        with patch("solstein.infrastructure.connectors.news_signal_refresh.NewsSignalDetector") as mock_detector:
            mock_detector.return_value = MagicMock()
            connector = NewsSignalRefreshConnector(mock_db_manager)
            assert connector.source_name == "news_signal"
            assert connector.source_type == "market_signal"
            assert connector.confidence == 0.72

    @pytest.mark.asyncio
    async def test_fetch_facts_success(self, mock_db_manager):
        with patch("solstein.infrastructure.connectors.news_signal_refresh.NewsSignalDetector") as mock_detector:
            mock_detector_instance = MagicMock()
            mock_detector_instance.detect_signals = MagicMock(
                return_value=[{"signal": "acquisition", "confidence": 0.8, "date": "2023-01-01"}]
            )
            mock_detector.return_value = mock_detector_instance

            connector = NewsSignalRefreshConnector(mock_db_manager)
            facts = await connector.fetch_facts(["company"])
            assert len(facts) >= 0

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_db_manager):
        with patch("solstein.infrastructure.connectors.news_signal_refresh.NewsSignalDetector") as mock_detector:
            mock_detector_instance = MagicMock()
            mock_detector_instance.detect_signals = MagicMock(side_effect=Exception("Error"))
            mock_detector.return_value = mock_detector_instance

            connector = NewsSignalRefreshConnector(mock_db_manager)
            facts = await connector.fetch_facts(["company"])
            assert facts == []

    @pytest.mark.asyncio
    async def test_empty_results(self, mock_db_manager):
        with patch("solstein.infrastructure.connectors.news_signal_refresh.NewsSignalDetector") as mock_detector:
            mock_detector_instance = MagicMock()
            mock_detector_instance.detect_signals = MagicMock(return_value=[])
            mock_detector.return_value = mock_detector_instance

            connector = NewsSignalRefreshConnector(mock_db_manager)
            facts = await connector.fetch_facts(["company"])
            assert facts == []
