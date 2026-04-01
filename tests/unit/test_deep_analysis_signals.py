"""Tests for STORY-184: Signal-based deep analysis strengths/weaknesses.

Verifies that the deep analysis report uses actual company dimensions
(AI, SaaS, CAGR, funding, margins, sub-scores) instead of boilerplate.
"""

from __future__ import annotations

from solstein.domain.models import Company, FinancialMetric
from solstein.exporters.markdown.base import ReportFormatter, ScoreInterpreter
from solstein.exporters.markdown.report_strategies.deep_analysis import (
    DeepAnalysisStrategy,
)


def _make_company(**overrides: object) -> Company:
    """Create a Company with sensible defaults, overridable per-test."""
    defaults = {
        "id": "test-company-abc",
        "name": "TestCo",
        "classification": "Salt",
        "composite_score": 5.5,
        "growth_score": 5.0,
        "financial_health_score": 5.0,
        "competitive_position_score": 5.0,
        "ai_score": 4.0,
        "saas_maturity": 4,
        "revenue_cagr_3yr": 8.0,
        "total_funding_raised_eur": None,
        "financials": FinancialMetric(revenue=10.0, profit_margin=5.0),
    }
    defaults.update(overrides)
    return Company(**defaults)  # type: ignore[arg-type]


def _strategy() -> DeepAnalysisStrategy:
    return DeepAnalysisStrategy(ReportFormatter(), ScoreInterpreter())


class TestStrengthSignals:
    """Strengths should reflect actual company dimension values."""

    def test_phoenix_leader_strength(self) -> None:
        report = _strategy()._generate_strengths(_make_company(composite_score=8.5))
        assert "Market leader" in report

    def test_high_growth_score_strength(self) -> None:
        report = _strategy()._generate_strengths(_make_company(growth_score=7.5))
        assert "High growth trajectory" in report

    def test_high_cagr_strength(self) -> None:
        report = _strategy()._generate_strengths(_make_company(revenue_cagr_3yr=25.0))
        assert "Rapid revenue expansion" in report
        assert "25.0%" in report

    def test_moderate_cagr_strength(self) -> None:
        report = _strategy()._generate_strengths(_make_company(revenue_cagr_3yr=12.0))
        assert "Healthy revenue growth" in report

    def test_advanced_ai_strength(self) -> None:
        report = _strategy()._generate_strengths(_make_company(ai_score=8.0))
        assert "Advanced AI" in report

    def test_solid_ai_strength(self) -> None:
        report = _strategy()._generate_strengths(_make_company(ai_score=5.5))
        assert "Solid AI adoption" in report

    def test_mature_saas_strength(self) -> None:
        report = _strategy()._generate_strengths(_make_company(saas_maturity=8))
        assert "Mature SaaS platform" in report

    def test_strong_margin_strength(self) -> None:
        fin = FinancialMetric(revenue=10.0, profit_margin=20.0)
        report = _strategy()._generate_strengths(_make_company(financials=fin))
        assert "Strong profitability" in report

    def test_well_funded_strength(self) -> None:
        report = _strategy()._generate_strengths(_make_company(total_funding_raised_eur=50.0))
        assert "Well-funded" in report

    def test_no_strengths_fallback(self) -> None:
        """Company with all low signals gets fallback message."""
        report = _strategy()._generate_strengths(
            _make_company(
                composite_score=3.0,
                growth_score=2.0,
                financial_health_score=2.0,
                competitive_position_score=2.0,
                revenue_cagr_3yr=2.0,
                ai_score=2.0,
                saas_maturity=2,
                total_funding_raised_eur=None,
                financials=FinancialMetric(revenue=1.0, profit_margin=-5.0),
            )
        )
        assert "No dominant strengths" in report


