"""STORY-207: None-Safety Tests for Scorers.

Validates that scoring handles None fields gracefully:
- Warnings are logged for missing data
- Data confidence is reduced for missing fields
- Scores are still produced (not crashing) with incomplete data
- No silent 'or 0' substitutions hide data quality issues
"""

import pytest

from solstein.analytics.scorers._shared import calculate_data_confidence
from solstein.analytics.scorers.financial_health import FinancialHealthScorer
from solstein.analytics.scorers.growth_momentum import GrowthMomentumScorer
from solstein.domain.models import FinancialMetric

# -----------------------------------------------------------------------
# Data confidence calculation
# -----------------------------------------------------------------------


class TestDataConfidence:
    """Tests for calculate_data_confidence helper."""

    def test_complete_data_full_confidence(self):
        """Complete FinancialMetric returns confidence=1.0 with no warnings."""
        fm = FinancialMetric(
            revenue=1000.0,
            growth_rate=15.0,
            employees=100,
            profit_margin=10.0,
            funding_raised=5000.0,
        )
        confidence, warnings = calculate_data_confidence(fm)
        assert confidence == 1.0
        assert len(warnings) == 0

    def test_one_missing_field_reduces_confidence(self):
        """One missing field reduces confidence by 0.15."""
        fm = FinancialMetric(
            revenue=1000.0,
            growth_rate=None,
            employees=100,
            profit_margin=10.0,
            funding_raised=5000.0,
        )
        confidence, warnings = calculate_data_confidence(fm)
        assert confidence == pytest.approx(0.85, abs=0.01)
        assert len(warnings) == 1
        assert "Growth rate" in warnings[0]

    def test_two_missing_fields_reduces_more(self):
        """Two missing fields reduce confidence further."""
        fm = FinancialMetric(
            revenue=None,
            growth_rate=None,
            employees=100,
        )
        confidence, warnings = calculate_data_confidence(fm)
        # 3 fields missing: growth_rate, revenue, profit_margin, funding_raised = 4 * 0.15 = 0.60 reduction
        # Wait: revenue=None, growth_rate=None, profit_margin=None (default), funding_raised=None (default) = 4 missing
        assert confidence < 0.5
        assert len(warnings) >= 2

    def test_all_missing_fields_minimum_confidence(self):
        """All critical fields missing returns minimum confidence."""
        fm = FinancialMetric(allow_empty_primary=True)
        confidence, warnings = calculate_data_confidence(fm)
        assert confidence <= 0.25  # 5 fields * 0.15 = 0.75 reduction
        assert len(warnings) == 5

    def test_warnings_contain_field_names(self):
        """Warnings include field names for debugging."""
        fm = FinancialMetric(
            revenue=None,
            employees=100,
            growth_rate=None,
        )
        _, warnings = calculate_data_confidence(fm)
        warning_text = " ".join(warnings)
        assert "revenue" in warning_text.lower()
        assert "growth_rate" in warning_text.lower()


# -----------------------------------------------------------------------
# GrowthMomentumScorer None-safety
# -----------------------------------------------------------------------


