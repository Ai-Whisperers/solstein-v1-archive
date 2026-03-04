"""
Unit tests for NewsSignalDetector.

Tests cover:
1. Funding signal detection
2. Partnership signal detection
3. Key hire signal detection
4. Deduplication logic
5. Rate limit tracking
6. Confidence scoring
7. Error handling
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from solstein.data.connectors.news_signal_detector import NewsSignalDetector


class TestNewsSignalDetectorInitialization:
    """Test NewsSignalDetector initialization."""

    def test_init_with_api_key_parameter(self):
        """Test initialization with explicit API key."""
        detector = NewsSignalDetector(api_key="test-key-123")
        assert detector.api_key == "test-key-123"
        assert detector.daily_query_limit == 100
        assert detector.queries_today == 0

    def test_init_with_env_variable(self, monkeypatch):
        """Test initialization reading from environment variable."""
        from solstein.config import get_settings

        get_settings.cache_clear()
        monkeypatch.setenv("NEWSAPI_KEY", "env-key-456")
        detector = NewsSignalDetector()
        assert detector.api_key == "env-key-456"

    def test_init_missing_api_key_raises_error(self, monkeypatch):
        """Test initialization fails without API key."""
        from solstein.config import get_settings

        get_settings.cache_clear()
        monkeypatch.delenv("NEWSAPI_KEY", raising=False)
        # Also ensure it's not in settings if already loaded
        with patch("solstein.config.get_settings") as mock_get:
            mock_settings = MagicMock()
            mock_settings.news_api_key = None
            mock_get.return_value = mock_settings
            with pytest.raises(ValueError, match="NewsAPI key required"):
                NewsSignalDetector()


class TestFundingSignalDetection:
    """Test funding signal detection."""

    @patch("solstein.data.connectors.news_signal_detector.requests.get")
    def test_detect_funding_signal_success(self, mock_get):
        """Test successful funding signal detection."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "articles": [
                {
                    "title": "TechCorp Raises Series B Funding",
                    "description": "TechCorp announced Series B funding of $50 million",
                    "content": "The company raised $50 million in Series B funding",
                    "publishedAt": "2024-02-20T10:00:00Z",
                    "url": "https://example.com/article1",
                    "source": {"name": "TechNews"},
                }
            ],
        }
        mock_get.return_value = mock_response

        detector = NewsSignalDetector(api_key="test-key")
        signals = detector.detect_funding_signal("TechCorp")

        assert len(signals) == 1
        assert signals[0]["signal_type"] == "funding_round"
        assert signals[0]["confidence"] == 0.75
        assert signals[0]["company_name"] == "TechCorp"
        assert "Series B" in signals[0]["title"]

    @patch("solstein.data.connectors.news_signal_detector.requests.get")
    def test_detect_funding_signal_no_matches(self, mock_get):
        """Test funding detection with no matching articles."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "articles": [
                {
                    "title": "TechCorp Launches New Product",
                    "description": "TechCorp released a new product today",
                    "content": "The product is available now",
                    "publishedAt": "2024-02-20T10:00:00Z",
                    "url": "https://example.com/article1",
                    "source": {"name": "TechNews"},
                }
            ],
        }
        mock_get.return_value = mock_response

        detector = NewsSignalDetector(api_key="test-key")
        signals = detector.detect_funding_signal("TechCorp")

        assert len(signals) == 0

    @patch("solstein.data.connectors.news_signal_detector.requests.get")
    def test_detect_funding_signal_multiple_patterns(self, mock_get):
        """Test funding detection with multiple pattern matches."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "articles": [
                {
                    "title": "StartupX Raises $25 Million",
                    "description": "StartupX announced funding round",
                    "content": "The company secured $25 million in investment",
                    "publishedAt": "2024-02-20T10:00:00Z",
                    "url": "https://example.com/article1",
                    "source": {"name": "VCNews"},
                },
                {
                    "title": "StartupX Series A Complete",
                    "description": "Series A funding announced",
                    "content": "StartupX completed Series A",
                    "publishedAt": "2024-02-21T10:00:00Z",
                    "url": "https://example.com/article2",
                    "source": {"name": "VCNews"},
                },
            ],
        }
        mock_get.return_value = mock_response

        detector = NewsSignalDetector(api_key="test-key")
        signals = detector.detect_funding_signal("StartupX")

        assert len(signals) == 2
        assert all(s["signal_type"] == "funding_round" for s in signals)


