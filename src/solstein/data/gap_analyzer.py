from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class GapStatus(StrEnum):
    MISSING = "missing"
    LOW_CONFIDENCE = "low_confidence"
    PROVENANCE_INVALID = "provenance_invalid"
    READY = "ready"


REQUIRED_FINANCIAL_FIELDS = (
    "revenue",
    "employees",
    "growth_rate",
    "profit_margin",
)

ZERO_ALLOWED_FIELDS = {
    "growth_rate",
    "profit_margin",
    "revenue",   # pre-revenue companies legitimately have revenue=0.0
    "employees",  # 0 employees is technically valid (solo founder, etc.)
}


@dataclass(frozen=True)
class FieldGap:
    field: str
    status: GapStatus
    confidence: float | None
    reason: str


def _has_valid_provenance(company: Any, field_name: str) -> bool:
    """A field has valid provenance if it has any non-empty source entry.

    Previously required HTTP/HTTPS/URN URIs, which always failed for JSON-loaded
    companies. Now accepts any non-empty string source identifier (API names,
    file identifiers, URL-based sources all qualify).
    """
    metric_sources = getattr(company, "metric_sources", {}) or {}
    sources = metric_sources.get(field_name, [])
    return any(isinstance(s, str) and s.strip() for s in sources)


def _extract_confidence(company: Any, field_name: str) -> float | None:
    financials = getattr(company, "financials", None)
    if financials is None:
        return None

    mapping = {
        "revenue": "revenue_confidence",
        "employees": "employees_confidence",
        "growth_rate": "growth_confidence",
        "profit_margin": "margin_confidence",
    }
    confidence_key = mapping.get(field_name)
    if confidence_key is None:
        return None

    confidence_value = getattr(financials, confidence_key, None)
    if confidence_value is None:
        return None
    try:
        return float(confidence_value)
    except (TypeError, ValueError):
        confidence_name = str(confidence_value).lower()
        if "confirmed" in confidence_name:
            return 1.0
        if "estimated" in confidence_name:
            return 0.6
        if "unknown" in confidence_name:
            return 0.0
        return None


def _is_missing_value(field_name: str, value: float | int | None) -> bool:
    if value is None:
        return True
    if value == 0 and field_name not in ZERO_ALLOWED_FIELDS:
        return True
    return False


def analyze_company_gaps(company: Any, min_confidence: float = 0.5) -> dict[str, Any]:
    field_states: list[dict[str, Any]] = []

    financials = getattr(company, "financials", None)
    for field_name in REQUIRED_FINANCIAL_FIELDS:
        value = getattr(financials, field_name, None) if financials else None
        confidence = _extract_confidence(company, field_name)

        if _is_missing_value(field_name, value):
            field_states.append(
                FieldGap(
                    field=field_name,
                    status=GapStatus.MISSING,
                    confidence=confidence,
                    reason=f"field is null or zero (zero allowed for: {', '.join(sorted(ZERO_ALLOWED_FIELDS))})",
                ).__dict__
            )
            continue

        if confidence is not None and confidence < min_confidence:
            field_states.append(
                FieldGap(
                    field=field_name,
                    status=GapStatus.LOW_CONFIDENCE,
                    confidence=confidence,
                    reason=f"confidence below threshold {min_confidence}",
                ).__dict__
            )
            continue

        if not _has_valid_provenance(company, field_name):
            field_states.append(
                FieldGap(
                    field=field_name,
                    status=GapStatus.PROVENANCE_INVALID,
                    confidence=confidence,
                    reason="missing canonical source uri",
                ).__dict__
            )
            continue

        field_states.append(
            FieldGap(
                field=field_name,
                status=GapStatus.READY,
                confidence=confidence,
                reason="field passed completeness/provenance checks",
            ).__dict__
        )

    unresolved = [item for item in field_states if item["status"] != GapStatus.READY]
    return {
        "company_name": getattr(company, "name", "unknown"),
        "field_states": field_states,
        "unresolved_count": len(unresolved),
        "is_ready": len(unresolved) == 0,
    }
