"""
Tests for STORY-227: Extraction contract with unit normalization
and contradiction flags.

Tests cover:
- Currency detection from text
- Scale detection (K/M/B/T)
- Monetary normalization to canonical millions
- Employee count normalization
- Year normalization
- Ambiguity flagging
- Contradiction detection between sources
- Contradiction severity classification
- Serialization helpers
"""

import pytest

from solstein.research.numeric_normalization import (
    COUNT_FIELDS,
    MONETARY_FIELDS,
    YEAR_FIELDS,
    ContradictionFlag,
    Currency,
    NormalizedValue,
    NumericUnit,
    build_contradiction_summary,
    contradiction_to_dict,
    detect_contradictions,
    detect_currency,
    detect_scale,
    extract_number,
    normalize_count,
    normalize_monetary,
    normalize_year,
    normalized_value_to_dict,
)

# ---------------------------------------------------------------------------
# Currency detection tests
# ---------------------------------------------------------------------------


class TestDetectCurrency:
    """Test currency symbol and keyword detection."""

    def test_dollar_sign(self) -> None:
        currency, conf = detect_currency("$1.5M")
        assert currency == Currency.USD
        assert conf >= 0.8

    def test_euro_sign(self) -> None:
        currency, conf = detect_currency("€200M")
        assert currency == Currency.EUR

    def test_pound_sign(self) -> None:
        currency, conf = detect_currency("£50M")
        assert currency == Currency.GBP

    def test_usd_keyword(self) -> None:
        currency, conf = detect_currency("150 million USD")
        assert currency == Currency.USD

    def test_eur_keyword(self) -> None:
        currency, conf = detect_currency("200M EUR")
        assert currency == Currency.EUR

    def test_chf_keyword(self) -> None:
        currency, conf = detect_currency("CHF 50 million")
        assert currency == Currency.CHF

    def test_no_currency_returns_unknown(self) -> None:
        currency, conf = detect_currency("500")
        assert currency == Currency.UNKNOWN
        assert conf < 0.5

    def test_empty_string(self) -> None:
        currency, _ = detect_currency("")
        assert currency == Currency.UNKNOWN


# ---------------------------------------------------------------------------
# Scale detection tests
# ---------------------------------------------------------------------------


class TestDetectScale:
    """Test numeric scale keyword detection."""

    def test_million_full_word(self) -> None:
        unit, conf = detect_scale("2.3 million")
        assert unit == NumericUnit.MILLIONS
        assert conf >= 0.9

    def test_billion_full_word(self) -> None:
        unit, conf = detect_scale("1.5 billion")
        assert unit == NumericUnit.BILLIONS
        assert conf >= 0.9

    def test_thousand_full_word(self) -> None:
        unit, conf = detect_scale("500 thousand")
        assert unit == NumericUnit.THOUSANDS

    def test_m_suffix(self) -> None:
        unit, conf = detect_scale("$200M")
        assert unit == NumericUnit.MILLIONS

    def test_b_suffix(self) -> None:
        unit, conf = detect_scale("$1.5B")
        assert unit == NumericUnit.BILLIONS

    def test_bn_suffix(self) -> None:
        unit, conf = detect_scale("€3.2bn")
        assert unit == NumericUnit.BILLIONS
        assert conf >= 0.7

    def test_no_scale_returns_unknown(self) -> None:
        unit, conf = detect_scale("500")
        assert unit == NumericUnit.UNKNOWN
        assert conf < 0.5

    def test_trillion(self) -> None:
        unit, _ = detect_scale("1.2 trillion")
        assert unit == NumericUnit.TRILLIONS


# ---------------------------------------------------------------------------
# Number extraction tests
# ---------------------------------------------------------------------------


class TestExtractNumber:
    """Test core numeric value extraction."""

    def test_simple_integer(self) -> None:
        assert extract_number("1500") == 1500.0

    def test_comma_separated(self) -> None:
        assert extract_number("1,500,000") == 1500000.0

    def test_decimal(self) -> None:
        assert extract_number("2.5") == 2.5

    def test_with_currency_prefix(self) -> None:
        assert extract_number("$1.5") == 1.5

    def test_with_scale_suffix(self) -> None:
        assert extract_number("200M") == 200.0

    def test_empty_returns_none(self) -> None:
        assert extract_number("") is None

    def test_none_returns_none(self) -> None:
        assert extract_number(None) is None

    def test_non_numeric_returns_none(self) -> None:
        assert extract_number("not a number") is None


# ---------------------------------------------------------------------------
# Monetary normalization tests
# ---------------------------------------------------------------------------


