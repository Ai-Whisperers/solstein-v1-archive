"""Excel sheet generators.

EPIC-022: Extracted from ImprovedExcelExporter for modularity.
Each sheet type has its own generator function.
"""

from typing import Any

from loguru import logger

from ...domain.models import Company
from ...exporters.export_schema import get_headers_for_sheet
from .styles import ExcelStyles, LayoutConstants
from .utils import auto_adjust_columns, format_number, format_percentage, safe_get, safe_get_financial


def add_title_banner(
    ws: Any, styles: ExcelStyles, title: str, subtitle: str = "", num_columns: int = 10
) -> None:
    """Add a title banner to the worksheet.

    Args:
        ws: Worksheet to add banner to
        styles: Excel styles
        title: Main title
        subtitle: Optional subtitle
        num_columns: Number of columns to span for merge
    """

    # Merge cells for title
    ws.merge_cells(
        start_row=LayoutConstants.TITLE_ROW,
        start_column=LayoutConstants.TITLE_COLUMN,
        end_row=LayoutConstants.TITLE_ROW,
        end_column=num_columns,
    )

    # Add title
    title_cell = ws.cell(row=LayoutConstants.TITLE_ROW, column=LayoutConstants.TITLE_COLUMN)
    title_cell.value = title
    title_cell.font = styles.title_font
    title_cell.fill = styles.header_fill
    title_cell.alignment = styles.header_alignment

    # Add subtitle if provided
    if subtitle:
        ws.merge_cells(
            start_row=LayoutConstants.SUBTITLE_ROW,
            start_column=LayoutConstants.TITLE_COLUMN,
            end_row=LayoutConstants.SUBTITLE_ROW,
            end_column=num_columns,
        )
        subtitle_cell = ws.cell(row=LayoutConstants.SUBTITLE_ROW, column=LayoutConstants.TITLE_COLUMN)
        subtitle_cell.value = subtitle
        subtitle_cell.font = styles.subheader_font
        subtitle_cell.fill = styles.subheader_fill
        subtitle_cell.alignment = styles.subheader_alignment

    # Set row heights
    ws.row_dimensions[LayoutConstants.TITLE_ROW].height = 30
    if subtitle:
        ws.row_dimensions[LayoutConstants.SUBTITLE_ROW].height = 25


def write_headers(ws: Any, styles: ExcelStyles, headers: list[str], row: int | None = None) -> None:
    """Write column headers to the worksheet.

    Args:
        ws: Worksheet to write to
        styles: Excel styles
        headers: List of header strings
        row: Row number (defaults to HEADER_ROW)
    """
    if row is None:
        row = LayoutConstants.HEADER_ROW

    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=row, column=col_idx)
        cell.value = header
        cell.font = styles.header_font
        cell.fill = styles.header_fill
        cell.alignment = styles.header_alignment
        cell.border = styles.standard_border


