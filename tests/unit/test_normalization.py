"""Tests for normalization module.

E2: Tests for extracted normalization utilities.
"""

import pytest
from decimal import Decimal

from solstein.data.normalization import (
    DataNormalizer,
    NormalizationError,
    clean_company_name,
    extract_domain_from_url,
    format_error_for_display,
    is_valid_number,
    normalize_boolean,
    normalize_date,
    normalize_dict,
    normalize_list,
    normalize_string,
    parse_decimal,
    parse_integer,
    parse_number,
    truncate_for_log,
)


class TestIsValidNumber:
    """Tests for is_valid_number function."""

    def test_valid_integers(self) -> None:
        assert is_valid_number(42) is True
        assert is_valid_number(0) is True
        assert is_valid_number(-10) is True

    def test_valid_floats(self) -> None:
        assert is_valid_number(3.14) is True
        assert is_valid_number(0.0) is True
        assert is_valid_number(-2.5) is True

    def test_valid_numeric_strings(self) -> None:
        assert is_valid_number("42") is True
        assert is_valid_number("3.14") is True
        assert is_valid_number("1,000") is True
        assert is_valid_number("$100") is True

    def test_invalid_values(self) -> None:
        assert is_valid_number(None) is False
        assert is_valid_number("abc") is False
        assert is_valid_number("") is False
        assert is_valid_number("   ") is False

    def test_nan_is_invalid(self) -> None:
        assert is_valid_number(float("nan")) is False


class TestParseNumber:
    """Tests for parse_number function."""

    def test_parse_integers(self) -> None:
        assert parse_number(42) == 42.0
        assert parse_number(0) == 0.0

    def test_parse_floats(self) -> None:
        assert parse_number(3.14) == 3.14

    def test_parse_strings(self) -> None:
        assert parse_number("42") == 42.0
        assert parse_number("3.14") == 3.14
        assert parse_number("1,000") == 1000.0
        assert parse_number("$100") == 100.0
        assert parse_number("50%") == 50.0

    def test_parse_parentheses_negative(self) -> None:
        assert parse_number("(100)") == -100.0
        assert parse_number("(1,000.50)") == -1000.5

    def test_default_on_failure(self) -> None:
        assert parse_number("abc") is None
        assert parse_number("abc", default=0.0) == 0.0

    def test_none_returns_default(self) -> None:
        assert parse_number(None) is None
        assert parse_number(None, default=0.0) == 0.0


class TestParseInteger:
    """Tests for parse_integer function."""

    def test_parse_valid_integers(self) -> None:
        assert parse_integer(42) == 42
        assert parse_integer("42") == 42
        assert parse_integer(3.14) == 3

    def test_default_on_failure(self) -> None:
        assert parse_integer("abc") is None
        assert parse_integer("abc", default=0) == 0


class TestParseDecimal:
    """Tests for parse_decimal function."""

    def test_parse_valid_decimals(self) -> None:
        result = parse_decimal("1000.50")
        assert isinstance(result, Decimal)
        assert result == Decimal("1000.50")

    def test_parse_from_float(self) -> None:
        result = parse_decimal(3.14)
        assert isinstance(result, Decimal)

    def test_parse_from_decimal(self) -> None:
        original = Decimal("100.50")
        result = parse_decimal(original)
        assert result == original

    def test_default_on_failure(self) -> None:
        assert parse_decimal("abc") is None
        assert parse_decimal("abc", default=Decimal("0")) == Decimal("0")


class TestNormalizeString:
    """Tests for normalize_string function."""

    def test_strip_whitespace(self) -> None:
        assert normalize_string("  hello  ") == "hello"

    def test_none_returns_default(self) -> None:
        assert normalize_string(None) == ""
        assert normalize_string(None, default="N/A") == "N/A"

    def test_empty_returns_default(self) -> None:
        assert normalize_string("   ") == ""
        assert normalize_string("   ", default="N/A") == "N/A"

    def test_converts_to_string(self) -> None:
        assert normalize_string(42) == "42"


class TestNormalizeBoolean:
    """Tests for normalize_boolean function."""

    def test_boolean_values(self) -> None:
        assert normalize_boolean(True) is True
        assert normalize_boolean(False) is False

    def test_true_strings(self) -> None:
        assert normalize_boolean("true") is True
        assert normalize_boolean("TRUE") is True
        assert normalize_boolean("yes") is True
        assert normalize_boolean("1") is True
        assert normalize_boolean("y") is True
        assert normalize_boolean("on") is True

    def test_false_strings(self) -> None:
        assert normalize_boolean("false") is False
        assert normalize_boolean("FALSE") is False
        assert normalize_boolean("no") is False
        assert normalize_boolean("0") is False
        assert normalize_boolean("n") is False
        assert normalize_boolean("off") is False
        assert normalize_boolean("") is False

    def test_numeric_values(self) -> None:
        assert normalize_boolean(1) is True
        assert normalize_boolean(0) is False
        assert normalize_boolean(0.5) is True

    def test_default_on_unknown(self) -> None:
        assert normalize_boolean("maybe") is None
        assert normalize_boolean("maybe", default=False) is False


class TestNormalizeList:
    """Tests for normalize_list function."""

    def test_list_unchanged(self) -> None:
        assert normalize_list([1, 2, 3]) == [1, 2, 3]

    def test_none_returns_default(self) -> None:
        assert normalize_list(None) == []
        assert normalize_list(None, default=["default"]) == ["default"]

    def test_single_value_wrapped(self) -> None:
        assert normalize_list("single") == ["single"]
        assert normalize_list(42) == [42]

    def test_tuple_converted(self) -> None:
        assert normalize_list((1, 2, 3)) == [1, 2, 3]

    def test_set_converted(self) -> None:
        result = normalize_list({1, 2, 3})
        assert isinstance(result, list)
        assert set(result) == {1, 2, 3}


