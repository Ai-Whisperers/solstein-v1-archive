from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MetricNormalizationResult:
    value: float | None
    assumed_unit: str


def normalize_revenue_to_millions(value: Any) -> MetricNormalizationResult:
    if value is None:
        return MetricNormalizationResult(value=None, assumed_unit="missing")
    if not isinstance(value, (int, float)):
        return MetricNormalizationResult(value=None, assumed_unit="invalid")

    numeric_value = float(value)
    if numeric_value == 0:
        return MetricNormalizationResult(value=0.0, assumed_unit="millions")

    abs_value = abs(numeric_value)
    if abs_value >= 1_000_000:
        return MetricNormalizationResult(value=numeric_value / 1_000_000, assumed_unit="absolute_currency")

    return MetricNormalizationResult(value=numeric_value, assumed_unit="millions")


def normalize_percent(value: Any) -> MetricNormalizationResult:
    if value is None:
        return MetricNormalizationResult(value=None, assumed_unit="missing")
    if not isinstance(value, (int, float)):
        return MetricNormalizationResult(value=None, assumed_unit="invalid")

    numeric_value = float(value)
    if -1 <= numeric_value <= 1:
        return MetricNormalizationResult(value=numeric_value * 100, assumed_unit="ratio")
    return MetricNormalizationResult(value=numeric_value, assumed_unit="percent")


def normalize_financial_payload(financials: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(financials)

    revenue_result = normalize_revenue_to_millions(normalized.get("revenue"))
    normalized["revenue"] = revenue_result.value
    normalized["revenue_unit"] = revenue_result.assumed_unit

    funding_result = normalize_revenue_to_millions(normalized.get("funding_raised"))
    normalized["funding_raised"] = funding_result.value
    normalized["funding_unit"] = funding_result.assumed_unit

    valuation_result = normalize_revenue_to_millions(normalized.get("valuation"))
    normalized["valuation"] = valuation_result.value
    normalized["valuation_unit"] = valuation_result.assumed_unit

    growth_result = normalize_percent(normalized.get("growth_rate"))
    normalized["growth_rate"] = growth_result.value
    normalized["growth_unit"] = growth_result.assumed_unit

    margin_result = normalize_percent(normalized.get("profit_margin"))
    normalized["profit_margin"] = margin_result.value
    normalized["profit_margin_unit"] = margin_result.assumed_unit

    return normalized
