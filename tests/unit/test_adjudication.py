from __future__ import annotations

from solstein.data.adjudication import (
    AdjudicationDecision,
    get_adjudication_decision,
    list_adjudication_decisions,
    record_adjudication_decision,
)
from solstein.domain.models import Company


def _company() -> Company:
    company = Company(id="cmp1", name="ACME")
    company.confidence_scores = {
        "revenue": 0.9,
        "growth_rate": 0.8,
        "employees": 0.8,
        "profit_margin": 0.8,
        "funding": 0.7,
        "valuation": 0.7,
    }
    company.metric_sources = {
        "revenue": ["https://example.com/revenue"],
        "growth_rate": ["https://example.com/growth"],
        "employees": ["https://example.com/employees"],
        "profit_margin": ["https://example.com/margin"],
        "funding": ["https://example.com/funding"],
        "valuation": ["https://example.com/valuation"],
    }
    return company


def test_record_and_fetch_adjudication_decision() -> None:
    company = _company()
    decision = AdjudicationDecision(
        decision_id="dec-001",
        metric="revenue",
        decision="override",
        status="approved",
        actor="reviewer@solstein.local",
        reason="Audited statement",
        value=180.0,
    )

    record_adjudication_decision(company, decision)
    parsed = get_adjudication_decision(company, "revenue")

    assert parsed is not None
    assert parsed["decision_id"] == "dec-001"
    assert parsed["decision"] == "override"
    assert parsed["status"] == "approved"


def test_list_adjudication_decisions_returns_metric_map() -> None:
    company = _company()
    record_adjudication_decision(
        company,
        AdjudicationDecision(
            decision_id="dec-001",
            metric="revenue",
            decision="override",
            status="approved",
            actor="reviewer@solstein.local",
            reason="Audited statement",
            value=180.0,
        ),
    )
    record_adjudication_decision(
        company,
        AdjudicationDecision(
            decision_id="dec-002",
            metric="employees",
            decision="keep_existing",
            status="approved",
            actor="reviewer@solstein.local",
            reason="Payroll source stronger",
        ),
    )

    decisions = list_adjudication_decisions(company)

    assert set(decisions) == {"revenue", "employees"}
    assert decisions["revenue"]["decision_id"] == "dec-001"
    assert decisions["employees"]["decision"] == "keep_existing"
