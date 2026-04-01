"""PDF exporter for competitive intelligence reports.

STORY-114: Full-featured PDF export with structured sections, source
citations as footnotes, revenue charts, financial overview, and
configurable page sizes (A4 / Letter).

Uses ``fpdf2`` (``pip install fpdf2``) for PDF generation. Falls back
to a plain-text ``.txt`` file when fpdf2 is not installed.

Usage::

    from pathlib import Path
    from solstein.exporters.pdf import PDFExporter

    exporter = PDFExporter()
    path = exporter.export(
        companies,
        title="Q1 2026 Market Intelligence Report",
        page_format="a4",
    )
"""

from __future__ import annotations

import textwrap
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from loguru import logger

from solstein.domain.models import Company

# Try to import fpdf2; fall back gracefully
try:
    from fpdf import FPDF  # type: ignore[import]

    _FPDF_AVAILABLE = True
except ImportError:
    _FPDF_AVAILABLE = False

# Supported page formats
SUPPORTED_PAGE_FORMATS = frozenset({"a4", "letter"})
DEFAULT_PAGE_FORMAT = "a4"


def is_fpdf_available() -> bool:
    """Check whether fpdf2 is installed (useful for tests)."""
    return _FPDF_AVAILABLE


class PDFExporter:
    """Generates competitive intelligence PDF reports from Company objects.

    Supports configurable page size (A4 or Letter) and optional
    progress callbacks for async export tracking.

    When fpdf2 is not installed, falls back to a plain-text report
    with ``.txt`` extension so callers always get a usable file.
    """

    def export(
        self,
        companies: Sequence[Company],
        output_path: Path | None = None,
        title: str = "Solstein Competitive Intelligence Report",
        page_format: str = DEFAULT_PAGE_FORMAT,
        progress_callback: Any | None = None,
    ) -> Path:
        """Write the report to *output_path*.

        Args:
            companies: Companies to include in the report.
            output_path: Destination path.  Defaults to ``./report.pdf``.
            title: Report title shown on the cover page.
            page_format: Page size - ``"a4"`` or ``"letter"``.
            progress_callback: Optional ``(pct: int) -> None`` for progress.

        Returns:
            Resolved path to the written file.
        """
        fmt = page_format.lower()
        if fmt not in SUPPORTED_PAGE_FORMATS:
            logger.warning(
                "[PDFExporter] Unknown page format '%s', defaulting to A4",
                page_format,
            )
            fmt = DEFAULT_PAGE_FORMAT

        if _FPDF_AVAILABLE:
            return self._export_pdf(
                companies,
                output_path or Path("report.pdf"),
                title,
                fmt,
                progress_callback,
            )

        txt_path = (output_path or Path("report.pdf")).with_suffix(".txt")
        logger.warning(
            "fpdf2 not installed — generating plain-text report instead. "
            "Install fpdf2 for PDF output: pip install fpdf2",
            output=str(txt_path),
        )
        return self._export_text(companies, txt_path, title)

    # ------------------------------------------------------------------
    # fpdf2 implementation
    # ------------------------------------------------------------------

    def _export_pdf(
        self,
        companies: Sequence[Company],
        path: Path,
        title: str,
        page_format: str,
        progress_callback: Any | None,
    ) -> Path:
        """Generate a structured PDF report using fpdf2."""
        from .pdf_sections import (
            render_company_profile,
            render_cover_page,
            render_executive_summary,
            render_financial_overview,
            render_footnotes,
            render_revenue_chart,
            render_scoring_methodology,
        )

        pdf = FPDF(format=page_format)
        pdf.set_auto_page_break(auto=True, margin=15)

        _notify(progress_callback, 5)

        # 1. Cover page
        render_cover_page(pdf, title, len(companies), page_format)
        _notify(progress_callback, 10)

        # 2. Executive summary
        render_executive_summary(pdf, companies)
        _notify(progress_callback, 20)

        # 3. Financial overview table
        render_financial_overview(pdf, companies)
        _notify(progress_callback, 30)

        # 4. Revenue chart
        render_revenue_chart(pdf, companies)
        _notify(progress_callback, 40)

        # 5. Company profiles with source citations
        footnotes: list[tuple[int, str]] = []
        total = len(companies)
        for rank, company in enumerate(companies, 1):
            render_company_profile(pdf, company, rank, footnotes)
            if total > 0:
                pct = 40 + int((rank / total) * 40)  # 40-80%
                _notify(progress_callback, min(pct, 80))

        # 6. Scoring methodology
        render_scoring_methodology(pdf)
        _notify(progress_callback, 85)

        # 7. Footnotes / endnotes
        render_footnotes(pdf, footnotes)
        _notify(progress_callback, 90)

        # Write file
        path.parent.mkdir(parents=True, exist_ok=True)
        pdf.output(str(path))
        _notify(progress_callback, 99)

        logger.info(
            "[PDFExporter] PDF report generated",
            path=str(path),
            companies=len(companies),
            page_format=page_format,
        )
        return path.resolve()

    # ------------------------------------------------------------------
    # Plain-text fallback
    # ------------------------------------------------------------------

    def _export_text(
        self,
        companies: Sequence[Company],
        path: Path,
        title: str,
    ) -> Path:
        """Write a plain-text intelligence report (fpdf2 not available)."""
        lines: list[str] = []
        sep = "=" * 80

        lines += [
            sep,
            title.upper().center(80),
            f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}".center(80),
            f"Companies: {len(companies)}".center(80),
            sep,
            "",
        ]

        for rank, c in enumerate(companies, 1):
            tier = getattr(c, "tier", "N/A")
            tier_str = tier.value if hasattr(tier, "value") else str(tier)
            score = getattr(c, "composite_score", 0.0) or 0.0
            industry = getattr(c, "industry", "N/A") or "N/A"
            description = getattr(c, "description", "") or ""

            lines += [
                f"{rank:3}. {c.name}",
                f"     Tier: {tier_str}  |  Score: {score:.2f}  |  Industry: {industry}",
            ]
            if description:
                excerpt = textwrap.shorten(description, width=76, placeholder="...")
                lines.append(f"     {excerpt}")
            lines.append("")

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines), encoding="utf-8")
        logger.info("Text report generated (fpdf2 not available)", path=str(path))
        return path.resolve()


def _notify(callback: Any | None, pct: int) -> None:
    """Call the progress callback if provided."""
    if callback is not None:
        try:
            callback(pct)
        except Exception:  # noqa: BLE001
            pass  # Progress updates are best-effort
