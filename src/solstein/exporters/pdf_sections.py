"""PDF report section renderers.

STORY-114: Helper functions that render individual sections of the
competitive intelligence PDF report. Split from pdf.py to comply
with the 500-line file size limit.

Each function receives the FPDF instance and the data it needs,
then renders its section in-place (no return value).
"""

from __future__ import annotations

import textwrap
from collections.abc import Sequence
from datetime import datetime, timezone

from fpdf import FPDF  # type: ignore[import]

from solstein.domain.models import Company

# Colour palette (RGB tuples)
_CLR_HEADING = (30, 58, 95)       # Dark navy
_CLR_SUBHEADING = (50, 90, 140)   # Medium blue
_CLR_BODY = (40, 40, 40)          # Near-black
_CLR_MUTED = (100, 100, 100)      # Grey
_CLR_ACCENT = (0, 120, 180)       # Bright blue for links / highlights
_CLR_WHITE = (255, 255, 255)
_CLR_LIGHT_BG = (240, 244, 248)   # Light blue-grey for table rows


def render_cover_page(
    pdf: FPDF,
    title: str,
    company_count: int,
    page_format: str,
) -> None:
    """Render the cover page with title, date, and classification badge."""
    pdf.add_page()

    # Push content down
    pdf.ln(40)

    # Title
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(*_CLR_HEADING)
    pdf.cell(0, 14, title, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(8)

    # Subtitle line
    pdf.set_font("Helvetica", size=12)
    pdf.set_text_color(*_CLR_MUTED)
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    pdf.cell(
        0, 8,
        f"Generated: {generated}  |  Companies: {company_count}  |  Format: {page_format.upper()}",
        new_x="LMARGIN", new_y="NEXT", align="C",
    )

    # Classification badge
    pdf.ln(20)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(220, 230, 241)
    pdf.set_text_color(*_CLR_HEADING)
    pdf.cell(0, 10, "CONFIDENTIAL - COMPETITIVE INTELLIGENCE", new_x="LMARGIN", new_y="NEXT", align="C", fill=True)

    pdf.set_text_color(*_CLR_BODY)


def render_executive_summary(pdf: FPDF, companies: Sequence[Company]) -> None:
    """Render executive summary section with tier distribution and avg score."""
    pdf.add_page()
    _section_heading(pdf, "Executive Summary")

    tier_counts: dict[str, int] = {}
    scores: list[float] = []
    for c in companies:
        tier_str = _tier_str(c)
        tier_counts[tier_str] = tier_counts.get(tier_str, 0) + 1
        score = getattr(c, "composite_score", None)
        if score is not None:
            scores.append(float(score))

    avg_score = sum(scores) / len(scores) if scores else 0.0

    pdf.set_font("Helvetica", size=11)
    pdf.set_text_color(*_CLR_BODY)
    pdf.multi_cell(
        0, 7,
        f"This report covers {len(companies)} companies.\n"
        f"Average composite score: {avg_score:.2f} / 10.0\n",
    )

    # Tier distribution table
    if tier_counts:
        _subsection_heading(pdf, "Tier Distribution")
        col_w = 60
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(*_CLR_HEADING)
        pdf.set_text_color(*_CLR_WHITE)
        pdf.cell(col_w, 8, "Tier", border=1, fill=True)
        pdf.cell(col_w, 8, "Count", border=1, new_x="LMARGIN", new_y="NEXT", fill=True)
        pdf.set_text_color(*_CLR_BODY)

        for idx, (tier, count) in enumerate(sorted(tier_counts.items())):
            pdf.set_font("Helvetica", size=10)
            if idx % 2 == 0:
                pdf.set_fill_color(*_CLR_LIGHT_BG)
            else:
                pdf.set_fill_color(*_CLR_WHITE)
            pdf.cell(col_w, 7, tier, border=1, fill=True)
            pdf.cell(col_w, 7, str(count), border=1, new_x="LMARGIN", new_y="NEXT", fill=True)

    pdf.ln(5)


def render_financial_overview(pdf: FPDF, companies: Sequence[Company]) -> None:
    """Render financial overview section with revenue and employee data."""
    _section_heading(pdf, "Financial Overview")

    # Collect financial data
    rows: list[tuple[str, str, str, str, str]] = []
    for c in companies:
        revenue = c.revenue or (c.financials.revenue if c.financials else None)
        employees = c.financials.employees if c.financials else None
        growth = c.growth_rate or (c.financials.growth_rate if c.financials else None)
        funding = c.funding or (c.financials.funding_raised if c.financials else None)

        rows.append((
            c.name[:30],
            _fmt_currency(revenue),
            str(employees) if employees else "N/A",
            f"{growth:.1%}" if growth is not None else "N/A",
            _fmt_currency(funding),
        ))

    if not rows:
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 8, "No financial data available.", new_x="LMARGIN", new_y="NEXT")
        return

    headers = ("Company", "Revenue", "Employees", "Growth", "Funding")
    col_widths = (55, 35, 30, 25, 35)

    # Header row
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(*_CLR_HEADING)
    pdf.set_text_color(*_CLR_WHITE)
    for header, w in zip(headers, col_widths):
        pdf.cell(w, 7, header, border=1, fill=True)
    pdf.ln()

    # Data rows
    pdf.set_text_color(*_CLR_BODY)
    pdf.set_font("Helvetica", size=9)
    for idx, row in enumerate(rows[:50]):  # Cap at 50 rows per table
        if idx % 2 == 0:
            pdf.set_fill_color(*_CLR_LIGHT_BG)
        else:
            pdf.set_fill_color(*_CLR_WHITE)
        for val, w in zip(row, col_widths):
            pdf.cell(w, 6, val, border=1, fill=True)
        pdf.ln()
        if pdf.get_y() > 260:
            pdf.add_page()

    pdf.ln(5)