class TestNormalizeDict:
    """Tests for normalize_dict function."""

    def test_dict_unchanged(self) -> None:
        assert normalize_dict({"key": "value"}) == {"key": "value"}

    def test_none_returns_default(self) -> None:
        assert normalize_dict(None) == {}
        assert normalize_dict(None, default={"default": "value"}) == {"default": "value"}

    def test_non_dict_returns_default(self) -> None:
        assert normalize_dict("string") == {}


class TestNormalizeDate:
    """Tests for normalize_date function."""

    def test_iso_format_preserved(self) -> None:
        assert normalize_date("2024-03-15") == "2024-03-15"
        assert normalize_date("2024-03-15T10:30:00") == "2024-03-15T10:30:00"

    def test_common_formats_parsed(self) -> None:
        assert normalize_date("03/15/2024") == "2024-03-15"
        assert normalize_date("15/03/2024") == "2024-03-15"
        assert normalize_date("2024/03/15") == "2024-03-15"

    def test_none_returns_none(self) -> None:
        assert normalize_date(None) is None

    def test_empty_returns_none(self) -> None:
        assert normalize_date("") is None
        assert normalize_date("   ") is None


class TestCleanCompanyName:
    """Tests for clean_company_name function."""

    def test_strip_whitespace(self) -> None:
        assert clean_company_name("  TestCo  ") == "TestCo"

    def test_remove_common_suffixes(self) -> None:
        assert clean_company_name("TestCo Inc") == "TestCo"
        assert clean_company_name("TestCo LLC") == "TestCo"
        assert clean_company_name("TestCo Ltd") == "TestCo"
        assert clean_company_name("TestCo Corp") == "TestCo"

    def test_none_returns_none(self) -> None:
        assert clean_company_name(None) is None

    def test_empty_returns_none(self) -> None:
        assert clean_company_name("") is None


class TestExtractDomainFromUrl:
    """Tests for extract_domain_from_url function."""

    def test_extract_from_http(self) -> None:
        assert extract_domain_from_url("http://example.com") == "example.com"

    def test_extract_from_https(self) -> None:
        assert extract_domain_from_url("https://example.com") == "example.com"

    def test_remove_www(self) -> None:
        assert extract_domain_from_url("https://www.example.com") == "example.com"

    def test_remove_path(self) -> None:
        assert extract_domain_from_url("https://example.com/path") == "example.com"

    def test_remove_port(self) -> None:
        assert extract_domain_from_url("https://example.com:8080") == "example.com"

    def test_none_returns_none(self) -> None:
        assert extract_domain_from_url(None) is None


class TestFormatErrorForDisplay:
    """Tests for format_error_for_display function."""

    def test_basic_formatting(self) -> None:
        error = ValueError("Something went wrong")
        result = format_error_for_display(error)
        assert result == "ValueError: Something went wrong"

    def test_with_context(self) -> None:
        error = ValueError("Something went wrong")
        result = format_error_for_display(error, "validation")
        assert result == "[validation] ValueError: Something went wrong"

    def test_empty_message(self) -> None:
        error = ValueError()
        result = format_error_for_display(error)
        assert "ValueError" in result


class TestTruncateForLog:
    """Tests for truncate_for_log function."""

    def test_short_string_unchanged(self) -> None:
        assert truncate_for_log("short") == "short"

    def test_long_string_truncated(self) -> None:
        long_string = "a" * 300
        result = truncate_for_log(long_string, max_length=100)
        assert len(result) == 100
        assert result.endswith("...")

    def test_non_string_converted(self) -> None:
        assert truncate_for_log(12345) == "12345"


class TestDataNormalizer:
    """Tests for DataNormalizer class."""

    def test_normalize_basic_record(self) -> None:
        normalizer = DataNormalizer()
        raw = {"name": "TestCo", "domain": "testco.com", "revenue": "1000000"}
        result = normalizer.normalize(raw)

        assert result["name"] == "TestCo"
        assert result["domain"] == "testco.com"
        assert result["revenue"] == Decimal("1000000")

    def test_field_mapping(self) -> None:
        normalizer = DataNormalizer()
        # Test various field name variants
        raw = {
            "company_name": "TestCo",
            "website": "testco.com",
            "annual_revenue": "5000000",
            "employee_count": "50",
        }
        result = normalizer.normalize(raw)

        assert result["name"] == "TestCo"
        assert result["domain"] == "testco.com"
        assert result["revenue"] == Decimal("5000000")
        assert result["employees"] == 50

    def test_numeric_normalization(self) -> None:
        normalizer = DataNormalizer()
        raw = {
            "name": "TestCo",
            "revenue": "$1,000,000",
            "employees": "100",
            "growth_rate": "25.5%",
        }
        result = normalizer.normalize(raw)

        assert result["revenue"] == Decimal("1000000")
        assert result["employees"] == 100
        assert result["growth_rate"] == 25.5

    def test_non_dict_raises_error(self) -> None:
        normalizer = DataNormalizer()
        with pytest.raises(NormalizationError):
            normalizer.normalize("not a dict")

    def test_ensures_required_fields(self) -> None:
        normalizer = DataNormalizer()
        raw = {"other_field": "value"}
        result = normalizer.normalize(raw)

        assert "name" in result
        assert "domain" in result
