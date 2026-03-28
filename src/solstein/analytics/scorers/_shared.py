from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from ...domain.models import ConfidenceLevel, FinancialMetric

if TYPE_CHECKING:
    from ...infrastructure.repositories import FactRepository


def confidence_to_level(confidence: float) -> ConfidenceLevel:
    if confidence >= 0.9:
        return ConfidenceLevel.CONFIRMED
    elif confidence >= 0.7:
        return ConfidenceLevel.ESTIMATED
    else:
        return ConfidenceLevel.UNKNOWN


# STORY-207: Data confidence calculation based on field availability
# Each missing critical field reduces confidence by this amount
_CONFIDENCE_REDUCTION_PER_FIELD = 0.15

# Critical fields for scoring — if these are None, confidence drops
_CRITICAL_SCORING_FIELDS = [
    ("revenue", "Revenue data"),
    ("growth_rate", "Growth rate data"),
    ("employees", "Employee count"),
    ("profit_margin", "Profit margin data"),
    ("funding_raised", "Funding data"),
]


def calculate_data_confidence(financials: FinancialMetric) -> tuple[float, list[str]]:
    """Calculate data confidence score based on field availability.

    Returns:
        Tuple of (confidence: 0.0-1.0, warnings: list of human-readable messages)
    """
    confidence = 1.0
    warnings: list[str] = []

    for field_name, description in _CRITICAL_SCORING_FIELDS:
        value = getattr(financials, field_name, None)
        if value is None:
            confidence -= _CONFIDENCE_REDUCTION_PER_FIELD
            warnings.append(f"{description} missing ({field_name}=None)")

    # Clamp to [0.0, 1.0]
    confidence = max(0.0, min(confidence, 1.0))

    return confidence, warnings


def merge_facts_into_financials(
    financials: FinancialMetric,
    fact_repo: FactRepository,
    company_id: str,
) -> FinancialMetric:
    try:
        facts_result = fact_repo.get_company_facts(company_id)
    except Exception:
        return financials

    if asyncio.iscoroutine(facts_result):
        return financials

    facts: list[Any] = list(facts_result)

    fact_map = {
        "annual_revenue": ("revenue", "revenue_confidence"),
        "revenue_growth_yoy": ("growth_rate", "growth_confidence"),
        "employee_count": ("employees", "employees_confidence"),
        "gross_margin": ("profit_margin", "margin_confidence"),
        "total_funding_raised": ("funding_raised", "funding_confidence"),
        "company_valuation": ("valuation", "valuation_confidence"),
    }

    for fact in facts:
        if fact.fact_type not in fact_map:
            continue

        metric_field, confidence_field = fact_map[fact.fact_type]

        if fact.value is not None:
            confidence_level = confidence_to_level(fact.confidence)
            setattr(financials, metric_field, fact.value)
            setattr(financials, confidence_field, confidence_level)

    return financials