def _write_executive_row(ws: Any, styles: ExcelStyles, row: int, idx: int, company: Company) -> None:
    """Write a single company row to the Executive Summary sheet.

    Args:
        ws: Worksheet to write to
        styles: Excel styles
        row: Row number (1-based)
        idx: Row index for alternating fills (0-based)
        company: Company data
    """
    row_fill = styles.get_row_fill(idx)
    classified_fill = styles.get_row_fill(idx, safe_get(company, "classification"))

    # Core identification columns
    cell = ws.cell(row=row, column=1)
    cell.value = safe_get(company, "name", "Unknown")
    cell.font, cell.alignment, cell.fill = styles.data_font, styles.data_alignment, classified_fill

    cell = ws.cell(row=row, column=2)
    cell.value = safe_get(company, "industry", "N/A")
    cell.font, cell.alignment, cell.fill = styles.data_font, styles.data_alignment, row_fill

    # Financial metrics
    cell = ws.cell(row=row, column=3)
    cell.value = format_number(safe_get_financial(company, "revenue_eur_m"), 1, "M")
    cell.font, cell.alignment, cell.fill = styles.data_font, styles.number_alignment, row_fill

    cell = ws.cell(row=row, column=4)
    cell.value = format_percentage(safe_get_financial(company, "growth_rate_pct"), 1)
    cell.font, cell.alignment, cell.fill = styles.data_font, styles.number_alignment, row_fill

    # AI & readiness scores
    cell = ws.cell(row=row, column=5)
    cell.value = format_number(safe_get(company, "ai_score"), 2)
    cell.font, cell.alignment, cell.fill = styles.data_font, styles.number_alignment, row_fill

    ai_readiness = safe_get(company, "ai_readiness_score")
    cell = ws.cell(row=row, column=6)
    cell.value = format_number(ai_readiness, 1) if ai_readiness else "N/A"
    cell.font, cell.alignment, cell.fill = styles.data_font, styles.number_alignment, row_fill

    cell = ws.cell(row=row, column=7)
    cell.value = safe_get(company, "ai_readiness_tier", "N/A")
    cell.font, cell.alignment, cell.fill = styles.data_font, styles.data_alignment, row_fill

    # Classification
    cell = ws.cell(row=row, column=8)
    cell.value = safe_get(company, "tier", "Unknown")
    cell.font, cell.alignment, cell.fill = styles.data_font, styles.data_alignment, row_fill

    cell = ws.cell(row=row, column=9)
    cell.value = safe_get(company, "threat_level", "Unknown")
    cell.font, cell.alignment, cell.fill = styles.data_font, styles.data_alignment, row_fill

    # STORY-125: Company detail fields
    tech = safe_get(company, "tech_stack", [])
    cell = ws.cell(row=row, column=10)
    cell.value = ", ".join(tech) if tech else "N/A"
    cell.font, cell.alignment, cell.fill = styles.data_font, styles.data_alignment, row_fill

    customers = safe_get(company, "key_customers", [])
    cell = ws.cell(row=row, column=11)
    cell.value = ", ".join(customers) if customers else "N/A"
    cell.font, cell.alignment, cell.fill = styles.data_font, styles.data_alignment, row_fill

    positions = safe_get(company, "open_positions")
    cell = ws.cell(row=row, column=12)
    cell.value = format_number(positions, 0) if positions else "N/A"
    cell.font, cell.alignment, cell.fill = styles.data_font, styles.number_alignment, row_fill

    cell = ws.cell(row=row, column=13)
    cell.value = safe_get(company, "data_availability", "N/A")
    cell.font, cell.alignment, cell.fill = styles.data_font, styles.data_alignment, row_fill

    # STORY-250: Transformation Readiness fields
    transform_time = safe_get(company, "transformation_time_months")
    cell = ws.cell(row=row, column=14)
    cell.value = format_number(transform_time, 1) if transform_time else "N/A"
    cell.font, cell.alignment, cell.fill = styles.data_font, styles.number_alignment, row_fill

    transform_cost = safe_get(company, "transformation_cost_eur")
    cell = ws.cell(row=row, column=15)
    cell.value = format_number(transform_cost, 0) if transform_cost else "N/A"
    cell.font, cell.alignment, cell.fill = styles.data_font, styles.number_alignment, row_fill

    cell = ws.cell(row=row, column=16)
    cell.value = safe_get(company, "transformation_risk_level", "N/A")
    cell.font, cell.alignment, cell.fill = styles.data_font, styles.data_alignment, row_fill


def add_executive_summary(ws: Any, styles: ExcelStyles, profiles: list[Company]) -> None:
    """Add executive summary sheet.

    Args:
        ws: Worksheet to add to
        styles: Excel styles
        profiles: List of company profiles
    """
    logger.info(f"Adding executive summary for {len(profiles)} companies")

    # Title
    add_title_banner(ws, styles, "Executive Summary", "Market Intelligence Dashboard", num_columns=16)

    # STORY-250: Headers derived from single authoritative schema — drift-proof
    headers = get_headers_for_sheet("Executive Summary")
    write_headers(ws, styles, headers)

    # Data rows
    for idx, company in enumerate(profiles):
        _write_executive_row(ws, styles, LayoutConstants.DATA_START_ROW + idx, idx, company)

    # Auto-adjust columns
    auto_adjust_columns(ws)

    logger.info("Executive summary complete")


