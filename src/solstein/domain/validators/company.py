"""Company field validators.

EPIC-022: Extracted from Company model for modularity.
"""

import re
from typing import Any

from pydantic import field_validator


class CompanyValidators:
    """Container for Company field validators.

    These validators are applied to Company model fields
    to ensure data integrity and consistency.
    """

    @staticmethod
    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Validate company ID format."""
        if not v:
            raise ValueError("Company ID cannot be empty")
        if len(v) < 3:
            raise ValueError("Company ID must be at least 3 characters")
        if " " in v:
            raise ValueError("Company ID cannot contain spaces")
        return v.strip()

    @staticmethod
    @field_validator("ai_score")
    @classmethod
    def validate_ai_score_value(cls, v: float | None) -> float | None:
        """Validate AI score is between 0 and 10."""
        if v is not None and (v < 0 or v > 10):
            raise ValueError("AI score must be between 0 and 10")
        return v

    @staticmethod
    @field_validator("saas_maturity")
    @classmethod
    def validate_saas_maturity(cls, v: int) -> int:
        """Validate SaaS maturity is between 1 and 5."""
        if v < 1 or v > 5:
            raise ValueError("SaaS maturity must be between 1 and 5")
        return v

    @staticmethod
    @field_validator("revenue_cagr_3yr", "revenue_cagr_5yr")
    @classmethod
    def validate_cagr(cls, v: float | None) -> float | None:
        """Validate CAGR is reasonable (-50% to +200%)."""
        if v is not None and (v < -0.5 or v > 2.0):
            raise ValueError("CAGR must be between -50% and +200%")
        return v

    @staticmethod
    @field_validator("growth_rate", "profit_margin", "recurring_revenue_pct")
    @classmethod
    def validate_percentage(cls, v: float | None) -> float | None:
        """Validate percentage fields are reasonable (-100% to +1000%)."""
        if v is not None and (v < -1.0 or v > 10.0):
            raise ValueError("Percentage must be between -100% and +1000%")
        return v

    @staticmethod
    @field_validator("employees", "open_positions", "founded_year")
    @classmethod
    def validate_positive_int(cls, v: int | None) -> int | None:
        """Validate positive integer fields."""
        if v is not None and v < 0:
            raise ValueError("Value must be non-negative")
        return v

    @staticmethod
    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, v: str | None) -> str | None:
        """Validate ticker symbol format."""
        if v is None:
            return None
        v = v.strip().upper()
        if not v:
            return None
        # Allow 1-5 uppercase letters, optionally with exchange suffix
        if not re.match(r"^[A-Z]{1,5}([.][A-Z]{1,4})?$", v):
            raise ValueError("Ticker must be 1-5 uppercase letters, optionally with exchange suffix")
        return v

    @staticmethod
    @field_validator("company_number")
    @classmethod
    def validate_company_number(cls, v: str | None) -> str | None:
        """Validate company registration number format."""
        if v is None:
            return None
        v = v.strip().upper()
        if not v:
            return None
        # Allow alphanumeric with common separators
        if not re.match(r"^[A-Z0-9\-]{5,20}$", v):
            raise ValueError("Company number must be 5-20 alphanumeric characters")
        return v

    @staticmethod
    @field_validator("isin")
    @classmethod
    def validate_isin(cls, v: str | None) -> str | None:
        """Validate ISIN format."""
        if v is None:
            return None
        v = v.strip().upper()
        if not v:
            return None
        # ISIN: 2 letters (country) + 9 alphanumeric + 1 check digit
        if not re.match(r"^[A-Z]{2}[A-Z0-9]{9}[0-9]$", v):
            raise ValueError("ISIN must be 12 characters: 2 letters + 9 alphanumeric + 1 digit")
        return v

    @staticmethod
    @field_validator("geography_code")
    @classmethod
    def validate_geography_code(cls, v: str | None) -> str | None:
        """Validate geography/region code."""
        if v is None:
            return None
        v = v.strip().upper()
        if not v:
            return None
        # Allow 2-letter country codes or region codes
        if not re.match(r"^[A-Z]{2,3}$", v):
            raise ValueError("Geography code must be 2-3 uppercase letters")
        return v
