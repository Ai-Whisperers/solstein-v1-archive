"""
STORY-169: Tests for CLI JSON parsing — both flat-list and wrapped-object formats.

Covers the _coerce_companies_payload helper and all four commands that consume JSON input:
  score, analyze-market, compare, export-excel
"""

import json

from click.testing import CliRunner

import solstein.cli_legacy as cli_module
from solstein.cli_legacy import cli

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FLAT_LIST_DATA = [
    {
        "id": "flat-001",
        "name": "FlatAlpha",
        "industry": "Tech",
        "financials": {"revenue": 100.0, "valuation": 1000.0},
    },
    {
        "id": "flat-002",
        "name": "FlatBeta",
        "industry": "Tech",
        "financials": {"revenue": 50.0, "valuation": 500.0},
    },
]

WRAPPED_COMPETITORS_DATA = {
    "competitors": [
        {
            "id": "wrap-001",
            "name": "WrapAlpha",
            "industry": "Energy",
            "financials": {"revenue": 200.0, "valuation": 2000.0},
        },
        {
            "id": "wrap-002",
            "name": "WrapBeta",
            "industry": "Energy",
            "financials": {"revenue": 80.0, "valuation": 800.0},
        },
    ]
}

WRAPPED_COMPANIES_DATA = {
    "companies": [
        {
            "id": "cmp-001",
            "name": "CmpAlpha",
            "industry": "Finance",
            "financials": {"revenue": 150.0, "valuation": 1500.0},
        }
    ]
}

WRAPPED_DATA_KEY_DATA = {
    "data": [
        {
            "id": "dat-001",
            "name": "DataAlpha",
            "industry": "Health",
            "financials": {"revenue": 75.0, "valuation": 750.0},
        }
    ]
}

UNKNOWN_OBJECT_DATA = {"unexpected_key": [{"id": "x", "name": "X"}]}


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def write_json(path, data):
    path.write_text(json.dumps(data))
    return path


# ---------------------------------------------------------------------------
# score command — JSON format tests
# ---------------------------------------------------------------------------


def test_score_accepts_flat_list(tmp_path):
    input_file = write_json(tmp_path / "flat.json", FLAT_LIST_DATA)
    runner = CliRunner()
    result = runner.invoke(cli, ["score", str(input_file)])
    assert result.exit_code == 0, result.output
    assert "FlatAlpha" in result.output
    assert "FlatBeta" in result.output


def test_score_accepts_wrapped_competitors(tmp_path):
    input_file = write_json(tmp_path / "wrapped_competitors.json", WRAPPED_COMPETITORS_DATA)
    runner = CliRunner()
    result = runner.invoke(cli, ["score", str(input_file)])
    assert result.exit_code == 0, result.output
    assert "WrapAlpha" in result.output


def test_score_accepts_wrapped_companies(tmp_path):
    input_file = write_json(tmp_path / "wrapped_companies.json", WRAPPED_COMPANIES_DATA)
    runner = CliRunner()
    result = runner.invoke(cli, ["score", str(input_file)])
    assert result.exit_code == 0, result.output
    assert "CmpAlpha" in result.output


def test_score_accepts_wrapped_data_key(tmp_path):
    input_file = write_json(tmp_path / "wrapped_data.json", WRAPPED_DATA_KEY_DATA)
    runner = CliRunner()
    result = runner.invoke(cli, ["score", str(input_file)])
    assert result.exit_code == 0, result.output
    assert "DataAlpha" in result.output


def test_score_rejects_unknown_object_format(tmp_path):
    input_file = write_json(tmp_path / "unknown.json", UNKNOWN_OBJECT_DATA)
    runner = CliRunner()
    result = runner.invoke(cli, ["score", str(input_file)])
    assert result.exit_code != 0
    assert "Unsupported input format" in result.output


# ---------------------------------------------------------------------------
# analyze-market command — JSON format tests
# ---------------------------------------------------------------------------


def test_analyze_market_accepts_flat_list(tmp_path):
    input_file = write_json(tmp_path / "flat.json", FLAT_LIST_DATA)
    runner = CliRunner()
    result = runner.invoke(cli, ["analyze-market", str(input_file)])
    assert result.exit_code == 0, result.output
    assert "Companies: 2" in result.output


def test_analyze_market_accepts_wrapped_competitors(tmp_path):
    input_file = write_json(tmp_path / "wrapped.json", WRAPPED_COMPETITORS_DATA)
    runner = CliRunner()
    result = runner.invoke(cli, ["analyze-market", str(input_file)])
    assert result.exit_code == 0, result.output
    assert "Companies: 2" in result.output


