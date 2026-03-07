"""String and data type normalization for Solstein."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from loguru import logger


def normalize_string(value: Any, default: str = "") -> str:
    """
    Normalize a string value.

    - Strips whitespace
    - Handles None
    - Converts non-strings to strings safely
    """
    if value is None:
        return default

    if isinstance(value, str):
        return value.strip() or default

    # Convert other types to string
    try:
        return str(value).strip() or default
    except Exception as e:
        logger.debug(f"Failed to convert value to string: {e}", value=value)
        return default


def normalize_boolean(value: Any, default: bool | None = None) -> bool | None:
    """
    Normalize a value to boolean.

    Handles:
    - True/False directly
    - "true", "yes", "1", "y" (case insensitive) -> True
    - "false", "no", "0", "n", "" (case insensitive) -> False
    """
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        lower = value.lower().strip()
        if lower in ("true", "yes", "1", "y", "on"):
            return True
        if lower in ("false", "no", "0", "n", "off", ""):
            return False
        return default

    if isinstance(value, (int, float)):
        return bool(value)

    return default


def normalize_list(value: Any, default: list[Any] | None = None) -> list[Any]:
    """
    Normalize a value to a list.

    - Lists are returned as-is
    - None returns default (or empty list)
    - Single values are wrapped in a list
    - Strings are treated as single values (not split)
    """
    if value is None:
        return default if default is not None else []

    if isinstance(value, list):
        return value

    if isinstance(value, (tuple, set)):
        return list(value)

    return [value]


def normalize_dict(value: Any, default: dict[str, Any] | None = None) -> dict[str, Any]:
    """Normalize a value to a dictionary."""
    if value is None:
        return default if default is not None else {}

    if isinstance(value, dict):
        return value

    return default if default is not None else {}


def normalize_date(value: Any) -> str | None:
    """
    Normalize a date value to ISO format string.

    Handles:
    - ISO format strings (returned as-is)
    - Various common date formats
    - datetime objects
    - None returns None
    """
    if value is None:
        return None

    # If already a string in ISO format, validate and return
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None

        # Basic ISO format validation (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
        iso_pattern = r"^\d{4}-\d{2}-\d{2}"
        if re.match(iso_pattern, value):
            return value

        # Try common formats
        formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y/%m/%d",
            "%m-%d-%Y",
            "%d-%m-%Y",
            "%b %d, %Y",
            "%B %d, %Y",
            "%d %b %Y",
            "%d %B %Y",
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(value, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue

        logger.debug("Failed to parse date", value=value)
        return None

    # Handle datetime objects
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d")  # type: ignore

    return None


def clean_company_name(name: str | None) -> str | None:
    """
    Clean and normalize a company name.

    - Strips whitespace
    - Removes common suffixes (Inc, LLC, Ltd, etc.)
    - Normalizes case
    """
    if not name:
        return None

    name = name.strip()
    if not name:
        return None

    # Common suffixes to optionally remove
    suffixes = [
        r"\s+Inc\.?$",
        r"\s+LLC\.?$",
        r"\s+Ltd\.?$",
        r"\s+Limited$",
        r"\s+Corp\.?$",
        r"\s+Corporation$",
        r"\s+Co\.?$",
        r"\s+Company$",
    ]

    cleaned = name
    for suffix in suffixes:
        cleaned = re.sub(suffix, "", cleaned, flags=re.IGNORECASE)

    return cleaned.strip() or name


def extract_domain_from_url(url: str | None) -> str | None:
    """Extract domain from a URL."""
    if not url:
        return None

    url = url.strip()
    if not url:
        return None

    # Remove protocol
    url = re.sub(r"^https?://", "", url, flags=re.IGNORECASE)
    url = re.sub(r"^www\.", "", url, flags=re.IGNORECASE)

    # Extract domain (everything before first /)
    match = re.match(r"([^/]+)", url)
    if match:
        domain = match.group(1).lower()
        # Remove port if present
        domain = domain.split(":")[0]
        return domain

    return None


def format_error_for_display(error: Exception, context: str = "") -> str:
    """Format an exception for user-friendly display."""
    error_type = type(error).__name__
    message = str(error) or "Unknown error"

    if context:
        return f"[{context}] {error_type}: {message}"
    return f"{error_type}: {message}"


def truncate_for_log(value: Any, max_length: int = 200) -> str:
    """Truncate a value for safe logging."""
    text = str(value)
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
