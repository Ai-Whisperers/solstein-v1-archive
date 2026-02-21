import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from solstein.cli import cli
from solstein.domain.models import Company, FinancialMetric

@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()

@pytest.fixture
def mock_profiles(tmp_path: Path) -> Path:
    profiles = [
        {
            "id": "c1",
            "name": "Test1",
            "description": "d1",
            "financials": {"revenue": 1000.0, "growth_rate": 10.0},
            "tier": "Tier 1",
            "threat_level": "High",
            "ai_maturity": "Strong",
            "geographic_presence": ["US"],
            "tech_stack": ["Python"],
        },
        {
            "id": "c2",
            "name": "Test2",
            "description": "d2",
            "financials": {"revenue": 500.0, "employees": 50},
            "tier": "Tier 2",
            "threat_level": "Medium",
            "ai_maturity": "Moderate",
            "geographic_presence": ["UK"],
            "tech_stack": ["Java"],
        },
    ]
    file_path = tmp_path / "profiles.json"
    file_path.write_text(json.dumps(profiles))
    return file_path

def test_version_command(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["version"])
    assert result.exit_code == 0
    assert "SolStein v" in result.output

def test_verbose_logger(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["-v", "version"])
    assert result.exit_code == 0

@patch("solstein.cli.BatchExtractor")
def test_extract_command(mock_batch_cls: MagicMock, runner: CliRunner, tmp_path: Path) -> None:
    mock_batch = MagicMock()
    mock_batch_cls.return_value = mock_batch

    # Empty case
    mock_batch.extract_directory.return_value = []
    res = runner.invoke(cli, ["extract", str(tmp_path)])
    assert res.exit_code == 0
    assert "No profiles extracted" in res.output

    # Success case without output
    dummy_profile = MagicMock()
    dummy_profile.name = "Test"
    dummy_profile.id = "c1"
    mock_batch.extract_directory.return_value = [dummy_profile] * 6
    res = runner.invoke(cli, ["extract", str(tmp_path)])
    assert res.exit_code == 0
    assert "Extracted 6 profiles" in res.output
    assert "and 1 more" in res.output

    # Success case with output
    out_file = tmp_path / "out.json"
    res = runner.invoke(cli, ["extract", str(tmp_path), "-o", str(out_file)])
    assert res.exit_code == 0
    assert "Saved to" in res.output
    mock_batch.save_to_json.assert_called_once()

@patch("solstein.cli.ExcelExporter")
def test_export_excel_command(
    mock_exporter_cls: MagicMock, runner: CliRunner, mock_profiles: Path, tmp_path: Path
) -> None:
    mock_export = MagicMock()
    mock_exporter_cls.return_value = mock_export

    out_file = tmp_path / "out.xlsx"
    res = runner.invoke(cli, ["export-excel", str(mock_profiles), str(out_file)])
    assert res.exit_code == 0
    assert "Dashboard created" in res.output

    # Error case
    mock_export.create_dashboard.side_effect = Exception("err")
    res = runner.invoke(cli, ["export-excel", str(mock_profiles), str(out_file)])
    assert res.exit_code != 0
    assert "Failed to create dashboard" in res.output

@patch("solstein.cli.GrowthScorer")
def test_score_command(
    mock_scorer_cls: MagicMock, runner: CliRunner, mock_profiles: Path, tmp_path: Path
) -> None:
    mock_scorer = MagicMock()
    mock_scorer_cls.return_value = mock_scorer

    # Mock return
    scored = Company(
        id="x",
        name="X",
        financials=FinancialMetric(),
        growth_score=5.0,
        financial_health_score=None,
        competitive_position_score=10.0,
    )
    mock_scorer.calculate_scores.return_value = scored

    out_file = tmp_path / "scores.json"
    res = runner.invoke(cli, ["score", str(mock_profiles), "-o", str(out_file)])
    assert res.exit_code == 0
    assert "Calculating scores" in res.output
    assert "Saved scored profiles" in res.output

    # Error case
    mock_scorer.calculate_scores.side_effect = Exception("err")
    res = runner.invoke(cli, ["score", str(mock_profiles)])
    assert res.exit_code != 0
    assert "Failed to calculate scores" in res.output

def test_analyze_market_command(runner: CliRunner, mock_profiles: Path, tmp_path: Path) -> None:
    res = runner.invoke(cli, ["analyze-market", str(mock_profiles), "-n", "Test Market"])
    assert res.exit_code == 0
    assert "Market Analysis:" in res.output
    assert "Companies: 2" in res.output

    # Error case - bad json
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("not json")
    res = runner.invoke(cli, ["analyze-market", str(bad_file)])
    assert res.exit_code != 0
    assert "Failed to analyze market" in res.output

def test_compare_command(runner: CliRunner, mock_profiles: Path, tmp_path: Path) -> None:
    res = runner.invoke(cli, ["compare", "c1", "c2", str(mock_profiles)])
    assert res.exit_code == 0
    assert "Comparing c1 vs c2" in res.output
    assert "Revenue" in res.output

    # Not found cases
    res = runner.invoke(cli, ["compare", "invalid", "c2", str(mock_profiles)])
    assert res.exit_code == 0
    assert "Profile not found" in res.output

    res = runner.invoke(cli, ["compare", "c1", "invalid", str(mock_profiles)])
    assert res.exit_code == 0
    assert "Profile not found" in res.output

    # Error case - bad json
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("not json")
    res = runner.invoke(cli, ["compare", "c1", "c2", str(bad_file)])
    assert res.exit_code != 0
    assert "Failed to compare profiles" in res.output
