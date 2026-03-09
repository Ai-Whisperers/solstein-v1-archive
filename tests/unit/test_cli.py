"""
Tests for CLI commands.
"""

import json

from click.testing import CliRunner

import solstein.cli as cli_module
from solstein.cli import cli


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["version"])
    assert result.exit_code == 0
    assert "SolStein" in result.output


def test_cli_extract_no_profiles(tmp_path):
    runner = CliRunner()
    result = runner.invoke(cli, ["extract", str(tmp_path)])
    assert result.exit_code == 0
    assert "No profiles extracted" in result.output


def test_cli_score(tmp_path):
    # Create mock input JSON
    input_file = tmp_path / "input.json"
    output_file = tmp_path / "output.json"
    data = [
        {
            "id": "c01",
            "name": "TestCorp",
            "industry": "Tech",
            "financials": {"revenue": 100.0, "valuation": 1000.0},
        }
    ]
    input_file.write_text(json.dumps(data))

    runner = CliRunner()
    result = runner.invoke(cli, ["score", str(input_file), "-o", str(output_file)])
    assert result.exit_code == 0
    assert "Calculating scores" in result.output
    assert output_file.exists()


def test_cli_analyze_market(tmp_path):
    input_file = tmp_path / "input.json"
    data = [
        {
            "id": "c01",
            "name": "TestCorp",
            "industry": "Tech",
            "financials": {"revenue": 100.0, "valuation": 1000.0},
        }
    ]
    input_file.write_text(json.dumps(data))

    runner = CliRunner()
    result = runner.invoke(cli, ["analyze-market", str(input_file), "-n", "Test Market"])
    assert result.exit_code == 0
    assert "Analyzing market: Test Market" in result.output
    assert "Companies: 1" in result.output


def test_cli_compare(tmp_path):
    input_file = tmp_path / "input.json"
    data = [
        {
            "id": "c01",
            "name": "Alpha",
            "industry": "Tech",
            "financials": {"revenue": 100.0, "valuation": 1000.0},
        },
        {
            "id": "c02",
            "name": "Beta",
            "industry": "Tech",
            "financials": {"revenue": 50.0, "valuation": 500.0},
        },
    ]
    input_file.write_text(json.dumps(data))

    runner = CliRunner()
    result = runner.invoke(cli, ["compare", "c01", "c02", str(input_file)])
    assert result.exit_code == 0
    assert "Comparing c01 vs c02" in result.output
    assert "Alpha vs Beta" in result.output


def test_cli_compare_not_found(tmp_path):
    input_file = tmp_path / "input.json"
    input_file.write_text("[]")

    runner = CliRunner()
    result = runner.invoke(cli, ["compare", "c1", "c2", str(input_file)])
    assert result.exit_code == 0
    assert "Profile not found: c1" in result.output


def test_cli_verbose(tmp_path):
    input_file = tmp_path / "input.json"
    input_file.write_text("not json")

    runner = CliRunner()
    result = runner.invoke(cli, ["-v", "analyze-market", str(input_file)])
    assert result.exit_code != 0
    assert "Failed to analyze market" in result.output


def test_cli_score_accepts_wrapped_competitors_payload(tmp_path):
    input_file = tmp_path / "wrapped.json"
    output_file = tmp_path / "scored.json"
    wrapped_data = {
        "competitors": [
            {
                "id": "cmp-001",
                "name": "Alpha",
                "industry": "Tech",
                "financials": {"revenue": 100.0, "valuation": 1000.0},
            },
            {
                "id": "cmp-002",
                "name": "Beta",
                "industry": "Tech",
                "financials": {"revenue": 80.0, "valuation": 700.0},
            },
        ]
    }
    input_file.write_text(json.dumps(wrapped_data))

    runner = CliRunner()
    result = runner.invoke(cli, ["score", str(input_file), "-o", str(output_file)])

    assert result.exit_code == 0
    assert output_file.exists()


def test_cli_compare_rejects_unknown_object_payload(tmp_path):
    input_file = tmp_path / "invalid_payload.json"
    input_file.write_text(json.dumps({"unexpected": []}))

    runner = CliRunner()
    result = runner.invoke(cli, ["compare", "c1", "c2", str(input_file)])

    assert result.exit_code != 0
    assert "Unsupported input format" in result.output


