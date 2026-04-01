"""
STORY-172: Tests for CLI input validation.

Covers all failure modes in cli_validators:
  - validate_input_file: missing, directory, empty, bad JSON, bad structure
  - validate_company_exists: no match, ambiguous match, exact match, id match, substring
  - validate_output_dir: create on missing, fail on unwritable
"""

from __future__ import annotations

import json
import stat
from pathlib import Path

import click
import pytest
from click.testing import CliRunner

from solstein.cli_legacy import cli
from solstein.cli_validators import (
    validate_company_exists,
    validate_input_file,
    validate_output_dir,
)
from solstein.domain.models import Company

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_company(id: str, name: str) -> Company:
    return Company(
        id=id,
        name=name,
        industry="Tech",
        financials={"revenue": 100.0, "valuation": 500.0},
    )


# ---------------------------------------------------------------------------
# validate_input_file
# ---------------------------------------------------------------------------


def test_validate_input_file_missing(tmp_path: Path) -> None:
    """Non-existent path raises UsageError mentioning 'not found'."""
    missing = tmp_path / "ghost.json"
    with pytest.raises(click.UsageError, match="not found"):
        validate_input_file(missing)


def test_validate_input_file_is_directory(tmp_path: Path) -> None:
    """Passing a directory raises UsageError."""
    with pytest.raises(click.UsageError, match="directory"):
        validate_input_file(tmp_path)


def test_validate_input_file_empty(tmp_path: Path) -> None:
    """Empty file raises UsageError."""
    empty = tmp_path / "empty.json"
    empty.write_text("")
    with pytest.raises(click.UsageError, match="empty"):
        validate_input_file(empty)


def test_validate_input_file_invalid_json(tmp_path: Path) -> None:
    """Malformed JSON raises UsageError mentioning 'Invalid JSON'."""
    bad = tmp_path / "bad.json"
    bad.write_text("{this is not valid json}")
    with pytest.raises(click.UsageError, match="Invalid JSON"):
        validate_input_file(bad)


def test_validate_input_file_accepts_flat_list(tmp_path: Path) -> None:
    """Flat list of objects is a valid structure — no error raised."""
    f = tmp_path / "flat.json"
    f.write_text(json.dumps([{"id": "x", "name": "X"}]))
    validate_input_file(f)  # must not raise


def test_validate_input_file_accepts_wrapped_competitors(tmp_path: Path) -> None:
    """{'competitors': [...]} wrapper is a valid structure."""
    f = tmp_path / "wrapped.json"
    f.write_text(json.dumps({"competitors": [{"id": "x", "name": "X"}]}))
    validate_input_file(f)  # must not raise


def test_validate_input_file_accepts_wrapped_companies(tmp_path: Path) -> None:
    """{'companies': [...]} wrapper is a valid structure."""
    f = tmp_path / "wrapped2.json"
    f.write_text(json.dumps({"companies": [{"id": "x", "name": "X"}]}))
    validate_input_file(f)  # must not raise


def test_validate_input_file_accepts_wrapped_data(tmp_path: Path) -> None:
    """{'data': [...]} wrapper is a valid structure."""
    f = tmp_path / "wrapped3.json"
    f.write_text(json.dumps({"data": [{"id": "x", "name": "X"}]}))
    validate_input_file(f)  # must not raise


def test_validate_input_file_rejects_unknown_object(tmp_path: Path) -> None:
    """Dict with no recognised wrapper key raises UsageError."""
    f = tmp_path / "bad_struct.json"
    f.write_text(json.dumps({"unexpected_key": []}))
    with pytest.raises(click.UsageError, match="Unsupported JSON structure"):
        validate_input_file(f)


def test_validate_input_file_rejects_scalar(tmp_path: Path) -> None:
    """A bare JSON number/string raises UsageError."""
    f = tmp_path / "scalar.json"
    f.write_text("42")
    with pytest.raises(click.UsageError, match="Unsupported JSON structure"):
        validate_input_file(f)


# ---------------------------------------------------------------------------
# validate_company_exists
# ---------------------------------------------------------------------------


COMPANIES = [
    _make_company("alpha-001", "Alpha Corp"),
    _make_company("beta-002", "Beta Ltd"),
    _make_company("gamma-003", "Gamma Industries"),
]


def test_validate_company_exists_exact_id() -> None:
    """Exact ID match returns the right company."""
    result = validate_company_exists(COMPANIES, "beta-002")
    assert result.name == "Beta Ltd"