class TestWeaknessSignals:
    """Weaknesses should reflect actual company dimension values."""

    def test_critical_score_weakness(self) -> None:
        report = _strategy()._generate_weaknesses(_make_company(composite_score=3.0))
        assert "Critical position" in report

    def test_below_phoenix_weakness(self) -> None:
        report = _strategy()._generate_weaknesses(_make_company(composite_score=6.0))
        assert "Below Phoenix" in report

    def test_stagnant_growth_weakness(self) -> None:
        report = _strategy()._generate_weaknesses(_make_company(growth_score=3.0))
        assert "Stagnant growth" in report

    def test_low_cagr_weakness(self) -> None:
        report = _strategy()._generate_weaknesses(_make_company(revenue_cagr_3yr=2.0))
        assert "Low growth trajectory" in report

    def test_minimal_ai_weakness(self) -> None:
        report = _strategy()._generate_weaknesses(_make_company(ai_score=2.0))
        assert "Minimal AI adoption" in report

    def test_below_avg_ai_weakness(self) -> None:
        report = _strategy()._generate_weaknesses(_make_company(ai_score=4.0))
        assert "Below-average AI" in report

    def test_legacy_saas_weakness(self) -> None:
        report = _strategy()._generate_weaknesses(_make_company(saas_maturity=3))
        assert "Legacy technology" in report

    def test_unprofitable_weakness(self) -> None:
        fin = FinancialMetric(revenue=10.0, profit_margin=-10.0)
        report = _strategy()._generate_weaknesses(_make_company(financials=fin))
        assert "Unprofitable" in report

    def test_unfunded_weakness(self) -> None:
        report = _strategy()._generate_weaknesses(_make_company(total_funding_raised_eur=None))
        assert "Unfunded" in report

    def test_strong_company_no_weaknesses(self) -> None:
        """Company with all high signals gets 'no weaknesses' message."""
        report = _strategy()._generate_weaknesses(
            _make_company(
                composite_score=8.5,
                growth_score=8.0,
                financial_health_score=8.0,
                competitive_position_score=8.0,
                revenue_cagr_3yr=25.0,
                ai_score=8.0,
                saas_maturity=8,
                total_funding_raised_eur=50.0,
                financials=FinancialMetric(revenue=100.0, profit_margin=20.0),
            )
        )
        assert "Strong position" in report


class TestStrategicAssessment:
    """Strategic assessment should use classification and score."""

    def test_phoenix_leader(self) -> None:
        report = _strategy()._generate_strategic_assessment(
            _make_company(classification="Phoenix", composite_score=8.5)
        )
        assert "Phoenix-class market leader" in report
        assert "defend position" in report

    def test_phoenix_growth(self) -> None:
        report = _strategy()._generate_strategic_assessment(
            _make_company(classification="Phoenix", composite_score=7.2)
        )
        assert "Phoenix classification" in report
        assert "accelerate growth" in report

    def test_salt_assessment(self) -> None:
        report = _strategy()._generate_strategic_assessment(_make_company(classification="Salt", composite_score=5.5))
        assert "Salt-class" in report
        assert "transformation" in report

    def test_lead_assessment(self) -> None:
        report = _strategy()._generate_strategic_assessment(_make_company(classification="Lead", composite_score=3.0))
        assert "Lead-class" in report
        assert "strategic pivot" in report

    def test_unclassified_viable(self) -> None:
        report = _strategy()._generate_strategic_assessment(_make_company(classification=None, composite_score=5.0))
        assert "competitive pressures" in report


class TestFullReport:
    """Integration test — full report generation."""

    def test_report_contains_signal_analysis_header(self) -> None:
        strategy = _strategy()
        report = strategy.generate(_make_company())
        assert "## Signal Analysis" in report

    def test_report_no_boilerplate_phrases(self) -> None:
        """Report should not contain generic boilerplate phrases."""
        strategy = _strategy()
        report = strategy.generate(_make_company())
        # Old boilerplate used "Strategic Analysis" header
        assert "## Strategic Analysis" not in report
