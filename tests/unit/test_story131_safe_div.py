"""Tests for STORY-131: safe_div and related math utilities.

Verifies that:
- safe_div returns correct quotient for valid inputs
- safe_div returns default for zero, None, and NaN denominators
- safe_div distinguishes "calculated as zero" from "could not calculate"
- safe_pct computes percentages safely
- safe_avg handles None values and empty lists
"""

import pytest

from solstein.core.math_utils import safe_avg, safe_div, safe_pct


class TestSafeDiv:
    """Tests for safe_div utility."""

    def test_normal_division(self):
        assert safe_div(100, 10) == 10.0

    def test_returns_float(self):
        result = safe_div(10, 3)
        assert isinstance(result, float)
        assert abs(result - 3.3333) < 0.01

    def test_zero_denominator_returns_default(self):
        assert safe_div(100, 0, default=0.0) == 0.0

    def test_zero_denominator_default_none(self):
        assert safe_div(100, 0) is None

    def test_none_denominator_returns_default(self):
        assert safe_div(100, None, default=-1.0) == -1.0

    def test_none_numerator_returns_default(self):
        assert safe_div(None, 10, default=0.0) == 0.0

    def test_both_none_returns_default(self):
        assert safe_div(None, None) is None

    def test_nan_denominator_returns_default(self):
        assert safe_div(100, float("nan"), default=0.0) == 0.0

    def test_negative_division(self):
        assert safe_div(-100, 10) == -10.0

    def test_zero_numerator(self):
        """Zero numerator with non-zero denominator should return 0.0, not default."""
        assert safe_div(0, 10) == 0.0

    def test_calculated_zero_vs_could_not_calculate(self):
        """CRITICAL: 0/10 = 0.0 (calculated) vs 10/0 = None (could not calculate).

        These are semantically different in financial analysis.
        """
        calculated_zero = safe_div(0, 10)
        could_not_calculate = safe_div(10, 0)

        assert calculated_zero == 0.0
        assert could_not_calculate is None
        assert calculated_zero != could_not_calculate

    def test_label_does_not_affect_result(self):
        assert safe_div(100, 10, label="revenue_per_employee") == 10.0

    def test_integer_inputs(self):
        assert safe_div(10, 3) == pytest.approx(3.3333, abs=0.01)

    def test_mixed_int_float(self):
        assert safe_div(10, 3.0) == pytest.approx(3.3333, abs=0.01)


class TestSafePct:
    """Tests for safe_pct utility."""

    def test_normal_percentage(self):
        assert safe_pct(25, 100) == 25.0

    def test_zero_whole_returns_default(self):
        assert safe_pct(25, 0, default=0.0) == 0.0

    def test_none_whole_returns_default(self):
        assert safe_pct(25, None) is None

    def test_over_100_percent(self):
        assert safe_pct(150, 100) == 150.0

    def test_zero_part(self):
        assert safe_pct(0, 100) == 0.0


class TestSafeAvg:
    """Tests for safe_avg utility."""

    def test_normal_average(self):
        assert safe_avg([10, 20, 30]) == 20.0

    def test_empty_list_returns_default(self):
        assert safe_avg([], default=0.0) == 0.0

    def test_empty_list_default_none(self):
        assert safe_avg([]) is None

    def test_all_none_returns_default(self):
        assert safe_avg([None, None, None]) is None

    def test_mixed_none_values(self):
        """Ignores None values in the average."""
        assert safe_avg([10, None, 30]) == 20.0

    def test_single_value(self):
        assert safe_avg([42]) == 42.0

    def test_none_input(self):
        assert safe_avg(None) is None
