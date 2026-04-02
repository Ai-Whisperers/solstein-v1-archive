"""STORY-208: Confidence Score Preservation from Metric Lineage.

Validates that:
- signal_confidences are used by the scoring engine
- Low-confidence signals contribute less to score than high-confidence
- Narrative output includes confidence percentages
- Default 0.50 confidence is used for data without metadata
- Two companies with same data but different confidence get different scores
"""

import pytest

from solstein.analytics.scoring import (
    _DEFAULT_SIGNAL_CONFIDENCE,
    GrowthScorer,
    _apply_confidence_weights,
    _confidence_weight,
)
from solstein.domain.models import (
    Company,
    FinancialMetric,
    ScoreComponent,
    ScoringExplanation,
)

# -----------------------------------------------------------------------
# Default confidence constant
# -----------------------------------------------------------------------


class TestDefaultSignalConfidence:
    """Tests for _DEFAULT_SIGNAL_CONFIDENCE constant."""

    def test_default_confidence_is_half(self):
        """Default confidence for missing metadata is 0.50 (neutral)."""
        assert _DEFAULT_SIGNAL_CONFIDENCE == 0.50

    def test_missing_signal_uses_default(self):
        """When signal_confidences has some signals but not all, missing ones get 0.50."""
        # "Revenue Growth" maps to ["growth_rate"]
        # If "growth_rate" is missing from the dict, it should default to 0.50
        signal_confidences = {"revenue_level": 0.9}  # growth_rate NOT present
        weight = _confidence_weight("Revenue Growth", signal_confidences)
        assert weight == pytest.approx(0.50, abs=0.01)

    def test_present_signal_uses_actual(self):
        """When signal IS present in dict, use the actual confidence value."""
        signal_confidences = {"growth_rate": 0.8}
        weight = _confidence_weight("Revenue Growth", signal_confidences)
        assert weight == pytest.approx(0.8, abs=0.01)

    def test_unmapped_component_returns_one(self):
        """Components with no mapped signals (SaaS Maturity, etc.) return 1.0."""
        signal_confidences = {"growth_rate": 0.5}
        weight = _confidence_weight("SaaS Maturity", signal_confidences)
        assert weight == 1.0

    def test_mixed_present_and_missing_averages(self):
        """Component with mixed present/missing signals averages them correctly."""
        # "Employee Efficiency" maps to ["revenue", "employees", "revenue_level", "company_size"]
        signal_confidences = {
            "revenue": 0.9,
            "employees": 0.8,
            # "revenue_level" missing -> 0.50
            # "company_size" missing -> 0.50
        }
        weight = _confidence_weight("Employee Efficiency", signal_confidences)
        expected = (0.9 + 0.8 + 0.50 + 0.50) / 4  # = 0.675
        assert weight == pytest.approx(expected, abs=0.01)


# -----------------------------------------------------------------------
# Same data, different confidence -> different scores
# -----------------------------------------------------------------------


class TestConfidenceDifferentiatesScores:
    """AC: Two companies with same data but different confidence -> different scores."""

    def test_high_vs_low_confidence_different_scores(self):
        """Same financials but different signal confidences produce different composite scores."""
        financials = FinancialMetric(
            revenue=500.0,
            growth_rate=25.0,
            employees=2000,
            profit_margin=15.0,
            funding_raised=100.0,
        )

        high_conf = Company(
            id="high-conf",
            name="High Confidence Corp",
            industry="Software",
            financials=financials,
            signal_confidences={
                "revenue_level": 0.95,
                "revenue": 0.95,
                "growth_rate": 0.95,
                "profitability": 0.95,
                "profit_margin": 0.95,
                "company_size": 0.95,
                "employees": 0.95,
                "funding": 0.95,
                "funding_raised": 0.95,
                "valuation": 0.95,
            },
        )

        low_conf = Company(
            id="low-conf",
            name="Low Confidence Corp",
            industry="Software",
            financials=financials,
            signal_confidences={
                "revenue_level": 0.50,
                "revenue": 0.50,
                "growth_rate": 0.50,
                "profitability": 0.50,
                "profit_margin": 0.50,
                "company_size": 0.50,
                "employees": 0.50,
                "funding": 0.50,
                "funding_raised": 0.50,
                "valuation": 0.50,
            },
        )

        scorer = GrowthScorer()
        scorer.calculate_scores(high_conf)
        scorer.calculate_scores(low_conf)

        # High confidence should score higher
        assert high_conf.composite_score > low_conf.composite_score
        assert high_conf.growth_score > low_conf.growth_score
        assert high_conf.financial_health_score > low_conf.financial_health_score

    def test_partial_confidence_mixed_effect(self):
        """Mixed confidence (some high, some low) produces intermediate scores."""
        financials = FinancialMetric(
            revenue=500.0,
            growth_rate=25.0,
            employees=2000,
            profit_margin=15.0,
            funding_raised=100.0,
        )

        full_conf = Company(
            id="full",
            name="Full Confidence",
            industry="Software",
            financials=financials,
            signal_confidences={
                "revenue_level": 1.0,
                "revenue": 1.0,
                "growth_rate": 1.0,
                "profitability": 1.0,
                "profit_margin": 1.0,
                "company_size": 1.0,
                "employees": 1.0,
                "funding": 1.0,
                "funding_raised": 1.0,
                "valuation": 1.0,
            },
        )

        mixed_conf = Company(
            id="mixed",
            name="Mixed Confidence",
            industry="Software",
            financials=financials,
            signal_confidences={
                "revenue_level": 1.0,
                "revenue": 1.0,
                "growth_rate": 0.3,
                "profitability": 0.3,
                "profit_margin": 0.3,
                "company_size": 1.0,
                "employees": 1.0,
                "funding": 0.3,
                "funding_raised": 0.3,
                "valuation": 0.3,
            },
        )

        scorer = GrowthScorer()
        scorer.calculate_scores(full_conf)
        scorer.calculate_scores(mixed_conf)

        # Mixed should be lower than full
        assert mixed_conf.composite_score < full_conf.composite_score


