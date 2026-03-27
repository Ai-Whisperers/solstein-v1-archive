"""Record normalization for Solstein."""

from __future__ import annotations

from typing import Any

from .errors import NormalizationError
from .numbers import parse_decimal, parse_integer, parse_number
from .strings import (
    extract_domain_from_url,
    normalize_boolean,
    normalize_date,
    normalize_list,
    normalize_string,
)


class DataNormalizer:
    """Normalizes raw data records to standard format."""

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
        """
        Normalize a raw data record to standard format.

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
