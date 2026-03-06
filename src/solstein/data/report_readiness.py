from typing import Any

from solstein.domain.models import Company
from solstein.data.report_release_gate import ReportReleaseGate


REQUIRED_FINANCIAL_FIELDS = ("revenue", "employees", "growth_rate", "profit_margin")
REQUIRED_PE_FIELDS = (
    "revenue",
    "employees",
    "growth_rate",
    "profit_margin",
    "funding",
    "valuation",
)


def _get_company_field(company: Company, field_name: str) -> Any:
    value = getattr(company, field_name, None)
    if value is not None:
        return value
    financials = getattr(company, "financials", None)
    if financials is None:
        return None
    return getattr(financials, field_name, None)


def get_missing_financial_fields(company: Company) -> list[str]:
    missing = []
    for field_name in REQUIRED_FINANCIAL_FIELDS:
        value = _get_company_field(company, field_name)
        if value is None:
            missing.append(field_name)
    return missing


def get_missing_pe_fields(company: Company) -> list[str]:
    missing = []
    for field_name in REQUIRED_PE_FIELDS:
        value = _get_company_field(company, field_name)
        if value is None:
            missing.append(field_name)
    return missing


def get_low_confidence_fields(company: Company, min_confidence: float = 0.6) -> list[str]:
    confidence_scores = getattr(company, "confidence_scores", {}) or {}
    low_confidence = []
    for field_name in REQUIRED_PE_FIELDS:
        field_confidence = confidence_scores.get(field_name)
        if not isinstance(field_confidence, (int, float)):
            low_confidence.append(field_name)
            continue
        if float(field_confidence) < min_confidence:
            low_confidence.append(field_name)
    return low_confidence


def get_report_readiness_issues(companies: list[Company]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for company in companies:
        missing = get_missing_financial_fields(company)
        if missing:
            issues.append(
                {
                    "company_id": company.id,
                    "company_name": company.name,
                    "missing_fields": missing,
                }
            )
    return issues


def assert_report_ready(companies: list[Company]) -> None:
    gate = ReportReleaseGate(min_confidence=0.6, allow_synthetic=False)
    gate.ensure_release_ready(companies)


def build_report_gate_snapshot(companies: list[Company], min_confidence: float = 0.6) -> dict[str, object]:
    gate = ReportReleaseGate(min_confidence=min_confidence, allow_synthetic=False)
    result = gate.evaluate(companies)
    return result.to_dict()


def assert_client_report_ready(
    target: Company,
    competitors: list[Company],
    min_ready_peers: int = 3,
    min_confidence: float = 0.6,
) -> None:
    gate = ReportReleaseGate(min_confidence=min_confidence, allow_synthetic=False)

    target_result = gate.evaluate([target])
    if not target_result.passed:
        reason_codes = ", ".join(reason.code for reason in target_result.reasons)
        raise ValueError(f"Client report blocked: target company is not PE-ready ({reason_codes})")

    ready_peers = 0
    blocked_peers: list[str] = []
    for peer in competitors:
        peer_result = gate.evaluate([peer])
        if peer_result.passed:
            ready_peers += 1
        else:
            blocked_peers.append(f"{peer.name} ({', '.join(reason.code for reason in peer_result.reasons)})")

    if ready_peers < min_ready_peers:
        raise ValueError(
            "Client report blocked: insufficient PE-ready peer coverage. "
            f"Ready peers={ready_peers}/{min_ready_peers}. "
            f"Peer gaps: {'; '.join(blocked_peers[:8])}"
        )