# -----------------------------------------------------------------------
# Narrative output includes confidence
# -----------------------------------------------------------------------


class TestNarrativeIncludesConfidence:
    """AC: Narrative includes confidence percentages."""

    def test_format_narrative_includes_data_confidence(self):
        """Narrative output includes overall data confidence percentage."""
        explanation = ScoringExplanation(
            base_score=5.0,
            final_score=7.5,
            data_confidence=0.85,
            components=[
                ScoreComponent(
                    name="Revenue Growth",
                    value=2.5,
                    formula="growth_rate / 10",
                    reasoning="Strong growth",
                    confidence_weight=0.9,
                ),
            ],
        )
        narrative = explanation.format_narrative()
        assert "85%" in narrative
        assert "data confidence" in narrative.lower()

    def test_format_narrative_includes_component_confidence(self):
        """Each component in the narrative shows its confidence weight."""
        explanation = ScoringExplanation(
            base_score=5.0,
            final_score=7.0,
            data_confidence=0.70,
            components=[
                ScoreComponent(
                    name="Revenue Growth",
                    value=1.5,
                    formula="growth_rate / 10",
                    reasoning="Moderate growth",
                    confidence_weight=0.6,
                ),
                ScoreComponent(
                    name="Employee Efficiency",
                    value=0.5,
                    formula="rev_per_emp > threshold",
                    reasoning="Good efficiency",
                    confidence_weight=1.0,
                ),
            ],
        )
        narrative = explanation.format_narrative()
        assert "60% confident" in narrative
        assert "100% confident" in narrative

    def test_format_narrative_includes_warnings(self):
        """Narrative includes data warnings when present."""
        explanation = ScoringExplanation(
            base_score=5.0,
            final_score=5.0,
            data_confidence=0.55,
            data_warnings=[
                "Revenue data missing (revenue=None)",
                "Growth rate data missing (growth_rate=None)",
            ],
            components=[],
        )
        narrative = explanation.format_narrative()
        assert "Revenue data missing" in narrative
        assert "Growth rate data missing" in narrative
        assert "55%" in narrative

    def test_format_narrative_no_warnings_clean(self):
        """Narrative without warnings doesn't include warning section."""
        explanation = ScoringExplanation(
            base_score=5.0,
            final_score=8.0,
            data_confidence=1.0,
            components=[],
        )
        narrative = explanation.format_narrative()
        assert "Warning" not in narrative
        assert "100%" in narrative

    def test_format_narrative_negative_component(self):
        """Negative components show minus sign correctly."""
        explanation = ScoringExplanation(
            base_score=5.0,
            final_score=3.0,
            data_confidence=0.70,
            components=[
                ScoreComponent(
                    name="Missing Revenue Data",
                    value=-2.0,
                    formula="revenue = None",
                    reasoning="No revenue data",
                    confidence_weight=1.0,
                ),
            ],
        )
        narrative = explanation.format_narrative()
        assert "-2.00" in narrative


# -----------------------------------------------------------------------
# _apply_confidence_weights integration
# -----------------------------------------------------------------------