class TestPartnershipSignalDetection:
    """Test partnership signal detection."""

    @patch("solstein.data.connectors.news_signal_detector.requests.get")
    def test_detect_partnership_signal_success(self, mock_get):
        """Test successful partnership signal detection."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "articles": [
                {
                    "title": "CompanyA Announces Partnership with CompanyB",
                    "description": "Strategic partnership announced",
                    "content": "CompanyA and CompanyB form strategic alliance",
                    "publishedAt": "2024-02-20T10:00:00Z",
                    "url": "https://example.com/article1",
                    "source": {"name": "BusinessNews"},
                }
            ],
        }
        mock_get.return_value = mock_response

        detector = NewsSignalDetector(api_key="test-key")
        signals = detector.detect_partnership_signal("CompanyA")

        assert len(signals) == 1
        assert signals[0]["signal_type"] == "partnership"
        assert signals[0]["confidence"] == 0.72
        assert "Partnership" in signals[0]["title"]

    @patch("solstein.data.connectors.news_signal_detector.requests.get")
    def test_detect_partnership_collaboration_pattern(self, mock_get):
        """Test partnership detection with collaboration keyword."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "articles": [
                {
                    "title": "TechCorp Collaboration with Partner",
                    "description": "New collaboration announced",
                    "content": "TechCorp collaborates with partner",
                    "publishedAt": "2024-02-20T10:00:00Z",
                    "url": "https://example.com/article1",
                    "source": {"name": "TechNews"},
                }
            ],
        }
        mock_get.return_value = mock_response

        detector = NewsSignalDetector(api_key="test-key")
        signals = detector.detect_partnership_signal("TechCorp")

        assert len(signals) == 1
        assert signals[0]["signal_type"] == "partnership"


class TestKeyHireSignalDetection:
    """Test key hire signal detection."""

    @patch("solstein.data.connectors.news_signal_detector.requests.get")
    def test_detect_key_hire_signal_success(self, mock_get):
        """Test successful key hire signal detection."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "articles": [
                {
                    "title": "TechCorp Appoints New CEO",
                    "description": "John Smith appointed as CEO",
                    "content": "TechCorp appoints John Smith as new CEO",
                    "publishedAt": "2024-02-20T10:00:00Z",
                    "url": "https://example.com/article1",
                    "source": {"name": "BusinessNews"},
                }
            ],
        }
        mock_get.return_value = mock_response

        detector = NewsSignalDetector(api_key="test-key")
        signals = detector.detect_key_hire_signal("TechCorp")

        assert len(signals) == 1
        assert signals[0]["signal_type"] == "key_hire"
        assert signals[0]["confidence"] == 0.70
        assert "CEO" in signals[0]["title"]

    @patch("solstein.data.connectors.news_signal_detector.requests.get")
    def test_detect_key_hire_executive_pattern(self, mock_get):
        """Test key hire detection with executive keyword."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "articles": [
                {
                    "title": "New CTO Joins TechCorp",
                    "description": "Executive appointment announced",
                    "content": "Jane Doe joins TechCorp as Chief Technology Officer",
                    "publishedAt": "2024-02-20T10:00:00Z",
                    "url": "https://example.com/article1",
                    "source": {"name": "TechNews"},
                }
            ],
        }
        mock_get.return_value = mock_response

        detector = NewsSignalDetector(api_key="test-key")
        signals = detector.detect_key_hire_signal("TechCorp")

        assert len(signals) == 1
        assert signals[0]["signal_type"] == "key_hire"
        assert signals[0]["confidence"] == 0.70


class TestDeduplication:
    """Test signal deduplication logic."""

    @patch("solstein.data.connectors.news_signal_detector.requests.get")
    def test_deduplication_same_signal_twice(self, mock_get):
        """Test that duplicate signals are not stored."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "articles": [
                {
                    "title": "TechCorp Raises Series B",
                    "description": "Series B funding announced",
                    "content": "TechCorp raised $50 million",
                    "publishedAt": "2024-02-20T10:00:00Z",
                    "url": "https://example.com/article1",
                    "source": {"name": "News1"},
                }
            ],
        }
        mock_get.return_value = mock_response

        detector = NewsSignalDetector(api_key="test-key")

        signals1 = detector.detect_funding_signal("TechCorp")
        assert len(signals1) == 1

        signals2 = detector.detect_funding_signal("TechCorp")
        assert len(signals2) == 0

    @patch("solstein.data.connectors.news_signal_detector.requests.get")
    def test_deduplication_case_insensitive(self, mock_get):
        """Test deduplication is case-insensitive."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "articles": [
                {
                    "title": "Company Raises Series B",
                    "description": "Funding announced",
                    "content": "Company raised $50 million",
                    "publishedAt": "2024-02-20T10:00:00Z",
                    "url": "https://example.com/article1",
                    "source": {"name": "News1"},
                }
            ],
        }
        mock_get.return_value = mock_response

        detector = NewsSignalDetector(api_key="test-key")

        signals1 = detector.detect_funding_signal("TechCorp")
        assert len(signals1) == 1

        signals2 = detector.detect_funding_signal("techcorp")
        assert len(signals2) == 0

    def test_clear_seen_signals(self):
        """Test clearing deduplication cache."""
        detector = NewsSignalDetector(api_key="test-key")
        detector.seen_signals.add(("company", "funding", "2024-02-20"))

        assert len(detector.seen_signals) == 1
        detector.clear_seen_signals()
        assert len(detector.seen_signals) == 0