class TestNormalizeMonetary:
    """Test monetary value normalization to canonical millions."""

    def test_dollar_millions(self) -> None:
        result = normalize_monetary("$200M", "revenue")
        assert result.value == 200.0
        assert result.unit == NumericUnit.MILLIONS
        assert result.currency == Currency.USD
        assert not result.is_ambiguous

    def test_euro_billions(self) -> None:
        result = normalize_monetary("€1.5B", "valuation")
        assert result.value == 1500.0
        assert result.unit == NumericUnit.MILLIONS
        assert result.currency == Currency.EUR

    def test_raw_large_number_as_units(self) -> None:
        result = normalize_monetary("50000000", "revenue")
        assert result.value == pytest.approx(50.0, abs=0.01)
        assert result.unit == NumericUnit.MILLIONS

    def test_word_million(self) -> None:
        result = normalize_monetary("2.3 million USD", "funding_raised")
        assert result.value == pytest.approx(2.3, abs=0.01)
        assert result.currency == Currency.USD

    def test_word_billion(self) -> None:
        result = normalize_monetary("1.5 billion EUR", "valuation")
        assert result.value == pytest.approx(1500.0, abs=0.1)

    def test_ambiguous_medium_number(self) -> None:
        """A number like 5000 with no scale hint is ambiguous."""
        result = normalize_monetary("5000", "revenue")
        assert result.is_ambiguous

    def test_none_input(self) -> None:
        result = normalize_monetary(None)
        assert result.value is None
        assert not result.is_ambiguous

    def test_empty_input(self) -> None:
        result = normalize_monetary("")
        assert result.value is None

    def test_non_numeric_input(self) -> None:
        result = normalize_monetary("N/A", "revenue")
        assert result.value is None
        assert result.is_ambiguous

    def test_pound_millions(self) -> None:
        result = normalize_monetary("£50M", "revenue")
        assert result.value == 50.0
        assert result.currency == Currency.GBP

    def test_numeric_passthrough(self) -> None:
        """A plain float should be handled."""
        result = normalize_monetary(1.5, "revenue")
        assert result.value is not None

    def test_integer_passthrough(self) -> None:
        result = normalize_monetary(200, "revenue")
        assert result.value is not None


# ---------------------------------------------------------------------------
# Count normalization tests
# ---------------------------------------------------------------------------


class TestNormalizeCount:
    """Test employee/headcount normalization."""

    def test_simple_count(self) -> None:
        result = normalize_count("500", "employees")
        assert result.value == 500
        assert result.unit == NumericUnit.UNITS

    def test_thousands_suffix(self) -> None:
        result = normalize_count("5K", "employees")
        assert result.value == 5000

    def test_comma_formatted(self) -> None:
        result = normalize_count("1,500", "employees")
        assert result.value == 1500

    def test_none_input(self) -> None:
        result = normalize_count(None)
        assert result.value is None

    def test_non_numeric(self) -> None:
        result = normalize_count("many", "employees")
        assert result.value is None
        assert result.is_ambiguous


# ---------------------------------------------------------------------------
# Year normalization tests
# ---------------------------------------------------------------------------


class TestNormalizeYear:
    """Test founded year normalization."""

    def test_four_digit_year(self) -> None:
        result = normalize_year("2015")
        assert result.value == 2015
        assert result.confidence > 0.9

    def test_year_in_text(self) -> None:
        result = normalize_year("Founded in 2008")
        assert result.value == 2008

    def test_none_input(self) -> None:
        result = normalize_year(None)
        assert result.value is None

    def test_invalid_year(self) -> None:
        result = normalize_year("abc")
        assert result.value is None
        assert result.is_ambiguous

    def test_year_boundary_low(self) -> None:
        result = normalize_year("1800")
        assert result.value == 1800

    def test_future_year_rejected(self) -> None:
        result = normalize_year("2099")
        assert result.value is None


# ---------------------------------------------------------------------------
# Contradiction detection tests
# ---------------------------------------------------------------------------


