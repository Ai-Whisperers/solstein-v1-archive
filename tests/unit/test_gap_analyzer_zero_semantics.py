from solstein.data.gap_analyzer import GapStatus, analyze_company_gaps
from solstein.domain.models import Company, ConfidenceLevel, FinancialMetric


def _company(revenue: float, growth_rate: float, profit_margin: float) -> Company:
    return Company(
        id="gap-1",
        name="Gap Test Co",
        industry="Energy",
        financials=FinancialMetric(
            revenue=revenue,
            employees=25,
            growth_rate=growth_rate,
            profit_margin=profit_margin,
            growth_confidence=ConfidenceLevel.CONFIRMED,
            margin_confidence=ConfidenceLevel.CONFIRMED,
        ),
        metric_sources={
            "revenue": ["https://example.com/revenue"],
            "employees": ["https://example.com/employees"],
            "growth_rate": ["https://example.com/growth"],
            "profit_margin": ["https://example.com/margin"],
        },
        confidence_scores={
            "revenue_confidence": 0.9,
            "employees_confidence": 0.9,
            "growth_rate_confidence": 0.9,
            "profit_margin_confidence": 0.9,
        },
    )


def test_zero_revenue_is_missing_by_policy() -> None:
    company = _company(revenue=0.0, growth_rate=10.0, profit_margin=5.0)

    gaps = analyze_company_gaps(company, min_confidence=0.5)

    revenue_state = next(item for item in gaps["field_states"] if item["field"] == "revenue")
    assert revenue_state["status"] == GapStatus.MISSING


def test_zero_growth_rate_is_allowed() -> None:
    company = _company(revenue=10.0, growth_rate=0.0, profit_margin=5.0)

    gaps = analyze_company_gaps(company, min_confidence=0.5)

    growth_state = next(item for item in gaps["field_states"] if item["field"] == "growth_rate")
    assert growth_state["status"] == GapStatus.READY


def test_zero_profit_margin_is_allowed() -> None:
    company = _company(revenue=10.0, growth_rate=5.0, profit_margin=0.0)

    gaps = analyze_company_gaps(company, min_confidence=0.5)

    margin_state = next(item for item in gaps["field_states"] if item["field"] == "profit_margin")
    assert margin_state["status"] == GapStatus.READY
