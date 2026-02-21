"""Input validators for SolStein domain models."""

from pydantic import (
    BaseModel,
    field_validator,
    ValidationError as PydanticValidationError,
)
from typing import Any


class CompanyValidator(BaseModel):
    """Validator for company data."""

    name: str
    revenue: float | None = None
    employees: int | None = None
    growth_rate: float | None = None
    valuation: float | None = None

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Company name cannot be empty")
        return v.strip()

    @field_validator("revenue")
    @classmethod
    def revenue_must_be_positive(cls, v: float | None) -> float | None:
        if v is not None and v < 0:
            raise ValueError("Revenue must be positive")
        return v

    @field_validator("employees")
    @classmethod
    def employees_must_be_positive(cls, v: int | None) -> int | None:
        if v is not None and v < 0:
            raise ValueError("Employees must be positive")
        return v

    @field_validator("growth_rate")
    @classmethod
    def growth_rate_bounds(cls, v: float | None) -> float | None:
        if v is not None and (v < -100 or v > 1000):
            raise ValueError("Growth rate must be between -100% and 1000%")
        return v


def validate_company_data(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate company data and return (is_valid, errors)."""
    errors = []
    try:
        CompanyValidator(**data)
        return True, []
    except PydanticValidationError as e:
        for error in e.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            errors.append(f"{field}: {error['msg']}")
        return False, errors


class ScoringInputValidator(BaseModel):
    """Validator for scoring input data."""

    revenue: float | None = None
    revenue_cagr: float | None = None
    employees: int | None = None
    employee_cagr: float | None = None
    profit_margin: float | None = None

    @field_validator("revenue_cagr", "employee_cagr")
    @classmethod
    def cagr_must_be_reasonable(cls, v: float | None) -> float | None:
        if v is not None and (v < -50 or v > 200):
            raise ValueError("CAGR must be between -50% and 200%")
        return v

    @field_validator("profit_margin")
    @classmethod
    def profit_margin_bounds(cls, v: float | None) -> float | None:
        if v is not None and (v < -100 or v > 100):
            raise ValueError("Profit margin must be between -100% and 100%")
        return v