class TestRateLimitTracking:
    """Test rate limit tracking and warnings."""

    def test_rate_limit_status_initial(self):
        """Test initial rate limit status."""
        detector = NewsSignalDetector(api_key="test-key")
        status = detector.get_rate_limit_status()

        assert status["queries_used"] == 0
        assert status["queries_remaining"] == 100
        assert status["daily_limit"] == 100

    @patch("solstein.data.connectors.news_signal_detector.requests.get")
    def test_rate_limit_increments(self, mock_get):
        """Test that query count increments."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "articles": [],
        }
        mock_get.return_value = mock_response

        detector = NewsSignalDetector(api_key="test-key")
        assert detector.queries_today == 0

        detector._search_news("test")
        assert detector.queries_today == 1

        detector._search_news("test2")
        assert detector.queries_today == 2

    def test_rate_limit_exceeded_raises_error(self):
        """Test that exceeding rate limit raises error."""
        detector = NewsSignalDetector(api_key="test-key")
        detector.queries_today = 100

        with pytest.raises(RuntimeError, match="daily query limit exceeded"):
            detector._check_rate_limit()

    def test_rate_limit_warning_at_90(self):
        """Test warning when approaching limit."""
        detector = NewsSignalDetector(api_key="test-key")
        detector.queries_today = 90

        with patch("solstein.data.connectors.news_signal_detector.logger") as mock_logger:
            detector._check_rate_limit()
            mock_logger.warning.assert_called()

    def test_daily_counter_reset(self):
        """Test daily counter resets on new day."""
        detector = NewsSignalDetector(api_key="test-key")
        detector.queries_today = 50
        detector.last_reset = datetime.now().date() - timedelta(days=1)

        detector._reset_daily_counter()

        assert detector.queries_today == 0
        assert detector.last_reset == datetime.now().date()


class TestConfidenceScoring:
    """Test confidence scoring for different signal types."""

    @patch("solstein.data.connectors.news_signal_detector.requests.get")
    def test_funding_confidence_score(self, mock_get):
        """Test funding signals have 0.75 confidence."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "articles": [
                {
                    "title": "Company Raises Series B",
                    "description": "Funding announced",
                    "content": "Company raised $50 million",
                    "publishedAt": "2024-02-20T10:00:00Z",
                    "url": "https://example.com/article1",
                    "source": {"name": "News1"},
                }
            ],
        }
        mock_get.return_value = mock_response

        detector = NewsSignalDetector(api_key="test-key")
        signals = detector.detect_funding_signal("Company")

        assert signals[0]["confidence"] == 0.75

    @patch("solstein.data.connectors.news_signal_detector.requests.get")
    def test_partnership_confidence_score(self, mock_get):
        """Test partnership signals have 0.72 confidence."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "articles": [
                {
                    "title": "Company Announces Partnership",
                    "description": "Partnership announced",
                    "content": "Company partners with another company",
                    "publishedAt": "2024-02-20T10:00:00Z",
                    "url": "https://example.com/article1",
                    "source": {"name": "News1"},
                }
            ],
        }
        mock_get.return_value = mock_response

        detector = NewsSignalDetector(api_key="test-key")
        signals = detector.detect_partnership_signal("Company")

        assert signals[0]["confidence"] == 0.72

    @patch("solstein.data.connectors.news_signal_detector.requests.get")
    def test_key_hire_confidence_score(self, mock_get):
        """Test key hire signals have 0.70 confidence."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "articles": [
                {
                    "title": "Company Appoints New CEO",
                    "description": "CEO appointed",
                    "content": "Company appoints new CEO",
                    "publishedAt": "2024-02-20T10:00:00Z",
                    "url": "https://example.com/article1",
                    "source": {"name": "News1"},
                }
            ],
        }
        mock_get.return_value = mock_response

        detector = NewsSignalDetector(api_key="test-key")
        signals = detector.detect_key_hire_signal("Company")

        assert signals[0]["confidence"] == 0.70


class TestErrorHandling:
    """Test error handling for API failures."""

    @patch("solstein.data.connectors.news_signal_detector.requests.get")
    def test_api_rate_limit_429(self, mock_get):
        """Test handling of 429 rate limit response."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response

        detector = NewsSignalDetector(api_key="test-key")

        with pytest.raises(RuntimeError, match="rate limit exceeded"):
            detector._search_news("test")

    @patch("solstein.data.connectors.news_signal_detector.requests.get")
    def test_api_error_response(self, mock_get):
        """Test handling of API error responses."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        detector = NewsSignalDetector(api_key="test-key")

        with pytest.raises(RuntimeError, match="NewsAPI error"):
            detector._search_news("test")

    @patch("solstein.data.connectors.news_signal_detector.requests.get")
    def test_api_status_not_ok(self, mock_get):
        """Test handling of non-ok status in response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "error",
            "message": "Invalid API key",
        }
        mock_get.return_value = mock_response

        detector = NewsSignalDetector(api_key="test-key")

        with pytest.raises(RuntimeError, match="Invalid API key"):
            detector._search_news("test")

    @patch("solstein.data.connectors.news_signal_detector.requests.get")
    def test_network_error(self, mock_get):
        """Test handling of network errors."""
        import requests

        mock_get.side_effect = requests.RequestException("Connection timeout")

        detector = NewsSignalDetector(api_key="test-key")

        with pytest.raises(RuntimeError, match="Failed to search news"):
            detector._search_news("test")