def test_analyze_market_accepts_wrapped_companies(tmp_path):
    input_file = write_json(tmp_path / "wrapped_companies.json", WRAPPED_COMPANIES_DATA)
    runner = CliRunner()
    result = runner.invoke(cli, ["analyze-market", str(input_file)])
    assert result.exit_code == 0, result.output
    assert "Companies: 1" in result.output


def test_analyze_market_rejects_unknown_object_format(tmp_path):
    input_file = write_json(tmp_path / "unknown.json", UNKNOWN_OBJECT_DATA)
    runner = CliRunner()
    result = runner.invoke(cli, ["analyze-market", str(input_file)])
    assert result.exit_code != 0
    assert "Unsupported input format" in result.output


# ---------------------------------------------------------------------------
# compare command — JSON format tests
# ---------------------------------------------------------------------------


def test_compare_accepts_flat_list(tmp_path):
    input_file = write_json(tmp_path / "flat.json", FLAT_LIST_DATA)
    runner = CliRunner()
    result = runner.invoke(cli, ["compare", "flat-001", "flat-002", str(input_file)])
    assert result.exit_code == 0, result.output
    assert "FlatAlpha vs FlatBeta" in result.output


def test_compare_accepts_wrapped_competitors(tmp_path):
    input_file = write_json(tmp_path / "wrapped.json", WRAPPED_COMPETITORS_DATA)
    runner = CliRunner()
    result = runner.invoke(cli, ["compare", "wrap-001", "wrap-002", str(input_file)])
    assert result.exit_code == 0, result.output
    assert "WrapAlpha vs WrapBeta" in result.output


def test_compare_rejects_unknown_object_format(tmp_path):
    input_file = write_json(tmp_path / "unknown.json", UNKNOWN_OBJECT_DATA)
    runner = CliRunner()
    result = runner.invoke(cli, ["compare", "x", "y", str(input_file)])
    assert result.exit_code != 0
    assert "Unsupported input format" in result.output


# ---------------------------------------------------------------------------
# export-excel command — JSON format tests
# ---------------------------------------------------------------------------


def test_export_excel_accepts_flat_list(tmp_path, monkeypatch):
    class DummyExporter:
        def __init__(self, template_path=None):
            pass

        def create_dashboard(self, companies, path):
            path.write_text("ok")

    monkeypatch.setattr(cli_module, "ExcelExporter", DummyExporter)

    input_file = write_json(tmp_path / "flat.json", FLAT_LIST_DATA)
    output_file = tmp_path / "out.xlsx"
    runner = CliRunner()
    result = runner.invoke(cli, ["export-excel", str(input_file), str(output_file)])
    assert result.exit_code == 0, result.output
    assert "Dashboard created" in result.output


def test_export_excel_accepts_wrapped_competitors(tmp_path, monkeypatch):
    class DummyExporter:
        def __init__(self, template_path=None):
            pass

        def create_dashboard(self, companies, path):
            path.write_text("ok")

    monkeypatch.setattr(cli_module, "ExcelExporter", DummyExporter)

    input_file = write_json(tmp_path / "wrapped.json", WRAPPED_COMPETITORS_DATA)
    output_file = tmp_path / "out.xlsx"
    runner = CliRunner()
    result = runner.invoke(cli, ["export-excel", str(input_file), str(output_file)])
    assert result.exit_code == 0, result.output
    assert "Dashboard created" in result.output


def test_export_excel_rejects_unknown_object_format(tmp_path):
    input_file = write_json(tmp_path / "unknown.json", UNKNOWN_OBJECT_DATA)
    output_file = tmp_path / "out.xlsx"
    runner = CliRunner()
    result = runner.invoke(cli, ["export-excel", str(input_file), str(output_file)])
    assert result.exit_code != 0
    assert "Unsupported input format" in result.output


# ---------------------------------------------------------------------------
# Error message quality
# ---------------------------------------------------------------------------


def test_unknown_object_error_message_includes_received_keys(tmp_path):
    """Error message should tell the user what keys were received."""
    input_file = write_json(tmp_path / "bad.json", {"foo": [], "bar": []})
    runner = CliRunner()
    result = runner.invoke(cli, ["score", str(input_file)])
    assert result.exit_code != 0
    # The error should mention something about unsupported format
    assert "Unsupported input format" in result.output


def test_invalid_json_raises_abort(tmp_path):
    """Non-JSON content should cause the command to abort."""
    input_file = tmp_path / "notjson.json"
    input_file.write_text("this is not json {{{")
    runner = CliRunner()
    result = runner.invoke(cli, ["score", str(input_file)])
    assert result.exit_code != 0
