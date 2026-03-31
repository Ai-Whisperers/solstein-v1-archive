"""Excel export utilities and generators.

EPIC-022: Modularized Excel export functionality.
"""

from pathlib import Path
from typing import Any, cast

from ...domain.models import Company
from ..excel_improved import ImprovedExcelExporter
from .sheets import (
    add_executive_summary,
    add_financial_intelligence,
    add_market_rankings,
    add_title_banner,
    write_headers,
)
from .styles import ColorPalette, ExcelStyles, LayoutConstants
from .utils import (
    auto_adjust_columns,
    format_number,
    format_percentage,
    safe_get,
    safe_get_financial,
)


class ExcelExporter(ImprovedExcelExporter):
    def export_market_analysis(self, analysis: Any, output_path: Path) -> None:
        profiles_obj: object = (
            getattr(analysis, "profiles", None)
            or getattr(analysis, "companies", None)
            or getattr(analysis, "scored_companies", None)
            or []
        )
        profiles = cast("list[Company]", profiles_obj if isinstance(profiles_obj, list) else [])
        self.create_dashboard(profiles, output_path)


__all__ = [
    # Styles
    "ColorPalette",
    "ExcelStyles",
    "LayoutConstants",
    # Utils
    "safe_get",
    "safe_get_financial",
    "format_number",
    "format_percentage",
    "auto_adjust_columns",
    # Sheets
    "add_title_banner",
    "write_headers",
    "add_executive_summary",
    "add_market_rankings",
    "add_financial_intelligence",
    "ExcelExporter",
]
