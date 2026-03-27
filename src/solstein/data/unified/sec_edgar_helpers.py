"""SEC EDGAR enrichment helpers.

EPIC-020: Extracted from fill_nulls_from_sec_edgar function.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from solstein.domain.models import ConfidenceLevel

from .company import UnifiedCompany
from .error_tracking import build_error_context, format_enrichment_error

if TYPE_CHECKING:
    from typing import Any


def _validate_and_fill_revenue(
    company: UnifiedCompany,
    filing_data: dict[str, Any],
) -> bool:
    """Validate and fill revenue from SEC EDGAR data.

    Returns True if field was filled, False otherwise.
    """
    from .enrichment import is_valid_number

    if filing_data.get("revenue") is None:
        return False

    revenue = filing_data["revenue"]
    if not is_valid_number(revenue) or not (0 < revenue < 1e15):
        return False

    if company.financials.revenue is not None:
        return False

    company.financials.revenue = revenue
    company.financials.revenue_confidence = ConfidenceLevel.CONFIRMED
    company.data_source_per_field["revenue"] = "SEC EDGAR"
    company.enrichment_sources.append("SEC EDGAR")
    return True


def _validate_and_fill_growth_rate(
    company: UnifiedCompany,
    filing_data: dict[str, Any],
) -> bool:
    """Validate and fill growth_rate from SEC EDGAR data.

    Returns True if field was filled, False otherwise.
    """
    from .enrichment import is_valid_number

    if filing_data.get("growth_rate") is None:
        return False

    growth_rate = filing_data["growth_rate"]
    if not is_valid_number(growth_rate) or not (-0.5 <= growth_rate <= 2.0):
        return False

    if company.financials.growth_rate is not None:
        return False

    company.financials.growth_rate = growth_rate
    company.financials.growth_confidence = ConfidenceLevel.CONFIRMED
    company.data_source_per_field["growth_rate"] = "SEC EDGAR"
    return True


def _validate_and_fill_employees(
    company: UnifiedCompany,
    filing_data: dict[str, Any],
) -> bool:
    """Validate and fill employees from SEC EDGAR data.

    Returns True if field was filled, False otherwise.
    """

    if filing_data.get("employees") is None:
        return False

    employees = filing_data["employees"]
    try:
        employees_int = int(employees) if not isinstance(employees, int) else employees
        if not (0 < employees_int < 10_000_000):
            return False
    except (ValueError, TypeError):
        return False

    if company.financials.employees is not None:
        return False

    company.financials.employees = employees_int
    company.financials.employees_confidence = ConfidenceLevel.CONFIRMED
    company.data_source_per_field["employees"] = "SEC EDGAR"
    return True


def _validate_and_fill_profit_margin(
    company: UnifiedCompany,
    filing_data: dict[str, Any],
) -> bool:
    """Validate and fill profit_margin from SEC EDGAR data.

    Returns True if field was filled, False otherwise.
    """
    from .enrichment import is_valid_number

    if filing_data.get("profit_margin") is None:
        return False

    profit_margin = filing_data["profit_margin"]
    if not is_valid_number(profit_margin) or not (-1.0 <= profit_margin <= 1.0):
        return False

    if company.financials.profit_margin is not None:
        return False

    company.financials.profit_margin = profit_margin
    company.financials.margin_confidence = ConfidenceLevel.CONFIRMED
    company.data_source_per_field["profit_margin"] = "SEC EDGAR"
    return True


def _store_additional_metrics(
    company: UnifiedCompany,
    filing_data: dict[str, Any],
) -> None:
    """Store additional metrics in profitability_raw_metrics for reference."""
    if filing_data.get("ebitda"):
        company.profitability_raw_metrics["ebitda_sec"] = filing_data["ebitda"]

    if filing_data.get("cash_position"):
        company.profitability_raw_metrics["cash_position_sec"] = filing_data["cash_position"]


def _track_enrichment_timestamp(company: UnifiedCompany) -> None:
    """Track enrichment timestamp for SEC EDGAR."""
    company.enrichment_timestamps["SEC EDGAR"] = datetime.now(timezone.utc)


def _handle_sec_edgar_error(
    company: UnifiedCompany,
    error: Exception,
    error_type: str,
) -> None:
    """Handle SEC EDGAR enrichment error."""
    from loguru import logger

    logger.warning(f"SEC EDGAR {error_type} for {company.name}: {error}")

    error_context = build_error_context(ticker=company.ticker)
    error_msg = format_enrichment_error("SEC EDGAR", error_context, str(error))
    company.enrichment_errors.append(error_msg)
