"""
Tests for CLI commands.
"""

import json

from click.testing import CliRunner

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
            "id": "c1",
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
            "id": "c1",
            "name": "TestCorp",
            "industry": "Tech",
            "financials": {"revenue": 100.0, "valuation": 1000.0},
        }
    ]
    input_file.write_text(json.dumps(data))

    runner = CliRunner()
    result = runner.invoke(
        cli, ["analyze-market", str(input_file), "-n", "Test Market"]
    )
    assert result.exit_code == 0
    assert "Analyzing market: Test Market" in result.output
    assert "Companies: 1" in result.output


def test_cli_compare(tmp_path):
    input_file = tmp_path / "input.json"
    data = [
        {
            "id": "c1",
            "name": "Alpha",
            "industry": "Tech",
            "financials": {"revenue": 100.0, "valuation": 1000.0},
        },
        {
            "id": "c2",
            "name": "Beta",
            "industry": "Tech",
            "financials": {"revenue": 50.0, "valuation": 500.0},
        },
    ]
    input_file.write_text(json.dumps(data))

    runner = CliRunner()
    result = runner.invoke(cli, ["compare", "c1", "c2", str(input_file)])
    assert result.exit_code == 0
    assert "Comparing c1 vs c2" in result.output
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
