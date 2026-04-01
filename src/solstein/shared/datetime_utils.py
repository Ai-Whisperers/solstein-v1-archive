"""Canonical UTC datetime utilities with zero application-layer imports.

STORY-120: Enforces UTC timezone policy across all modules.

Usage:
    from solstein.shared.datetime_utils import utc_now, to_utc, parse_iso_to_utc

Rules:
    - All datetime objects must be timezone-aware UTC
    - Never use datetime.now() without tz=timezone.utc
    - Never use datetime.utcnow() (deprecated)
    - Convert external datetimes to UTC at ingestion boundaries
"""

from __future__ import annotations

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return the current UTC datetime (timezone-aware).

    Use instead of ``datetime.now()`` or ``datetime.utcnow()``.
    """
    return datetime.now(tz=timezone.utc)


def to_utc(dt: datetime) -> datetime:
    """Convert a datetime to UTC.

    If the datetime is naive (no tzinfo), assume it is already UTC
    and attach the UTC timezone. If it has a timezone, convert to UTC.

    Args:
        dt: A datetime object (naive or aware).

    Returns:
        A timezone-aware UTC datetime.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def parse_iso_to_utc(iso_string: str) -> datetime:
    """Parse an ISO 8601 string and return a UTC-aware datetime.

    Handles both timezone-aware and naive ISO strings. Naive strings
    are assumed to be UTC.

    Args:
        iso_string: An ISO 8601 formatted datetime string.

    Returns:
        A timezone-aware UTC datetime.

    Raises:
        ValueError: If the string cannot be parsed.
    """
    dt = datetime.fromisoformat(iso_string)
    return to_utc(dt)