def test_validate_company_exists_exact_name_case_insensitive() -> None:
    """Exact name match is case-insensitive."""
    result = validate_company_exists(COMPANIES, "alpha corp")
    assert result.id == "alpha-001"


def test_validate_company_exists_substring_match() -> None:
    """Unique substring match returns the company."""
    result = validate_company_exists(COMPANIES, "Gamma")
    assert result.id == "gamma-003"


def test_validate_company_exists_not_found_raises() -> None:
    """No match raises UsageError mentioning the name."""
    with pytest.raises(click.UsageError, match="not found"):
        validate_company_exists(COMPANIES, "Nonexistent Corp")


def test_validate_company_exists_did_you_mean_hint() -> None:
    """A near-miss name gets a 'Did you mean?' suggestion."""
    with pytest.raises(click.UsageError, match="Did you mean"):
        validate_company_exists(COMPANIES, "Alph Corp")


def test_validate_company_exists_ambiguous_raises() -> None:
    """Substring that matches multiple companies raises UsageError."""
    companies = [
        _make_company("a001", "Alpha One"),
        _make_company("a002", "Alpha Two"),
    ]
    with pytest.raises(click.UsageError, match="ambiguous"):
        validate_company_exists(companies, "Alpha")


def test_validate_company_exists_available_companies_listed() -> None:
    """Error message lists available company names."""
    with pytest.raises(click.UsageError, match="Available companies"):
        validate_company_exists(COMPANIES, "Unknown Co")


# ---------------------------------------------------------------------------
# validate_output_dir
# ---------------------------------------------------------------------------


def test_validate_output_dir_creates_missing_dir(tmp_path: Path) -> None:
    """validate_output_dir creates the directory when it does not exist."""
    target = tmp_path / "new" / "nested" / "dir"
    assert not target.exists()
    result = validate_output_dir(target)
    assert target.exists()
    assert target.is_dir()
    assert result == target


def test_validate_output_dir_accepts_existing_dir(tmp_path: Path) -> None:
    """validate_output_dir is a no-op on an already-existing writable dir."""
    result = validate_output_dir(tmp_path)
    assert result == tmp_path


def test_validate_output_dir_returns_path(tmp_path: Path) -> None:
    """validate_output_dir returns the validated path for chaining."""
    returned = validate_output_dir(tmp_path)
    assert returned == tmp_path


@pytest.mark.skipif(
    __import__("os").getuid() == 0,
    reason="Root can write anywhere — skip unwritable-dir test",
)
def test_validate_output_dir_unwritable_raises(tmp_path: Path) -> None:
    """Unwritable directory raises UsageError."""
    locked = tmp_path / "locked"
    locked.mkdir()
    locked.chmod(stat.S_IRUSR | stat.S_IXUSR)  # read + execute only

    try:
        with pytest.raises(click.UsageError, match="not writable"):
            validate_output_dir(locked)
    finally:
        locked.chmod(stat.S_IRWXU)  # restore so tmp_path cleanup works


# ---------------------------------------------------------------------------
# Integration: CLI commands reject bad input early
# ---------------------------------------------------------------------------


def test_cli_score_missing_file_error(tmp_path: Path) -> None:
    """score command with a non-existent file exits non-zero with clear message."""
    runner = CliRunner()
    missing = tmp_path / "missing.json"
    # click.Path(exists=True) rejects missing files at argument level
    result = runner.invoke(cli, ["score", str(missing)])
    assert result.exit_code != 0


def test_cli_compare_bad_json_exits_nonzero(tmp_path: Path) -> None:
    """compare command with malformed JSON exits non-zero."""
    bad = tmp_path / "bad.json"
    bad.write_text("not json at all")
    runner = CliRunner()
    result = runner.invoke(cli, ["compare", "c1", "c2", str(bad)])
    assert result.exit_code != 0


def test_cli_analyze_market_unknown_structure_exits_nonzero(tmp_path: Path) -> None:
    """analyze-market with unknown JSON structure exits non-zero with clear message."""
    f = tmp_path / "bad_struct.json"
    f.write_text(json.dumps({"unexpected": []}))
    runner = CliRunner()
    result = runner.invoke(cli, ["analyze-market", str(f)])
    assert result.exit_code != 0
    assert "Unsupported" in result.output or "Unsupported" in (result.exception and str(result.exception) or "")
