"""Confidence-Based Weighting for Scoring Components.

EPIC-021: Refactored to use core.scoring_utils to avoid module boundary violations.
Data layer can now import from core.scoring_utils instead of analytics.
"""

from solstein.core.scoring_utils import (
    confidence_level_to_weight,
    populate_signal_confidences,
)
from solstein.domain.models import Company


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
    if not company.signal_confidences:
        return 0.3  # Default to unknown

    weights = list(company.signal_confidences.values())
    return sum(weights) / len(weights) if weights else 0.3


# Re-export for backward compatibility
__all__ = [
    "confidence_level_to_weight",
    "populate_signal_confidences",
    "get_confidence_summary",
    "has_high_confidence_data",
    "get_average_confidence",
]
