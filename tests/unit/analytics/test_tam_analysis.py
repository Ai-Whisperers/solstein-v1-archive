"""Unit tests for TAM/SAM/SOM Analysis (EPIC-040).

Run with: pytest tests/unit/analytics/test_tam_analysis.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from unittest.mock import MagicMock

import pytest

from solstein.analytics.tam_analysis import MarketParams, TamAnalyzer, TamResult
from solstein.domain.models import Company


class TestTamAnalyzer:
    """Test suite for TAM/SAM/SOM analysis."""

    @pytest.fixture
    def analyzer(self) -> TamAnalyzer:
        return TamAnalyzer()

    @pytest.fixture
    def market_params(self) -> MarketParams:
        return MarketParams(
            market_name="B2B SaaS",
            total_market_size_eur_bn=45.0,
            target_segment_share=0.15,
            realistic_capture_rate=0.05,
            cagr_pct=22.0,
            forecast_years=5,
        )

    @pytest.fixture
    def mock_company(self) -> MagicMock:
        company = MagicMock(spec=Company)
        company.name = "TestCorp"
        company.financials = MagicMock()
        company.financials.revenue = 10.0  # EUR millions
        company.financials.growth_rate = 30.0
        return company

    def test_analyze_returns_result(
        self, analyzer: TamAnalyzer, mock_company: MagicMock, market_params: MarketParams
    ) -> None:
        result = analyzer.analyze(mock_company, market_params)
        assert isinstance(result, TamResult)
        assert result.tam_eur_bn == 45.0
        assert result.sam_eur_bn == 6.75  # 45 * 0.15
        assert result.som_eur_bn == 0.3375  # 6.75 * 0.05

    def test_sam_calculation(self, analyzer: TamAnalyzer, mock_company: MagicMock) -> None:
        params = MarketParams(
            market_name="Test",
            total_market_size_eur_bn=100.0,
            target_segment_share=0.20,
            realistic_capture_rate=0.10,
        )
        result = analyzer.analyze(mock_company, params)
        assert result.sam_eur_bn == 20.0  # 100 * 0.20
        assert result.som_eur_bn == 2.0  # 20 * 0.10

    def test_forecast_calculation(self, analyzer: TamAnalyzer, mock_company: MagicMock) -> None:
        params = MarketParams(
            market_name="Test",
            total_market_size_eur_bn=100.0,
            cagr_pct=10.0,
            forecast_years=5,
        )
        result = analyzer.analyze(mock_company, params)
        # 100 * (1.10)^5 = 161.05
        assert result.tam_forecast_eur_bn > 160.0

    def test_market_share_calculation(self, analyzer: TamAnalyzer, mock_company: MagicMock) -> None:
        params = MarketParams(market_name="Test", total_market_size_eur_bn=100.0)
        mock_company.financials.revenue = 5.0  # 5M revenue
        result = analyzer.analyze(mock_company, params)
        # 5M / 100B = 0.005%
        assert result.market_share_pct == 0.005

    def test_headroom_calculation(self, analyzer: TamAnalyzer, mock_company: MagicMock) -> None:
        params = MarketParams(
            market_name="Test",
            total_market_size_eur_bn=100.0,
            target_segment_share=0.10,
            realistic_capture_rate=0.10,
        )
        mock_company.financials.revenue = 10.0  # 10M
        result = analyzer.analyze(mock_company, params)
        # SOM = 1B, Revenue = 10M, Headroom = 100x
        assert result.headroom_multiplier == 100.0

    def test_insight_generation(self, analyzer: TamAnalyzer, mock_company: MagicMock) -> None:
        params = MarketParams(market_name="Test", total_market_size_eur_bn=100.0)
        result = analyzer.analyze(mock_company, params)
        assert isinstance(result.insight, str)
        assert len(result.insight) > 0

    def test_high_growth_insight(self, analyzer: TamAnalyzer, mock_company: MagicMock) -> None:
        params = MarketParams(
            market_name="Test",
            total_market_size_eur_bn=100.0,
            cagr_pct=25.0,
        )
        result = analyzer.analyze(mock_company, params)
        assert "CAGR" in result.insight or "growth" in result.insight.lower()
