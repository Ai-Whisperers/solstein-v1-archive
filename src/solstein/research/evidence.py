from urllib.parse import urlparse

from solstein.domain.models import Company

REQUIRED_METRICS = [
    "revenue",
    "growth_rate",
    "employees",
    "profit_margin",
    "funding",
    "valuation",
]


def _domains(links: list[str]) -> list[str]:
    out: list[str] = []
    for link in links:
        try:
            host = urlparse(link).netloc.lower().strip()
        except Exception:
            host = ""
        if host and host not in out:
            out.append(host)
    return out


def evaluate_company_evidence(company: Company) -> dict[str, object]:
    source_links = company.source_links or []
    metric_sources = company.metric_sources or {}
    metric_justifications = company.metric_justifications or {}

    metric_with_sources = 0
    metric_with_justification = 0
    unsupported_metrics = 0
    ticker_backed_metrics = 0
    missing_source_metrics: list[str] = []
    justified_only_metrics: list[str] = []

    for metric in REQUIRED_METRICS:
        sources = metric_sources.get(metric, [])
        justification = str(metric_justifications.get(metric, "")).strip()

        if sources:
            metric_with_sources += 1
            if any("finance.yahoo.com/quote" in src for src in sources):
                ticker_backed_metrics += 1
        if justification:
            metric_with_justification += 1
            if not sources:
                justified_only_metrics.append(metric)
        if not sources and not justification:
            unsupported_metrics += 1
            missing_source_metrics.append(metric)

    total_required = len(REQUIRED_METRICS)
    metric_source_coverage = metric_with_sources / total_required
    metric_explainability = (metric_with_sources + metric_with_justification) / total_required
    domain_count = len(_domains(source_links))
    source_count = len(source_links)

    source_count_score = min(1.0, source_count / 6)
    domain_diversity_score = min(1.0, domain_count / 4)
    coverage_score = metric_source_coverage
    explainability_score = metric_explainability
    unsupported_penalty = unsupported_metrics / total_required

    readiness_score = (
        source_count_score * 0.20
        + domain_diversity_score * 0.20
        + coverage_score * 0.35
        + explainability_score * 0.25
    ) * 100
    readiness_score -= unsupported_penalty * 40
    readiness_score = max(0.0, min(100.0, readiness_score))

    if readiness_score >= 85:
        readiness_level = "investment_ready"
    elif readiness_score >= 70:
        readiness_level = "decision_support_ready"
    elif readiness_score >= 50:
        readiness_level = "needs_more_evidence"
    else:
        readiness_level = "insufficient_evidence"

    return {
        "company_id": company.id,
        "company_name": company.name,
        "readiness_score": round(readiness_score, 2),
        "readiness_level": readiness_level,
        "source_count": source_count,
        "source_domain_count": domain_count,
        "metric_source_coverage": round(metric_source_coverage, 3),
        "metric_explainability": round(metric_explainability, 3),
        "ticker_backed_metrics": ticker_backed_metrics,
        "unsupported_metrics": unsupported_metrics,
        "missing_source_metrics": missing_source_metrics,
        "justified_only_metrics": justified_only_metrics,
    }


def evaluate_market_evidence(companies: list[Company]) -> dict[str, object]:
    reports = [evaluate_company_evidence(company) for company in companies]
    if not reports:
        return {
            "company_reports": [],
            "average_readiness_score": 0.0,
            "investment_ready_count": 0,
            "decision_support_ready_count": 0,
            "needs_more_evidence_count": 0,
            "insufficient_evidence_count": 0,
        }

    readiness_values: list[float] = []
    for report in reports:
        value = report.get("readiness_score")
        if isinstance(value, float):
            readiness_values.append(value)
        elif isinstance(value, int):
            readiness_values.append(value * 1.0)
        else:
            readiness_values.append(0.0)
    avg_score = sum(readiness_values) / len(readiness_values)
    levels = [str(r["readiness_level"]) for r in reports]
    return {
        "company_reports": reports,
        "average_readiness_score": round(avg_score, 2),
        "investment_ready_count": sum(1 for level in levels if level == "investment_ready"),
        "decision_support_ready_count": sum(
            1 for level in levels if level == "decision_support_ready"
        ),
        "needs_more_evidence_count": sum(
            1 for level in levels if level == "needs_more_evidence"
        ),
        "insufficient_evidence_count": sum(
            1 for level in levels if level == "insufficient_evidence"
        ),
    }
