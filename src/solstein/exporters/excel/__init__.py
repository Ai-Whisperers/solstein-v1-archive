"""Excel export utilities and generators.

EPIC-022: Modularized Excel export functionality.
"""

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
]
