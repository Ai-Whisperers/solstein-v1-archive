from solstein.data.report_release_gate import GateReason, ReportGateResult, ReportReleaseGate, determine_quality_tier
from solstein.domain.models import Company, ConfidenceLevel


def _company() -> Company:
    company = Company(id="cmp1", name="ACME")
    company.data_source_type = "real"
    company.financials.revenue = 12.0
    company.financials.employees = 50
    company.financials.growth_rate = 10.0
    company.financials.profit_margin = 5.0
    company.financials.revenue_confidence = ConfidenceLevel.CONFIRMED
    company.financials.employees_confidence = ConfidenceLevel.CONFIRMED
    company.financials.growth_confidence = ConfidenceLevel.CONFIRMED
    company.financials.margin_confidence = ConfidenceLevel.CONFIRMED
    company.metric_sources = {
        "revenue": ["https://example.com/rev"],
        "employees": ["https://example.com/emp"],
        "growth_rate": ["https://example.com/gro"],
        "profit_margin": ["https://example.com/mar"],
    }
    return company


def test_report_release_gate_passes_with_valid_company() -> None:
    company = _company()

    result = ReportReleaseGate(min_completeness_score=20.0).evaluate([company])

    assert result.passed is True
    assert result.reasons == []


def test_report_release_gate_blocks_synthetic_data() -> None:
    company = _company()
    company.data_source_type = "synthetic"

    result = ReportReleaseGate(min_completeness_score=20.0).evaluate([company])

    assert result.passed is False
    codes = {reason.code for reason in result.reasons}
    assert "synthetic_data" in codes


def test_report_release_gate_blocks_missing_boundary_provenance() -> None:
    company = _company()
    company.metric_sources["revenue"] = []

    result = ReportReleaseGate(min_completeness_score=20.0).evaluate([company])

    assert result.passed is False
    codes = {reason.code for reason in result.reasons}
    assert "provenance_boundary" in codes


def test_report_release_gate_warn_mode_allows_export_with_reasons() -> None:
    company = _company()
    company.metric_sources["revenue"] = []

    result = ReportReleaseGate(min_completeness_score=20.0, warn_mode=True).evaluate([company])

    assert result.passed is True
    assert result.warn_mode is True
    codes = {reason.code for reason in result.reasons}
    assert "provenance_boundary" in codes


def test_report_release_gate_skip_gate_allows_export_with_reasons() -> None:
    company = _company()
    company.data_source_type = "synthetic"

    result = ReportReleaseGate(min_completeness_score=20.0, skip_gate=True).evaluate([company])

    assert result.passed is True
    assert result.skipped is True
    codes = {reason.code for reason in result.reasons}
    assert "synthetic_data" in codes


def test_report_release_gate_min_completeness_threshold_applies() -> None:
    company = _company()

    result = ReportReleaseGate(min_completeness_score=99.0).evaluate([company])

    assert result.passed is False
    codes = {reason.code for reason in result.reasons}
    assert "completeness" in codes


def test_determine_quality_tier_maps_completeness_only_to_silver() -> None:
    result = ReportGateResult(
        passed=False,
        reasons=[GateReason(code="completeness", message="low", details={})],
    )

    assert determine_quality_tier(result) == "silver"


def test_determine_quality_tier_maps_two_issues_to_bronze() -> None:
    result = ReportGateResult(
        passed=False,
        reasons=[
            GateReason(code="completeness", message="low", details={}),
            GateReason(code="gap_analysis", message="gap", details={}),
        ],
    )

    assert determine_quality_tier(result) == "bronze"


def test_report_release_gate_escalates_critical_claim_contradictions() -> None:
    company = _company()
    company.metric_observations = {
        "revenue": [
            {"source": "https://example.com/rev-a", "value": 100.0},
            {"source": "https://example.com/rev-b", "value": 180.0},
        ]
    }

    result = ReportReleaseGate(min_completeness_score=20.0).evaluate([company])

    assert result.passed is False
    codes = {reason.code for reason in result.reasons}
    assert "critical_claim_contradiction" in codes


def test_report_release_gate_allows_adjudicated_critical_contradictions() -> None:
    company = _company()
    company.metric_observations = {
        "revenue": [
            {"source": "https://example.com/rev-a", "value": 100.0},
            {"source": "https://example.com/rev-b", "value": 180.0},
        ]
    }
    company.metric_justifications["adjudication:revenue"] = (
        "decision_id=dec-001;decision=override;status=approved;"
        "actor=reviewer@solstein.local;reason=Latest audited filing"
    )

    result = ReportReleaseGate(min_completeness_score=20.0).evaluate([company])

    assert result.passed is True
    codes = {reason.code for reason in result.reasons}
    assert "critical_claim_contradiction" not in codes
    assert "adjudication_override" in codes
