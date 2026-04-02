"""Tests for STORY-103: Yahoo Finance stabilization.

Covers:
- SourceHealthStatus tracking and DEGRADED detection
- Data freshness computation (fresh/aging/stale)
- add_freshness_metadata enrichment
- FinancialBackendDispatcher fallback logic
- Circuit breaker integration with Yahoo Finance
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from solstein.agents.financial_backends import (
    DATA_FRESHNESS_HOURS,
    DEGRADED_THRESHOLD,
    FinancialBackendDispatcher,
    SourceHealthStatus,
    add_freshness_metadata,
    compute_data_freshness,
)
from solstein.connectors.base import RawData

# -----------------------------------------------------------------------
# SourceHealthStatus tests
# -----------------------------------------------------------------------


class TestSourceHealthStatus:
    """Verify health tracking and DEGRADED detection."""

    def test_initial_state(self):
        """New source starts healthy with zero failures."""
        health = SourceHealthStatus(name="test_source")
        assert health.consecutive_failures == 0
        assert health.is_degraded is False
        assert health.last_success is None
        assert health.last_failure is None

    def test_record_success_resets_failures(self):
        """Successful fetch resets consecutive failure counter."""
        health = SourceHealthStatus(name="test_source")
        health.consecutive_failures = 2
        health.record_success()
        assert health.consecutive_failures == 0
        assert health.last_success is not None

    def test_record_failure_increments(self):
        """Each failure increments the counter."""
        health = SourceHealthStatus(name="test_source")
        health.record_failure("timeout")
        assert health.consecutive_failures == 1
        assert health.last_failure is not None

    def test_degraded_after_threshold(self):
        """Source marked DEGRADED after DEGRADED_THRESHOLD failures."""
        health = SourceHealthStatus(name="test_source")
        for i in range(DEGRADED_THRESHOLD):
            health.record_failure(f"failure {i}")
        assert health.is_degraded is True
        assert health.consecutive_failures == DEGRADED_THRESHOLD

    def test_recovery_from_degraded(self):
        """Success after DEGRADED clears the degraded flag."""
        health = SourceHealthStatus(name="test_source")
        for i in range(DEGRADED_THRESHOLD):
            health.record_failure(f"failure {i}")
        assert health.is_degraded is True

        health.record_success()
        assert health.is_degraded is False
        assert health.consecutive_failures == 0


# -----------------------------------------------------------------------
# Data freshness tests
# -----------------------------------------------------------------------


class TestDataFreshness:
    """Verify data freshness computation."""

    def test_fresh_data(self):
        """Recently fetched data is marked fresh."""
        now = datetime.now(timezone.utc)
        result = compute_data_freshness(now)
        assert result["data_freshness"] == "fresh"
        assert result["is_stale"] is False
        assert result["staleness_hours"] < 1.0

    def test_aging_data(self):
        """Data older than half the SLA but under SLA is aging."""
        threshold = DATA_FRESHNESS_HOURS / 2 + 1
        old_time = datetime.now(timezone.utc) - timedelta(hours=threshold)
        result = compute_data_freshness(old_time)
        assert result["data_freshness"] == "aging"
        assert result["is_stale"] is False

    def test_stale_data(self):
        """Data older than SLA is marked stale."""
        old_time = datetime.now(timezone.utc) - timedelta(hours=DATA_FRESHNESS_HOURS + 1)
        result = compute_data_freshness(old_time)
        assert result["data_freshness"] == "stale"
        assert result["is_stale"] is True

    def test_add_freshness_metadata(self):
        """add_freshness_metadata enriches RawData metadata."""
        raw = RawData(
            source_name="test",
            source_url="https://example.com",
            raw_content={"ticker": "AAPL"},
            extracted_at=datetime.now(timezone.utc),
            metadata={"source_type": "stock"},
        )
        results = add_freshness_metadata([raw])
        assert len(results) == 1
        assert "data_freshness" in results[0].metadata
        assert "fetched_at" in results[0].metadata
        assert "is_stale" in results[0].metadata


# -----------------------------------------------------------------------
# FinancialBackendDispatcher tests
# -----------------------------------------------------------------------


class TestFinancialBackendDispatcher:
    """Test Yahoo Finance primary / Alpha Vantage fallback logic."""

    def _make_dispatcher(self, alpha_vantage_key=None):
        """Create a dispatcher with mocked settings."""
        with patch("solstein.agents.financial_backends.get_settings") as mock_settings:
            settings = MagicMock()
            settings.circuit_breaker.failure_threshold = 3
            settings.circuit_breaker.recovery_timeout = 60.0
            mock_settings.return_value = settings
            return FinancialBackendDispatcher(alpha_vantage_key=alpha_vantage_key)

    def _make_raw_data(self, ticker: str, source: str = "yahoo_finance") -> RawData:
        return RawData(
            source_name=source,
            source_url=f"https://finance.yahoo.com/quote/{ticker}",
            raw_content={"symbol": ticker, "marketCap": 1000000, "longName": "Test Corp"},
            extracted_at=datetime.now(timezone.utc),
            metadata={"ticker": ticker, "source_type": "stock_info"},
        )

    @pytest.mark.asyncio
    async def test_yahoo_primary_success(self):
        """When Yahoo Finance succeeds, Alpha Vantage is never called."""
        dispatcher = self._make_dispatcher(alpha_vantage_key="test-key")
        yf_data = [self._make_raw_data("AAPL")]

        with patch.object(dispatcher, "_search_yahoo", new_callable=AsyncMock, return_value=yf_data):
            with patch.object(dispatcher, "_search_alpha_vantage", new_callable=AsyncMock) as mock_av:
                results = await dispatcher.search("AAPL")
                assert len(results) == 1
                mock_av.assert_not_called()
                # Verify freshness metadata was added
                assert "data_freshness" in results[0].metadata

    @pytest.mark.asyncio
    async def test_yahoo_failure_triggers_alpha_vantage(self):
        """When Yahoo fails and AV key exists, falls back to Alpha Vantage."""
        dispatcher = self._make_dispatcher(alpha_vantage_key="test-key")
        av_data = [self._make_raw_data("AAPL", "alpha_vantage")]

        with patch.object(dispatcher, "_search_yahoo", new_callable=AsyncMock, return_value=None):
            with patch.object(dispatcher, "_search_alpha_vantage", new_callable=AsyncMock, return_value=av_data):
                results = await dispatcher.search("AAPL")
                assert len(results) == 1
                assert results[0].source_name == "alpha_vantage"

    @pytest.mark.asyncio
    async def test_no_alpha_vantage_key_skips_fallback(self):
        """When Yahoo fails and no AV key, returns empty."""
        dispatcher = self._make_dispatcher(alpha_vantage_key=None)

        with patch.object(dispatcher, "_search_yahoo", new_callable=AsyncMock, return_value=None):
            results = await dispatcher.search("AAPL")
            assert results == []

    @pytest.mark.asyncio
    async def test_degraded_after_consecutive_failures(self):
        """Yahoo marked DEGRADED after threshold consecutive failures."""
        dispatcher = self._make_dispatcher()

        with patch.object(dispatcher, "_search_yahoo", new_callable=AsyncMock, return_value=None):
            for _ in range(DEGRADED_THRESHOLD):
                await dispatcher.search("AAPL")
            assert dispatcher.yf_health.is_degraded is True
            assert dispatcher.yf_health.consecutive_failures == DEGRADED_THRESHOLD

    @pytest.mark.asyncio
    async def test_health_status_report(self):
        """get_health_status returns structured health data."""
        dispatcher = self._make_dispatcher(alpha_vantage_key="test-key")
        status = dispatcher.get_health_status()
        assert "yahoo_finance" in status
        assert "alpha_vantage" in status
        assert status["yahoo_finance"]["consecutive_failures"] == 0
        assert status["yahoo_finance"]["is_degraded"] is False
        assert status["alpha_vantage"]["configured"] is True

    @pytest.mark.asyncio
    async def test_success_resets_degraded(self):
        """Successful fetch after DEGRADED resets health."""
        dispatcher = self._make_dispatcher()
        yf_data = [self._make_raw_data("AAPL")]

        # First: force degraded state
        with patch.object(dispatcher, "_search_yahoo", new_callable=AsyncMock, return_value=None):
            for _ in range(DEGRADED_THRESHOLD):
                await dispatcher.search("AAPL")
        assert dispatcher.yf_health.is_degraded is True

        # Then: successful fetch
        with patch.object(dispatcher, "_search_yahoo", new_callable=AsyncMock, return_value=yf_data):
            results = await dispatcher.search("AAPL")
            assert len(results) == 1
            assert dispatcher.yf_health.is_degraded is False
            assert dispatcher.yf_health.consecutive_failures == 0
