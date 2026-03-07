"""Scoring utilities for data layer.

This module provides scoring-related utilities that can be used by the data layer
without creating circular dependencies with the analytics layer.

EPIC-021: Module boundary violation fix - moved from analytics to core.
"""

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
        "Employee Efficiency": ["revenue_level", "company_size"],
        "Funding Momentum": ["funding"],
        "Profitability Profile": ["profitability"],
        "Revenue Scale": ["revenue_level"],
        "Profitability Health": ["profitability"],
        "Operating Efficiency": ["revenue_level", "company_size"],
        "Funding Cushion": ["funding", "revenue_level"],
        "Market Tier": ["company_size", "valuation"],
        "AI Maturity": ["ai_maturity"],
        "SaaS Maturity": [],
        "Geographic Footprint": [],
        "Stack Diversity": [],
    }

    # Initialize signal_confidences if not present
    if not hasattr(company, "signal_confidences") or company.signal_confidences is None:
        company.signal_confidences = {}

    # Extract confidence levels from financial metrics
    financials = company.financials

    # Map each financial metric confidence to signal confidences
    if hasattr(financials, "growth_confidence") and financials.growth_confidence:
        company.signal_confidences["growth_rate"] = confidence_level_to_weight(financials.growth_confidence)

    if hasattr(financials, "revenue_confidence") and financials.revenue_confidence:
        company.signal_confidences["revenue_level"] = confidence_level_to_weight(financials.revenue_confidence)

    if hasattr(financials, "funding_confidence") and financials.funding_confidence:
        company.signal_confidences["funding"] = confidence_level_to_weight(financials.funding_confidence)

    if hasattr(financials, "margin_confidence") and financials.margin_confidence:
        company.signal_confidences["profitability"] = confidence_level_to_weight(financials.margin_confidence)

    if hasattr(financials, "employees_confidence") and financials.employees_confidence:
        company.signal_confidences["company_size"] = confidence_level_to_weight(financials.employees_confidence)

    if hasattr(financials, "ai_maturity") and financials.ai_maturity:
        company.signal_confidences["ai_maturity"] = 0.7  # Default to estimated

    return company
