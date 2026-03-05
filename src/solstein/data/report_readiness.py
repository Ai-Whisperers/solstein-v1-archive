from typing import Any

from solstein.domain.models import Company


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
    issues = get_report_readiness_issues(companies)
    if not issues:
        return
    issue_lines = []
    for issue in issues:
        issue_lines.append(f"{issue['company_name']}: missing {', '.join(issue['missing_fields'])}")
    details = "; ".join(issue_lines)
    raise ValueError(f"Report generation blocked: incomplete real data. {details}")


def assert_client_report_ready(
    target: Company,
    competitors: list[Company],
    min_ready_peers: int = 3,
    min_confidence: float = 0.6,
) -> None:
    target_missing = get_missing_pe_fields(target)
    target_low_conf = get_low_confidence_fields(target, min_confidence=min_confidence)
    if target_missing or target_low_conf:
        raise ValueError(
            "Client report blocked: target company is not PE-ready. "
            f"Missing fields: {', '.join(target_missing) if target_missing else 'none'}; "
            f"Low-confidence fields: {', '.join(target_low_conf) if target_low_conf else 'none'}"
        )

    ready_peers = 0
    peer_gaps: list[str] = []
    for peer in competitors:
        missing = get_missing_pe_fields(peer)
        low_conf = get_low_confidence_fields(peer, min_confidence=min_confidence)
        if not missing and not low_conf:
            ready_peers += 1
        else:
            peer_gaps.append(
                f"{peer.name} (missing: {', '.join(missing) if missing else 'none'}; "
                f"low_conf: {', '.join(low_conf) if low_conf else 'none'})"
            )

    if ready_peers < min_ready_peers:
        raise ValueError(
            "Client report blocked: insufficient PE-ready peer coverage. "
            f"Ready peers={ready_peers}/{min_ready_peers}. "
            f"Peer gaps: {'; '.join(peer_gaps[:8])}"
        )
