"""PDF exporter for competitive intelligence reports.

Generates a structured PDF report from company profiles.

**Dependency approach**:
- Uses ``fpdf2`` (``pip install fpdf2``) when available — rich formatted output
- Falls back to a plain-text ``.txt`` file when fpdf2 is not installed

Usage::

    from pathlib import Path
    from solstein.exporters.pdf import PDFExporter

    exporter = PDFExporter()
    path = exporter.export(companies, title="Q1 2026 Market Intelligence Report")
    print(f"Report written to {path}")
"""

from __future__ import annotations

import textwrap
from datetime import datetime
from pathlib import Path
from typing import Sequence

from loguru import logger

from solstein.domain.models import Company

# Try to import fpdf2; fall back gracefully
try:
    from fpdf import FPDF  # type: ignore[import]

    _FPDF_AVAILABLE = True
except ImportError:
    _FPDF_AVAILABLE = False


class PDFExporter:
    """Generates competitive intelligence PDF reports from Company objects.

    When fpdf2 is not installed, falls back to a plain-text report
    with ``.txt`` extension so callers always get a usable file.
    """

    def export(
        self,
        companies: Sequence[Company],
        output_path: Path | None = None,
        title: str = "Solstein Competitive Intelligence Report",
    ) -> Path:
        """Write the report to *output_path*.

        Args:
            companies: Companies to include in the report.
            output_path: Destination path.  Defaults to ``./report.pdf``.
            title: Report title shown on the cover page.

        Returns:
            Resolved path to the written file.
        """
        if _FPDF_AVAILABLE:
            return self._export_pdf(companies, output_path or Path("report.pdf"), title)
        else:
            txt_path = (output_path or Path("report.pdf")).with_suffix(".txt")
            logger.warning(
                "fpdf2 not installed \u2014 generating plain-text report instead. "
                "Install fpdf2 for PDF output: pip install fpdf2",
                output=str(txt_path),
            )
            return self._export_text(companies, txt_path, title)

    # ------------------------------------------------------------------
    # fpdf2 implementation
    # ------------------------------------------------------------------

    def _export_pdf(self, companies: Sequence[Company], path: Path, title: str) -> Path:
        """Generate a PDF report using fpdf2."""
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Cover page
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 24)
        pdf.cell(0, 40, title, ln=True, align="C")
        pdf.set_font("Helvetica", size=12)
        pdf.cell(
            0,
            10,
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}  |  Companies: {len(companies)}",
            ln=True,
            align="C",
        )
        pdf.ln(20)

        # Executive summary
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Executive Summary", ln=True)
        pdf.set_font("Helvetica", size=11)

        phoenix_count = sum(1 for c in companies if str(getattr(c, "tier", "")).lower() == "phoenix")
        salt_count = sum(1 for c in companies if str(getattr(c, "tier", "")).lower() == "salt")
        lead_count = sum(1 for c in companies if str(getattr(c, "tier", "")).lower() == "lead")
        scores = [s for c in companies if (s := getattr(c, "composite_score", None)) is not None]
        avg_score = sum(scores) / len(scores) if scores else 0.0

        pdf.multi_cell(
            0,
            7,
            f"Total companies analysed: {len(companies)}\n"
            f"Phoenix tier: {phoenix_count}  |  Salt tier: {salt_count}  |  Lead tier: {lead_count}\n"
            f"Average composite score: {avg_score:.2f} / 10.0",
        )
        pdf.ln(10)

        # Company profiles
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Company Profiles", ln=True)

        for rank, company in enumerate(companies, 1):
            if pdf.get_y() > 240:
                pdf.add_page()

            pdf.set_font("Helvetica", "B", 13)
            pdf.cell(0, 8, f"{rank}. {company.name}", ln=True)
            pdf.set_font("Helvetica", size=10)

            tier = getattr(company, "tier", "N/A")
            tier_str = tier.value if hasattr(tier, "value") else str(tier)
            score = getattr(company, "composite_score", 0.0) or 0.0
            industry = getattr(company, "industry", "N/A") or "N/A"
            headquarters = getattr(company, "headquarters", "N/A") or "N/A"

            pdf.multi_cell(
                0,
                6,
                f"Tier: {tier_str}  |  Score: {score:.2f}  |  Industry: {industry}\nHeadquarters: {headquarters}",
            )

            description = getattr(company, "description", "") or ""
            if description:
                excerpt = textwrap.shorten(description, width=300, placeholder="...")
                pdf.set_text_color(80, 80, 80)
                pdf.multi_cell(0, 6, excerpt)
                pdf.set_text_color(0, 0, 0)
            pdf.ln(5)

        path.parent.mkdir(parents=True, exist_ok=True)
        pdf.output(str(path))
        logger.info("PDF report generated", path=str(path), companies=len(companies))
        return path.resolve()

    # ------------------------------------------------------------------
    # Plain-text fallback
    # ------------------------------------------------------------------

    def _export_text(self, companies: Sequence[Company], path: Path, title: str) -> Path:
        """Write a plain-text intelligence report (fpdf2 not available)."""
        lines: list[str] = []
        sep = "=" * 80

        lines += [
            sep,
            title.upper().center(80),
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}".center(80),
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
