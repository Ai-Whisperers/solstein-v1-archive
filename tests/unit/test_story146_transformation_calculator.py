"""Tests for STORY-146: AI Transformation Readiness Calculator.

Validates the TransformationCalculator against known scenarios and
edge cases per EPIC-038 acceptance criteria.
"""

from __future__ import annotations

import pytest

from solstein.analytics.ai_transformation_calculator import (
    ConfidenceInterval,
    RiskLevel,
    TransformationCalculator,
    TransformationEstimate,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_company(**overrides):  # type: ignore[no-untyped-def]
    """Create a minimal Company for testing."""
    from solstein.domain.models import Company

    defaults = {
        "id": "test-corp-146",
        "name": "Test Corp",
        "industry": "Energy Software",
        "revenue": 10_000_000,
        "employees": 150,
    }
    defaults.update(overrides)
    return Company(**defaults)


@pytest.fixture
def calculator() -> TransformationCalculator:
    return TransformationCalculator()


# ---------------------------------------------------------------------------
# TestTransformationEstimateStructure
# ---------------------------------------------------------------------------


class TestTransformationEstimateStructure:
    """Verify the estimate returns all required fields."""

    def test_estimate_returns_transformation_estimate(self, calculator: TransformationCalculator) -> None:
        company = _make_company()
        result = calculator.estimate(company)
        assert isinstance(result, TransformationEstimate)

    def test_estimate_has_time_months(self, calculator: TransformationCalculator) -> None:
        result = calculator.estimate(_make_company())
        assert isinstance(result.time_to_ai_ready_months, ConfidenceInterval)
        assert result.time_to_ai_ready_months.point > 0

    def test_estimate_has_investment_eur(self, calculator: TransformationCalculator) -> None:
        result = calculator.estimate(_make_company())
        assert isinstance(result.investment_required_eur, ConfidenceInterval)
        assert result.investment_required_eur.point > 0

    def test_estimate_has_efficiency_gain(self, calculator: TransformationCalculator) -> None:
        result = calculator.estimate(_make_company())
        assert isinstance(result.expected_efficiency_gain_pct, ConfidenceInterval)
        assert result.expected_efficiency_gain_pct.point > 0

    def test_estimate_has_risk_factors(self, calculator: TransformationCalculator) -> None:
        result = calculator.estimate(_make_company())
        assert isinstance(result.risk_factors, list)

    def test_estimate_has_breakdown(self, calculator: TransformationCalculator) -> None:
        result = calculator.estimate(_make_company())
        assert isinstance(result.breakdown, dict)
        assert "base_months" in result.breakdown
        assert "combined_factor" in result.breakdown


# ---------------------------------------------------------------------------
# TestConfidenceIntervals
# ---------------------------------------------------------------------------


class TestConfidenceIntervals:
    """Verify confidence intervals are properly bounded."""

    def test_ci_low_less_than_point(self, calculator: TransformationCalculator) -> None:
        result = calculator.estimate(_make_company())
        ci = result.time_to_ai_ready_months
        assert ci.low <= ci.point

    def test_ci_point_less_than_high(self, calculator: TransformationCalculator) -> None:
        result = calculator.estimate(_make_company())
        ci = result.investment_required_eur
        assert ci.point <= ci.high

    def test_ci_low_non_negative(self, calculator: TransformationCalculator) -> None:
        result = calculator.estimate(_make_company())
        assert result.time_to_ai_ready_months.low >= 0
        assert result.investment_required_eur.low >= 0
        assert result.expected_efficiency_gain_pct.low >= 0

    def test_more_data_tighter_ci(self, calculator: TransformationCalculator) -> None:
        """Companies with more data should have tighter confidence intervals."""
        sparse = _make_company(revenue=None, growth_rate=None)
        rich = _make_company(
            revenue=10_000_000,
            growth_rate=25.0,
            tech_stack=["python", "kubernetes", "aws"],
            ai_maturity="Strong",
            saas_maturity=7,
        )
        sparse_result = calculator.estimate(sparse)
        rich_result = calculator.estimate(rich)
        # Relative margin should be smaller for rich data
        sparse_margin = sparse_result.breakdown.get("confidence_margin", 1.0)
        rich_margin = rich_result.breakdown.get("confidence_margin", 1.0)
        assert rich_margin < sparse_margin


# ---------------------------------------------------------------------------
# TestSizeClassScaling
# ---------------------------------------------------------------------------


class TestSizeClassScaling:
    """Larger companies should cost more and take longer."""

    def test_enterprise_costs_more_than_startup(self, calculator: TransformationCalculator) -> None:
        startup = _make_company(employees=30)
        enterprise = _make_company(employees=3000)
        s_result = calculator.estimate(startup)
        e_result = calculator.estimate(enterprise)
        assert e_result.investment_required_eur.point > s_result.investment_required_eur.point

    def test_enterprise_takes_longer_than_startup(self, calculator: TransformationCalculator) -> None:
        startup = _make_company(employees=30)
        enterprise = _make_company(employees=3000)
        s_result = calculator.estimate(startup)
        e_result = calculator.estimate(enterprise)
        assert e_result.time_to_ai_ready_months.point > s_result.time_to_ai_ready_months.point


# ---------------------------------------------------------------------------
# TestMaturityDiscount
# ---------------------------------------------------------------------------


class TestMaturityDiscount:
    """More mature companies should need less time and investment."""

    def test_advanced_cheaper_than_none(self, calculator: TransformationCalculator) -> None:
        immature = _make_company(ai_maturity="None")
        mature = _make_company(ai_maturity="Strong")
        i_result = calculator.estimate(immature)
        m_result = calculator.estimate(mature)
        assert m_result.investment_required_eur.point < i_result.investment_required_eur.point

    def test_saas_mature_faster(self, calculator: TransformationCalculator) -> None:
        low_saas = _make_company(saas_maturity=1)
        high_saas = _make_company(saas_maturity=9)
        l_result = calculator.estimate(low_saas)
        h_result = calculator.estimate(high_saas)
        assert h_result.time_to_ai_ready_months.point < l_result.time_to_ai_ready_months.point


# ---------------------------------------------------------------------------
# TestTechStackImpact
# ---------------------------------------------------------------------------


class TestTechStackImpact:
    """Modern tech stack should reduce cost; legacy should increase it."""

    def test_modern_stack_reduces_cost(self, calculator: TransformationCalculator) -> None:
        no_stack = _make_company(tech_stack=[])
        modern = _make_company(tech_stack=["python", "kubernetes", "aws", "docker"])
        n_result = calculator.estimate(no_stack)
        m_result = calculator.estimate(modern)
        assert m_result.investment_required_eur.point < n_result.investment_required_eur.point

    def test_legacy_stack_increases_cost(self, calculator: TransformationCalculator) -> None:
        no_stack = _make_company(tech_stack=[])
        legacy = _make_company(tech_stack=["cobol", "mainframe", "on-premise"])
        n_result = calculator.estimate(no_stack)
        l_result = calculator.estimate(legacy)
        assert l_result.investment_required_eur.point > n_result.investment_required_eur.point


# ---------------------------------------------------------------------------
# TestRiskAssessment
# ---------------------------------------------------------------------------


class TestRiskAssessment:
    """Verify risk factors are identified correctly."""

    def test_small_team_has_talent_risk(self, calculator: TransformationCalculator) -> None:
        company = _make_company(employees=20)
        result = calculator.estimate(company)
        talent_risks = [r for r in result.risk_factors if r.category == "talent"]
        assert len(talent_risks) > 0
        assert talent_risks[0].level == RiskLevel.HIGH

    def test_legacy_tech_has_technology_risk(self, calculator: TransformationCalculator) -> None:
        company = _make_company(tech_stack=["cobol", "mainframe"])
        result = calculator.estimate(company)
        tech_risks = [r for r in result.risk_factors if r.category == "technology"]
        assert len(tech_risks) > 0

    def test_low_saas_maturity_has_data_risk(self, calculator: TransformationCalculator) -> None:
        company = _make_company(saas_maturity=1)
        result = calculator.estimate(company)
        data_risks = [r for r in result.risk_factors if r.category == "data"]
        assert len(data_risks) > 0

    def test_no_ai_experience_has_experience_risk(self, calculator: TransformationCalculator) -> None:
        company = _make_company(ai_maturity="None")
        result = calculator.estimate(company)
        exp_risks = [r for r in result.risk_factors if r.category == "experience"]
        assert len(exp_risks) > 0

    def test_all_risks_have_mitigation(self, calculator: TransformationCalculator) -> None:
        company = _make_company(employees=20, saas_maturity=1, ai_maturity="None")
        result = calculator.estimate(company)
        for risk in result.risk_factors:
            assert risk.mitigation, f"Risk {risk.category} missing mitigation"

    def test_overall_risk_high_when_multiple_high_risks(self, calculator: TransformationCalculator) -> None:
        company = _make_company(
            employees=20,
            saas_maturity=1,
            tech_stack=["cobol", "mainframe"],
        )
        result = calculator.estimate(company)
        assert result.overall_risk == RiskLevel.HIGH


# ---------------------------------------------------------------------------
# TestScenarioPlanning
# ---------------------------------------------------------------------------


class TestScenarioPlanning:
    """Verify simulate() applies overrides correctly."""

    def test_simulate_with_budget_override(self, calculator: TransformationCalculator) -> None:
        company = _make_company()
        baseline = calculator.estimate(company)
        scenario = calculator.simulate(company, overrides={"ai_budget_eur": 5_000_000})
        assert scenario.scenario_label == "simulation"
        assert scenario.overrides_applied == {"ai_budget_eur": 5_000_000}
        # Higher budget should reduce timeline
        assert scenario.time_to_ai_ready_months.point <= baseline.time_to_ai_ready_months.point

    def test_simulate_with_more_employees(self, calculator: TransformationCalculator) -> None:
        company = _make_company(employees=50)
        baseline = calculator.estimate(company)
        scenario = calculator.simulate(company, overrides={"employees": 500})
        # More employees -> higher cost
        assert scenario.investment_required_eur.point > baseline.investment_required_eur.point

    def test_simulate_with_maturity_upgrade(self, calculator: TransformationCalculator) -> None:
        company = _make_company(ai_maturity="None")
        baseline = calculator.estimate(company)
        scenario = calculator.simulate(company, overrides={"ai_maturity": "advanced"})
        assert scenario.investment_required_eur.point < baseline.investment_required_eur.point


# ---------------------------------------------------------------------------
# TestEstimateFromParams
# ---------------------------------------------------------------------------


class TestEstimateFromParams:
    """Verify direct parameter-based estimation works."""

    def test_estimate_from_params_basic(self, calculator: TransformationCalculator) -> None:
        result = calculator.estimate_from_params(
            {
                "employees": 200,
                "ai_maturity": "emerging",
                "saas_maturity": 5,
            }
        )
        assert isinstance(result, TransformationEstimate)
        assert result.time_to_ai_ready_months.point > 0
        assert result.scenario_label == "manual"


# ---------------------------------------------------------------------------
# TestCompanyModelIntegration
# ---------------------------------------------------------------------------


class TestCompanyModelIntegration:
    """Verify Company model has transformation fields."""

    def test_company_has_transformation_fields(self) -> None:
        company = _make_company()
        assert hasattr(company, "transformation_time_months")
        assert hasattr(company, "transformation_cost_eur")
        assert hasattr(company, "transformation_efficiency_gain_pct")
        assert hasattr(company, "transformation_risk_level")
        assert hasattr(company, "transformation_breakdown")

    def test_store_transformation_results(self, calculator: TransformationCalculator) -> None:
        company = _make_company()
        result = calculator.estimate(company)
        company.transformation_time_months = result.time_to_ai_ready_months.point
        company.transformation_cost_eur = result.investment_required_eur.point
        company.transformation_efficiency_gain_pct = result.expected_efficiency_gain_pct.point
        company.transformation_risk_level = result.overall_risk.value
        company.transformation_breakdown = result.breakdown
        assert company.transformation_time_months > 0
        assert company.transformation_cost_eur > 0
        assert company.transformation_risk_level in ("high", "medium", "low")


# ---------------------------------------------------------------------------
# TestEdgeCases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Handle sparse / minimal data gracefully."""

    def test_minimal_company(self, calculator: TransformationCalculator) -> None:
        """Company with only required fields should still get an estimate."""
        company = _make_company()
        result = calculator.estimate(company)
        assert result.time_to_ai_ready_months.point > 0

    def test_empty_params(self, calculator: TransformationCalculator) -> None:
        """Empty params dict should produce a reasonable default estimate."""
        result = calculator.estimate_from_params({})
        assert result.time_to_ai_ready_months.point > 0
        assert result.investment_required_eur.point > 0

    def test_zero_employees_uses_default(self, calculator: TransformationCalculator) -> None:
        """Zero employees should fall back to default assumption."""
        result = calculator.estimate_from_params({"employees": 0})
        assert result.time_to_ai_ready_months.point > 0
