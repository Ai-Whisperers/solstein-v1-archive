"""Number normalization for Solstein."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from loguru import logger


def is_valid_number(value: Any) -> bool:
    """Check if a value is a valid number (int, float, or numeric string)."""
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return not (isinstance(value, float) and (value != value))  # NaN check
    if isinstance(value, str):
        cleaned = value.replace(",", "").replace("$", "").strip()
        if not cleaned:
            return False
        try:
            float(cleaned)
            return True
        except ValueError:
            return False
    return False


def parse_number(value: Any, default: float | None = None) -> float | None:
    """
    Parse a value into a float.

    Handles:
    - Integers and floats directly
    - Strings with commas, dollar signs, percentages
    - Scientific notation
    - None returns default
    """
    if value is None:
        return default

    if isinstance(value, (int, float)):
        if isinstance(value, float) and (value != value):  # NaN
            return default
        return float(value)

    if isinstance(value, str):
        # Remove common formatting characters
        cleaned = value.replace(",", "").replace("$", "").replace("%", "").strip()

        # Handle empty strings
        if not cleaned:
            return default

        # Handle parentheses for negative numbers: (123) -> -123
        if cleaned.startswith("(") and cleaned.endswith(")"):
            cleaned = "-" + cleaned[1:-1]

        try:
            return float(cleaned)
        except ValueError:
            logger.debug("Failed to parse number", value=value, cleaned=cleaned)
            return default

    return default


def parse_integer(value: Any, default: int | None = None) -> int | None:
    """Parse a value into an integer."""
    parsed = parse_number(value)
    if parsed is None:
        return default
    return int(parsed)


def parse_decimal(value: Any, default: Decimal | None = None) -> Decimal | None:
    """Parse a value into a Decimal for precise financial calculations."""
    if value is None:
        return default

    if isinstance(value, Decimal):
        return value

    if isinstance(value, (int, float)):
        try:
            return Decimal(str(value))
        except InvalidOperation:
            return default

    if isinstance(value, str):
        cleaned = value.replace(",", "").replace("$", "").replace("%", "").strip()
        if cleaned.startswith("(") and cleaned.endswith(")"):
            cleaned = "-" + cleaned[1:-1]
        try:
            return Decimal(cleaned)
        except InvalidOperation:
            return default

    return default
