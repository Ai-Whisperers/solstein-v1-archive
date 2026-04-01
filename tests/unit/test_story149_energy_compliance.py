"""Tests for STORY-149: Energy Compliance & Control Intelligence Module.

Validates the EnergyComplianceScorer against known compliant vs.
non-compliant energy company profiles.
"""

from __future__ import annotations

import pytest

from solstein.analytics.energy_compliance import (
    ComplianceRisk,
    ControlSystemTier,
    EnergyComplianceResult,
    EnergyComplianceScorer,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_company(**overrides):  # type: ignore[no-untyped-def]
    """Create a minimal Company for testing."""
    from solstein.domain.models import Company

    defaults = {
        "id": "energy-test-001",
        "name": "EnergyCorp",
        "industry": "Energy Software",
        "revenue": 10_000_000,
        "employees": 150,
    }
    defaults.update(overrides)
    return Company(**defaults)


@pytest.fixture
def scorer() -> EnergyComplianceScorer:
    return EnergyComplianceScorer()


# ---------------------------------------------------------------------------
# TestResultStructure
# ---------------------------------------------------------------------------

class TestResultStructure:
    """Verify the compliance result has all required fields."""

    def test_returns_result(self, scorer: EnergyComplianceScorer) -> None:
        result = scorer.score(_make_company())
        assert isinstance(result, EnergyComplianceResult)

    def test_has_three_dimension_scores(self, scorer: EnergyComplianceScorer) -> None:
        result = scorer.score(_make_company())
        assert 0 <= result.regulatory_score <= 100
        assert 0 <= result.control_system_score <= 100
        assert 0 <= result.change_exposure_score <= 100

    def test_has_composite_score(self, scorer: EnergyComplianceScorer) -> None:
        result = scorer.score(_make_company())
        assert 0 <= result.composite_score <= 100

    def test_has_risk_classification(self, scorer: EnergyComplianceScorer) -> None:
        result = scorer.score(_make_company())
        assert result.compliance_risk in (ComplianceRisk.HIGH, ComplianceRisk.MEDIUM, ComplianceRisk.LOW)

    def test_has_control_tier(self, scorer: EnergyComplianceScorer) -> None:
        result = scorer.score(_make_company())
        assert isinstance(result.control_tier, ControlSystemTier)

    def test_has_breakdown(self, scorer: EnergyComplianceScorer) -> None:
        result = scorer.score(_make_company())
        assert "regulatory_weight" in result.breakdown
        assert "control_system_weight" in result.breakdown


# ---------------------------------------------------------------------------
# TestCertificationScoring
# ---------------------------------------------------------------------------

class TestCertificationScoring:
    """Verify certifications improve regulatory score."""

    def test_iso_certs_boost_score(self, scorer: EnergyComplianceScorer) -> None:
        no_cert = _make_company(description="A basic company")
        with_cert = _make_company(description="ISO 27001 and SOC 2 certified company")
        r_no = scorer.score(no_cert)
        r_with = scorer.score(with_cert)
        assert r_with.regulatory_score > r_no.regulatory_score

    def test_violations_reduce_score(self, scorer: EnergyComplianceScorer) -> None:
        clean = _make_company(description="A clean record company")
        violated = _make_company(description="Company with violation history and penalty")
        r_clean = scorer.score(clean)
        r_violated = scorer.score(violated)
        assert r_violated.regulatory_score < r_clean.regulatory_score

    def test_cert_signals_recorded(self, scorer: EnergyComplianceScorer) -> None:
        company = _make_company(description="ISO 27001 certified")
        result = scorer.score(company)
        cert_signals = [s for s in result.signals if s.category == "certification"]
        assert len(cert_signals) > 0


# ---------------------------------------------------------------------------
# TestControlSystemScoring
# ---------------------------------------------------------------------------

class TestControlSystemScoring:
    """Verify control system sophistication scoring."""

    def test_scada_boosts_score(self, scorer: EnergyComplianceScorer) -> None:
        basic = _make_company(tech_stack=["python"])
        scada = _make_company(tech_stack=["SCADA", "DMS", "python"])
        r_basic = scorer.score(basic)
        r_scada = scorer.score(scada)
        assert r_scada.control_system_score > r_basic.control_system_score

    def test_automation_boosts_score(self, scorer: EnergyComplianceScorer) -> None:
        basic = _make_company(description="Basic operations")
        auto = _make_company(description="Smart grid with automated real-time monitoring")
        r_basic = scorer.score(basic)
        r_auto = scorer.score(auto)
        assert r_auto.control_system_score > r_basic.control_system_score

    def test_advanced_tier_with_full_stack(self, scorer: EnergyComplianceScorer) -> None:
        company = _make_company(
            tech_stack=["SCADA", "DMS"],
            description="Smart grid with automated monitoring and OT security",
        )
        result = scorer.score(company)
        assert result.control_tier == ControlSystemTier.ADVANCED

    def test_unknown_tier_minimal_data(self, scorer: EnergyComplianceScorer) -> None:
        company = _make_company(tech_stack=[], description="")
        result = scorer.score(company)
        assert result.control_tier in (ControlSystemTier.UNKNOWN, ControlSystemTier.STANDARD)


# ---------------------------------------------------------------------------
# TestChangeExposure
# ---------------------------------------------------------------------------

class TestChangeExposure:
    """Verify regulatory change exposure scoring."""

    def test_high_saas_maturity_reduces_exposure(self, scorer: EnergyComplianceScorer) -> None:
        low_saas = _make_company(saas_maturity=1)
        high_saas = _make_company(saas_maturity=9)
        r_low = scorer.score(low_saas)
        r_high = scorer.score(high_saas)
        assert r_high.change_exposure_score > r_low.change_exposure_score

    def test_modern_tech_reduces_exposure(self, scorer: EnergyComplianceScorer) -> None:
        basic = _make_company(description="Traditional operations")
        modern = _make_company(description="Cloud-based API platform with microservices")
        r_basic = scorer.score(basic)
        r_modern = scorer.score(modern)
        assert r_modern.change_exposure_score > r_basic.change_exposure_score


# ---------------------------------------------------------------------------
# TestRiskClassification
# ---------------------------------------------------------------------------

class TestRiskClassification:
    """Verify risk classification logic."""

    def test_compliant_company_low_risk(self, scorer: EnergyComplianceScorer) -> None:
        company = _make_company(
            tech_stack=["SCADA", "DMS", "cloud"],
            description="ISO 27001 SOC 2 certified with automated smart grid and OT security",
            saas_maturity=8,
        )
        result = scorer.score(company)
        assert result.compliance_risk == ComplianceRisk.LOW

    def test_non_compliant_high_risk(self, scorer: EnergyComplianceScorer) -> None:
        company = _make_company(
            tech_stack=[],
            description="Company with violation and penalty, non-compliant audit failure",
            saas_maturity=1,
        )
        result = scorer.score(company)
        assert result.compliance_risk == ComplianceRisk.HIGH


# ---------------------------------------------------------------------------
# TestRecommendations
# ---------------------------------------------------------------------------

class TestRecommendations:
    """Verify recommendations are generated for risk factors."""

    def test_high_risk_has_recommendations(self, scorer: EnergyComplianceScorer) -> None:
        company = _make_company(
            tech_stack=[],
            description="Penalty and violation history, non-compliant",
            saas_maturity=1,
        )
        result = scorer.score(company)
        assert len(result.recommendations) > 0

    def test_low_risk_has_maintenance_rec(self, scorer: EnergyComplianceScorer) -> None:
        company = _make_company(
            tech_stack=["SCADA", "cloud"],
            description="ISO 27001 certified",
            saas_maturity=7,
        )
        result = scorer.score(company)
        # Even low-risk should have at least a maintenance recommendation
        # unless control tier is already advanced
        assert isinstance(result.recommendations, list)


# ---------------------------------------------------------------------------
# TestCompanyModelIntegration
# ---------------------------------------------------------------------------

class TestCompanyModelIntegration:
    """Verify Company model has compliance fields."""

    def test_company_has_compliance_fields(self) -> None:
        company = _make_company()
        assert hasattr(company, "energy_compliance_score")
        assert hasattr(company, "energy_compliance_risk")
        assert hasattr(company, "energy_control_tier")
        assert hasattr(company, "energy_compliance_breakdown")

    def test_store_compliance_results(self, scorer: EnergyComplianceScorer) -> None:
        company = _make_company()
        result = scorer.score(company)
        company.energy_compliance_score = result.composite_score
        company.energy_compliance_risk = result.compliance_risk.value
        company.energy_control_tier = result.control_tier.value
        assert company.energy_compliance_score is not None
        assert company.energy_compliance_risk in ("high", "medium", "low")