def render_company_profile(
    pdf: FPDF,
    company: Company,
    rank: int,
    footnotes: list[tuple[int, str]],
) -> None:
    """Render a single company profile section with source citations."""
    if pdf.get_y() > 220:
        pdf.add_page()

    _subsection_heading(pdf, f"{rank}. {company.name}")
    pdf.set_font("Helvetica", size=10)
    pdf.set_text_color(*_CLR_BODY)

    # Basic info
    tier_str = _tier_str(company)
    score = getattr(company, "composite_score", 0.0) or 0.0
    industry = getattr(company, "industry", "N/A") or "N/A"
    hq = getattr(company, "headquarters", "N/A") or "N/A"
    website = getattr(company, "website", "") or ""

    info_lines = (
        f"Tier: {tier_str}  |  Score: {score:.2f}  |  Industry: {industry}\n"
        f"Headquarters: {hq}"
    )
    if website:
        info_lines += f"  |  Website: {website}"
    if pdf.get_y() > 260:
        pdf.add_page()
    pdf.multi_cell(0, 6, info_lines)

    # Description
    description = getattr(company, "description", "") or ""
    if description:
        if pdf.get_y() > 260:
            pdf.add_page()
        excerpt = textwrap.shorten(description, width=400, placeholder="...")
        pdf.set_text_color(*_CLR_MUTED)
        pdf.set_font("Helvetica", "I", 9)
        usable_w = pdf.w - pdf.l_margin - pdf.r_margin
        pdf.multi_cell(usable_w, 5, excerpt)
        pdf.set_text_color(*_CLR_BODY)

    # Financial details
    _render_company_financials(pdf, company)

    # Signal confidences
    signal_confs = getattr(company, "signal_confidences", {}) or {}
    if signal_confs:
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(0, 6, "Signal Confidence Scores:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=9)
        for signal, conf in sorted(signal_confs.items()):
            conf_pct = conf * 100 if conf <= 1.0 else conf
            pdf.cell(0, 5, f"  {signal}: {conf_pct:.0f}%", new_x="LMARGIN", new_y="NEXT")

    # Source citations as footnotes
    source_links = getattr(company, "source_links", []) or []
    metric_sources = getattr(company, "metric_sources", {}) or {}
    enrichment_sources = getattr(company, "enrichment_sources", []) or []

    all_sources = list(source_links)
    for src_list in metric_sources.values():
        all_sources.extend(src_list)
    all_sources.extend(enrichment_sources)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_sources: list[str] = []
    for src in all_sources:
        if src and src not in seen:
            seen.add(src)
            unique_sources.append(src)

    if unique_sources:
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(0, 6, "Sources:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=8)
        pdf.set_text_color(*_CLR_ACCENT)
        for src in unique_sources[:10]:  # Cap at 10 sources per company
            fn_num = len(footnotes) + 1
            footnotes.append((fn_num, src))
            display = textwrap.shorten(src, width=80, placeholder="...")
            pdf.cell(0, 5, f"  [{fn_num}] {display}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(*_CLR_BODY)

    pdf.ln(4)


def render_scoring_methodology(pdf: FPDF) -> None:
    """Render scoring methodology section."""
    if pdf.get_y() > 220:
        pdf.add_page()

    _section_heading(pdf, "Scoring Methodology")
    pdf.set_font("Helvetica", size=10)
    pdf.set_text_color(*_CLR_BODY)
    pdf.multi_cell(
        0, 6,
        "Companies are scored on a 0-10 composite scale derived from three "
        "sub-scores: Growth Score (revenue trajectory, employee growth, market "
        "expansion), Financial Health Score (profitability, margins, funding "
        "efficiency), and Competitive Position Score (market share, AI maturity, "
        "threat level). Each sub-score is weighted equally at 33.3%. Tier "
        "assignments follow: Phoenix (8.0+), Salt (5.0-7.9), Lead (<5.0).",
    )
    pdf.ln(5)


def render_footnotes(pdf: FPDF, footnotes: list[tuple[int, str]]) -> None:
    """Render endnotes/footnotes page with all source citations."""
    if not footnotes:
        return

    pdf.add_page()
    _section_heading(pdf, "Data Sources & Citations")
    pdf.set_font("Helvetica", size=8)
    pdf.set_text_color(*_CLR_BODY)

    for num, source in footnotes:
        if pdf.get_y() > 270:
            pdf.add_page()
        display = textwrap.shorten(source, width=120, placeholder="...")
        pdf.cell(0, 5, f"[{num}] {display}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(5)


# ------------------------------------------------------------------
# Revenue trend chart (simple bar chart via cell drawing)
# ------------------------------------------------------------------

def render_revenue_chart(pdf: FPDF, companies: Sequence[Company]) -> None:
    """Render a simple revenue comparison bar chart using fpdf2 drawing."""
    # Filter companies with revenue data
    chart_data: list[tuple[str, float]] = []
    for c in companies:
        rev = c.revenue or (c.financials.revenue if c.financials else None)
        if rev is not None and rev > 0:
            chart_data.append((c.name[:20], rev))

    if len(chart_data) < 2:
        return  # Not enough data for a chart

    # Sort by revenue descending, take top 15
    chart_data.sort(key=lambda x: x[1], reverse=True)
    chart_data = chart_data[:15]

    if pdf.get_y() > 180:
        pdf.add_page()

    _subsection_heading(pdf, "Revenue Comparison (Top Companies)")

    max_rev = max(r for _, r in chart_data)
    bar_max_width = 100
    bar_height = 6
    label_width = 45

    pdf.set_font("Helvetica", size=8)
    for name, rev in chart_data:
        bar_width = (rev / max_rev) * bar_max_width if max_rev > 0 else 0

        # Company name
        pdf.set_text_color(*_CLR_BODY)
        pdf.cell(label_width, bar_height, name, new_x="RIGHT")

        # Bar
        pdf.set_fill_color(*_CLR_ACCENT)
        pdf.cell(bar_width, bar_height, "", fill=True, new_x="RIGHT")

        # Value label
        pdf.set_text_color(*_CLR_MUTED)
        pdf.cell(30, bar_height, f"  {_fmt_currency(rev)}", new_x="LMARGIN", new_y="NEXT")

        if pdf.get_y() > 270:
            pdf.add_page()

    pdf.ln(5)


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------

def _section_heading(pdf: FPDF, text: str) -> None:
    """Render a section heading."""
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*_CLR_HEADING)
    pdf.cell(0, 10, text, new_x="LMARGIN", new_y="NEXT")
    # Underline
    pdf.set_draw_color(*_CLR_ACCENT)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(4)
    pdf.set_text_color(*_CLR_BODY)


def _subsection_heading(pdf: FPDF, text: str) -> None:
    """Render a subsection heading."""
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*_CLR_SUBHEADING)
    pdf.cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*_CLR_BODY)


def _tier_str(company: Company) -> str:
    """Extract tier as a display string."""
    tier = getattr(company, "tier", "N/A")
    return tier.value if hasattr(tier, "value") else str(tier)


def _fmt_currency(value: float | None) -> str:
    """Format a number as a compact currency string."""
    if value is None:
        return "N/A"
    if abs(value) >= 1_000_000_000:
        return f"${value / 1_000_000_000:.1f}B"
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:.0f}K"
    return f"${value:,.0f}"


def _render_company_financials(pdf: FPDF, company: Company) -> None:
    """Render inline financial details for a company profile."""
    fin = company.financials
    if not fin:
        return

    parts: list[str] = []
    if fin.revenue is not None:
        parts.append(f"Revenue: {_fmt_currency(fin.revenue)}")
    if fin.employees is not None:
        parts.append(f"Employees: {fin.employees:,}")
    if fin.profit_margin is not None:
        parts.append(f"Margin: {fin.profit_margin:.1%}")
    if fin.funding_raised is not None:
        parts.append(f"Funding: {_fmt_currency(fin.funding_raised)}")

    if parts:
        pdf.set_font("Helvetica", size=9)
        pdf.cell(0, 5, "  |  ".join(parts), new_x="LMARGIN", new_y="NEXT")
