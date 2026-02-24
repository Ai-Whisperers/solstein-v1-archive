from typing import Any, cast

from solstein.domain.models import Company

NUMERIC_METRICS = {
    "revenue",
    "growth_rate",
    "employees",
    "profit_margin",
    "funding",
    "valuation",
}


def _as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def detect_company_contradictions(
    company: Company,
    numeric_divergence_threshold: float = 0.20,
) -> list[dict[str, Any]]:
    contradictions: list[dict[str, Any]] = []
    observations = company.metric_observations or {}

    for metric, rows in observations.items():
        if not isinstance(rows, list) or len(rows) < 2:
            continue

        values = [_as_float(r.get("value")) for r in rows if isinstance(r, dict)]
        values = cast(list[float], [v for v in values if v is not None])
        if len(values) < 2:
            continue

        if metric in NUMERIC_METRICS:
            max_val = max(values)
            min_val = min(values)
            if min_val == 0:
                divergence = 1.0 if max_val != 0 else 0.0
            else:
                divergence = abs(max_val - min_val) / abs(min_val)

            if divergence >= numeric_divergence_threshold:
                contradictions.append(
                    {
                        "metric": metric,
                        "type": "numeric_divergence",
                        "divergence": round(divergence, 4),
                        "threshold": numeric_divergence_threshold,
                        "observed_values": values,
                    }
                )
        else:
            distinct = list(dict.fromkeys(str(v).strip().lower() for v in values))
            if len(distinct) > 1:
                contradictions.append(
                    {
                        "metric": metric,
                        "type": "categorical_conflict",
                        "observed_values": distinct,
                    }
                )

    return contradictions


def detect_market_contradictions(companies: list[Company]) -> dict[str, list[dict[str, Any]]]:
    report: dict[str, list[dict[str, Any]]] = {}
    for company in companies:
        found = detect_company_contradictions(company)
        if found:
            report[company.id] = found
    return report
