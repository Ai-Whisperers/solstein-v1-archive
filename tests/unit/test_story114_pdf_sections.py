"""Tests for STORY-114: PDF section renderers.

Covers individual section rendering functions from pdf_sections.py.
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from fpdf import FPDF

from solstein.domain.models import Company, CompanyTier, FinancialMetric
from solstein.exporters.pdf_sections import (
    render_company_profile,
    render_cover_page,
    render_executive_summary,
    render_financial_overview,
    render_footnotes,
    render_revenue_chart,
    render_scoring_methodology,
)


def _make_company(**kwargs: Any) -> Company:
    """Create a test Company."""
    defaults: dict[str, Any] = {
        "id": f"TEST-{uuid.uuid4().hex[:8].upper()}",
        "name": kwargs.pop("name", "Acme Corp"),
        "industry": "Energy Software",
        "description": "Test company description.",
        "headquarters": "Munich",
        "tier": CompanyTier.TIER_1,
        "composite_score": 8.5,
        "revenue": 50_000_000,
        "source_links": ["https://source.example.com"],
        "enrichment_sources": ["SEC EDGAR"],
        "signal_confidences": {"growth": 0.85},
        "financials": FinancialMetric(
            revenue=50_000_000,
            employees=200,
            profit_margin=0.15,
            allow_empty_primary=True,
        ),
    }
    defaults.update(kwargs)
    return Company(**defaults)


def _new_pdf() -> FPDF:
    """Create a fresh FPDF instance for testing."""
    pdf = FPDF(format="a4")
    pdf.set_auto_page_break(auto=True, margin=15)
    return pdf


class TestCoverPage:
    def test_renders_without_error(self, tmp_path: Path) -> None:
        pdf = _new_pdf()
        render_cover_page(pdf, "Test Report", 5, "a4")
        pdf.output(str(tmp_path / "cover.pdf"))
        assert (tmp_path / "cover.pdf").exists()

    def test_letter_format(self, tmp_path: Path) -> None:
        pdf = FPDF(format="letter")
        pdf.set_auto_page_break(auto=True, margin=15)
        render_cover_page(pdf, "Letter Report", 3, "letter")
        pdf.output(str(tmp_path / "cover_letter.pdf"))
        assert (tmp_path / "cover_letter.pdf").exists()


class TestExecutiveSummary:
    def test_renders(self, tmp_path: Path) -> None:
        pdf = _new_pdf()
        pdf.add_page()
        companies = [_make_company(name=f"Co {i}") for i in range(3)]
        render_executive_summary(pdf, companies)
        pdf.output(str(tmp_path / "exec.pdf"))
        assert (tmp_path / "exec.pdf").exists()

    def test_empty_companies(self, tmp_path: Path) -> None:
        pdf = _new_pdf()
        pdf.add_page()
        render_executive_summary(pdf, [])
        pdf.output(str(tmp_path / "exec_empty.pdf"))
        assert (tmp_path / "exec_empty.pdf").exists()


class TestFinancialOverview:
    def test_renders_with_data(self, tmp_path: Path) -> None:
        pdf = _new_pdf()
        pdf.add_page()
        render_financial_overview(pdf, [_make_company()])
        pdf.output(str(tmp_path / "fin.pdf"))
        assert (tmp_path / "fin.pdf").exists()

    def test_no_financials(self, tmp_path: Path) -> None:
        pdf = _new_pdf()
        pdf.add_page()
        render_financial_overview(pdf, [_make_company(financials=None, revenue=None)])
        pdf.output(str(tmp_path / "fin_none.pdf"))
        assert (tmp_path / "fin_none.pdf").exists()


class TestCompanyProfile:
    def test_renders_with_sources(self, tmp_path: Path) -> None:
        pdf = _new_pdf()
        pdf.add_page()
        footnotes: list[tuple[int, str]] = []
        render_company_profile(pdf, _make_company(), 1, footnotes)
        pdf.output(str(tmp_path / "profile.pdf"))
        assert (tmp_path / "profile.pdf").exists()
        assert len(footnotes) > 0  # Sources should generate footnotes

    def test_no_sources(self, tmp_path: Path) -> None:
        pdf = _new_pdf()
        pdf.add_page()
        footnotes: list[tuple[int, str]] = []
        render_company_profile(
            pdf,
            _make_company(source_links=[], enrichment_sources=[]),
            1,
            footnotes,
        )
        pdf.output(str(tmp_path / "profile_nosrc.pdf"))
        assert len(footnotes) == 0


class TestRevenueChart:
    def test_renders_with_multiple(self, tmp_path: Path) -> None:
        pdf = _new_pdf()
        pdf.add_page()
        companies = [_make_company(name=f"Co {i}", revenue=1_000_000 * (i + 1)) for i in range(5)]
        render_revenue_chart(pdf, companies)
        pdf.output(str(tmp_path / "chart.pdf"))
        assert (tmp_path / "chart.pdf").exists()

    def test_skips_with_one_company(self, tmp_path: Path) -> None:
        pdf = _new_pdf()
        pdf.add_page()
        initial_pages = pdf.pages_count
        render_revenue_chart(pdf, [_make_company()])
        # Should not add content (need 2+ companies for chart)
        assert pdf.pages_count == initial_pages


class TestFootnotes:
    def test_renders_list(self, tmp_path: Path) -> None:
        pdf = _new_pdf()
        notes = [(1, "https://a.com"), (2, "https://b.com")]
        render_footnotes(pdf, notes)
        pdf.output(str(tmp_path / "fn.pdf"))
        assert (tmp_path / "fn.pdf").exists()
        assert pdf.pages_count >= 1  # At least one page added for footnotes

    def test_empty_list(self) -> None:
        pdf = _new_pdf()
        render_footnotes(pdf, [])
        assert pdf.pages_count == 0


class TestScoringMethodology:
    def test_renders(self, tmp_path: Path) -> None:
        pdf = _new_pdf()
        pdf.add_page()
        render_scoring_methodology(pdf)
        pdf.output(str(tmp_path / "scoring.pdf"))
        assert (tmp_path / "scoring.pdf").exists()
        assert (tmp_path / "scoring.pdf").stat().st_size > 100
