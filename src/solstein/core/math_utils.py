"""Safe arithmetic utilities for scoring and analytics.

STORY-131: Null safety guards for division operations.

Provides safe_div() for all division operations where the denominator
may be zero, None, or NaN. All scoring paths must use safe_div instead
of raw division on potentially unsafe values.
"""

from __future__ import annotations

import math
from typing import Any

from loguru import logger


def safe_div(
    numerator: float | int | None,
    denominator: float | int | None,
    *,
    default: float | None = None,
    label: str = "",
) -> float | None:
    """Safely divide two numbers, returning default when division is unsafe.

    Use this instead of raw ``/`` whenever the denominator may be zero, None,
    or NaN.  The function logs a warning (at DEBUG level) when the default is
    returned so callers can audit which calculations fell back.

    Args:
        numerator: The dividend.  If None, returns *default*.
        denominator: The divisor.  If zero, None, or NaN, returns *default*.
        default: Value to return when division is unsafe.  ``None`` signals
            "could not be calculated" (distinct from a calculated zero).
        label: Human-readable label for log messages, e.g. ``"revenue_per_employee"``.

    Returns:
        The quotient, or *default* if the operation is unsafe.

    Examples:
        >>> safe_div(100, 10)
        10.0
        >>> safe_div(100, 0, default=0.0, label="margin")
        0.0
        >>> safe_div(None, 10, label="growth")  # numerator missing
        >>> safe_div(100, None, label="ratio")  # denominator missing
    """
    if numerator is None:
        if label:
            logger.debug(
                "[safe_div] Numerator is None, returning default",
                label=label,
                default=default,
            )
        return default

    if denominator is None:
        if label:
            logger.debug(
                "[safe_div] Denominator is None, returning default",
                label=label,
                default=default,
            )
        return default

    # Guard against NaN denominators (from upstream float parsing)
    if isinstance(denominator, float) and math.isnan(denominator):
        if label:
            logger.debug(
                "[safe_div] Denominator is NaN, returning default",
                label=label,
                default=default,
            )
        return default

    if denominator == 0:
        if label:
            logger.debug(
                "[safe_div] Denominator is zero, returning default",
                label=label,
                default=default,
            )
        return default

    return float(numerator) / float(denominator)


def safe_pct(
    part: float | int | None,
    whole: float | int | None,
    *,
    default: float | None = None,
    label: str = "",
) -> float | None:
    """Compute a percentage safely: ``(part / whole) * 100``.

    Convenience wrapper around :func:`safe_div` for percentage calculations
    common in scoring (market share, concentration ratios, margins).
    """
    ratio = safe_div(part, whole, default=None, label=label)
    if ratio is None:
        return default
    return ratio * 100.0


def safe_avg(
    values: list[float | int | None] | Any,
    *,
    default: float | None = None,
    label: str = "",
) -> float | None:
    """Compute the average of a list, ignoring None values.

    Returns *default* if the list is empty or all values are None.
    """
    if not values:
        if label:
            logger.debug("[safe_avg] Empty list, returning default", label=label)
        return default

    clean = [v for v in values if v is not None]
    if not clean:
        if label:
            logger.debug("[safe_avg] All values None, returning default", label=label)
        return default

    return sum(clean) / len(clean)