def test_cli_analyze_market_accepts_wrapped_companies_payload(tmp_path):
    input_file = tmp_path / "wrapped_companies.json"
    wrapped_data = {
        "companies": [
            {
                "id": "cmp-101",
                "name": "Gamma",
                "industry": "Tech",
                "financials": {"revenue": 120.0, "valuation": 900.0},
            }
        ]
    }
    input_file.write_text(json.dumps(wrapped_data))

    runner = CliRunner()
    result = runner.invoke(cli, ["analyze-market", str(input_file), "-n", "Wrapped Market"])

    assert result.exit_code == 0
    assert "Analyzing market: Wrapped Market" in result.output
    assert "Companies: 1" in result.output


def test_cli_export_excel_rejects_unknown_object_payload(tmp_path):
    input_file = tmp_path / "invalid_export_payload.json"
    output_file = tmp_path / "out.xlsx"
    input_file.write_text(json.dumps({"unexpected": []}))

    runner = CliRunner()
    result = runner.invoke(cli, ["export-excel", str(input_file), str(output_file)])

    assert result.exit_code != 0
    assert "Unsupported input format" in result.output


def test_generate_report_default_output_dir_not_company_nested(monkeypatch):
    captured = {}

    class DummyScorer:
        def calculate_scores(self, company):
            return company

    class DummyLoader:
        def load_competitors(self, _path=None):
            return [
                cli_module.Company(
                    id="cmp-201", name="Acme", industry="Tech", financials={"revenue": 100.0, "valuation": 500.0}
                ),
                cli_module.Company(
                    id="cmp-202", name="Beta", industry="Tech", financials={"revenue": 80.0, "valuation": 450.0}
                ),
            ]

        def load_companies(self, _path=None):
            return self.load_competitors(_path)

    class DummyGenerator:
        def __init__(self, output_dir):
            captured["output_dir"] = str(output_dir)

        def generate_client_report(self, _target, _competitors):
            return {"client_report": "ok"}

    monkeypatch.setattr(cli_module, "CompetitorDataLoader", DummyLoader)
    monkeypatch.setattr(cli_module, "GrowthScorer", DummyScorer)
    monkeypatch.setattr(cli_module, "assert_client_report_ready", lambda *_, **__: None)
    monkeypatch.setattr(cli_module, "ClientReportGenerator", DummyGenerator)

    runner = CliRunner()
    result = runner.invoke(cli, ["generate-report", "Acme"])

    assert result.exit_code == 0
    assert captured["output_dir"] == "data/output/reports"


def test_generate_llm_report_default_output_dir_not_company_nested(monkeypatch):
    captured = {}

    class DummyScorer:
        def calculate_scores(self, company):
            return company

    class DummyLoader:
        def load_competitors(self, _path=None):
            return [
                cli_module.Company(
                    id="cmp-301", name="Acme", industry="Tech", financials={"revenue": 100.0, "valuation": 500.0}
                ),
                cli_module.Company(
                    id="cmp-302", name="Beta", industry="Tech", financials={"revenue": 80.0, "valuation": 450.0}
                ),
            ]

        def load_companies(self, _path=None):
            return self.load_competitors(_path)

    class DummyGenerator:
        def __init__(self, output_dir):
            captured["output_dir"] = str(output_dir)

        def generate_client_report(self, _target, _competitors):
            return {"client_report": "ok"}

    monkeypatch.setattr(cli_module, "CompetitorDataLoader", DummyLoader)
    monkeypatch.setattr(cli_module, "GrowthScorer", DummyScorer)
    monkeypatch.setattr(cli_module, "assert_client_report_ready", lambda *_, **__: None)
    monkeypatch.setattr(cli_module, "ClientReportGenerator", DummyGenerator)

    runner = CliRunner()
    result = runner.invoke(cli, ["generate-llm-report", "Acme", "--no-llm"])

    assert result.exit_code == 0
    assert captured["output_dir"] == "data/output/reports/llm"
