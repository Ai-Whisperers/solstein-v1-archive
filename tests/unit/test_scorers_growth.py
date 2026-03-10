"""Tests for GrowthMomentumScorer."""

import pytest

from solstein.analytics.scorers.growth_momentum import GrowthMomentumScorer
from solstein.core.scoring_config import ScoringSettings
from solstein.domain.models import FinancialMetric


class TestGrowthMomentumScorer:
    """Test GrowthMomentumScorer comprehensively."""

    @pytest.fixture
    def scorer(self):
        return GrowthMomentumScorer()

    @pytest.fixture
    def baseline_financials(self):
        return FinancialMetric(
            revenue=1_000_000.0,
            growth_rate=10.0,
            employees=50,
            profit_margin=10.0,
            funding_raised=500_000.0,
        )

    def test_score_returns_tuple(self, scorer, baseline_financials):
        """Test that score returns (float, ScoringExplanation)."""
        result = scorer.score(baseline_financials)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], float)

    def test_score_within_bounds(self, scorer, baseline_financials):
        """Test that score is always between 0 and 10."""
        score, _ = scorer.score(baseline_financials)
        assert 0.0 <= score <= 10.0

    def test_base_score_applied(self, scorer):
        """Test that base score is applied."""
        financials = FinancialMetric()
        score, expl = scorer.score(financials)
        expected_base = scorer.config.growth.base_score or 0.0
        assert expl.base_score == expected_base

    def test_revenue_growth_high_boost(self, scorer):
        """Test that high growth rate boosts score."""
        financials = FinancialMetric(growth_rate=30.0)
        score, expl = scorer.score(financials)
        assert len(expl.components) > 0
        assert any(c.name == "Revenue Growth" for c in expl.components)
        assert score > (scorer.config.growth.base_score or 0.0)

    def test_revenue_growth_capped(self, scorer):
        """Test that revenue growth boost is capped."""
        financials = FinancialMetric(growth_rate=200.0)
        score, _ = scorer.score(financials)
        assert score <= 10.0

    def test_employee_efficiency_high_threshold(self, scorer):
        """Test employee efficiency scoring at high threshold."""
        financials = FinancialMetric(
            revenue=25_000_000.0,
            employees=50,
        )
        score, expl = scorer.score(financials)
        components = [c.name for c in expl.components]
        assert "Employee Efficiency" in components

    def test_employee_efficiency_no_division_by_zero(self, scorer):
        """Test that division by zero is handled."""
        financials = FinancialMetric(
            revenue=1_000_000.0,
            employees=0,
        )
        score, _ = scorer.score(financials)
        assert not isinstance(score, float) or 0.0 <= score <= 10.0

    def test_funding_momentum_high_bonus(self, scorer):
        """Test funding momentum scoring at high level."""
        financials = FinancialMetric(funding_raised=5_000_000.0)
        score, expl = scorer.score(financials)
        assert any(c.name == "Funding Momentum" for c in expl.components)

    def test_profitability_positive_margin(self, scorer):
        """Test profitability scoring with positive margin."""
        financials = FinancialMetric(profit_margin=20.0)
        score, expl = scorer.score(financials)
        assert any(c.name == "Profitability Profile" for c in expl.components)

    def test_profitability_negative_margin(self, scorer):
        """Test profitability scoring with negative margin."""
        financials = FinancialMetric(profit_margin=-5.0)
        score, expl = scorer.score(financials)
        components = [c.name for c in expl.components]
        assert "Profitability Profile" in components

    def test_zero_growth_rate(self, scorer):
        """Test with zero growth rate."""
        financials = FinancialMetric(growth_rate=0.0)
        score, _ = scorer.score(financials)
        assert 0.0 <= score <= 10.0

    def test_none_fields_ignored(self, scorer):
        """Test that None fields are safely ignored."""
        financials = FinancialMetric(
            growth_rate=None,
            employees=None,
            revenue=None,
            funding_raised=None,
            profit_margin=None,
        )
        score, _ = scorer.score(financials)
        assert 0.0 <= score <= 10.0

    def test_explanation_populated(self, scorer, baseline_financials):
        """Test that explanation is properly populated."""
        score, expl = scorer.score(baseline_financials)
        assert expl.final_score == score
        assert len(expl.components) > 0
        for component in expl.components:
            assert component.name
            assert component.formula
            assert component.reasoning

    def test_multiple_factors_combined(self, scorer):
        """Test that multiple factors are combined correctly."""
        financials = FinancialMetric(
            growth_rate=20.0,
            revenue=5_000_000.0,
            employees=100,
            profit_margin=15.0,
            funding_raised=2_000_000.0,
        )
        score, expl = scorer.score(financials)
        assert len(expl.components) >= 3
        assert score > (scorer.config.growth.base_score or 0.0)

    def test_custom_config(self):
        """Test with custom configuration."""
        config = ScoringSettings()
        config.growth.base_score = 5.0
        scorer = GrowthMomentumScorer(config)
        financials = FinancialMetric()
        score, expl = scorer.score(financials)
        assert expl.base_score == 5.0

    def test_score_consistency(self, scorer, baseline_financials):
        """Test that scoring is deterministic."""
        score1, _ = scorer.score(baseline_financials)
        score2, _ = scorer.score(baseline_financials)
        assert score1 == score2

    def test_efficiency_medium_threshold(self, scorer):
        """Test employee efficiency at medium threshold."""
        financials = FinancialMetric(
            revenue=2_000_000.0,
            employees=100,
        )
        score, expl = scorer.score(financials)
        rev_per_emp = financials.revenue / financials.employees
        if rev_per_emp > scorer.config.growth.efficiency_med_threshold:
            assert any(c.name == "Employee Efficiency" for c in expl.components)

    def test_funding_medium_threshold(self, scorer):
        """Test funding at medium threshold."""
        financials = FinancialMetric(funding_raised=1_000_000.0)
        score, expl = scorer.score(financials)
        if financials.funding_raised > scorer.config.growth.funding_med_threshold:
            assert any(c.name == "Funding Momentum" for c in expl.components)

    def test_profit_margin_boundaries(self, scorer):
        """Test profit margin at various boundaries."""
        margins = [0.0, 5.0, 10.0, 20.0, -5.0]
        for margin in margins:
            financials = FinancialMetric(profit_margin=margin)
            score, _ = scorer.score(financials)
            assert 0.0 <= score <= 10.0

    def test_components_have_values(self, scorer, baseline_financials):
        """Test that all components have numeric values."""
        _, expl = scorer.score(baseline_financials)
        for component in expl.components:
            assert isinstance(component.value, (int, float))

    def test_large_numbers(self, scorer):
        """Test with very large financial numbers."""
        financials = FinancialMetric(
            revenue=1_000_000_000.0,
            employees=10_000,
            growth_rate=50.0,
            funding_raised=500_000_000.0,
            profit_margin=30.0,
        )
        score, _ = scorer.score(financials)
        assert 0.0 <= score <= 10.0

    def test_small_numbers(self, scorer):
        """Test with very small financial numbers."""
        financials = FinancialMetric(
            revenue=10_000.0,
            employees=2,
            growth_rate=5.0,
            funding_raised=50_000.0,
            profit_margin=2.0,
        )
        score, _ = scorer.score(financials)
        assert 0.0 <= score <= 10.0
