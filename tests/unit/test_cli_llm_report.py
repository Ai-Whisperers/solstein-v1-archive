"""
STORY-170: Tests for the generate-llm-report CLI command.

Verifies:
- No ModuleNotFoundError on import (LLMEnhancedReportGenerator accessible from generator.py)
- --no-llm flag invokes template-only path via ClientReportGenerator
- LLM-enhanced path (mocked LLM enhancer) produces output without crashing
- Graceful fallback when LLM enhancer is unavailable
"""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

import solstein.cli_legacy as cli_module
from solstein.cli_legacy import cli
from solstein.domain.models import Company

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

COMPANY_ALPHA = Company(
    id="alpha-001",
    name="Alpha Corp",
    industry="Tech",
    financials={"revenue": 100.0, "valuation": 1000.0},
)

COMPANY_BETA = Company(
    id="beta-001",
    name="Beta Ltd",
    industry="Tech",
    financials={"revenue": 50.0, "valuation": 500.0},
)


class DummyScorer:
    def calculate_scores(self, company: Company) -> Company:
        return company


class DummyLoader:
    """Replacement for CompetitorDataLoader — no deprecation warning."""

    def load_companies(self, _path: Path | None = None) -> list[Company]:
        return [COMPANY_ALPHA, COMPANY_BETA]

    def load_from_json(self, path: Path, limit: int | None = None) -> list[Company]:
        return [COMPANY_ALPHA, COMPANY_BETA]


# ---------------------------------------------------------------------------
# Import sanity check
# ---------------------------------------------------------------------------


def test_llm_enhanced_report_generator_importable():
    """STORY-170: LLMEnhancedReportGenerator must be importable without ModuleNotFoundError."""
    from solstein.exporters.markdown.generator import LLMEnhancedReportGenerator  # noqa: F401

    assert LLMEnhancedReportGenerator is not None


def test_client_report_generator_importable():
    """ClientReportGenerator must also be importable from generator.py."""
    from solstein.exporters.markdown.generator import ClientReportGenerator  # noqa: F401

    assert ClientReportGenerator is not None


# ---------------------------------------------------------------------------
# --no-llm flag: uses ClientReportGenerator / template path
# ---------------------------------------------------------------------------


def test_generate_llm_report_no_llm_flag_produces_report(tmp_path, monkeypatch):
    """--no-llm flag should invoke ClientReportGenerator and produce output."""
    captured: dict = {}

    class DummyClientGenerator:
        def __init__(self, output_dir: Path):
            captured["output_dir"] = output_dir

        def generate_client_report(self, target: Company, competitors: list[Company]) -> dict:
            return {"client_report": tmp_path / "report.md"}

    monkeypatch.setattr(cli_module, "_load_companies_for_report", lambda *a, **kw: DummyLoader().load_companies())
    monkeypatch.setattr(cli_module, "GrowthScorer", DummyScorer)
    monkeypatch.setattr(cli_module, "assert_client_report_ready", lambda *_, **__: None)
    monkeypatch.setattr(cli_module, "ClientReportGenerator", DummyClientGenerator)

    runner = CliRunner()
    result = runner.invoke(cli, ["generate-llm-report", "Alpha Corp", "--no-llm", "-o", str(tmp_path)])

    assert result.exit_code == 0, result.output
    assert "LLM-enhanced reports generated" in result.output


def test_generate_llm_report_no_llm_default_output_dir(monkeypatch):
    """--no-llm without -o flag should use data/output/reports/llm default."""
    captured: dict = {}

    class DummyClientGenerator:
        def __init__(self, output_dir: Path):
            captured["output_dir"] = str(output_dir)

        def generate_client_report(self, target: Company, competitors: list[Company]) -> dict:
            return {}

    monkeypatch.setattr(cli_module, "_load_companies_for_report", lambda *a, **kw: DummyLoader().load_companies())
    monkeypatch.setattr(cli_module, "GrowthScorer", DummyScorer)
    monkeypatch.setattr(cli_module, "assert_client_report_ready", lambda *_, **__: None)
    monkeypatch.setattr(cli_module, "ClientReportGenerator", DummyClientGenerator)

    runner = CliRunner()
    result = runner.invoke(cli, ["generate-llm-report", "Alpha Corp", "--no-llm"])

    assert result.exit_code == 0, result.output
    assert captured.get("output_dir") == "data/output/reports/llm"


def test_generate_llm_report_company_not_found(tmp_path, monkeypatch):
    """Should print error and exit 0 when company name does not match any loaded company."""
    monkeypatch.setattr(cli_module, "_load_companies_for_report", lambda *a, **kw: DummyLoader().load_companies())
    monkeypatch.setattr(cli_module, "GrowthScorer", DummyScorer)
    monkeypatch.setattr(cli_module, "assert_client_report_ready", lambda *_, **__: None)

    runner = CliRunner()
    result = runner.invoke(cli, ["generate-llm-report", "NonExistentCo", "--no-llm"])

    assert result.exit_code == 0
    assert "Company not found" in result.output or "not found" in result.output.lower()


# ---------------------------------------------------------------------------
# LLM-enhanced path (mocked)
# ---------------------------------------------------------------------------


def test_generate_llm_report_llm_path_mocked(tmp_path, monkeypatch):
    """LLM-enhanced path should call LLMEnhancedReportGenerator and produce reports."""

    expected_reports = {
        "executive_summary": tmp_path / "exec.md",
        "competitive_narrative": tmp_path / "narrative.md",
    }

    class DummyLLMGenerator:
        def __init__(self, output_dir: Path):
            pass

        async def generate_llm_enhanced_report(self, target: Company, competitors: list[Company]) -> dict:
            return expected_reports

    monkeypatch.setattr(cli_module, "_load_companies_for_report", lambda *a, **kw: DummyLoader().load_companies())
    monkeypatch.setattr(cli_module, "GrowthScorer", DummyScorer)
    monkeypatch.setattr(cli_module, "assert_client_report_ready", lambda *_, **__: None)
    monkeypatch.setattr(cli_module, "LLMEnhancedReportGenerator", DummyLLMGenerator)

    runner = CliRunner()
    result = runner.invoke(cli, ["generate-llm-report", "Alpha Corp", "-o", str(tmp_path)])

    assert result.exit_code == 0, result.output
    assert "LLM-enhanced reports generated" in result.output


def test_generate_llm_report_llm_exception_handled(tmp_path, monkeypatch):
    """If LLM generator raises, the CLI should catch it and abort with non-zero exit."""

    class FailingLLMGenerator:
        def __init__(self, output_dir: Path):
            pass

        async def generate_llm_enhanced_report(self, target: Company, competitors: list[Company]) -> dict:
            raise RuntimeError("LLM provider unavailable")

    monkeypatch.setattr(cli_module, "_load_companies_for_report", lambda *a, **kw: DummyLoader().load_companies())
    monkeypatch.setattr(cli_module, "GrowthScorer", DummyScorer)
    monkeypatch.setattr(cli_module, "assert_client_report_ready", lambda *_, **__: None)
    monkeypatch.setattr(cli_module, "LLMEnhancedReportGenerator", FailingLLMGenerator)

    runner = CliRunner()
    result = runner.invoke(cli, ["generate-llm-report", "Alpha Corp", "-o", str(tmp_path)])

    # Should abort (non-zero) and show error message
    assert result.exit_code != 0
    assert "Failed to generate LLM report" in result.output
