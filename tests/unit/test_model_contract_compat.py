from typing import cast

from solstein.domain.models import Company


def test_persisted_legacy_flat_payload_remains_compatible() -> None:
    persisted = {
        "id": "legacy-json-1",
        "name": "Legacy JSON Co",
        "industry": "Energy",
        "revenue": 14.2,
        "employees": 48,
        "growth_rate": 19.0,
        "profit_margin": 8.5,
        "funding": 7.0,
        "valuation": 96.0,
    }

    company = Company.model_validate(persisted)
    dumped = company.model_dump()

    assert dumped["revenue"] == 14.2
    assert dumped["employees"] == 48
    assert dumped["growth_rate"] == 19.0
    assert dumped["profit_margin"] == 8.5
    assert dumped["funding"] == 7.0
    assert dumped["valuation"] == 96.0

    assert dumped["financials"]["revenue"] == 14.2
    assert dumped["financials"]["employees"] == 48
    assert dumped["financials"]["growth_rate"] == 19.0
    assert dumped["financials"]["profit_margin"] == 8.5


def test_persisted_nested_payload_remains_compatible() -> None:
    persisted = {
        "id": "nested-json-1",
        "name": "Nested JSON Co",
        "industry": "Energy",
        "financials": {
            "revenue": 22.0,
            "employees": 70,
            "growth_rate": 24.0,
            "profit_margin": 11.0,
            "funding_raised": 16.0,
            "valuation": 180.0,
        },
    }

    company = Company.model_validate(persisted)
    dumped = company.model_dump()

    assert dumped["financials"]["revenue"] == 22.0
    assert dumped["financials"]["employees"] == 70
    assert dumped["financials"]["growth_rate"] == 24.0
    assert dumped["financials"]["profit_margin"] == 11.0
    assert dumped["financials"]["funding_raised"] == 16.0
    assert dumped["financials"]["valuation"] == 180.0

    assert dumped["revenue"] == 22.0
    assert dumped["employees"] == 70
    assert dumped["growth_rate"] == 24.0
    assert dumped["profit_margin"] == 11.0
    assert dumped["funding"] == 16.0
    assert dumped["valuation"] == 180.0


def test_api_response_contract_fields_are_stable() -> None:
    company = Company.model_validate(
        {
            "id": "api-shape-1",
            "name": "API Shape Co",
            "industry": "Energy",
            "financials": {
                "revenue": 10.0,
                "employees": 20,
                "growth_rate": 12.0,
                "profit_margin": 6.0,
                "valuation": 50.0,
            },
            "classification": "Lead",
        }
    )

    api_payload = company.model_dump(mode="json")

    required_top_level = {
        "id",
        "name",
        "industry",
        "financials",
        "revenue",
        "employees",
        "growth_rate",
        "profit_margin",
        "valuation",
        "classification",
    }

    assert required_top_level.issubset(set(api_payload.keys()))
    assert isinstance(api_payload["financials"], dict)
    financials_payload = cast(dict[str, object], api_payload["financials"])

    required_financial_keys = {
        "revenue",
        "employees",
        "growth_rate",
        "profit_margin",
        "valuation",
    }
    assert required_financial_keys.issubset(set(financials_payload.keys()))


def test_mixed_payload_contract_is_deterministic_for_overlaps() -> None:
    mixed = {
        "id": "mixed-contract-1",
        "name": "Mixed Contract Co",
        "industry": "Energy",
        "revenue": 9.0,
        "employees": 25,
        "financials": {
            "revenue": 12.0,
            "employees": 30,
            "growth_rate": 15.0,
        },
    }

    dumped = Company.model_validate(mixed).model_dump()

    # Contract expectation under current validator: nested financial values remain authoritative.
    assert dumped["financials"]["revenue"] == 12.0
    assert dumped["financials"]["employees"] == 30
    # Flat fields are preserved for backward compatibility.
    assert dumped["revenue"] == 9.0
    assert dumped["employees"] == 25
