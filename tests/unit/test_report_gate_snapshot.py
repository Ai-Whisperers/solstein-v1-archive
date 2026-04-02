from solstein.data.report_readiness import build_report_gate_snapshot
from solstein.domain.models import Company, FinancialMetric


def _company(name: str, data_source_type: str, revenue: float, employees: int) -> Company:
    return Company(
        id=name.lower().replace(" ", "-"),
        name=name,
        industry="Energy",
        data_source_type=data_source_type,
        financials=FinancialMetric(
            revenue=revenue,
            employees=employees,
            growth_rate=20.0,
            profit_margin=10.0,
            valuation=100.0,
        ),
        confidence_scores={
            "revenue_confidence": 0.9,
            "employees_confidence": 0.9,
            "growth_rate_confidence": 0.9,
            "profit_margin_confidence": 0.9,
            "funding_raised_confidence": 0.9,
            "valuation_confidence": 0.9,
        },
    )


def test_report_gate_snapshot_machine_readable_shape() -> None:
    companies = [_company("Real Co", "real", 12.0, 30)]

    snapshot = build_report_gate_snapshot(companies)

    assert isinstance(snapshot, dict)
    assert set(snapshot.keys()) == {"passed", "reason_count", "reasons", "skipped", "warn_mode"}
    assert isinstance(snapshot["passed"], bool)
    assert isinstance(snapshot["reason_count"], int)
    assert isinstance(snapshot["reasons"], list)


def test_report_gate_snapshot_contains_reason_objects() -> None:
    companies = [_company("Synthetic Co", "synthetic", 0.0, 0)]

    snapshot = build_report_gate_snapshot(companies)

    assert snapshot["passed"] is False
    assert snapshot["reason_count"] >= 1
    reason = snapshot["reasons"][0]
    assert set(reason.keys()) == {"code", "message", "details"}
