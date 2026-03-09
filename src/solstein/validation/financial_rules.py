from __future__ import annotations

from dataclasses import dataclass


FINANCIAL_VALIDATION_RULES = {
    "revenue": {
        "min": 0.0,
        "max": 1e15,
        "growth_rate_max": 10.0,
        "required_fields": ["amount", "currency", "date"],
    },
    "valuation": {
        "min": 0.0,
        "max": 1e13,
        "revenue_multiple_max": 100.0,
    },
    "employee_count": {
        "min": 1,
        "max": 3_000_000,
        "growth_rate_max": 5.0,
    },
}


@dataclass(frozen=True)
class FinancialValidationIssue:
    field: str
    code: str
    message: str


def validate_financial_payload(payload: dict[str, object]) -> list[FinancialValidationIssue]:
    issues: list[FinancialValidationIssue] = []

    revenue = _as_float(payload.get("revenue"))
    valuation = _as_float(payload.get("valuation"))
    employee_count = _as_int(payload.get("employee_count"))
    growth_rate = _as_float(payload.get("growth_rate"))

    if revenue is not None:
        rules = FINANCIAL_VALIDATION_RULES["revenue"]
        if revenue < rules["min"] or revenue > rules["max"]:
            issues.append(
                FinancialValidationIssue(
                    field="revenue",
                    code="OUT_OF_RANGE",
                    message=f"Revenue {revenue} is out of supported range",
                )
            )
        if growth_rate is not None and abs(growth_rate) > rules["growth_rate_max"]:
            issues.append(
                FinancialValidationIssue(
                    field="growth_rate",
                    code="UNREALISTIC_GROWTH",
                    message=f"Growth rate {growth_rate} exceeds configured sanity threshold",
                )
            )

    if valuation is not None:
        rules = FINANCIAL_VALIDATION_RULES["valuation"]
        if valuation < rules["min"] or valuation > rules["max"]:
            issues.append(
                FinancialValidationIssue(
                    field="valuation",
                    code="OUT_OF_RANGE",
                    message=f"Valuation {valuation} is out of supported range",
                )
            )

        if revenue is not None and revenue > 0:
            multiple = valuation / revenue
            if multiple > rules["revenue_multiple_max"]:
                issues.append(
                    FinancialValidationIssue(
                        field="valuation",
                        code="EXTREME_REVENUE_MULTIPLE",
                        message=f"Revenue multiple {multiple:.2f} exceeds threshold",
                    )
                )

    if employee_count is not None:
        rules = FINANCIAL_VALIDATION_RULES["employee_count"]
        if employee_count < rules["min"] or employee_count > rules["max"]:
            issues.append(
                FinancialValidationIssue(
                    field="employee_count",
                    code="OUT_OF_RANGE",
                    message=f"Employee count {employee_count} is out of supported range",
                )
            )

    return issues


def _as_float(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _as_int(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None
