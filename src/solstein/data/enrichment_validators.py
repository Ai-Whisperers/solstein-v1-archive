"""
Phase 3: Data Validation Module

Comprehensive validation for all enrichment data to prevent invalid data from entering the system.
Covers revenue, growth rate, employees, profit margin, and general data validation.
"""

import math
from datetime import datetime, timezone
from typing import Any

# Revenue Validation (Items 62-64)


def validate_revenue(revenue: Any, existing_revenue: float | None = None) -> tuple[bool, str | None]:
    """Validate revenue value.

    Args:
        revenue: Revenue value to validate
        existing_revenue: Existing revenue for comparison (optional)

    Returns:
        (is_valid, error_message)
    """
    # Check if valid number
    if not isinstance(revenue, (int, float)):
        return False, f"Revenue must be numeric, got {type(revenue).__name__}"

    if math.isnan(revenue) or math.isinf(revenue):
        return False, "Revenue cannot be NaN or Infinity"

    # Check minimum (Item 62)
    if revenue <= 0:
        return False, f"Revenue must be positive, got {revenue}"

    # Check maximum (Item 63)
    if revenue >= 1e15:  # 1 quadrillion
        return False, f"Revenue exceeds maximum (1 quadrillion), got {revenue}"

    # Check against existing (Item 64)
    if existing_revenue is not None and existing_revenue > 0:
        ratio = revenue / existing_revenue
        if ratio > 10 or ratio < 0.1:
            return False, f"Revenue differs by >10x from existing ({revenue} vs {existing_revenue})"

    return True, None


# Growth Rate Validation (Items 65-66)


def validate_growth_rate(growth_rate: Any, company_age_years: int | None = None) -> tuple[bool, str | None]:
    """Validate growth rate value.

    Args:
        growth_rate: Growth rate (as decimal, e.g., 0.25 for 25%)
        company_age_years: Company age in years (optional, for reasonableness check)

    Returns:
        (is_valid, error_message)
    """
    # Check if valid number
    if not isinstance(growth_rate, (int, float)):
        return False, f"Growth rate must be numeric, got {type(growth_rate).__name__}"

    if math.isnan(growth_rate) or math.isinf(growth_rate):
        return False, "Growth rate cannot be NaN or Infinity"

    # Check bounds (Item 65)
    if growth_rate < -0.5 or growth_rate > 2.0:
        return False, f"Growth rate must be between -50% and 200%, got {growth_rate * 100}%"

    # Check reasonableness vs company age (Item 66)
    if company_age_years is not None:
        if company_age_years > 20 and growth_rate > 1.0:
            # Mature companies shouldn't have >100% growth
            return False, f"Growth rate {growth_rate * 100}% unrealistic for {company_age_years}-year-old company"

    return True, None


# Employee Count Validation (Items 67-69)


def validate_employee_count(employees: Any) -> tuple[bool, str | None]:
    """Validate employee count value.

    Args:
        employees: Employee count (int or string like "10-50")

    Returns:
        (is_valid, error_message)
    """
    # Handle string ranges (Item 69)
    if isinstance(employees, str):
        if "-" in employees:
            try:
                parts = employees.split("-")
                if len(parts) == 2:
                    low = int(parts[0].strip())
                    high = int(parts[1].strip())
                    midpoint = (low + high) // 2
                    return validate_employee_count(midpoint)
            except (ValueError, IndexError):
                return False, f"Cannot parse employee range: {employees}"
        else:
            try:
                employees = int(employees)
            except ValueError:
                return False, f"Employee count must be numeric or range, got {employees}"

    # Check if valid number
    if not isinstance(employees, int):
        return False, f"Employee count must be integer, got {type(employees).__name__}"

    # Check minimum (Item 67)
    if employees < 1:
        return False, f"Employee count must be >= 1, got {employees}"

    # Check maximum (Item 68)
    if employees > 500_000:
        return False, f"Employee count exceeds maximum (500k), got {employees}"

    return True, None


# Profit Margin Validation (Items 70-71)


def validate_profit_margin(margin: Any, industry: str | None = None) -> tuple[bool, str | None]:
    """Validate profit margin value.

    Args:
        margin: Profit margin (as decimal, e.g., 0.25 for 25%)
        industry: Industry type (optional, for reasonableness check)

    Returns:
        (is_valid, error_message)
    """
    # Check if valid number
    if not isinstance(margin, (int, float)):
        return False, f"Profit margin must be numeric, got {type(margin).__name__}"

    if math.isnan(margin) or math.isinf(margin):
        return False, "Profit margin cannot be NaN or Infinity"

    # Check bounds (Item 70)
    if margin < -1.0 or margin > 0.95:
        return False, f"Profit margin must be between -100% and 95%, got {margin * 100}%"

    # Check reasonableness vs industry (Item 71)
    if industry and industry.lower() in ["retail", "grocery", "food"]:
        if margin > 0.15:
            return False, f"Profit margin {margin * 100}% unrealistic for {industry} industry"

    return True, None


# General Data Validation (Items 72-86)


def validate_required_keys(data: dict, required_keys: list[str]) -> tuple[bool, str | None]:
    """Validate that dict has required keys (Item 72).

    Args:
        data: Dictionary to validate
        required_keys: List of required keys

    Returns:
        (is_valid, error_message)
    """
    if not isinstance(data, dict):
        return False, f"Data must be dict, got {type(data).__name__}"

    missing = [k for k in required_keys if k not in data]
    if missing:
        return False, f"Missing required keys: {missing}"

    return True, None