class TestDetectContradictions:
    """Test cross-source contradiction detection."""

    def test_no_contradiction_for_similar_values(self) -> None:
        flags = detect_contradictions(
            "revenue",
            [
                {"source": "source_a", "value": 100.0},
                {"source": "source_b", "value": 110.0},
            ],
        )
        assert len(flags) == 0

    def test_minor_contradiction(self) -> None:
        flags = detect_contradictions(
            "revenue",
            [
                {"source": "source_a", "value": 100.0},
                {"source": "source_b", "value": 160.0},
            ],
        )
        assert len(flags) == 1
        assert flags[0].severity == "minor"

    def test_major_contradiction(self) -> None:
        flags = detect_contradictions(
            "revenue",
            [
                {"source": "crunchbase", "value": 50.0},
                {"source": "bloomberg", "value": 200.0},
            ],
        )
        assert len(flags) == 1
        assert flags[0].severity == "major"

    def test_critical_contradiction(self) -> None:
        flags = detect_contradictions(
            "valuation",
            [
                {"source": "source_a", "value": 10.0},
                {"source": "source_b", "value": 1000.0},
            ],
        )
        assert len(flags) == 1
        assert flags[0].severity == "critical"
        assert flags[0].ratio >= 10.0

    def test_skips_zero_values(self) -> None:
        flags = detect_contradictions(
            "revenue",
            [
                {"source": "source_a", "value": 0},
                {"source": "source_b", "value": 100.0},
            ],
        )
        assert len(flags) == 0

    def test_skips_ambiguous_normalized_values(self) -> None:
        ambiguous = NormalizedValue(
            raw_input="5000",
            value=5000.0,
            unit=NumericUnit.UNKNOWN,
            currency=Currency.UNKNOWN,
            confidence=0.2,
            is_ambiguous=True,
        )
        flags = detect_contradictions(
            "revenue",
            [
                {"source": "source_a", "value": ambiguous},
                {"source": "source_b", "value": 100.0},
            ],
        )
        assert len(flags) == 0

    def test_uses_normalized_value_when_not_ambiguous(self) -> None:
        nv = NormalizedValue(
            raw_input="$200M",
            value=200.0,
            unit=NumericUnit.MILLIONS,
            currency=Currency.USD,
            confidence=0.9,
            is_ambiguous=False,
        )
        flags = detect_contradictions(
            "revenue",
            [
                {"source": "sec", "value": nv},
                {"source": "news", "value": 800.0},
            ],
        )
        assert len(flags) == 1
        assert flags[0].severity == "major"

    def test_multiple_sources_pairwise(self) -> None:
        flags = detect_contradictions(
            "employees",
            [
                {"source": "a", "value": 100.0},
                {"source": "b", "value": 500.0},
                {"source": "c", "value": 110.0},
            ],
        )
        # a vs b = 5x (major), b vs c = 4.5x (major), a vs c = 1.1x (no flag)
        assert len(flags) == 2

    def test_empty_sources(self) -> None:
        flags = detect_contradictions("revenue", [])
        assert len(flags) == 0

    def test_single_source(self) -> None:
        flags = detect_contradictions(
            "revenue",
            [
                {"source": "a", "value": 100.0},
            ],
        )
        assert len(flags) == 0


# ---------------------------------------------------------------------------
# Contradiction summary tests
# ---------------------------------------------------------------------------


class TestBuildContradictionSummary:
    """Test contradiction summary builder."""

    def test_summary_with_flags(self) -> None:
        flags = [
            ContradictionFlag("revenue", "a", 100, "b", 500, 5.0, "major"),
            ContradictionFlag("valuation", "a", 10, "b", 1000, 100.0, "critical"),
        ]
        summary = build_contradiction_summary(flags, total_fields_checked=5)
        assert summary.contradiction_rate == pytest.approx(0.4, abs=0.01)
        assert len(summary.fields_with_contradictions) == 2
        assert "revenue" in summary.fields_with_contradictions

    def test_empty_summary(self) -> None:
        summary = build_contradiction_summary([], total_fields_checked=5)
        assert summary.contradiction_rate == 0.0
        assert len(summary.contradictions) == 0

    def test_zero_fields_checked(self) -> None:
        summary = build_contradiction_summary([], total_fields_checked=0)
        assert summary.contradiction_rate == 0.0


# ---------------------------------------------------------------------------
# Serialization tests
# ---------------------------------------------------------------------------


class TestSerialization:
    """Test dict serialization helpers."""

    def test_normalized_value_to_dict(self) -> None:
        nv = NormalizedValue(
            raw_input="$200M",
            value=200.0,
            unit=NumericUnit.MILLIONS,
            currency=Currency.USD,
            confidence=0.9,
            is_ambiguous=False,
        )
        d = normalized_value_to_dict(nv)
        assert d["value"] == 200.0
        assert d["unit"] == "millions"
        assert d["currency"] == "USD"
        assert d["is_ambiguous"] is False

    def test_contradiction_to_dict(self) -> None:
        flag = ContradictionFlag("revenue", "a", 100, "b", 500, 5.0, "major")
        d = contradiction_to_dict(flag)
        assert d["field"] == "revenue"
        assert d["severity"] == "major"
        assert d["ratio"] == 5.0


# ---------------------------------------------------------------------------
# Field set constants tests
# ---------------------------------------------------------------------------


class TestFieldConstants:
    """Test field classification constants."""

    def test_monetary_fields(self) -> None:
        assert "revenue" in MONETARY_FIELDS
        assert "funding_raised" in MONETARY_FIELDS
        assert "valuation" in MONETARY_FIELDS

    def test_count_fields(self) -> None:
        assert "employees" in COUNT_FIELDS

    def test_year_fields(self) -> None:
        assert "founded_year" in YEAR_FIELDS
