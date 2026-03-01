"""Domain value objects for Solstein.

Value objects are immutable, self-validating types that encapsulate
domain rules.  They replace raw primitives throughout the codebase,
making business invariants impossible to violate.

Usage::

    revenue = Money(amount=Decimal("1_500_000"), currency="EUR")
    score = Score(7.5)
    pct = Percentage(23.4)
    company_id = CompanyId("COMP-001")
    period = DateRange(start=date(2023, 1, 1), end=date(2023, 12, 31))
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

from pydantic import BaseModel, field_validator, model_validator

from solstein.analytics.constants import MAX_SCORE, MIN_SCORE


# ---------------------------------------------------------------------------
# Money
# ---------------------------------------------------------------------------

_ISO_4217_CODES = frozenset(
    {
        "EUR",
        "USD",
        "GBP",
        "JPY",
        "CHF",
        "AUD",
        "CAD",
        "CNY",
        "HKD",
        "SGD",
        "SEK",
        "NOK",
        "DKK",
        "NZD",
        "ZAR",
        "BRL",
        "INR",
        "RUB",
        "KRW",
        "MXN",
    }
)


class Money(BaseModel):
    """Immutable monetary amount with currency.

    Attributes:
        amount: Non-negative decimal amount.
        currency: ISO 4217 three-letter currency code.
    """

    model_config = {"frozen": True}

    amount: Decimal
    currency: str = "EUR"

    @field_validator("amount", mode="before")
    @classmethod
    def coerce_decimal(cls, v: Any) -> Decimal:
        try:
            return Decimal(str(v))
        except InvalidOperation as exc:
            raise ValueError(f"Invalid decimal amount: {v!r}") from exc

    @field_validator("amount")
    @classmethod
    def non_negative(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("Monetary amount must be non-negative")
        return v

    @field_validator("currency")
    @classmethod
    def valid_currency(cls, v: str) -> str:
        upper = v.upper()
        if upper not in _ISO_4217_CODES:
            raise ValueError(f"Unsupported currency code: {v!r}. Expected ISO 4217.")
        return upper

    def to_eur(self, exchange_rate: Decimal) -> "Money":
        """Return equivalent in EUR given the EUR/currency exchange rate."""
        return Money(amount=self.amount / exchange_rate, currency="EUR")

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(f"Cannot add {self.currency} and {other.currency}")
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def __repr__(self) -> str:
        return f"Money({self.amount:.2f} {self.currency})"


# ---------------------------------------------------------------------------
# Percentage
# ---------------------------------------------------------------------------


class Percentage(BaseModel):
    """A percentage value in the range –100 to 1000 (allows CAGR, growth rates).

    Stored as a float; call ``.fraction`` to get the 0-1 representation.
    """

    model_config = {"frozen": True}

    value: float

    @field_validator("value")
    @classmethod
    def valid_range(cls, v: float) -> float:
        if not (-100.0 <= v <= 1_000.0):
            raise ValueError(f"Percentage out of range: {v}. Expected –100 to 1000.")
        return v

    @property
    def fraction(self) -> float:
        """Return the 0-1 fraction representation."""
        return self.value / 100.0

    def __repr__(self) -> str:
        return f"Percentage({self.value:.1f}%)"


# ---------------------------------------------------------------------------
# Score
# ---------------------------------------------------------------------------


class Score(BaseModel):
    """Composite score in the range [MIN_SCORE, MAX_SCORE] (0.0–10.0).

    Used for growth, financial health, competitive position, and
    the final composite score.
    """

    model_config = {"frozen": True}

    value: float

    @field_validator("value")
    @classmethod
    def valid_range(cls, v: float) -> float:
        if not (MIN_SCORE <= v <= MAX_SCORE):
            raise ValueError(f"Score {v} outside valid range [{MIN_SCORE}, {MAX_SCORE}]")
        return v

    def is_phoenix(self) -> bool:
        from solstein.analytics.constants import PHOENIX_SCORE_THRESHOLD

        return self.value >= PHOENIX_SCORE_THRESHOLD

    def is_lead(self) -> bool:
        from solstein.analytics.constants import LEAD_SCORE_THRESHOLD

        return self.value <= LEAD_SCORE_THRESHOLD

    def __repr__(self) -> str:
        return f"Score({self.value:.2f})"


# ---------------------------------------------------------------------------
# CompanyId
# ---------------------------------------------------------------------------


class CompanyId(str):
    """Typed identifier for a Company entity.

    Prevents raw strings being accidentally used where a company ID is
    expected, and enforces non-empty constraint at construction time.
    """

    def __new__(cls, value: str) -> "CompanyId":
        stripped = str(value).strip()
        if not stripped:
            raise ValueError("CompanyId must not be blank")
        return super().__new__(cls, stripped)

    def __repr__(self) -> str:
        return f"CompanyId({str(self)!r})"


# ---------------------------------------------------------------------------
# DateRange
# ---------------------------------------------------------------------------


class DateRange(BaseModel):
    """An inclusive date range [start, end].

    Attributes:
        start: Start date (inclusive).
        end: End date (inclusive).
    """

    model_config = {"frozen": True}

    start: date
    end: date

    @model_validator(mode="after")
    def end_after_start(self) -> "DateRange":
        if self.end < self.start:
            raise ValueError(f"end ({self.end}) must be >= start ({self.start})")
        return self

    @property
    def duration_days(self) -> int:
        return (self.end - self.start).days

    def contains(self, d: date) -> bool:
        return self.start <= d <= self.end

    def __repr__(self) -> str:
        return f"DateRange({self.start} → {self.end})"


__all__ = [
    "Money",
    "Percentage",
    "Score",
    "CompanyId",
    "DateRange",
]
