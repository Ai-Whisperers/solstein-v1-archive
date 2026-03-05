from solstein.data.gap_analyzer import GapStatus, analyze_company_gaps
from solstein.domain.models import Company, ConfidenceLevel


def _company() -> Company:
    return Company(id="c1", name="ACME")


def test_analyze_company_gaps_marks_missing_fields() -> None:
    company = _company()

    result = analyze_company_gaps(company)

    assert result["unresolved_count"] == 4
    assert result["is_ready"] is False
    assert all(item["status"] == GapStatus.MISSING for item in result["field_states"])


def test_analyze_company_gaps_marks_provenance_invalid_when_value_exists_without_sources() -> None:
    company = _company()
    company.financials.revenue = 12.0
    company.financials.revenue_confidence = ConfidenceLevel.CONFIRMED

    result = analyze_company_gaps(company)
    revenue_state = next(item for item in result["field_states"] if item["field"] == "revenue")

    assert revenue_state["status"] == GapStatus.PROVENANCE_INVALID


def test_analyze_company_gaps_marks_ready_when_value_and_provenance_exist() -> None:
    company = _company()
    company.financials.revenue = 12.0
    company.financials.employees = 50
    company.financials.growth_rate = 22.0
    company.financials.profit_margin = 12.0
    company.financials.revenue_confidence = ConfidenceLevel.CONFIRMED
    company.financials.employees_confidence = ConfidenceLevel.CONFIRMED
    company.financials.growth_confidence = ConfidenceLevel.CONFIRMED
    company.financials.margin_confidence = ConfidenceLevel.CONFIRMED
    company.metric_sources = {
        "revenue": ["https://example.com/revenue"],
        "employees": ["https://example.com/employees"],
        "growth_rate": ["https://example.com/growth"],
        "profit_margin": ["https://example.com/margin"],
    }

    result = analyze_company_gaps(company)

    assert result["is_ready"] is True
    assert all(item["status"] == GapStatus.READY for item in result["field_states"])
