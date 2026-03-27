"""
Numeric normalization and contradiction detection for financial fields.

STORY-227: Canonical numeric contract with unit/currency normalization,
ambiguity flagging, and cross-source contradiction detection.

Canonical output contract:
- All monetary values normalized to millions (M) in their source currency
- All employee counts normalized to absolute integers
- All years normalized to 4-digit integers
- Every normalized field carries: value, unit, currency, confidence, is_ambiguous
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class NumericUnit(str, Enum):
    """Canonical unit scale for numeric values."""

    UNITS = "units"          # raw count (employees, years)
    THOUSANDS = "thousands"  # K
    MILLIONS = "millions"    # M  (canonical for monetary)
    BILLIONS = "billions"    # B
    TRILLIONS = "trillions"  # T
    UNKNOWN = "unknown"


class Currency(str, Enum):
    """Recognized currencies."""

    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CHF = "CHF"
    UNKNOWN = "unknown"


# Scale multipliers to convert TO millions
_SCALE_TO_MILLIONS: dict[NumericUnit, float] = {
    NumericUnit.UNITS: 1e-6,
    NumericUnit.THOUSANDS: 1e-3,
    NumericUnit.MILLIONS: 1.0,
    NumericUnit.BILLIONS: 1e3,
    NumericUnit.TRILLIONS: 1e6,
}

# Currency symbol/prefix mapping
_CURRENCY_SYMBOLS: dict[str, Currency] = {
    "$": Currency.USD, "usd": Currency.USD, "us$": Currency.USD,
    "€": Currency.EUR, "eur": Currency.EUR,
    "£": Currency.GBP, "gbp": Currency.GBP,
    "chf": Currency.CHF, "sfr": Currency.CHF,
}

# Scale keyword mapping
_SCALE_KEYWORDS: dict[str, NumericUnit] = {
    "k": NumericUnit.THOUSANDS, "thousand": NumericUnit.THOUSANDS,
    "m": NumericUnit.MILLIONS, "million": NumericUnit.MILLIONS, "mn": NumericUnit.MILLIONS,
    "mm": NumericUnit.MILLIONS, "mil": NumericUnit.MILLIONS,
    "b": NumericUnit.BILLIONS, "billion": NumericUnit.BILLIONS, "bn": NumericUnit.BILLIONS,
    "t": NumericUnit.TRILLIONS, "trillion": NumericUnit.TRILLIONS, "tn": NumericUnit.TRILLIONS,
}

# Regex to parse numeric strings like "$1.5B", "€200M", "1,500,000", "2.3 million"
_NUMERIC_PATTERN = re.compile(
    r"(?P<currency_prefix>[€$£]?)\s*"
    r"(?P<number>[\d,]+\.?\d*)\s*"
    r"(?P<scale_suffix>[kKmMbBtT](?:illion|ousand|n)?)?",
)


@dataclass(frozen=True)
class NormalizedValue:
    """A numeric value with full provenance metadata."""

    raw_input: str
    value: float | None
    unit: NumericUnit
    currency: Currency
    confidence: float
    is_ambiguous: bool
    ambiguity_reason: str = ""


@dataclass
class ContradictionFlag:
    """Records a contradiction between two source claims."""

    field_name: str
    source_a: str
    value_a: float
    source_b: str
    value_b: float
    ratio: float
    severity: str  # "minor" (<2x), "major" (2x-10x), "critical" (>10x)


@dataclass
class SynthesisContradictions:
    """Contradiction summary for a synthesis pass."""

    contradictions: list[ContradictionFlag] = field(default_factory=list)
    contradiction_rate: float = 0.0
    fields_with_contradictions: list[str] = field(default_factory=list)


def detect_currency(text: str) -> tuple[Currency, float]:
    """Detect currency from text, returning (currency, confidence).

    Returns Currency.UNKNOWN with low confidence if ambiguous.
    """
    lower = text.lower().strip()
    for symbol, currency in _CURRENCY_SYMBOLS.items():
        if symbol in lower:
            return currency, 0.9
    return Currency.UNKNOWN, 0.3


def detect_scale(text: str) -> tuple[NumericUnit, float]:
    """Detect numeric scale from text, returning (unit, confidence).

    Returns NumericUnit.UNKNOWN with low confidence if ambiguous.
    """
    lower = text.lower().strip()

    # Check full words first (higher confidence)
    for keyword, unit in _SCALE_KEYWORDS.items():
        if len(keyword) > 2 and keyword in lower:
            return unit, 0.95

    # Check single-letter suffixes (lower confidence)
    match = _NUMERIC_PATTERN.search(text)
    if match and match.group("scale_suffix"):
        suffix = match.group("scale_suffix")[0].lower()
        for keyword, unit in _SCALE_KEYWORDS.items():
            if keyword == suffix and len(keyword) == 1:
                return unit, 0.7

    return NumericUnit.UNKNOWN, 0.2


def extract_number(text: str) -> float | None:
    """Extract the core numeric value from a string, stripping formatting."""
    if not text or not isinstance(text, str):
        return None
    cleaned = text.replace(",", "").replace(" ", "")
    match = _NUMERIC_PATTERN.search(cleaned)
    if not match:
        return None
    try:
        return float(match.group("number").replace(",", ""))
    except (ValueError, AttributeError):
        return None


def normalize_monetary(raw: Any, field_name: str = "") -> NormalizedValue:
    """Normalize a monetary value to canonical millions.

    Handles strings like "$1.5B", "€200M", "1500000", "2.3 million USD".
    """
    if raw is None:
        return NormalizedValue(
            raw_input="", value=None, unit=NumericUnit.UNKNOWN,
            currency=Currency.UNKNOWN, confidence=0.0,
            is_ambiguous=False, ambiguity_reason="null input",
        )

    raw_str = str(raw).strip()
    if not raw_str:
        return NormalizedValue(
            raw_input=raw_str, value=None, unit=NumericUnit.UNKNOWN,
            currency=Currency.UNKNOWN, confidence=0.0,
            is_ambiguous=False, ambiguity_reason="empty input",
        )

    number = extract_number(raw_str)
    if number is None:
        return NormalizedValue(
            raw_input=raw_str, value=None, unit=NumericUnit.UNKNOWN,
            currency=Currency.UNKNOWN, confidence=0.0,
            is_ambiguous=True, ambiguity_reason="no numeric value found",
        )

    currency, currency_conf = detect_currency(raw_str)
    scale, scale_conf = detect_scale(raw_str)

    # Heuristic: bare large numbers are likely raw units
    if scale == NumericUnit.UNKNOWN:
        if number >= 1_000_000:
            scale = NumericUnit.UNITS
            scale_conf = 0.6
        elif number >= 1_000:
            # Ambiguous: could be thousands or millions
            scale = NumericUnit.UNKNOWN
            scale_conf = 0.2
        else:
            # Small number — likely already in millions
            scale = NumericUnit.MILLIONS
            scale_conf = 0.5

    is_ambiguous = scale == NumericUnit.UNKNOWN or currency == Currency.UNKNOWN
    ambiguity_reasons: list[str] = []
    if scale == NumericUnit.UNKNOWN:
        ambiguity_reasons.append(f"scale unclear for {field_name or 'value'}")
    if currency == Currency.UNKNOWN:
        ambiguity_reasons.append("currency not detected")

    # Convert to millions
    if scale != NumericUnit.UNKNOWN:
        multiplier = _SCALE_TO_MILLIONS.get(scale, 1.0)
        value_in_millions = number * multiplier
    else:
        value_in_millions = number  # pass through as-is

    combined_confidence = (currency_conf + scale_conf) / 2.0

    return NormalizedValue(
        raw_input=raw_str,
        value=round(value_in_millions, 4),
        unit=NumericUnit.MILLIONS if scale != NumericUnit.UNKNOWN else NumericUnit.UNKNOWN,
        currency=currency,
        confidence=round(combined_confidence, 3),
        is_ambiguous=is_ambiguous,
        ambiguity_reason="; ".join(ambiguity_reasons),
    )


def normalize_count(raw: Any, field_name: str = "") -> NormalizedValue:
    """Normalize a count value (employees, etc.) to absolute units."""
    if raw is None:
        return NormalizedValue(
            raw_input="", value=None, unit=NumericUnit.UNITS,
            currency=Currency.UNKNOWN, confidence=0.0,
            is_ambiguous=False, ambiguity_reason="null input",
        )

    raw_str = str(raw).strip()
    number = extract_number(raw_str)
    if number is None:
        return NormalizedValue(
            raw_input=raw_str, value=None, unit=NumericUnit.UNITS,
            currency=Currency.UNKNOWN, confidence=0.0,
            is_ambiguous=True, ambiguity_reason="no numeric value found",
        )

    scale, scale_conf = detect_scale(raw_str)

    # For counts, convert to absolute units
    scale_multipliers: dict[NumericUnit, float] = {
        NumericUnit.UNITS: 1.0,
        NumericUnit.THOUSANDS: 1_000.0,
        NumericUnit.MILLIONS: 1_000_000.0,
        NumericUnit.BILLIONS: 1_000_000_000.0,
        NumericUnit.UNKNOWN: 1.0,
    }

    multiplier = scale_multipliers.get(scale, 1.0)
    absolute_value = number * multiplier

    return NormalizedValue(
        raw_input=raw_str,
        value=round(absolute_value),
        unit=NumericUnit.UNITS,
        currency=Currency.UNKNOWN,
        confidence=round(scale_conf, 3),
        is_ambiguous=scale == NumericUnit.UNKNOWN and number < 1000,
        ambiguity_reason=f"scale unclear for {field_name}" if scale == NumericUnit.UNKNOWN and number < 1000 else "",
    )


def normalize_year(raw: Any) -> NormalizedValue:
    """Normalize a year value to a 4-digit integer."""
    if raw is None:
        return NormalizedValue(
            raw_input="", value=None, unit=NumericUnit.UNITS,
            currency=Currency.UNKNOWN, confidence=0.0,
            is_ambiguous=False, ambiguity_reason="null input",
        )

    raw_str = str(raw).strip()
    match = re.search(r"\b(1[89]\d{2}|20[0-2]\d)\b", raw_str)
    if match:
        return NormalizedValue(
            raw_input=raw_str, value=int(match.group(1)),
            unit=NumericUnit.UNITS, currency=Currency.UNKNOWN,
            confidence=0.95, is_ambiguous=False,
        )

    return NormalizedValue(
        raw_input=raw_str, value=None, unit=NumericUnit.UNITS,
        currency=Currency.UNKNOWN, confidence=0.0,
        is_ambiguous=True, ambiguity_reason="no valid year found",
    )


# ---------------------------------------------------------------------------
# Contradiction detection
# ---------------------------------------------------------------------------

# Monetary fields that participate in contradiction checks
MONETARY_FIELDS = frozenset({"revenue", "funding_raised", "valuation"})
COUNT_FIELDS = frozenset({"employees"})
YEAR_FIELDS = frozenset({"founded_year"})

# Contradiction thresholds: ratio of max/min between two sources
_MINOR_THRESHOLD = 1.5   # >1.5x difference
_MAJOR_THRESHOLD = 3.0   # >3x difference
_CRITICAL_THRESHOLD = 10.0  # >10x difference


def _classify_contradiction_severity(ratio: float) -> str:
    """Classify contradiction severity by ratio."""
    if ratio >= _CRITICAL_THRESHOLD:
        return "critical"
    if ratio >= _MAJOR_THRESHOLD:
        return "major"
    return "minor"


def detect_contradictions(
    field_name: str,
    source_values: list[dict[str, Any]],
) -> list[ContradictionFlag]:
    """Detect contradictions between multiple source claims for a field.

    Args:
        field_name: The field being checked.
        source_values: List of dicts with "source", "value" (NormalizedValue or float).

    Returns:
        List of ContradictionFlag for pairs that exceed threshold.
    """
    flags: list[ContradictionFlag] = []
    numeric_entries: list[tuple[str, float]] = []

    for entry in source_values:
        val = entry.get("value")
        source = entry.get("source", "unknown")
        if isinstance(val, NormalizedValue):
            if val.value is not None and not val.is_ambiguous:
                numeric_entries.append((source, val.value))
        elif isinstance(val, (int, float)) and val > 0:
            numeric_entries.append((source, float(val)))

    # Compare all pairs
    for i in range(len(numeric_entries)):
        for j in range(i + 1, len(numeric_entries)):
            src_a, val_a = numeric_entries[i]
            src_b, val_b = numeric_entries[j]
            if val_a == 0 or val_b == 0:
                continue
            ratio = max(val_a, val_b) / min(val_a, val_b)
            if ratio >= _MINOR_THRESHOLD:
                flags.append(ContradictionFlag(
                    field_name=field_name,
                    source_a=src_a, value_a=val_a,
                    source_b=src_b, value_b=val_b,
                    ratio=round(ratio, 2),
                    severity=_classify_contradiction_severity(ratio),
                ))

    return flags


def build_contradiction_summary(
    all_flags: list[ContradictionFlag],
    total_fields_checked: int,
) -> SynthesisContradictions:
    """Build a summary of all contradictions found during synthesis."""
    affected_fields = list({f.field_name for f in all_flags})
    rate = len(affected_fields) / total_fields_checked if total_fields_checked > 0 else 0.0

    return SynthesisContradictions(
        contradictions=all_flags,
        contradiction_rate=round(rate, 3),
        fields_with_contradictions=sorted(affected_fields),
    )


def normalized_value_to_dict(nv: NormalizedValue) -> dict[str, Any]:
    """Serialize a NormalizedValue to a dict for JSON output."""
    return {
        "raw_input": nv.raw_input,
        "value": nv.value,
        "unit": nv.unit.value,
        "currency": nv.currency.value,
        "confidence": nv.confidence,
        "is_ambiguous": nv.is_ambiguous,
        "ambiguity_reason": nv.ambiguity_reason,
    }


def contradiction_to_dict(flag: ContradictionFlag) -> dict[str, Any]:
    """Serialize a ContradictionFlag to a dict for JSON output."""
    return {
        "field": flag.field_name,
        "source_a": flag.source_a,
        "value_a": flag.value_a,
        "source_b": flag.source_b,
        "value_b": flag.value_b,
        "ratio": flag.ratio,
        "severity": flag.severity,
    }


__all__ = [
    "NumericUnit", "Currency", "NormalizedValue",
    "ContradictionFlag", "SynthesisContradictions",
    "normalize_monetary", "normalize_count", "normalize_year",
    "detect_currency", "detect_scale", "extract_number",
    "detect_contradictions", "build_contradiction_summary",
    "normalized_value_to_dict", "contradiction_to_dict",
    "MONETARY_FIELDS", "COUNT_FIELDS", "YEAR_FIELDS",
]
