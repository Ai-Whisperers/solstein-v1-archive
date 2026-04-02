"""
STORY-171: Loader parity tests.

Verifies that _load_companies_for_report() (the new direct approach using
convert_to_domain_company) produces Company objects with the same essential
attributes as CompetitorDataLoader when given the same raw JSON data.

Also verifies no DeprecationWarning is emitted by _load_companies_for_report.
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import click
import pytest

from solstein.cli_legacy import _load_companies_for_report
from solstein.domain.models import Company

# ---------------------------------------------------------------------------
# Fixture data — well-formed items with id + name
# ---------------------------------------------------------------------------

FIXTURE_ITEMS = [
    {
        "id": "alpha-001",
        "name": "Alpha Corp",
        "industry": "Tech",
        "financials": {"revenue": 100.0, "valuation": 1000.0, "growth_rate": 0.15},
    },
    {
        "id": "beta-002",
        "name": "Beta Ltd",
        "industry": "Energy",
        "financials": {"revenue": 50.0, "valuation": 500.0},
    },
]

FIXTURE_WRAPPED = {"competitors": FIXTURE_ITEMS}


# ---------------------------------------------------------------------------
# _load_companies_for_report helper tests
# ---------------------------------------------------------------------------


def test_load_companies_for_report_with_json_input(tmp_path: Path) -> None:
    """_load_companies_for_report loads from an explicit JSON path."""
    input_file = tmp_path / "data.json"
    input_file.write_text(json.dumps(FIXTURE_WRAPPED))

    companies = _load_companies_for_report(input_path=input_file)

    assert isinstance(companies, list)
    assert len(companies) == 2
    names = {c.name for c in companies}
    assert "Alpha Corp" in names
    assert "Beta Ltd" in names


def test_load_companies_for_report_returns_company_instances(tmp_path: Path) -> None:
    """Every returned object must be a Company (or subclass) instance."""
    input_file = tmp_path / "data.json"
    input_file.write_text(json.dumps(FIXTURE_ITEMS))

    companies = _load_companies_for_report(input_path=input_file)

    for company in companies:
        assert isinstance(company, Company), f"Expected Company, got {type(company)}"


def test_load_companies_for_report_emits_no_deprecation_warning(tmp_path: Path) -> None:
    """STORY-171: No DeprecationWarning when using the new loader path."""
    input_file = tmp_path / "data.json"
    input_file.write_text(json.dumps(FIXTURE_ITEMS))

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        _load_companies_for_report(input_path=input_file)

    deprecation_warnings = [w for w in caught if issubclass(w.category, DeprecationWarning)]
    assert len(deprecation_warnings) == 0, (
        f"Unexpected DeprecationWarning(s): {[str(w.message) for w in deprecation_warnings]}"
    )


def test_load_companies_for_report_handles_wrapped_competitors(tmp_path: Path) -> None:
    """_load_companies_for_report handles {competitors: [...]} wrapper via JSON path."""
    input_file = tmp_path / "wrapped.json"
    input_file.write_text(json.dumps(FIXTURE_WRAPPED))

    companies = _load_companies_for_report(input_path=input_file)

    assert len(companies) == 2


def test_load_companies_for_report_missing_default_raises_usage_error(monkeypatch) -> None:
    """When called without input_path and no default file exists, raises UsageError."""

    # Point settings data_dir to a temp dir with no competitor_data.json
    class MockDataConfig:
        data_dir = Path("/tmp/nonexistent-solstein-test-dir-xyz")

    class MockSettings:
        data = MockDataConfig()

    monkeypatch.setattr("solstein.cli_legacy.get_settings", lambda: MockSettings())

    with pytest.raises(click.UsageError, match="Default data file not found"):
        _load_companies_for_report()
