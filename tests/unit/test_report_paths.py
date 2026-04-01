"""STORY-181: Test that report output paths are not double-nested.

Verifies that all report types are written to a single company-named
directory (e.g., output/eneve/*.md) and NOT a nested path
(e.g., output/eneve/eneve/*.md).
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from solstein.domain.models import Company, FinancialMetric
from solstein.exporters.markdown.base import ReportFormatter, ScoreInterpreter
from solstein.exporters.markdown.client import ClientReportGenerator
from solstein.exporters.markdown.generator import ReportGenerator
from solstein.exporters.markdown.report_strategies.corporate_history import (
    CorporateHistoryStrategy,
)
from solstein.exporters.markdown.report_strategies.deep_analysis import (
    DeepAnalysisStrategy,
)
from solstein.exporters.markdown.report_strategies.financial_growth import (
    FinancialGrowthStrategy,
)


def _make_company(name: str = "Eneve") -> Company:
    """Create a minimal Company for report testing."""
    return Company(
        id=f"COMP-{name.upper()}-TEST",
        name=name,
        industry="Energy Software",
        financials=FinancialMetric(
            revenue=5_000_000,
            growth_rate=25.0,
            employees=150,
            allow_empty_primary=True,
        ),
        composite_score=7.14,
        growth_score=6.5,
        financial_health_score=5.8,
        competitive_position_score=7.14,
        classification="Phoenix",
        ai_score=7.5,
    )


class TestReportFilenames:
    """STORY-181: Verify clean filenames without company name prefix."""

    def test_corporate_history_filename(self) -> None:
        formatter = ReportFormatter()
        strategy = CorporateHistoryStrategy(formatter, ScoreInterpreter())
        company = _make_company()
        path = strategy.get_output_path(company, Path("/tmp/reports/eneve"))
        assert path.name == "corporate-history.md"
        assert "eneve" not in path.name.lower().replace("corporate", "")

    def test_deep_analysis_filename(self) -> None:
        formatter = ReportFormatter()
        strategy = DeepAnalysisStrategy(formatter, ScoreInterpreter())
        company = _make_company()
        path = strategy.get_output_path(company, Path("/tmp/reports/eneve"))
        assert path.name == "deep-analysis.md"

    def test_financial_growth_filename(self) -> None:
        formatter = ReportFormatter()
        strategy = FinancialGrowthStrategy(formatter, ScoreInterpreter())
        company = _make_company()
        path = strategy.get_output_path(company, Path("/tmp/reports/eneve"))
        assert path.name == "financial-growth.md"


class TestReportPathNesting:
    """STORY-181: Verify no double-nested company directories."""

    def test_generate_company_reports_no_double_nesting(self) -> None:
        """ReportGenerator.generate_company_reports should not create
        output/{company}/{company}/ directories."""
        company = _make_company("Eneve")

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            gen = ReportGenerator(output_dir=output, use_llm=False)
            gen.generate_company_reports(company, output)

            # Should have created output/Eneve/ with files
            company_dir = output / "Eneve"
            assert company_dir.exists(), f"Expected {company_dir} to exist"

            # Must NOT have a nested Eneve/Eneve/ directory
            nested_dir = company_dir / "Eneve"
            if nested_dir.exists():
                nested_files = list(nested_dir.glob("*.md"))
                assert (
                    len(nested_files) == 0
                ), f"Found nested files in {nested_dir}: {nested_files}"

    def test_client_report_no_double_nesting(self) -> None:
        """ClientReportGenerator should write all reports to one directory level."""
        company = _make_company("Eneve")
        competitor = _make_company("RivalCo")
        competitor.id = "COMP-RIVAL-TEST"
        competitor.composite_score = 6.0
        competitor.classification = "Salt"

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            gen = ClientReportGenerator(output_dir=output)
            generated = gen.generate_client_report(company, [competitor])

            # All generated files should be in the same directory
            dirs_used = set()
            for key, path in generated.items():
                if isinstance(path, Path) and path.exists():
                    dirs_used.add(path.parent)

            # Should use at most one directory (the company dir)
            assert (
                len(dirs_used) <= 1
            ), f"Reports scattered across multiple dirs: {dirs_used}"

    def test_all_five_report_types_same_directory(self) -> None:
        """All 5 report types should be in the same directory."""
        company = _make_company("Eneve")
        competitor = _make_company("RivalCo")
        competitor.id = "COMP-RIVAL-TEST"
        competitor.composite_score = 6.0
        competitor.classification = "Salt"

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            gen = ClientReportGenerator(output_dir=output)
            generated = gen.generate_client_report(company, [competitor])

            # Should have 5 report types
            assert len(generated) >= 4, f"Expected at least 4 reports, got {len(generated)}: {list(generated.keys())}"

            # All should be actual files
            for key, path in generated.items():
                if isinstance(path, Path):
                    assert path.exists(), f"Report '{key}' not found at {path}"
