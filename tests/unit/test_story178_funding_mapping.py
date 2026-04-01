"""
STORY-178: Map `funding_raised` to top-level funding fields on Company.

Verifies that convert_to_domain_company() correctly populates
Company.total_funding_raised_eur, Company.latest_valuation_eur,
Company.funding_rounds, and Company.lead_investors from raw JSON.

Prior to this fix, these fields were always None despite funding data
being present in the source JSON, causing reports to show "No funding data".
"""

from __future__ import annotations

import pytest

from solstein.data.converters.company import convert_to_domain_company

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FUNDED_COMPANY = {
    "id": "test-001",
    "name": "Funded Corp",
    "industry": "Energy Software",
    "financials": {"revenue": 10.0, "employees": 50},
    "funding_raised": 2_000_000.0,
    "valuation": 50_000_000.0,
    "funding_rounds": [
        {"round": "Seed", "amount_eur": 500_000, "date": "2022-01"},
        {"round": "Series A", "amount_eur": 1_500_000, "date": "2023-06"},
    ],
    "lead_investors": ["InnoFund", "EnergyVC"],
}

UNFUNDED_COMPANY = {
    "id": "test-002",
    "name": "Bootstrap Corp",
    "industry": "Energy Software",
    "financials": {"revenue": 5.0, "employees": 10},
}

LARGE_FUNDING_COMPANY = {
    "id": "test-003",
    "name": "Unicorn Corp",
    "industry": "Energy Software",
    "financials": {"revenue": 100.0, "employees": 500},
    "funding_raised": 15_000_000.0,
    "valuation": 200_000_000.0,
}


# ---------------------------------------------------------------------------
# STORY-178: total_funding_raised_eur
# ---------------------------------------------------------------------------


def test_total_funding_raised_eur_populated_from_json() -> None:
    """Company.total_funding_raised_eur is set from JSON funding_raised (raw EUR)."""
    company = convert_to_domain_company(FUNDED_COMPANY)
    assert company.total_funding_raised_eur == 2_000_000.0


def test_total_funding_raised_eur_none_when_missing() -> None:
    """Company.total_funding_raised_eur is None when JSON has no funding data."""
    company = convert_to_domain_company(UNFUNDED_COMPANY)
    assert company.total_funding_raised_eur is None


def test_total_funding_raised_eur_large_value() -> None:
    """Funding amounts above €10M are preserved with full precision."""
    company = convert_to_domain_company(LARGE_FUNDING_COMPANY)
    assert company.total_funding_raised_eur == 15_000_000.0


# ---------------------------------------------------------------------------
# STORY-178: latest_valuation_eur
# ---------------------------------------------------------------------------


def test_latest_valuation_eur_populated() -> None:
    """Company.latest_valuation_eur is set from JSON valuation (raw EUR)."""
    company = convert_to_domain_company(FUNDED_COMPANY)
    assert company.latest_valuation_eur == 50_000_000.0


def test_latest_valuation_eur_none_when_missing() -> None:
    """Company.latest_valuation_eur is None when JSON has no valuation."""
    company = convert_to_domain_company(UNFUNDED_COMPANY)
    assert company.latest_valuation_eur is None


# ---------------------------------------------------------------------------
# STORY-178: funding_rounds
# ---------------------------------------------------------------------------


def test_funding_rounds_populated_from_json() -> None:
    """Company.funding_rounds contains the raw round objects from JSON."""
    company = convert_to_domain_company(FUNDED_COMPANY)
    assert isinstance(company.funding_rounds, list)
    assert len(company.funding_rounds) == 2
    rounds = {r["round"] for r in company.funding_rounds}
    assert "Seed" in rounds
    assert "Series A" in rounds


def test_funding_rounds_empty_when_missing() -> None:
    """Company.funding_rounds defaults to [] when JSON has no rounds."""
    company = convert_to_domain_company(UNFUNDED_COMPANY)
    assert company.funding_rounds == []


# ---------------------------------------------------------------------------
# STORY-178: lead_investors
# ---------------------------------------------------------------------------


def test_lead_investors_populated() -> None:
    """Company.lead_investors is set from JSON lead_investors list."""
    company = convert_to_domain_company(FUNDED_COMPANY)
    assert company.lead_investors == ["InnoFund", "EnergyVC"]


def test_lead_investors_empty_when_missing() -> None:
    """Company.lead_investors defaults to [] when JSON has no investor data."""
    company = convert_to_domain_company(UNFUNDED_COMPANY)
    assert company.lead_investors == []


# ---------------------------------------------------------------------------
# Integration: GrowthMomentumScorer uses funding data
# ---------------------------------------------------------------------------


def test_funded_company_total_funding_is_raw_eur_not_millions() -> None:
    """Confirm total_funding_raised_eur is NOT normalized to millions.

    financials.funding_raised stores EUR millions (e.g. 2.0 for €2M).
    total_funding_raised_eur stores raw EUR (e.g. 2_000_000.0 for €2M).
    They serve different purposes — this test guards against regression.
    """
    company = convert_to_domain_company(FUNDED_COMPANY)
    # total_funding_raised_eur is raw EUR
    assert company.total_funding_raised_eur == 2_000_000.0
    # financials.funding_raised is EUR millions (normalized)
    assert company.financials is not None
    assert company.financials.funding_raised == pytest.approx(2.0, abs=0.01)
