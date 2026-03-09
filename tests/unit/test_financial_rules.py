from solstein.validation import validate_financial_payload


def test_validate_financial_payload_allows_reasonable_values() -> None:
    payload = {
        "revenue": 250_000_000.0,
        "valuation": 1_500_000_000.0,
        "employee_count": 1200,
        "growth_rate": 1.25,
    }

    issues = validate_financial_payload(payload)

    assert issues == []


def test_validate_financial_payload_flags_extreme_growth_and_valuation_multiple() -> None:
    payload = {
        "revenue": 5_000_000.0,
        "valuation": 1_000_000_000.0,
        "employee_count": 500,
        "growth_rate": 12.0,
    }

    issues = validate_financial_payload(payload)
    codes = {issue.code for issue in issues}

    assert "UNREALISTIC_GROWTH" in codes
    assert "EXTREME_REVENUE_MULTIPLE" in codes


def test_validate_financial_payload_flags_employee_out_of_range() -> None:
    payload = {
        "employee_count": 0,
    }

    issues = validate_financial_payload(payload)

    assert len(issues) == 1
    assert issues[0].field == "employee_count"
    assert issues[0].code == "OUT_OF_RANGE"
