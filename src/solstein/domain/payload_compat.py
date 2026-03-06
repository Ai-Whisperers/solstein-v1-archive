from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CompatibilityTransformResult:
    payload: dict[str, object]
    warnings: list[str]


def apply_company_payload_compat(payload: dict[str, object]) -> CompatibilityTransformResult:
    """Apply backward-compatible field aliases for Company payloads.

    This helper is intentionally non-destructive and deterministic:
    - It copies incoming payload.
    - It applies known legacy aliases.
    - It reports every applied alias in warnings.
    """

    transformed = dict(payload)
    warnings: list[str] = []

    if "name" not in transformed and transformed.get("company_name"):
        transformed["name"] = transformed["company_name"]
        warnings.append("company_name->name")

    if "financials" in transformed and isinstance(transformed["financials"], dict):
        fin: dict[str, object] = dict(transformed["financials"])
    else:
        fin = {}

    if "funding_raised" not in fin and transformed.get("funding") is not None:
        fin["funding_raised"] = transformed["funding"]
        warnings.append("funding->financials.funding_raised")

    for key in ("revenue", "employees", "growth_rate", "profit_margin", "valuation"):
        if key not in fin and transformed.get(key) is not None:
            fin[key] = transformed[key]
            warnings.append(f"{key}->financials.{key}")

    if fin:
        transformed["financials"] = fin

    return CompatibilityTransformResult(payload=transformed, warnings=warnings)
