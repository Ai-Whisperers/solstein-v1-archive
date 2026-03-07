"""Confidence level conversion utilities.

Extracted from loaders.py as part of EPIC-021 file splitting.
"""

from __future__ import annotations

from solstein.domain.models import ConfidenceLevel


def convert_confidence(confidence_str: str | None) -> ConfidenceLevel:
    """Convert string confidence to ConfidenceLevel enum."""
    if not confidence_str:
        return ConfidenceLevel.UNKNOWN

    confidence_str = confidence_str.lower()
    if "confirm" in confidence_str:
        return ConfidenceLevel.CONFIRMED
    elif "estimate" in confidence_str:
        return ConfidenceLevel.ESTIMATED
    else:
        return ConfidenceLevel.UNKNOWN
