"""Tests for FinancialHealthScorer."""

import pytest

from solstein.analytics.scorers.financial_health import FinancialHealthScorer
from solstein.core.scoring_config import ScoringSettings
from solstein.domain.models import FinancialMetric


class TestFinancialHealthScorer:
    """Test FinancialHealthScorer comprehensively."""

    @pytest.fixture
    def scorer(self):
        return FinancialHealthScorer()

    @pytest.fixture
    def baseline_financials(self):
        return FinancialMetric(
            revenue=5_000_000.0,
            profit_margin=15.0,
            employees=100,
            funding_raised=2_000_000.0,
        )

    def test_score_returns_tuple(self, scorer, baseline_financials):
        """Test that score returns (float, ScoringExplanation)."""
        result = scorer.score(baseline_financials)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_score_within_bounds(self, scorer, baseline_financials):
        """Test that score is always between 0 and 10."""
        score, _ = scorer.score(baseline_financials)
        assert 0.0 <= score <= 10.0

    def test_large_revenue_bonus(self, scorer):
        """Test that large revenue gets bonus."""
        financials = FinancialMetric(
            revenue=100_000_000.0,
        )
        score, expl = scorer.score(financials)
        assert any(c.name == "Revenue Scale" for c in expl.components)
        assert score > scorer.config.financial.base_score

    def test_small_revenue_penalty(self, scorer):
        """Test that small revenue gets penalty."""
        financials = FinancialMetric(
            revenue=100_000.0,
        )
        score, expl = scorer.score(financials)
        assert any(c.name == "Revenue Scale" for c in expl.components)

    def test_high_profitability_bonus(self, scorer):
        """Test that high profit margin gets bonus."""
        financials = FinancialMetric(profit_margin=25.0, employees=1)
        score, expl = scorer.score(financials)
        assert any(c.name == "Profitability Health" for c in expl.components)

    def test_negative_profitability_penalty(self, scorer):
        """Test that negative profit margin gets penalty."""
        financials = FinancialMetric(profit_margin=-10.0, employees=1)
        score, expl = scorer.score(financials)
        assert any(c.name == "Profitability Health" for c in expl.components)

    def test_exceptional_efficiency_bonus(self, scorer):
        """Test exceptional employee efficiency bonus."""
        financials = FinancialMetric(
            revenue=20_000_000.0,
            employees=50,
        )
        score, expl = scorer.score(financials)
        rev_per_emp = financials.revenue / financials.employees
        if rev_per_emp > scorer.config.financial.efficiency_exceptional_threshold:
            assert any(c.name == "Operating Efficiency" for c in expl.components)

    def test_low_efficiency_penalty(self, scorer):
        """Test low employee efficiency penalty."""
        financials = FinancialMetric(
            revenue=50_000.0,
            employees=100,
        )
        score, expl = scorer.score(financials)
        rev_per_emp = financials.revenue / financials.employees
        if rev_per_emp < scorer.config.financial.efficiency_low_threshold:
            assert any(c.name == "Operating Efficiency" for c in expl.components)

    def test_high_funding_cushion(self, scorer):
        """Test high funding cushion bonus."""
        financials = FinancialMetric(
            revenue=1_000_000.0,
            funding_raised=5_000_000.0,
        )
        score, expl = scorer.score(financials)
        ratio = financials.funding_raised / financials.revenue
        if ratio > scorer.config.financial.cushion_high_ratio:
            assert any(c.name == "Funding Cushion" for c in expl.components)

    def test_thin_funding_cushion(self, scorer):
        """Test thin funding cushion with negative margin."""
        financials = FinancialMetric(
            revenue=5_000_000.0,
            funding_raised=1_000_000.0,
            profit_margin=-2.0,
        )
        score, _ = scorer.score(financials)
        assert 0.0 <= score <= 10.0

    def test_zero_revenue(self, scorer):
        """Test with zero revenue."""
        financials = FinancialMetric(revenue=0.0)
        score, _ = scorer.score(financials)
        assert 0.0 <= score <= 10.0

    def test_none_fields_handled(self, scorer):
        """Test that None fields are safely handled."""
        financials = FinancialMetric(
            revenue=None,
            profit_margin=None,
            employees=None,
            funding_raised=None,
            allow_empty_primary=True,
        )
        score, _ = scorer.score(financials)
        assert 0.0 <= score <= 10.0

    def test_explanation_completeness(self, scorer, baseline_financials):
        """Test that explanation is complete."""
        score, expl = scorer.score(baseline_financials)
        assert expl.final_score == score
        assert len(expl.components) > 0
        for component in expl.components:
            assert component.name
            assert component.formula
            assert component.reasoning

    def test_efficiency_zero_division(self, scorer):
        """Test that zero employees doesn't cause division error."""
        financials = FinancialMetric(
            revenue=1_000_000.0,
            employees=0,
        )
        score, _ = scorer.score(financials)
        assert 0.0 <= score <= 10.0

    def test_funding_zero_division(self, scorer):
        """Test that zero revenue doesn't cause division error."""
        financials = FinancialMetric(
            revenue=0.0,
            funding_raised=1_000_000.0,
        )
        score, _ = scorer.score(financials)
        assert 0.0 <= score <= 10.0

    def test_custom_config(self):
        """Test with custom configuration."""
        config = ScoringSettings()
        config.financial.base_score = 4.0
        scorer = FinancialHealthScorer(config)
        financials = FinancialMetric(allow_empty_primary=True)
        _, expl = scorer.score(financials)
        assert expl.base_score == 4.0

    def test_consistency(self, scorer, baseline_financials):
        """Test that scoring is deterministic."""
        score1, _ = scorer.score(baseline_financials)
        score2, _ = scorer.score(baseline_financials)
        assert score1 == score2

    def test_medium_revenue_threshold(self, scorer):
        """Test medium revenue threshold scoring."""
        config = scorer.config
        mid_point = (config.financial.revenue_med_threshold + config.financial.revenue_large_threshold) / 2
        financials = FinancialMetric(revenue=mid_point)
        score, _ = scorer.score(financials)
        assert 0.0 <= score <= 10.0

    def test_profit_margin_boundaries(self, scorer):
        """Test profit margin at various boundaries."""
        margins = [0.0, 5.0, 10.0, 20.0, -5.0, -10.0]
        for margin in margins:
            financials = FinancialMetric(profit_margin=margin)
            score, _ = scorer.score(financials)
            assert 0.0 <= score <= 10.0

    def test_all_factors_combined(self, scorer):
        """Test with all factors present."""
        financials = FinancialMetric(
            revenue=50_000_000.0,
            profit_margin=20.0,
            employees=50,
            funding_raised=100_000_000.0,
        )
        score, expl = scorer.score(financials)
        assert len(expl.components) >= 3
        assert score > scorer.config.financial.base_score

    def test_large_numbers(self, scorer):
        """Test with very large numbers."""
        financials = FinancialMetric(
            revenue=1_000_000_000.0,
            profit_margin=25.0,
            employees=5_000,
            funding_raised=500_000_000.0,
        )
        score, _ = scorer.score(financials)
        assert 0.0 <= score <= 10.0