def add_market_rankings(ws: Any, styles: ExcelStyles, profiles: list[Company]) -> None:
    """Add market rankings sheet.

    Args:
        ws: Worksheet to add to
        styles: Excel styles
        profiles: List of company profiles
    """
    logger.info(f"Adding market rankings for {len(profiles)} companies")

    # Title
    add_title_banner(ws, styles, "Market Rankings", "Competitive Position Analysis")

    # STORY-250: Headers derived from single authoritative schema — drift-proof
    headers = get_headers_for_sheet("Market Rankings")
    write_headers(ws, styles, headers)

    # Sort by competitive score
    sorted_profiles = sorted(
        profiles,
        key=lambda x: safe_get(x, "competitive_position_score", 0) or 0,
        reverse=True,
    )

    # Data rows
    for idx, company in enumerate(sorted_profiles):
        row = LayoutConstants.DATA_START_ROW + idx

        # Rank
        cell = ws.cell(row=row, column=1)
        cell.value = idx + 1
        cell.font = styles.data_font
        cell.alignment = styles.number_alignment
        cell.fill = styles.get_row_fill(idx, safe_get(company, "classification"))

        # Company name
        cell = ws.cell(row=row, column=2)
        cell.value = safe_get(company, "name", "Unknown")
        cell.font = styles.data_font
        cell.alignment = styles.data_alignment
        cell.fill = styles.get_row_fill(idx)

        # Market Share
        cell = ws.cell(row=row, column=3)
        market_share = safe_get(company, "market_share_pct")
        cell.value = format_percentage(market_share, 1)
        cell.font = styles.data_font
        cell.alignment = styles.number_alignment
        cell.fill = styles.get_row_fill(idx)

        # Competitive Score
        cell = ws.cell(row=row, column=4)
        score = safe_get(company, "competitive_position_score")
        cell.value = format_number(score, 2)
        cell.font = styles.data_font
        cell.alignment = styles.number_alignment
        cell.fill = styles.get_row_fill(idx)

        # Growth Rate
        cell = ws.cell(row=row, column=5)
        growth = safe_get_financial(company, "growth_rate_pct")
        cell.value = format_percentage(growth, 1)
        cell.font = styles.data_font
        cell.alignment = styles.number_alignment
        cell.fill = styles.get_row_fill(idx)

        # Employees
        cell = ws.cell(row=row, column=6)
        employees = safe_get(company, "employee_count")
        cell.value = format_number(employees, 0)
        cell.font = styles.data_font
        cell.alignment = styles.number_alignment
        cell.fill = styles.get_row_fill(idx)

    # Auto-adjust columns
    auto_adjust_columns(ws)

    logger.info("Market rankings complete")


def _format_funding_rounds(rounds: list[Any]) -> str:
    """Format funding rounds list into a display string.

    Args:
        rounds: List of funding round dicts

    Returns:
        Formatted string or "N/A"
    """
    if not rounds:
        return "N/A"
    summaries = []
    for r in rounds:
        if isinstance(r, dict):
            label = r.get("round", r.get("stage", ""))
            amount = r.get("amount", r.get("amount_eur", ""))
            summaries.append(f"{label}: {amount}" if label else str(amount))
    return "; ".join(summaries) if summaries else "N/A"


