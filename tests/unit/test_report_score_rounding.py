"""STORY-182: Test that all score outputs in reports are rounded to 2 decimal places.

Ensures no raw Python floats like 7.138888888888889 appear in generated reports.
"""

from __future__ import annotations

import re
import tempfile
from pathlib import Path

from solstein.domain.models import Company, FinancialMetric
from solstein.exporters.markdown.base import ReportFormatter, ScoreInterpreter
from solstein.exporters.markdown.client import ClientReportGenerator
from solstein.exporters.markdown.report_strategies.corporate_history import (
    CorporateHistoryStrategy,
)
from solstein.exporters.markdown.report_strategies.deep_analysis import (
    DeepAnalysisStrategy,
)
from solstein.exporters.markdown.report_strategies.financial_growth import (
    FinancialGrowthStrategy,
)

# Pattern matching a float with 3+ decimal digits (e.g., 7.138888888888889)
# Excludes date-like patterns and version numbers
RAW_FLOAT_PATTERN = re.compile(r"(?<!\d)\d+\.\d{3,}(?!\d)")


def _make_company(
    name: str = "Eneve",
    composite_score: float = 7.138888888888889,
    growth_score: float = 6.533333333333333,
    financial_health_score: float = 5.822222222222222,
    competitive_position_score: float = 7.138888888888889,
) -> Company:
    """Create a Company with unrounded scores to test formatting."""
    return Company(
        id=f"COMP-{name.upper()}-TEST",
        name=name,
        industry="Energy Software",
        financials=FinancialMetric(
            revenue=5_000_000,
            growth_rate=25.3333333,
            employees=150,
            profit_margin=12.7777777,
            allow_empty_primary=True,
        ),
        composite_score=composite_score,
        growth_score=growth_score,
        financial_health_score=financial_health_score,
        competitive_position_score=competitive_position_score,
        classification="Phoenix",
        ai_score=7.5,
        saas_maturity=6,
    )


class TestScoreRounding:
    """STORY-182: All score outputs must be rounded to 2 decimal places."""

    def test_format_score_rounds_to_2_decimals(self) -> None:
        """ReportFormatter.format_score should round to 2 decimals."""
        formatter = ReportFormatter()
        assert formatter.format_score(7.138888888888889) == "7.14"
        assert formatter.format_score(8.366666666666667) == "8.37"
        assert formatter.format_score(9.75) == "9.75"
        assert formatter.format_score(None) == "N/A"

    def test_deep_analysis_no_raw_floats(self) -> None:
        """Deep analysis report should not contain unrounded floats."""
        formatter = ReportFormatter()
        strategy = DeepAnalysisStrategy(formatter, ScoreInterpreter())
        company = _make_company()
        report = strategy.generate(company)

        raw_matches = RAW_FLOAT_PATTERN.findall(report)
        assert not raw_matches, f"Found unrounded floats in deep analysis: {raw_matches}"

    def test_corporate_history_no_raw_floats(self) -> None:
        """Corporate history report should not contain unrounded floats."""
        formatter = ReportFormatter()
        strategy = CorporateHistoryStrategy(formatter, ScoreInterpreter())
        company = _make_company()
        report = strategy.generate(company)

        raw_matches = RAW_FLOAT_PATTERN.findall(report)
        assert not raw_matches, f"Found unrounded floats in corporate history: {raw_matches}"

    def test_financial_growth_no_raw_floats(self) -> None:
        """Financial growth report should not contain unrounded floats."""
        formatter = ReportFormatter()
        strategy = FinancialGrowthStrategy(formatter, ScoreInterpreter())
        company = _make_company()
        report = strategy.generate(company)

        raw_matches = RAW_FLOAT_PATTERN.findall(report)
        assert not raw_matches, f"Found unrounded floats in financial growth: {raw_matches}"

    def test_client_report_no_raw_floats(self) -> None:
        """Full client report should not contain unrounded floats."""
        company = _make_company()
        competitor = _make_company("RivalCo")
        competitor.id = "COMP-RIVAL-TEST"
        competitor.composite_score = 6.277777777777778
        competitor.classification = "Salt"

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            gen = ClientReportGenerator(output_dir=output)
            generated = gen.generate_client_report(company, [competitor])

            for key, path in generated.items():
                if isinstance(path, Path) and path.exists():
                    content = path.read_text()
                    raw_matches = RAW_FLOAT_PATTERN.findall(content)
                    assert not raw_matches, f"Found unrounded floats in {key} ({path.name}): {raw_matches}"

    def test_none_score_shows_na(self) -> None:
        """A company with None scores should show N/A, not crash."""
        formatter = ReportFormatter()
        strategy = DeepAnalysisStrategy(formatter, ScoreInterpreter())
        company = _make_company()
        company.growth_score = None
        company.financial_health_score = None
        report = strategy.generate(company)

        assert "N/A" in report
        # Should not crash
        assert "Deep Analysis" in report
