"""
Task 8: Confidence-Based Weighting for Scoring Components

Converts ConfidenceLevel enums to numeric weights and populates signal_confidences
for use in scoring component weighting.

Confidence Mapping:
- CONFIRMED: 1.0 (full weight - data is verified/audited)
- ESTIMATED: 0.7 (reduced weight - data is estimated/inferred)
- UNKNOWN: 0.3 (minimal weight - data source is unknown)
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
    signal_confidences = {}

    # Revenue signal
    if company.financials.revenue is not None:
        signal_confidences["revenue_level"] = confidence_level_to_weight(company.financials.revenue_confidence)

    # Growth signal
    if company.financials.growth_rate is not None:
        signal_confidences["growth_rate"] = confidence_level_to_weight(company.financials.growth_confidence)

    # Employee signal (company size)
    if company.financials.employees is not None:
        signal_confidences["company_size"] = confidence_level_to_weight(company.financials.employees_confidence)

    # Profitability signal
    if company.financials.profit_margin is not None:
        signal_confidences["profitability"] = confidence_level_to_weight(company.financials.margin_confidence)

    # Funding signal
    if company.financials.funding_raised is not None:
        signal_confidences["funding"] = confidence_level_to_weight(company.financials.funding_confidence)

    # Valuation signal
    if company.financials.valuation is not None:
        signal_confidences["valuation"] = confidence_level_to_weight(company.financials.valuation_confidence)

    # Update company's signal_confidences
    company.signal_confidences = signal_confidences

    return company


def get_confidence_summary(company: Company) -> dict[str, float]:
    """Get a summary of confidence levels for a company.

    Args:
        company: Company object

    Returns:
        Dict with signal names and their confidence weights
    """
    return company.signal_confidences or {}


def has_high_confidence_data(company: Company, threshold: float = 0.8) -> bool:
    """Check if company has high-confidence data.

    Args:
        company: Company object
        threshold: Minimum confidence weight to consider "high" (default 0.8)

    Returns:
        True if any signal has confidence >= threshold
    """
    if not company.signal_confidences:
        return False

    return any(weight >= threshold for weight in company.signal_confidences.values())


def get_average_confidence(company: Company) -> float:
    """Get average confidence across all signals.

    Args:
        company: Company object

    Returns:
        Average confidence weight (0.0-1.0)
    """
    if not company.signal_confidences or not company.signal_confidences:
        return 0.3  # Default to unknown

    weights = list(company.signal_confidences.values())
    return sum(weights) / len(weights) if weights else 0.3