def _write_financial_row(ws: Any, styles: ExcelStyles, row: int, idx: int, company: Company) -> None:
    """Write a single company row to the Financial Intelligence sheet.

    Args:
        ws: Worksheet to write to
        styles: Excel styles
        row: Row number (1-based)
        idx: Row index for alternating fills (0-based)
        company: Company data
    """
    row_fill = styles.get_row_fill(idx)
    classified_fill = styles.get_row_fill(idx, safe_get(company, "classification"))

    cell = ws.cell(row=row, column=1)
    cell.value = safe_get(company, "name", "Unknown")
    cell.font, cell.alignment, cell.fill = styles.data_font, styles.data_alignment, classified_fill

    cell = ws.cell(row=row, column=2)
    cell.value = format_number(safe_get_financial(company, "revenue_eur_m"), 1, "M")
    cell.font, cell.alignment, cell.fill = styles.data_font, styles.number_alignment, row_fill

    cell = ws.cell(row=row, column=3)
    cell.value = format_percentage(safe_get_financial(company, "growth_rate_pct"), 1)
    cell.font, cell.alignment, cell.fill = styles.data_font, styles.number_alignment, row_fill

    cell = ws.cell(row=row, column=4)
    cell.value = format_percentage(safe_get_financial(company, "profit_margin_pct"), 1)
    cell.font, cell.alignment, cell.fill = styles.data_font, styles.number_alignment, row_fill

    cell = ws.cell(row=row, column=5)
    cell.value = format_number(safe_get_financial(company, "total_funding_raised_eur"), 1, "M")
    cell.font, cell.alignment, cell.fill = styles.data_font, styles.number_alignment, row_fill

    cell = ws.cell(row=row, column=6)
    cell.value = format_number(safe_get_financial(company, "latest_valuation_eur"), 1, "M")
    cell.font, cell.alignment, cell.fill = styles.data_font, styles.number_alignment, row_fill

    investors = safe_get(company, "lead_investors", [])
    cell = ws.cell(row=row, column=7)
    cell.value = ", ".join(investors) if investors else "N/A"
    cell.font, cell.alignment, cell.fill = styles.data_font, styles.data_alignment, row_fill

    cell = ws.cell(row=row, column=8)
    cell.value = _format_funding_rounds(safe_get(company, "funding_rounds", []))
    cell.font, cell.alignment, cell.fill = styles.data_font, styles.data_alignment, row_fill

    cell = ws.cell(row=row, column=9)
    cell.value = safe_get(company, "funding_war_chest", "N/A")
    cell.font, cell.alignment, cell.fill = styles.data_font, styles.data_alignment, row_fill

    cell = ws.cell(row=row, column=10)
    cell.value = format_percentage(safe_get(company, "revenue_cagr_5yr"), 1)
    cell.font, cell.alignment, cell.fill = styles.data_font, styles.number_alignment, row_fill

    cell = ws.cell(row=row, column=11)
    cell.value = format_number(safe_get(company, "revenue_per_employee_eur_k"), 1, "K")
    cell.font, cell.alignment, cell.fill = styles.data_font, styles.number_alignment, row_fill

    cell = ws.cell(row=row, column=12)
    cell.value = format_percentage(safe_get(company, "employee_cagr_3yr"), 1)
    cell.font, cell.alignment, cell.fill = styles.data_font, styles.number_alignment, row_fill


def add_financial_intelligence(ws: Any, styles: ExcelStyles, profiles: list[Company]) -> None:
    """Add financial intelligence sheet.

    Args:
        ws: Worksheet to add to
        styles: Excel styles
        profiles: List of company profiles
    """
    logger.info(f"Adding financial intelligence for {len(profiles)} companies")

    # Title
    add_title_banner(ws, styles, "Financial Intelligence", "Revenue, Funding & Valuation", num_columns=12)

    # STORY-250: Headers derived from single authoritative schema — drift-proof
    headers = get_headers_for_sheet("Financial Intelligence")
    write_headers(ws, styles, headers)

    # Data rows
    for idx, company in enumerate(profiles):
        _write_financial_row(ws, styles, LayoutConstants.DATA_START_ROW + idx, idx, company)

    # Auto-adjust columns
    auto_adjust_columns(ws)

    logger.info("Financial intelligence complete")
