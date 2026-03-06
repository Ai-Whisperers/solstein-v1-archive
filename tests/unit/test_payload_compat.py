from solstein.domain.payload_compat import apply_company_payload_compat


def test_company_name_alias_maps_to_name() -> None:
    payload = {"company_name": "Alias Co", "industry": "Energy"}

    result = apply_company_payload_compat(payload)

    assert result.payload["name"] == "Alias Co"
    assert "company_name->name" in result.warnings


def test_funding_alias_maps_to_financials_field() -> None:
    payload = {
        "name": "Funding Co",
        "industry": "Energy",
        "funding": 12.0,
    }

    result = apply_company_payload_compat(payload)

    assert result.payload["financials"]["funding_raised"] == 12.0
    assert "funding->financials.funding_raised" in result.warnings


def test_flat_financial_fields_copied_into_financials() -> None:
    payload = {
        "name": "Flat Co",
        "industry": "Energy",
        "revenue": 8.0,
        "employees": 21,
        "growth_rate": 13.0,
        "profit_margin": 7.5,
        "valuation": 44.0,
    }

    result = apply_company_payload_compat(payload)

    fin = result.payload["financials"]
    assert fin["revenue"] == 8.0
    assert fin["employees"] == 21
    assert fin["growth_rate"] == 13.0
    assert fin["profit_margin"] == 7.5
    assert fin["valuation"] == 44.0


def test_existing_nested_values_are_preserved() -> None:
    payload = {
        "name": "Nested Co",
        "industry": "Energy",
        "funding": 50.0,
        "financials": {
            "funding_raised": 3.0,
            "revenue": 10.0,
        },
    }

    result = apply_company_payload_compat(payload)

    assert result.payload["financials"]["funding_raised"] == 3.0
    assert result.payload["financials"]["revenue"] == 10.0
