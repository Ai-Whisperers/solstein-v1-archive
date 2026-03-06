import pytest
from pydantic import ValidationError

from solstein.domain.models import Company


def test_legacy_flat_payload_parses_and_syncs() -> None:
    payload = {
        "id": "legacy-test",
        "name": "Legacy Test Co",
        "industry": "Energy Software",
        "revenue": 20.0,
        "employees": 60,
        "growth_rate": 25.0,
        "profit_margin": 11.0,
        "funding": 6.0,
        "valuation": 130.0,
    }

    company = Company.model_validate(payload)

    assert company.financials.revenue == 20.0
    assert company.financials.employees == 60
    assert company.financials.growth_rate == 25.0


def test_nested_payload_parses_and_round_trips() -> None:
    payload = {
        "id": "nested-test",
        "name": "Nested Test Co",
        "industry": "Energy Software",
        "financials": {
            "revenue": 15.0,
            "employees": 45,
            "growth_rate": 18.0,
            "profit_margin": 13.0,
            "funding_raised": 4.0,
            "valuation": 90.0,
        },
    }

    company = Company.model_validate(payload)
    dumped = company.model_dump()

    assert dumped["financials"]["revenue"] == 15.0
    assert dumped["financials"]["funding_raised"] == 4.0


def test_mixed_payload_resolves_deterministically() -> None:
    payload = {
        "id": "mixed-test",
        "name": "Mixed Test Co",
        "industry": "Energy Software",
        "revenue": 9.5,
        "employees": 22,
        "financials": {
            "revenue": 11.0,
            "employees": 30,
            "growth_rate": 17.0,
        },
    }

    company = Company.model_validate(payload)

    assert company.financials.revenue == 11.0
    assert company.financials.employees == 30
    assert company.revenue == 9.5
    assert company.employees == 22


def test_incompatible_payload_fails_with_explicit_reason() -> None:
    payload = {
        "id": "bad-test",
        "name": "Bad Test Co",
        "industry": "Energy Software",
        "revenue": "oops",
        "employees": -1,
    }

    with pytest.raises(ValidationError) as exc_info:
        _ = Company.model_validate(payload)

    errors_text = str(exc_info.value)
    assert "Input should be a valid number" in errors_text or "Employees cannot be negative" in errors_text
