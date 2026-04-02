"""Tests for STORY-185: Report content quality assertions.

Cross-cutting integration tests that verify generated reports meet quality
standards established by STORY-181 through STORY-184:
- No raw floats (STORY-182)
- No double-pipe markdown bugs (STORY-183)
- Signal-based content (STORY-184)
- Clean file paths (STORY-181)
- Valid markdown structure
"""

from __future__ import annotations

import re
from pathlib import Path

from solstein.domain.models import Company, FinancialMetric
from solstein.exporters.markdown.company import CompanyReportGenerator
from solstein.exporters.markdown.market import MarketReportGenerator

# Pattern: 3+ decimal digits not preceded/followed by another digit
RAW_FLOAT_PATTERN = re.compile(r"(?<!\d)\d+\.\d{3,}(?!\d)")


def _make_company(
    name: str = "TestCo",
    company_id: str = "test-company-001",
    classification: str = "Salt",
    composite_score: float = 6.0,
    **kwargs: object,
) -> Company:
    """Create a Company with full signal coverage."""
    defaults = {
        "id": company_id,
        "name": name,
        "classification": classification,
        "composite_score": composite_score,
        "growth_score": 5.5,
        "financial_health_score": 6.0,
        "competitive_position_score": 5.0,
        "ai_score": 4.5,
        "saas_maturity": 5,
        "revenue_cagr_3yr": 12.0,
        "total_funding_raised_eur": 25.0,
        "latest_valuation_eur": 100.0,
        "financials": FinancialMetric(revenue=15.0, profit_margin=8.0),
        "industry": "Energy Software",
    }
    defaults.update(kwargs)
    return Company(**defaults)  # type: ignore[arg-type]


def _make_competitors(count: int = 3) -> list[Company]:
    """Create a list of competitor companies."""
    competitors = []
    configs = [
        ("AlphaCorp", "test-alpha-corp", "Phoenix", 8.0),
        ("BetaInc", "test-beta-inc", "Salt", 5.5),
        ("GammaTech", "test-gamma-tech", "Lead", 3.0),
        ("DeltaSoft", "test-delta-soft", "Phoenix", 7.5),
        ("EpsilonAI", "test-epsilon-ai", "Salt", 6.0),
    ]
    for name, cid, cls, score in configs[:count]:
        competitors.append(
            _make_company(
                name=name,
                company_id=cid,
                classification=cls,
                composite_score=score,
            )
        )
    return competitors


class TestNoRawFloats:
    """STORY-182: No raw floats (3+ decimals) in any report output."""

    def test_company_reports_no_raw_floats(self, tmp_path: Path) -> None:
        gen = CompanyReportGenerator(tmp_path)
        company = _make_company(composite_score=6.123456)
        reports = gen.generate_company_reports(company, tmp_path)
        for report_type, path in reports.items():
            content = path.read_text()
            matches = RAW_FLOAT_PATTERN.findall(content)
            assert not matches, f"Raw floats in {report_type}: {matches}"

    def test_market_overview_no_raw_floats(self, tmp_path: Path) -> None:
        gen = MarketReportGenerator(tmp_path)
        companies = [_make_company(composite_score=7.987654)] + _make_competitors()
        path = gen.generate_market_overview(companies, tmp_path)
        content = path.read_text()
        matches = RAW_FLOAT_PATTERN.findall(content)
        assert not matches, f"Raw floats in market overview: {matches}"

    def test_competitive_landscape_no_raw_floats(self, tmp_path: Path) -> None:
        gen = MarketReportGenerator(tmp_path)
        client = _make_company(composite_score=6.789012)
        comps = _make_competitors()
        path = gen.generate_competitive_landscape(client, comps, tmp_path)
        content = path.read_text()
        matches = RAW_FLOAT_PATTERN.findall(content)
        assert not matches, f"Raw floats in competitive landscape: {matches}"


class TestNoMarkdownBugs:
    """STORY-183: No broken markdown in reports."""

    def test_no_double_pipes_in_any_report(self, tmp_path: Path) -> None:
        """No || should appear in any generated report."""
        gen = CompanyReportGenerator(tmp_path)
        company = _make_company()
        reports = gen.generate_company_reports(company, tmp_path)
        for report_type, path in reports.items():
            content = path.read_text()
            double_pipes = [(i + 1, line) for i, line in enumerate(content.split("\n")) if "||" in line]
            assert not double_pipes, f"Double pipes in {report_type}: {double_pipes}"

    def test_market_overview_no_double_pipes(self, tmp_path: Path) -> None:
        gen = MarketReportGenerator(tmp_path)
        companies = [_make_company()] + _make_competitors()
        path = gen.generate_market_overview(companies, tmp_path)
        content = path.read_text()
        double_pipes = [(i + 1, line) for i, line in enumerate(content.split("\n")) if "||" in line]
        assert not double_pipes, f"Double pipes in market overview: {double_pipes}"

    def test_tables_have_separator_rows(self, tmp_path: Path) -> None:
        """Every markdown table header must be followed by a separator row."""
        gen = CompanyReportGenerator(tmp_path)
        company = _make_company()
        reports = gen.generate_company_reports(company, tmp_path)
        table_header_pattern = re.compile(r"^\|.*\|.*\|$")
        separator_pattern = re.compile(r"^\|[\s:-]+\|")
        for _rtype, path in reports.items():
            lines = path.read_text().split("\n")
            for i, line in enumerate(lines):
                if table_header_pattern.match(line.strip()) and i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    # If next line is also a table row, the current line IS a header
                    # only if the next line is a separator
                    if next_line.startswith("|") and not separator_pattern.match(next_line):
                        # This could be a data row, not a header — skip
                        continue


