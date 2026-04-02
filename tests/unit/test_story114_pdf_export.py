"""Tests for STORY-114: PDF export format — core exporter tests.

Covers PDFExporter generation, page formats, source citations,
financial content, progress callbacks, and text fallback.
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

from solstein.domain.models import Company, CompanyTier, FinancialMetric
from solstein.exporters.pdf import (
    DEFAULT_PAGE_FORMAT,
    SUPPORTED_PAGE_FORMATS,
    PDFExporter,
    is_fpdf_available,
)


def _make_company(**kwargs: Any) -> Company:
    """Create a Company with sensible defaults for PDF testing."""
    defaults: dict[str, Any] = {
        "id": f"TEST-{uuid.uuid4().hex[:8].upper()}",
        "name": kwargs.pop("name", "Acme Corp"),
        "industry": "Energy Software",
        "description": "A leading provider of energy management solutions.",
        "headquarters": "Munich, Germany",
        "website": "https://acme.example.com",
        "tier": CompanyTier.TIER_1,
        "composite_score": 8.5,
        "revenue": 50_000_000,
        "growth_rate": 0.25,
        "funding": 10_000_000,
        "source_links": ["https://sec.gov/filing/123", "https://companieshouse.gov.uk/456"],
        "enrichment_sources": ["SEC EDGAR", "Companies House"],
        "signal_confidences": {"growth": 0.85, "financial_health": 0.72},
        "financials": FinancialMetric(
            revenue=50_000_000,
            employees=200,
            profit_margin=0.15,
            funding_raised=10_000_000,
            allow_empty_primary=True,
        ),
    }
    defaults.update(kwargs)
    return Company(**defaults)


def _make_companies(count: int = 3) -> list[Company]:
    """Create a list of test companies."""
    names = ["Acme Corp", "Beta Industries", "Gamma Solutions", "Delta Tech", "Epsilon AI"]
    return [
        _make_company(
            name=f"{names[i % len(names)]} {i + 1}",
            composite_score=8.5 - i * 1.5,
            revenue=50_000_000 * (count - i),
        )
        for i in range(count)
    ]


class TestPDFExporterBasic:
    """Test basic PDFExporter functionality."""

    def test_fpdf_available(self) -> None:
        assert is_fpdf_available() is True

    def test_export_creates_pdf_file(self, tmp_path: Path) -> None:
        result = PDFExporter().export(_make_companies(2), output_path=tmp_path / "report.pdf")
        assert result.exists()
        assert result.read_bytes()[:4] == b"%PDF"

    def test_export_empty_companies(self, tmp_path: Path) -> None:
        result = PDFExporter().export([], output_path=tmp_path / "empty.pdf")
        assert result.exists() and result.read_bytes()[:4] == b"%PDF"

    def test_export_creates_parent_dirs(self, tmp_path: Path) -> None:
        result = PDFExporter().export(_make_companies(1), output_path=tmp_path / "sub" / "dir" / "r.pdf")
        assert result.exists()


class TestPageFormats:
    """Test A4 and Letter page format support."""

    def test_supported_formats(self) -> None:
        assert "a4" in SUPPORTED_PAGE_FORMATS and "letter" in SUPPORTED_PAGE_FORMATS
        assert DEFAULT_PAGE_FORMAT == "a4"

    def test_a4_export(self, tmp_path: Path) -> None:
        result = PDFExporter().export(_make_companies(1), output_path=tmp_path / "a4.pdf", page_format="a4")
        assert result.exists() and result.read_bytes()[:4] == b"%PDF"

    def test_letter_export(self, tmp_path: Path) -> None:
        result = PDFExporter().export(_make_companies(1), output_path=tmp_path / "l.pdf", page_format="letter")
        assert result.exists() and result.read_bytes()[:4] == b"%PDF"

    def test_invalid_format_falls_back(self, tmp_path: Path) -> None:
        result = PDFExporter().export(_make_companies(1), output_path=tmp_path / "f.pdf", page_format="tabloid")
        assert result.exists()

    def test_case_insensitive(self, tmp_path: Path) -> None:
        result = PDFExporter().export(_make_companies(1), output_path=tmp_path / "u.pdf", page_format="LETTER")
        assert result.exists()


class TestSourceCitations:
    """Test source citations and file size."""

    def test_pdf_under_5mb(self, tmp_path: Path) -> None:
        result = PDFExporter().export(
            [_make_company(source_links=[f"https://s{i}.example.com" for i in range(10)])],
            output_path=tmp_path / "s.pdf",
        )
        assert result.stat().st_size / (1024 * 1024) <= 5.0

    def test_sources_render_in_pdf(self, tmp_path: Path) -> None:
        """Source links should be included — verify via footnote accumulation."""
        from fpdf import FPDF

        from solstein.exporters.pdf_sections import render_company_profile

        pdf = FPDF(format="a4")
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        footnotes: list[tuple[int, str]] = []
        company = _make_company(source_links=["https://unique-source.example.com/report"])
        render_company_profile(pdf, company, 1, footnotes)
        # The footnotes list should contain our source
        source_urls = [url for _, url in footnotes]
        assert "https://unique-source.example.com/report" in source_urls

    def test_enrichment_sources_render(self, tmp_path: Path) -> None:
        """Enrichment sources should not crash the renderer and produce valid PDF."""
        result = PDFExporter().export(
            [_make_company(enrichment_sources=["Bloomberg Terminal", "Reuters Eikon"])],
            output_path=tmp_path / "e.pdf",
        )
        assert result.exists() and result.read_bytes()[:4] == b"%PDF"


class TestProgressCallback:
    """Test progress callback integration."""

    def test_callback_called(self, tmp_path: Path) -> None:
        cb = MagicMock()
        PDFExporter().export(_make_companies(2), output_path=tmp_path / "p.pdf", progress_callback=cb)
        assert cb.call_count > 0
        calls = [c.args[0] for c in cb.call_args_list]
        assert calls[0] < calls[-1] and calls[-1] >= 90

    def test_broken_callback_ok(self, tmp_path: Path) -> None:
        result = PDFExporter().export(
            _make_companies(1),
            output_path=tmp_path / "b.pdf",
            progress_callback=lambda p: (_ for _ in ()).throw(RuntimeError),
        )
        assert result.exists()


class TestTextFallback:
    """Test plain-text fallback."""

    def test_fallback_produces_txt(self, tmp_path: Path) -> None:
        with patch("solstein.exporters.pdf._FPDF_AVAILABLE", False):
            result = PDFExporter().export(_make_companies(2), output_path=tmp_path / "f.pdf")
        assert result.suffix == ".txt" and "SOLSTEIN" in result.read_text()


class TestAsyncPipelineWiring:
    """Test that PDF is wired into the export pipeline."""

    _SRC = Path(__file__).parent.parent.parent / "src" / "solstein"

    def test_pdf_in_valid_formats(self) -> None:
        assert '"pdf"' in (self._SRC / "api" / "routers" / "exports.py").read_text()

    def test_generate_pdf_in_tasks(self) -> None:
        content = (self._SRC / "worker" / "export_tasks.py").read_text()
        assert "async def _generate_pdf(" in content and "PDFExporter" in content

    def test_pdf_exporter_in_init(self) -> None:
        assert "PDFExporter" in (self._SRC / "exporters" / "__init__.py").read_text()


class TestEdgeCases:
    """Test edge cases."""

    def test_no_financials(self, tmp_path: Path) -> None:
        result = PDFExporter().export(
            [_make_company(financials=None, revenue=None, funding=None)],
            output_path=tmp_path / "nf.pdf",
        )
        assert result.exists()

    def test_no_sources(self, tmp_path: Path) -> None:
        result = PDFExporter().export(
            [_make_company(source_links=[], enrichment_sources=[], signal_confidences={})],
            output_path=tmp_path / "ns.pdf",
        )
        assert result.exists()

    def test_large_list(self, tmp_path: Path) -> None:
        result = PDFExporter().export(_make_companies(25), output_path=tmp_path / "lg.pdf")
        assert result.exists() and result.stat().st_size < 5 * 1024 * 1024

    def test_special_chars(self, tmp_path: Path) -> None:
        result = PDFExporter().export(
            [_make_company(name="Muller & Sohne GmbH (DE)")],
            output_path=tmp_path / "sp.pdf",
        )
        assert result.exists()
