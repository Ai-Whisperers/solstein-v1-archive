"""Tests for STORY-183: Market overview classification counters.

Verifies:
- Case-insensitive classification counting
- Unclassified companies are counted
- Markdown table has correct column separators
- Dead code (unused tier_counts, discarded avg results) removed
"""

from __future__ import annotations

import inspect
import re
from pathlib import Path

from solstein.domain.models import Company, FinancialMetric
from solstein.exporters.markdown.market import MarketReportGenerator


def _make_company(
    name: str,
    classification: str | None = None,
    composite_score: float | None = 5.0,
) -> Company:
    """Create a minimal Company for testing."""
    company_id = f"test-{name.lower().replace(' ', '-')}"
    return Company(
        id=company_id,
        name=name,
        classification=classification,
        composite_score=composite_score,
        financials=FinancialMetric(revenue=10.0),
    )


class TestClassificationCounters:
    """Tests for classification counter logic in market overview."""

    def test_counts_standard_classifications(self, tmp_path: Path) -> None:
        """Phoenix, Salt, Lead companies are counted correctly."""
        companies = [
            _make_company("A", classification="Phoenix"),
            _make_company("B", classification="Phoenix"),
            _make_company("C", classification="Salt"),
            _make_company("D", classification="Lead"),
        ]
        gen = MarketReportGenerator(tmp_path)
        path = gen.generate_market_overview(companies, tmp_path)
        content = path.read_text()

        assert "| Phoenix Tier Companies | 2 |" in content
        assert "| Salt Tier Companies | 1 |" in content
        assert "| Lead Tier Companies | 1 |" in content

    def test_case_insensitive_classification(self, tmp_path: Path) -> None:
        """Classifications are normalised to title-case before counting."""
        companies = [
            _make_company("A", classification="phoenix"),
            _make_company("B", classification="PHOENIX"),
            _make_company("C", classification="Phoenix"),
            _make_company("D", classification="salt"),
            _make_company("E", classification="LEAD"),
        ]
        gen = MarketReportGenerator(tmp_path)
        path = gen.generate_market_overview(companies, tmp_path)
        content = path.read_text()

        assert "| Phoenix Tier Companies | 3 |" in content
        assert "| Salt Tier Companies | 1 |" in content
        assert "| Lead Tier Companies | 1 |" in content

    def test_unclassified_companies_counted(self, tmp_path: Path) -> None:
        """Companies with None classification appear in Unclassified row."""
        companies = [
            _make_company("A", classification="Phoenix"),
            _make_company("B", classification=None),
            _make_company("C", classification=None),
        ]
        gen = MarketReportGenerator(tmp_path)
        path = gen.generate_market_overview(companies, tmp_path)
        content = path.read_text()

        assert "| Unclassified | 2 |" in content

    def test_empty_classification_counted_as_unclassified(self, tmp_path: Path) -> None:
        """Empty-string classification treated as unclassified."""
        companies = [
            _make_company("A", classification=""),
            _make_company("B", classification="Phoenix"),
        ]
        gen = MarketReportGenerator(tmp_path)
        path = gen.generate_market_overview(companies, tmp_path)
        content = path.read_text()

        assert "| Unclassified | 1 |" in content
        assert "| Phoenix Tier Companies | 1 |" in content


class TestMarkdownTableFormat:
    """Tests for correct markdown table formatting."""

    def test_key_metrics_table_has_separator_row(self, tmp_path: Path) -> None:
        """Key Metrics table must have a proper |---|---| separator row."""
        companies = [_make_company("A", classification="Phoenix")]
        gen = MarketReportGenerator(tmp_path)
        path = gen.generate_market_overview(companies, tmp_path)
        content = path.read_text()

        # Find the Key Metrics table
        lines = content.split("\n")
        header_idx = None
        for i, line in enumerate(lines):
            if "| Metric | Value |" in line:
                header_idx = i
                break

        assert header_idx is not None, "Key Metrics table header not found"
        separator = lines[header_idx + 1]
        # Separator must be |---|---| pattern (not ||)
        assert re.match(r"^\|[\s-]+\|[\s-]+\|$", separator), (
            f"Expected separator row like |---|---|, got: {separator!r}"
        )

    def test_no_double_pipe_in_report(self, tmp_path: Path) -> None:
        """No || (double-pipe) should appear in the markdown output."""
        companies = [
            _make_company("A", classification="Phoenix"),
            _make_company("B", classification="Salt"),
        ]
        gen = MarketReportGenerator(tmp_path)
        path = gen.generate_market_overview(companies, tmp_path)
        content = path.read_text()

        double_pipes = [(i + 1, line) for i, line in enumerate(content.split("\n")) if "||" in line]
        assert not double_pipes, f"Found double-pipe '||' on lines: {double_pipes}"


class TestDeadCodeRemoved:
    """Verify dead code was cleaned up."""

    def test_no_unused_tier_counts(self) -> None:
        """tier_counts variable should no longer exist in market.py."""
        source = inspect.getsource(MarketReportGenerator.generate_market_overview)
        assert "tier_counts" not in source, "Dead code 'tier_counts' still present"

    def test_no_discarded_avg_calls(self) -> None:
        """formatter.avg() calls with discarded results should be removed."""
        source = inspect.getsource(MarketReportGenerator.generate_market_overview)
        # Look for standalone formatter.avg( calls (result not assigned)
        lines = source.split("\n")
        discarded = [
            line.strip() for line in lines if "formatter.avg(" in line and "=" not in line.split("formatter.avg(")[0]
        ]
        assert not discarded, f"Found discarded avg() calls: {discarded}"
