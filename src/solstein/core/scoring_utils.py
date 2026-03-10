"""Scoring utilities for data layer.

This module provides scoring-related utilities that can be used by the data layer
without creating circular dependencies with the analytics layer.

EPIC-021: Module boundary violation fix - moved from analytics to core.
"""

from typing import Any, cast

from solstein.domain.models import Company, ConfidenceLevel


def confidence_level_to_weight(confidence: ConfidenceLevel) -> float:
    """Convert ConfidenceLevel enum to numeric weight.

    Args:
        confidence: ConfidenceLevel enum value

    Returns:
        Numeric weight: 1.0 (confirmed), 0.7 (estimated), 0.3 (unknown)
    """
    if confidence == ConfidenceLevel.CONFIRMED:
        return 1.0
    elif confidence == ConfidenceLevel.ESTIMATED:
        return 0.7
    elif confidence == ConfidenceLevel.UNKNOWN:
        return 0.3
    else:
        return 0.3  # Default to unknown


def populate_signal_confidences(company: Company) -> Company:
    """Populate signal_confidences dict from financial metric confidence levels.

    This function extracts confidence levels from each financial metric and
    converts them to numeric weights for use in scoring component weighting.

    Args:
        company: Company object with financial metrics

    Returns:
        Company object with populated signal_confidences dict
    """
    if not company.financials:
        return company

    # Map financial metrics to signal names
    _COMPONENT_SIGNAL_MAP: dict[str, list[str]] = {
        "Revenue Growth": ["growth_rate"],
        "Employee Efficiency": ["revenue", "employees", "revenue_level", "company_size"],
        "Funding Momentum": ["funding", "funding_raised"],
        "Profitability Profile": ["profitability", "profit_margin"],
        "Revenue Scale": ["revenue", "revenue_level"],
        "Profitability Health": ["profitability", "profit_margin"],
        "Operating Efficiency": ["revenue", "employees", "revenue_level", "company_size"],
        "Funding Cushion": ["funding", "funding_raised", "revenue", "revenue_level"],
        "Market Tier": ["company_size", "employees", "valuation"],
        "AI Maturity": ["ai_maturity", "ai_score"],
        "SaaS Maturity": [],
        "Geographic Footprint": [],
        "Stack Diversity": [],
    }

    raw_signal_confidences = cast(dict[str, Any], company.signal_confidences or {})

    # Extract confidence levels from financial metrics
    financials = company.financials

    # Map each financial metric confidence to signal confidences
    signal_confidences: dict[str, float] = {
        str(key): float(value) for key, value in raw_signal_confidences.items() if isinstance(value, (int, float))
    }
    company.signal_confidences = signal_confidences

    def set_if_missing(key: str, value: float) -> None:
        if key not in signal_confidences:
            signal_confidences[key] = value

    if hasattr(financials, "growth_confidence") and financials.growth_confidence:
        set_if_missing("growth_rate", confidence_level_to_weight(financials.growth_confidence))

    if hasattr(financials, "revenue_confidence") and financials.revenue_confidence:
        set_if_missing("revenue_level", confidence_level_to_weight(financials.revenue_confidence))
        set_if_missing("revenue", confidence_level_to_weight(financials.revenue_confidence))

    if hasattr(financials, "funding_confidence") and financials.funding_confidence:
        set_if_missing("funding", confidence_level_to_weight(financials.funding_confidence))
        set_if_missing("funding_raised", confidence_level_to_weight(financials.funding_confidence))

    if hasattr(financials, "margin_confidence") and financials.margin_confidence:
        set_if_missing("profitability", confidence_level_to_weight(financials.margin_confidence))
        set_if_missing("profit_margin", confidence_level_to_weight(financials.margin_confidence))

    if hasattr(financials, "employees_confidence") and financials.employees_confidence:
        set_if_missing("company_size", confidence_level_to_weight(financials.employees_confidence))
        set_if_missing("employees", confidence_level_to_weight(financials.employees_confidence))

    if hasattr(financials, "ai_maturity") and financials.ai_maturity:
        set_if_missing("ai_maturity", 0.7)  # Default to estimated

    return company
