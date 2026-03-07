"""Excel export utility functions.

EPIC-022: Extracted from ImprovedExcelExporter for modularity.
"""

from typing import Any

from openpyxl.utils import get_column_letter

from ...domain.models import Company


def safe_get(obj: Any, attr: str, default: Any = "") -> Any:
    """Safely get attribute from object.

    Args:
        obj: Object to get attribute from
        attr: Attribute name (can be nested with dots)
        default: Default value if attribute not found

    Returns:
        Attribute value or default
    """
    if obj is None:
        return default

    try:
        value = obj
        for part in attr.split("."):
            if value is None:
                return default
            value = getattr(value, part, None)
        return value if value is not None else default
    except (AttributeError, TypeError):
        return default


def safe_get_financial(company: Company, attr: str, default: Any = "") -> Any:
    """Safely get financial attribute from company.

    Args:
        company: Company object
        attr: Financial attribute name
        default: Default value if not found

    Returns:
        Financial attribute value or default
    """
    if company is None:
        return default

    # Try direct attribute first
    value = safe_get(company, attr, None)
    if value is not None:
        return value

    # Try nested in financials
    value = safe_get(company, f"financials.{attr}", None)
    if value is not None:
        return value

    # Try nested in metrics
    value = safe_get(company, f"metrics.{attr}", None)
    if value is not None:
        return value

    return default


def format_number(value: float | None, decimals: int = 1, suffix: str = "") -> str:
    """Format a number with specified decimals and suffix.

    Args:
        value: Number to format
        decimals: Number of decimal places
        suffix: Suffix to append (e.g., 'M', '%')

    Returns:
        Formatted string
    """
    if value is None:
        return "N/A"

    try:
        formatted = f"{value:,.{decimals}f}"
        if suffix:
            formatted += f" {suffix}"
        return formatted
    except (TypeError, ValueError):
        return "N/A"


def format_percentage(value: float | None, decimals: int = 1) -> str:
    """Format a value as percentage.

    Args:
        value: Value to format (0.25 = 25%)
        decimals: Number of decimal places

    Returns:
        Formatted percentage string
    """
    if value is None:
        return "N/A"

    try:
        return f"{value * 100:,.{decimals}f}%"
    except (TypeError, ValueError):
        return "N/A"


def auto_adjust_columns(ws: Any) -> None:
    """Auto-adjust column widths based on content.

    Args:
        ws: Worksheet to adjust
    """
    from .styles import LayoutConstants

    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)

        for cell in column:
            try:
                if cell.value:
                    cell_length = len(str(cell.value))
                    if cell_length > max_length:
                        max_length = cell_length
            except Exception:
                pass

        # Set width with bounds
        adjusted_width = min(
            max(max_length + 2, LayoutConstants.MIN_COLUMN_WIDTH),
            LayoutConstants.MAX_COLUMN_WIDTH,
        )
        ws.column_dimensions[column_letter].width = adjusted_width
