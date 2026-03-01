"""Unit tests for domain value objects (EPIC-007).

Run with: pytest tests/unit/domain/test_value_objects.py -v
"""

from __future__ import annotations

import pytest
from datetime import date
from decimal import Decimal

# Adjust path for imports
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from solstein.domain.value_objects import Money, Percentage, Score, CompanyId, DateRange


class TestMoney:
    """Test suite for Money value object."""

    def test_creation_valid(self) -> None:
        m = Money(amount=Decimal("1000000"), currency="EUR")
        assert m.amount == Decimal("1000000")
        assert m.currency == "EUR"

    def test_creation_from_float(self) -> None:
        m = Money(amount=1000000.50, currency="USD")
        assert m.amount == Decimal("1000000.50")
        assert m.currency == "USD"

    def test_currency_normalization(self) -> None:
        m = Money(amount=100, currency="eur")
        assert m.currency == "EUR"

    def test_invalid_currency(self) -> None:
        with pytest.raises(ValueError, match="Unsupported currency"):
            Money(amount=100, currency="XYZ")

    def test_negative_amount(self) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            Money(amount=Decimal("-100"), currency="EUR")

    def test_addition_same_currency(self) -> None:
        m1 = Money(amount=Decimal("100"), currency="EUR")
        m2 = Money(amount=Decimal("50"), currency="EUR")
        result = m1 + m2
        assert result.amount == Decimal("150")
        assert result.currency == "EUR"

    def test_addition_different_currency_raises(self) -> None:
        m1 = Money(amount=Decimal("100"), currency="EUR")
        m2 = Money(amount=Decimal("50"), currency="USD")
        with pytest.raises(ValueError, match="Cannot add"):
            m1 + m2

    def test_to_eur_conversion(self) -> None:
        m = Money(amount=Decimal("100"), currency="USD")
        eur = m.to_eur(Decimal("0.85"))  # 1 EUR = 1.176 USD
        assert eur.currency == "EUR"
        assert eur.amount == Decimal("100") / Decimal("0.85")


class TestPercentage:
    """Test suite for Percentage value object."""

    def test_creation_valid(self) -> None:
        p = Percentage(value=25.5)
        assert p.value == 25.5

    def test_fraction_property(self) -> None:
        p = Percentage(value=50.0)
        assert p.fraction == 0.5

    def test_range_validation(self) -> None:
        with pytest.raises(ValueError, match="out of range"):
            Percentage(value=1500.0)  # Exceeds 1000 max
        with pytest.raises(ValueError, match="out of range"):
            Percentage(value=-150.0)  # Below -100 min

    def test_cagr_valid(self) -> None:
        p = Percentage(value=150.0)  # 150% CAGR is valid
        assert p.value == 150.0


class TestScore:
    """Test suite for Score value object."""

    def test_creation_valid(self) -> None:
        s = Score(value=7.5)
        assert s.value == 7.5

    def test_range_validation(self) -> None:
        with pytest.raises(ValueError, match="outside valid range"):
            Score(value=15.0)  # Exceeds 10 max
        with pytest.raises(ValueError, match="outside valid range"):
            Score(value=-2.0)  # Below 0 min

    def test_is_phoenix(self) -> None:
        from solstein.analytics.constants import PHOENIX_SCORE_THRESHOLD

        s = Score(value=PHOENIX_SCORE_THRESHOLD)
        assert s.is_phoenix() is True
        s = Score(value=PHOENIX_SCORE_THRESHOLD - 0.1)
        assert s.is_phoenix() is False

    def test_is_lead(self) -> None:
        from solstein.analytics.constants import LEAD_SCORE_THRESHOLD

        s = Score(value=LEAD_SCORE_THRESHOLD)
        assert s.is_lead() is True
        s = Score(value=LEAD_SCORE_THRESHOLD + 0.1)
        assert s.is_lead() is False


class TestCompanyId:
    """Test suite for CompanyId value object."""

    def test_creation_valid(self) -> None:
        cid = CompanyId("COMP-001")
        assert str(cid) == "COMP-001"

    def test_stripping(self) -> None:
        cid = CompanyId("  COMP-001  ")
        assert str(cid) == "COMP-001"

    def test_blank_raises(self) -> None:
        with pytest.raises(ValueError, match="must not be blank"):
            CompanyId("")
        with pytest.raises(ValueError, match="must not be blank"):
            CompanyId("   ")


class TestDateRange:
    """Test suite for DateRange value object."""

    def test_creation_valid(self) -> None:
        dr = DateRange(start=date(2023, 1, 1), end=date(2023, 12, 31))
        assert dr.start == date(2023, 1, 1)
        assert dr.end == date(2023, 12, 31)

    def test_end_before_start_raises(self) -> None:
        with pytest.raises(ValueError, match="must be"):
            DateRange(start=date(2023, 12, 31), end=date(2023, 1, 1))

    def test_duration_days(self) -> None:
        dr = DateRange(start=date(2023, 1, 1), end=date(2023, 1, 10))
        assert dr.duration_days == 9

    def test_contains(self) -> None:
        dr = DateRange(start=date(2023, 1, 1), end=date(2023, 1, 31))
        assert dr.contains(date(2023, 1, 15)) is True
        assert dr.contains(date(2022, 12, 31)) is False
        assert dr.contains(date(2023, 2, 1)) is False
