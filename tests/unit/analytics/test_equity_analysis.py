"""Unit tests for Equity Analysis (EPIC-041).

Run with: pytest tests/unit/analytics/test_equity_analysis.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from unittest.mock import MagicMock

import pytest

from solstein.analytics.equity_analysis import DealParams, EquityAnalyzer, EquityResult
from solstein.domain.models import Company


class TestEquityAnalyzer:
    """Test suite for PE/VC equity analysis."""

    @pytest.fixture
    def analyzer(self) -> EquityAnalyzer:
        return EquityAnalyzer()

    @pytest.fixture
    def deal_params(self) -> DealParams:
        return DealParams(
            entry_ev_eur_m=250.0,
            equity_stake_pct=30.0,
            hold_period_years=5,
            exit_ev_revenue_multiple=8.0,
            debt_eur_m=50.0,
        )

    @pytest.fixture
    def mock_company(self) -> MagicMock:
        company = MagicMock(spec=Company)
        company.name = "TestCorp"
        company.financials = MagicMock()
        company.financials.revenue = 50.0  # EUR millions
        company.financials.growth_rate = 20.0
        company.ebitda_margin = 15.0
        return company

    def test_analyze_returns_result(
        self, analyzer: EquityAnalyzer, mock_company: MagicMock, deal_params: DealParams
    ) -> None:
        result = analyzer.analyze(mock_company, deal_params)
        assert isinstance(result, EquityResult)
        assert result.entry_ev_revenue_multiple == 5.0  # 250 / 50
        assert result.invested_equity_eur_m == 75.0  # 250 * 0.30

    def test_ev_ebitda_calculation(
        self, analyzer: EquityAnalyzer, mock_company: MagicMock, deal_params: DealParams
    ) -> None:
        result = analyzer.analyze(mock_company, deal_params)
        # EBITDA = 50M * 15% = 7.5M
        # EV/EBITDA = 250 / 7.5 = 33.33
        assert result.entry_ev_ebitda_multiple > 30

    def test_exit_ev_projection(
        self, analyzer: EquityAnalyzer, mock_company: MagicMock, deal_params: DealParams
    ) -> None:
        result = analyzer.analyze(mock_company, deal_params)
        # Exit revenue = 50M * (1.20)^5 = ~124.4M
        # Exit EV = 124.4M * 8 = ~995M
        assert result.exit_ev_eur_m > 900

    def test_moic_calculation(self, analyzer: EquityAnalyzer, mock_company: MagicMock, deal_params: DealParams) -> None:
        result = analyzer.analyze(mock_company, deal_params)
        # MOIC = Exit stake value / Invested equity
        assert result.moic > 1.0

    def test_irr_calculation(self, analyzer: EquityAnalyzer, mock_company: MagicMock, deal_params: DealParams) -> None:
        result = analyzer.analyze(mock_company, deal_params)
        # IRR should be positive for growing company
        assert result.implied_irr_pct > 0
        assert result.implied_irr_pct < 1000  # Sanity check

    def test_attractive_verdict(self, analyzer: EquityAnalyzer, mock_company: MagicMock) -> None:
        # High growth, good multiple expansion
        params = DealParams(
            entry_ev_eur_m=100.0,
            equity_stake_pct=25.0,
            hold_period_years=5,
            exit_ev_revenue_multiple=12.0,
        )
        mock_company.financials.growth_rate = 50.0
        result = analyzer.analyze(mock_company, params)
        assert result.deal_verdict == "Attractive"

    def test_cautious_verdict(self, analyzer: EquityAnalyzer, mock_company: MagicMock) -> None:
        # Low growth, low multiple
        params = DealParams(
            entry_ev_eur_m=200.0,
            equity_stake_pct=20.0,
            hold_period_years=5,
            exit_ev_revenue_multiple=4.0,
        )
        mock_company.financials.growth_rate = 5.0
        result = analyzer.analyze(mock_company, params)
        assert result.deal_verdict == "Cautious"

    def test_irr_formula(self, analyzer: EquityAnalyzer) -> None:
        # Test IRR calculation: 2x over 5 years = ~14.9% IRR
        irr = analyzer._irr(100.0, 200.0, 5)
        assert 14.0 < irr < 15.5

    def test_zero_investment_irr(self, analyzer: EquityAnalyzer) -> None:
        irr = analyzer._irr(0.0, 100.0, 5)
        assert irr == 0.0
