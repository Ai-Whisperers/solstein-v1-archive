"""Data normalization package for Solstein.

EPIC-021: Modularized from monolithic 505-line normalization.py file.
"""

from __future__ import annotations

# Errors
from .errors import NormalizationError

# Numbers
from .numbers import (
    is_valid_number,
    parse_decimal,
    parse_integer,
    parse_number,
)

# Strings and collections
from .strings import (
    clean_company_name,
    extract_domain_from_url,
    format_error_for_display,
    normalize_boolean,
    normalize_date,
    normalize_dict,
    normalize_list,
    normalize_string,
    truncate_for_log,
)

# Records
from .records import DataNormalizer

__all__ = [
    # Errors
    "NormalizationError",
    # Numbers
    "is_valid_number",
    "parse_decimal",
    "parse_integer",
    "parse_number",
    # Strings
    "clean_company_name",
    "extract_domain_from_url",
    "format_error_for_display",
    "normalize_boolean",
    "normalize_date",
    "normalize_dict",
    "normalize_list",
    "normalize_string",
    "truncate_for_log",
    # Records
    "DataNormalizer",
]