class TestGrowthScorerNoneSafety:
    """Tests for GrowthMomentumScorer handling of None fields."""

    def test_none_growth_rate_no_crash(self):
        """Scorer handles None growth_rate without crashing."""
        fm = FinancialMetric(
            revenue=1000.0,
            growth_rate=None,
            employees=100,
            profit_margin=10.0,
        )
        scorer = GrowthMomentumScorer()
        score, explanation = scorer.score(fm)
        assert isinstance(score, float)
        assert 0.0 <= score <= 10.0

    def test_none_growth_rate_lower_score(self):
        """Score with None growth_rate is lower than with growth_rate."""
        fm_complete = FinancialMetric(
            revenue=1000.0,
            growth_rate=25.0,
            employees=100,
            profit_margin=10.0,
            funding_raised=5000.0,
        )
        fm_missing = FinancialMetric(
            revenue=1000.0,
            growth_rate=None,
            employees=100,
            profit_margin=10.0,
            funding_raised=5000.0,
        )
        scorer = GrowthMomentumScorer()
        score_complete, _ = scorer.score(fm_complete)
        score_missing, _ = scorer.score(fm_missing)
        assert score_missing <= score_complete

    def test_none_growth_rate_reduces_confidence(self):
        """None growth_rate reduces data_confidence in explanation."""
        fm = FinancialMetric(
            revenue=1000.0,
            growth_rate=None,
            employees=100,
            profit_margin=10.0,
        )
        scorer = GrowthMomentumScorer()
        _, explanation = scorer.score(fm)
        assert explanation.data_confidence < 1.0
        assert len(explanation.data_warnings) > 0

    def test_all_none_returns_low_score(self):
        """All financial fields None returns low score with many warnings."""
        fm = FinancialMetric(allow_empty_primary=True)
        scorer = GrowthMomentumScorer()
        score, explanation = scorer.score(fm)
        assert score <= 3.0  # Low score due to missing data penalties
        assert explanation.data_confidence <= 0.25
        assert len(explanation.data_warnings) >= 4

    def test_complete_data_high_confidence(self):
        """Complete data returns high confidence."""
        fm = FinancialMetric(
            revenue=1000.0,
            growth_rate=25.0,
            employees=100,
            profit_margin=10.0,
            funding_raised=5000.0,
        )
        scorer = GrowthMomentumScorer()
        _, explanation = scorer.score(fm)
        assert explanation.data_confidence == 1.0
        assert len(explanation.data_warnings) == 0

    def test_none_employees_skips_efficiency(self):
        """None employees skips efficiency component without crashing."""
        fm = FinancialMetric(
            revenue=1000.0,
            growth_rate=25.0,
            employees=None,
            profit_margin=10.0,
        )
        scorer = GrowthMomentumScorer()
        score, explanation = scorer.score(fm)
        assert isinstance(score, float)
        # Verify efficiency component was skipped (not in components)
        component_names = [c.name for c in explanation.components]
        assert "Employee Efficiency" not in component_names


# -----------------------------------------------------------------------
# FinancialHealthScorer None-safety
# -----------------------------------------------------------------------


class TestFinancialHealthScorerNoneSafety:
    """Tests for FinancialHealthScorer handling of None fields."""

    def test_none_revenue_no_crash(self):
        """Scorer handles None revenue without crashing."""
        fm = FinancialMetric(
            revenue=None,
            employees=100,
            growth_rate=15.0,
            profit_margin=10.0,
        )
        scorer = FinancialHealthScorer()
        score, explanation = scorer.score(fm)
        assert isinstance(score, float)
        assert 0.0 <= score <= 10.0

    def test_none_revenue_applies_penalty(self):
        """None revenue applies missing data penalty."""
        fm = FinancialMetric(
            revenue=None,
            employees=100,
            growth_rate=15.0,
            profit_margin=10.0,
        )
        scorer = FinancialHealthScorer()
        _, explanation = scorer.score(fm)
        component_names = [c.name for c in explanation.components]
        assert "Missing Revenue Data" in component_names

    def test_none_profit_margin_applies_penalty(self):
        """None profit margin applies missing data penalty."""
        fm = FinancialMetric(
            revenue=1000.0,
            employees=100,
            growth_rate=15.0,
            profit_margin=None,
        )
        scorer = FinancialHealthScorer()
        _, explanation = scorer.score(fm)
        component_names = [c.name for c in explanation.components]
        assert "Missing Profitability Data" in component_names

    def test_complete_vs_incomplete_score_difference(self):
        """Complete data scores higher than incomplete data."""
        fm_complete = FinancialMetric(
            revenue=1000.0,
            employees=100,
            growth_rate=15.0,
            profit_margin=15.0,
            funding_raised=5000.0,
        )
        fm_incomplete = FinancialMetric(
            revenue=None,
            employees=100,
            growth_rate=15.0,
            profit_margin=None,
        )
        scorer = FinancialHealthScorer()
        score_complete, _ = scorer.score(fm_complete)
        score_incomplete, _ = scorer.score(fm_incomplete)
        assert score_incomplete < score_complete

    def test_confidence_tracking(self):
        """Financial health scorer tracks data confidence."""
        fm = FinancialMetric(
            revenue=None,
            employees=100,
            growth_rate=None,
            profit_margin=None,
        )
        scorer = FinancialHealthScorer()
        _, explanation = scorer.score(fm)
        assert explanation.data_confidence < 1.0
        assert len(explanation.data_warnings) > 0