class TestApplyConfidenceWeightsIntegration:
    """Tests for _apply_confidence_weights with the new default."""

    def test_full_confidence_preserves_score(self):
        """All signals at 1.0 => component values unchanged."""
        explanation = ScoringExplanation(
            base_score=5.0,
            components=[
                ScoreComponent(
                    name="Revenue Growth",
                    value=2.0,
                    formula="test",
                    reasoning="test",
                ),
            ],
        )
        signal_confidences = {"growth_rate": 1.0}
        final, expl = _apply_confidence_weights(explanation, signal_confidences)
        assert expl.components[0].value == pytest.approx(2.0, abs=0.01)
        assert expl.components[0].confidence_weight == pytest.approx(1.0, abs=0.01)

    def test_half_confidence_halves_component(self):
        """Signal at 0.50 halves the component value."""
        explanation = ScoringExplanation(
            base_score=5.0,
            components=[
                ScoreComponent(
                    name="Revenue Growth",
                    value=2.0,
                    formula="test",
                    reasoning="test",
                ),
            ],
        )
        signal_confidences = {"growth_rate": 0.50}
        final, expl = _apply_confidence_weights(explanation, signal_confidences)
        assert expl.components[0].value == pytest.approx(1.0, abs=0.01)
        assert expl.components[0].confidence_weight == pytest.approx(0.50, abs=0.01)

    def test_missing_signal_uses_default_confidence(self):
        """Missing signals in dict default to 0.50 (not 1.0)."""
        explanation = ScoringExplanation(
            base_score=5.0,
            components=[
                ScoreComponent(
                    name="Revenue Growth",  # Maps to ["growth_rate"]
                    value=2.0,
                    formula="test",
                    reasoning="test",
                ),
            ],
        )
        # Dict is non-empty but growth_rate is NOT in it
        signal_confidences = {"revenue_level": 0.9}
        final, expl = _apply_confidence_weights(explanation, signal_confidences)
        # growth_rate missing => 0.50 default => value = 2.0 * 0.50 = 1.0
        assert expl.components[0].value == pytest.approx(1.0, abs=0.01)
        assert expl.components[0].confidence_weight == pytest.approx(0.50, abs=0.01)

    def test_scores_still_clamped(self):
        """Weighted scores remain in [0, 10]."""
        explanation = ScoringExplanation(
            base_score=5.0,
            components=[
                ScoreComponent(
                    name="Revenue Growth",
                    value=8.0,
                    formula="test",
                    reasoning="test",
                ),
            ],
        )
        signal_confidences = {"growth_rate": 1.0}
        final, expl = _apply_confidence_weights(explanation, signal_confidences)
        assert 0.0 <= final <= 10.0


# -----------------------------------------------------------------------
# End-to-end: scoring engine uses signal_confidences
# -----------------------------------------------------------------------


class TestScoringEngineUsesConfidences:
    """AC: ScoringEngine.score() uses company.signal_confidences values."""

    def test_scoring_applies_confidence_weights(self):
        """When signal_confidences is populated, ScoreComponent.confidence_weight is set."""
        company = Company(
            id="conf-test",
            name="Confidence Test",
            industry="Software",
            financials=FinancialMetric(
                revenue=500.0,
                growth_rate=25.0,
                employees=2000,
                profit_margin=15.0,
                funding_raised=100.0,
            ),
            signal_confidences={
                "revenue_level": 0.8,
                "revenue": 0.8,
                "growth_rate": 0.6,
                "profitability": 0.9,
                "profit_margin": 0.9,
                "funding": 0.7,
                "funding_raised": 0.7,
                "company_size": 0.5,
                "employees": 0.5,
            },
        )

        scorer = GrowthScorer()
        scorer.calculate_scores(company)

        # Verify confidence_weight is populated on components
        growth_expl = company.scoring_breakdown["growth"]
        for comp in growth_expl.components:
            assert 0.0 < comp.confidence_weight <= 1.0

        fin_expl = company.scoring_breakdown["financial"]
        for comp in fin_expl.components:
            assert 0.0 < comp.confidence_weight <= 1.0

    def test_legacy_companies_without_confidences_still_score(self):
        """Companies with empty signal_confidences score normally (no weighting applied)."""
        company = Company(
            id="legacy",
            name="Legacy Corp",
            industry="Software",
            financials=FinancialMetric(
                revenue=500.0,
                growth_rate=25.0,
                employees=2000,
                profit_margin=15.0,
            ),
            signal_confidences={},
        )

        scorer = GrowthScorer()
        scorer.calculate_scores(company)

        # Should score without errors
        assert company.composite_score is not None
        assert 0.0 <= company.composite_score <= 10.0

        # Components should have default confidence_weight=1.0 (no weighting applied)
        growth_expl = company.scoring_breakdown["growth"]
        for comp in growth_expl.components:
            assert comp.confidence_weight == 1.0
