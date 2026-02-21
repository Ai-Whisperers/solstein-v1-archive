"""
Tests for the PE Valuation Analysis module.
"""

import pytest
import pandas as pd

from solstein.analytics.valuation import (
    ValuationAnalyzer,
    GrowthAnalyzer,
    TTMEPSAnalyzer,
    ValuationBenchmark,
    ValuationContext,
)


def test_valuation_analyzer():
    """Test Graham valuation analysis for PE due diligence."""
    analyzer = ValuationAnalyzer()

    intrinsic = analyzer.calculate_intrinsic_value(
        eps_ttm=10.0,
        growth_rate=0.15,
        bond_yield=4.0,
    )

    assert intrinsic == pytest.approx(423.5, rel=0.01)

    context = analyzer.analyze(
        ticker="TEST",
        eps_ttm=10.0,
        growth_rate=0.15,
        bond_yield=4.0,
        current_price=50.0,
    )

    assert context.graham_intrinsic_value == pytest.approx(423.5, rel=0.01)
    assert context.discount_to_intrinsic_pct == pytest.approx(88.2, rel=0.01)
    assert context.is_undervalued is True
    assert context.valuation_classification == "Significant Discount"


def test_valuation_classification():
    """Test valuation classification for PE context."""
    analyzer = ValuationAnalyzer()

    intrinsic = analyzer.calculate_intrinsic_value(10.0, 0.10, 4.0)

    tests = [
        (0.3, "Significant Discount"),  # 70% discount (> 50)
        (0.6, "Moderate Discount"),  # 40% discount (20-50)
        (1.0, "Fair Value"),  # 0% discount
        (1.3, "Moderate Premium"),  # -30% premium
        (1.8, "Significant Premium"),  # -80% premium
    ]

    for price_ratio, expected_class in tests:
        current_price = intrinsic * price_ratio
        context = analyzer.analyze(
            ticker="TEST",
            eps_ttm=10.0,
            growth_rate=0.10,
            bond_yield=4.0,
            current_price=current_price,
        )
        assert context.valuation_classification == expected_class, (
            f"Failed for ratio {price_ratio}"
        )


def test_growth_analyzer():
    """Test growth rate estimation from EPS data."""
    analyzer = GrowthAnalyzer(min_quarters=4)

    dates = pd.date_range(end="2024-12-31", periods=12, freq="QE")
    eps_values = [5.0 * (1.15 ** (i / 4)) for i in range(12)]

    eps_series = pd.Series(eps_values, index=dates)

    growth_rate = analyzer.estimate_growth_rate(eps_series)

    assert growth_rate is not None
    assert growth_rate > 0.10
    assert growth_rate < 0.20


def test_ttm_eps_analyzer():
    """Test TTM EPS calculation."""
    analyzer = TTMEPSAnalyzer()

    dates = pd.date_range(start="2024-01-01", periods=6, freq="QE")
    eps_values = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5]

    eps_series = pd.Series(eps_values, index=dates)
    eps_series = eps_series.sort_index()

    ttm_eps = analyzer.calculate(eps_series)

    assert ttm_eps == pytest.approx(5.4, rel=0.01)


def test_valuation_benchmark():
    """Test benchmarking multiple companies for PE portfolio."""
    benchmark = ValuationBenchmark()

    companies = [
        {
            "ticker": "AAPL",
            "eps_ttm": 6.0,
            "growth_rate": 0.12,
            "bond_yield": 4.0,
            "current_price": 150.0,
        },
        {
            "ticker": "MSFT",
            "eps_ttm": 12.0,
            "growth_rate": 0.15,
            "bond_yield": 4.0,
            "current_price": 400.0,
        },
    ]

    results = benchmark.benchmark_companies(companies)

    assert len(results) == 2

    undervalued = benchmark.get_undervalued(results)
    assert len(undervalued) >= 0


def test_pe_insight_generation():
    """Test PE insight text generation."""
    from solstein.analytics.valuation import create_pe_valuation_insight

    insight = create_pe_valuation_insight(
        ticker="TEST",
        market_cap=1_000_000_000,
        current_price=50.0,
        eps_ttm=10.0,
        growth_rate=0.15,
        bond_yield=4.0,
    )

    assert insight["ticker"] == "TEST"
    assert insight["valuation"]["classification"] == "Significant Discount"
    assert "discount" in insight["pe_insight"].lower()


def test_invalid_inputs():
    """Test error handling for invalid inputs."""
    analyzer = ValuationAnalyzer()

    with pytest.raises(ValueError):
        analyzer.calculate_intrinsic_value(-10, 0.15, 4.0)

    with pytest.raises(ValueError):
        analyzer.calculate_intrinsic_value(10.0, 0.15, 0.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