def validate_field_types(data: dict, type_map: dict[str, type]) -> tuple[bool, str | None]:
    """Validate field types (Item 73).

    Args:
        data: Dictionary to validate
        type_map: Dict of field_name -> expected_type

    Returns:
        (is_valid, error_message)
    """
    for field, expected_type in type_map.items():
        if field in data and data[field] is not None:
            if not isinstance(data[field], expected_type):
                return False, f"Field {field} must be {expected_type.__name__}, got {type(data[field]).__name__}"

    return True, None


def validate_no_nan_inf(value: Any, field_name: str = "value") -> tuple[bool, str | None]:
    """Validate value is not NaN or Infinity (Item 74).

    Args:
        value: Value to validate
        field_name: Name of field (for error message)

    Returns:
        (is_valid, error_message)
    """
    if isinstance(value, float):
        if math.isnan(value):
            return False, f"{field_name} cannot be NaN"
        if math.isinf(value):
            return False, f"{field_name} cannot be Infinity"

    return True, None


def validate_enum_value(value: Any, valid_values: list[str], field_name: str = "value") -> tuple[bool, str | None]:
    """Validate value is in enum (Item 75).

    Args:
        value: Value to validate
        valid_values: List of valid values
        field_name: Name of field (for error message)

    Returns:
        (is_valid, error_message)
    """
    if value not in valid_values:
        return False, f"{field_name} must be one of {valid_values}, got {value}"

    return True, None


def validate_object_not_none(obj: Any, field_name: str = "object") -> tuple[bool, str | None]:
    """Validate object is not None (Item 76).

    Args:
        obj: Object to validate
        field_name: Name of field (for error message)

    Returns:
        (is_valid, error_message)
    """
    if obj is None:
        return False, f"{field_name} cannot be None"

    return True, None


def validate_no_duplicates(items: list[str], field_name: str = "items") -> tuple[bool, str | None]:
    """Validate list has no duplicates (Item 77).

    Args:
        items: List to validate
        field_name: Name of field (for error message)

    Returns:
        (is_valid, error_message)
    """
    if len(items) != len(set(items)):
        duplicates = [item for item in items if items.count(item) > 1]
        return False, f"{field_name} contains duplicates: {set(duplicates)}"

    return True, None


def validate_datetime_values(timestamps: dict[str, Any], field_name: str = "timestamps") -> tuple[bool, str | None]:
    """Validate all values in dict are datetime (Item 78).

    Args:
        timestamps: Dict to validate
        field_name: Name of field (for error message)

    Returns:
        (is_valid, error_message)
    """
    for key, value in timestamps.items():
        if not isinstance(value, datetime):
            return False, f"{field_name}[{key}] must be datetime, got {type(value).__name__}"

    return True, None


def validate_data_freshness(filing_date: datetime | None, max_age_months: int = 18) -> tuple[bool, str | None]:
    """Validate data is not too old (Items 85-86).

    Args:
        filing_date: Date of filing/data
        max_age_months: Maximum age in months (default 18)

    Returns:
        (is_valid, error_message)
    """
    if filing_date is None:
        return False, "Filing date cannot be None"

    age_days = (datetime.now(timezone.utc) - filing_date).days
    max_age_days = max_age_months * 30

    if age_days > max_age_days:
        return False, f"Data is {age_days} days old (max {max_age_days})"

    return True, None


def validate_cross_field_consistency(revenue: float | None, employees: int | None) -> tuple[bool, str | None]:
    """Validate cross-field consistency (Item 81).

    Args:
        revenue: Revenue value
        employees: Employee count

    Returns:
        (is_valid, error_message)
    """
    if revenue is not None and employees is not None and employees > 0:
        revenue_per_employee = revenue / employees

        # Sanity check: revenue per employee should be reasonable
        # Typical range: $50k - $5M per employee
        if revenue_per_employee < 50_000 or revenue_per_employee > 5_000_000:
            return False, f"Revenue per employee {revenue_per_employee} is unrealistic"

    return True, None


def validate_against_existing_data(
    new_value: Any, existing_value: Any, max_ratio: float = 10.0
) -> tuple[bool, str | None]:
    """Validate new data against existing (Item 82).

    Args:
        new_value: New value from API
        existing_value: Existing value in system
        max_ratio: Maximum ratio difference allowed

    Returns:
        (is_valid, error_message)
    """
    if existing_value is None or existing_value == 0:
        return True, None

    if new_value is None or new_value == 0:
        return False, "New value cannot be None or zero"

    ratio = abs(new_value / existing_value)
    if ratio > max_ratio or ratio < (1 / max_ratio):
        return False, f"New value differs by {ratio:.1f}x from existing"

    return True, None


def validate_source_format(source: str, valid_sources: list[str]) -> tuple[bool, str | None]:
    """Validate data source format (Item 83).

    Args:
        source: Source name
        valid_sources: List of valid sources

    Returns:
        (is_valid, error_message)
    """
    if source not in valid_sources:
        return False, f"Source must be one of {valid_sources}, got {source}"

    return True, None


def validate_enrichment_required(existing_data: dict[str, Any]) -> tuple[bool, str | None]:
    """Validate enrichment is actually needed (Item 84).

    Args:
        existing_data: Existing company data

    Returns:
        (is_valid, error_message)
    """
    # Check if data is already complete
    required_fields = ["revenue", "employees", "growth_rate", "profit_margin"]
    filled_fields = [f for f in required_fields if existing_data.get(f) is not None]

    if len(filled_fields) == len(required_fields):
        return False, "All required fields already filled, enrichment not needed"

    return True, None