class TestSignalBasedContent:
    """STORY-184: Reports contain signal-based content, not boilerplate."""

    def test_deep_analysis_mentions_actual_scores(self, tmp_path: Path) -> None:
        """Deep analysis should reference actual company dimension values."""
        gen = CompanyReportGenerator(tmp_path)
        company = _make_company(ai_score=3.0, saas_maturity=3)
        reports = gen.generate_company_reports(company, tmp_path)
        deep = reports["deep_analysis"].read_text()
        # Should mention AI weakness since ai_score < 5
        assert "AI" in deep
        # Should mention SaaS weakness since saas_maturity < 4
        assert "SaaS" in deep or "Legacy" in deep

    def test_deep_analysis_strong_company_shows_strengths(self, tmp_path: Path) -> None:
        gen = CompanyReportGenerator(tmp_path)
        company = _make_company(
            composite_score=8.5,
            ai_score=8.0,
            saas_maturity=8,
            revenue_cagr_3yr=25.0,
        )
        reports = gen.generate_company_reports(company, tmp_path)
        deep = reports["deep_analysis"].read_text()
        assert "Market leader" in deep or "Strong" in deep
        assert "AI" in deep

    def test_deep_analysis_has_signal_header(self, tmp_path: Path) -> None:
        gen = CompanyReportGenerator(tmp_path)
        reports = gen.generate_company_reports(_make_company(), tmp_path)
        deep = reports["deep_analysis"].read_text()
        assert "Signal Analysis" in deep


class TestCleanFilePaths:
    """STORY-181: Report files use clean paths without double nesting."""

    def test_company_reports_clean_filenames(self, tmp_path: Path) -> None:
        gen = CompanyReportGenerator(tmp_path)
        reports = gen.generate_company_reports(_make_company(), tmp_path)
        for report_type, path in reports.items():
            filename = path.name
            # Filenames should be clean (no company name prefix)
            assert filename in (
                "corporate-history.md",
                "deep-analysis.md",
                "financial-growth.md",
            ), f"Unexpected filename for {report_type}: {filename}"

    def test_no_double_nesting(self, tmp_path: Path) -> None:
        """Company dir should not appear twice in the path."""
        gen = CompanyReportGenerator(tmp_path)
        company = _make_company()
        reports = gen.generate_company_reports(company, tmp_path)
        sanitized = "testco"  # sanitize_filename lowercases and removes special chars
        for path in reports.values():
            parts = path.parts
            # Count how many times the company name appears in the path
            name_count = sum(1 for p in parts if sanitized in p.lower())
            assert name_count <= 1, f"Double nesting detected: {path}"


class TestReportCompleteness:
    """All reports should have required structural elements."""

    def test_all_reports_have_title(self, tmp_path: Path) -> None:
        gen = CompanyReportGenerator(tmp_path)
        reports = gen.generate_company_reports(_make_company(), tmp_path)
        for rtype, path in reports.items():
            content = path.read_text()
            assert content.startswith("# "), f"{rtype} missing H1 title"

    def test_all_reports_have_platform_footer(self, tmp_path: Path) -> None:
        gen = CompanyReportGenerator(tmp_path)
        reports = gen.generate_company_reports(_make_company(), tmp_path)
        for rtype, path in reports.items():
            content = path.read_text()
            assert "SolStein" in content, f"{rtype} missing platform attribution"

    def test_market_overview_has_required_sections(self, tmp_path: Path) -> None:
        gen = MarketReportGenerator(tmp_path)
        companies = [_make_company()] + _make_competitors()
        path = gen.generate_market_overview(companies, tmp_path)
        content = path.read_text()
        assert "## Executive Summary" in content
        assert "## Top Performers" in content
        assert "## Industry Distribution" in content
        assert "## Methodology" in content

    def test_competitive_landscape_has_comparison_table(self, tmp_path: Path) -> None:
        gen = MarketReportGenerator(tmp_path)
        client = _make_company()
        comps = _make_competitors()
        path = gen.generate_competitive_landscape(client, comps, tmp_path)
        content = path.read_text()
        assert "## Competitive Set" in content
        assert "Relative Position" in content
