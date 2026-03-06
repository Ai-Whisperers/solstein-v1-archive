"""Data normalization utilities.

E2: Extract normalization/parsing utilities from unified_loader.py
Provides safe, consistent data normalization for various input formats.
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Any

from loguru import logger


class NormalizationError(Exception):
    """Raised when data normalization fails."""

    pass


def is_valid_number(value: Any) -> bool:
    """Check if a value is a valid number (int, float, or numeric string).

    Args:
        value: Value to check

    Returns:
        True if the value represents a valid number
    """
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
    """Parse a value into a float.

    Handles:
    - Integers and floats directly
    - Strings with commas, dollar signs, percentages
    - Scientific notation
    - None returns default

    Args:
        value: Value to parse
        default: Default value if parsing fails

    Returns:
        Parsed float or default
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
    """Parse a value into an integer.

    Args:
        value: Value to parse
        default: Default value if parsing fails

    Returns:
        Parsed integer or default
    """
    parsed = parse_number(value)
    if parsed is None:
        return default
    return int(parsed)


def parse_decimal(value: Any, default: Decimal | None = None) -> Decimal | None:
    """Parse a value into a Decimal for precise financial calculations.

    Args:
        value: Value to parse
        default: Default value if parsing fails

    Returns:
        Parsed Decimal or default
    """
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


def normalize_string(value: Any, default: str = "") -> str:
    """Normalize a string value.

    - Strips whitespace
    - Handles None
    - Converts non-strings to strings safely

    Args:
        value: Value to normalize
        default: Default for None/empty

    Returns:
        Normalized string
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
    """Normalize a value to boolean.

    Handles:
    - True/False directly
    - "true", "yes", "1", "y" (case insensitive) -> True
    - "false", "no", "0", "n", "" (case insensitive) -> False

    Args:
        value: Value to normalize
        default: Default if cannot determine

    Returns:
        Normalized boolean or default
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
    """Normalize a value to a list.

    - Lists are returned as-is
    - None returns default (or empty list)
    - Single values are wrapped in a list
    - Strings are treated as single values (not split)

    Args:
        value: Value to normalize
        default: Default for None

    Returns:
        Normalized list
    """
    if value is None:
        return default if default is not None else []

    if isinstance(value, list):
        return value

    if isinstance(value, (tuple, set)):
        return list(value)

    return [value]


def normalize_dict(value: Any, default: dict[str, Any] | None = None) -> dict[str, Any]:
    """Normalize a value to a dictionary.

    Args:
        value: Value to normalize
        default: Default for None

    Returns:
        Normalized dict
    """
    if value is None:
        return default if default is not None else {}

    if isinstance(value, dict):
        return value

    return default if default is not None else {}


def normalize_date(value: Any) -> str | None:
    """Normalize a date value to ISO format string.

    Handles:
    - ISO format strings (returned as-is)
    - Various common date formats
    - datetime objects
    - None returns None

    Args:
        value: Date value to normalize

    Returns:
        ISO format date string or None
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
        from datetime import datetime

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
    """Clean and normalize a company name.

    - Strips whitespace
    - Removes common suffixes (Inc, LLC, Ltd, etc.)
    - Normalizes case

    Args:
        name: Raw company name

    Returns:
        Cleaned name or None
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
    """Extract domain from a URL.

    Args:
        url: URL string

    Returns:
        Domain or None
    """
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
    """Format an exception for user-friendly display.

    Args:
        error: The exception
        context: Additional context

    Returns:
        Formatted error string
    """
    error_type = type(error).__name__
    message = str(error) or "Unknown error"

    if context:
        return f"[{context}] {error_type}: {message}"
    return f"{error_type}: {message}"


def truncate_for_log(value: Any, max_length: int = 200) -> str:
    """Truncate a value for safe logging.

    Args:
        value: Value to truncate
        max_length: Maximum length

    Returns:
        Truncated string representation
    """
    text = str(value)
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


class DataNormalizer:
    """Normalizes raw data records to standard format.

    E2: Extracted from unified_loader.py
    """

    # Field mappings from various source formats to standard format
    FIELD_MAPPINGS: dict[str, list[str]] = {
        "name": ["name", "company_name", "organization", "org_name", "title"],
        "domain": ["domain", "website", "url", "homepage", "web"],
        "industry": ["industry", "sector", "category", "vertical"],
        "revenue": ["revenue", "annual_revenue", "total_revenue", "revenue_usd"],
        "employees": ["employees", "employee_count", "headcount", "team_size"],
        "founded_year": ["founded_year", "founded", "year_founded", "established"],
        "description": ["description", "about", "summary", "overview"],
        "location": ["location", "headquarters", "hq", "address"],
    }

    def __init__(self) -> None:
        self._reverse_mapping: dict[str, str] = {}
        for standard, variants in self.FIELD_MAPPINGS.items():
            for variant in variants:
                self._reverse_mapping[variant.lower()] = standard

    def normalize(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """Normalize a raw data record to standard format.

        Args:
            raw_data: Raw data from a source

        Returns:
            Normalized record with standard field names and types
        """
        if not isinstance(raw_data, dict):
            raise NormalizationError(f"Expected dict, got {type(raw_data).__name__}")

        normalized: dict[str, Any] = {}

        # Map fields to standard names
        for key, value in raw_data.items():
            standard_key = self._reverse_mapping.get(key.lower(), key.lower())

            # Apply type-specific normalization
            normalized[standard_key] = self._normalize_field(standard_key, value)

        # Ensure required fields exist
        normalized.setdefault("name", None)
        normalized.setdefault("domain", None)

        return normalized

    def _normalize_field(self, field_name: str, value: Any) -> Any:
        """Normalize a single field based on its name."""
        # Numeric fields
        if field_name in ("revenue", "valuation", "funding_total"):
            return parse_decimal(value)

        if field_name in ("employees", "founded_year"):
            return parse_integer(value)

        if field_name in ("growth_rate", "profit_margin", "market_share"):
            return parse_number(value)

        # String fields
        if field_name in ("name", "industry", "location", "description"):
            return normalize_string(value)

        if field_name == "domain":
            url = normalize_string(value)
            if url:
                # If it looks like a URL, extract domain
                if "." in url and " " not in url:
                    return extract_domain_from_url(url) or url
            return url

        # Date fields
        if field_name in ("founded_date", "last_funding_date"):
            return normalize_date(value)

        # Boolean fields
        if field_name in ("is_public", "is_acquired", "is_active"):
            return normalize_boolean(value)

        # List fields
        if field_name in ("competitors", "investors", "tags"):
            return normalize_list(value)

        # Default: return as-is
        return value
