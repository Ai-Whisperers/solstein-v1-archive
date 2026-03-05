from solstein.data.report_release_gate import ReportReleaseGate
from solstein.domain.models import Company, ConfidenceLevel


def _company() -> Company:
    company = Company(id="c1", name="ACME")
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
