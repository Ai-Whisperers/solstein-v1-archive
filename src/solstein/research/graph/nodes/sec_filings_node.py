"""LangGraph node: SEC EDGAR filing collection.

STORY-078: Implements the sec_filings graph node using the real
SECEdgarConnector (EDGAR full-text search API — no API key required).

This node replaces the stub SECEdgarAgent from additional_agents.py with a
real implementation. It fetches the most recent 10-K filing for each company
that has a known US ticker symbol. Non-US companies or companies without a
known ticker will produce a coverage gap (logged, not a pipeline error).

Input interface (fields read from ResearchState):
    - company_identifiers: list of company IDs / names to research
    - config: optional runtime config (keys: tickers — dict[company_id, ticker])

Output interface (fields written to ResearchState):
    - raw_sec_facts: list of per-company SEC filing fact dicts
    - data_collection_errors: list of error strings (appended, not overwritten)
    - completed_nodes: appends "sec_filings"

Each fact dict schema:
    {
        company_id: str,
        form_type: str,            # "10-K" or "10-Q"
        period_of_report: str,     # e.g. "2024-12-31"
        revenue: float | None,
        net_income: float | None,
        employees: int | None,
        filing_url: str | None,
        ticker: str,
    }

Note: SECEdgarConnector uses the `edgar` library which makes synchronous
HTTP calls. The node is implemented synchronously to match the library's
interface. Rate limiting is handled inside the connector.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any

from loguru import logger

from ..state import ResearchState

# Import SECEdgarConnector at module level so it can be patched in tests.
# Graceful fallback when the edgar library is not installed.
try:
    from solstein.data.connectors.sec_edgar_connector import (
        CompanyNotFoundError,
        SECEdgarConnector,
    )

    _SEC_EDGAR_AVAILABLE = True
except ImportError:
    CompanyNotFoundError = Exception  # type: ignore[assignment,misc]
    SECEdgarConnector = None  # type: ignore[assignment,misc]
    _SEC_EDGAR_AVAILABLE = False


def sec_filings_node(state: ResearchState, config: dict[str, Any] | None = None) -> dict[str, Any]:
    """SEC EDGAR filing collection node.

    Reads: company_identifiers, config
    Writes: raw_sec_facts, data_collection_errors, completed_nodes

    For each company, attempts to derive a US stock ticker from the company
    identifier (if the identifier looks like a ticker, uses it directly;
    otherwise tries the company name as a ticker guess). When the edgar
    library cannot find the company or no 10-K exists, the error is recorded
    in data_collection_errors — not as a pipeline error.

    Args:
        state: Current ResearchState dict.
        config: LangGraph config dict. May contain config["configurable"]["tickers"]
                as a dict mapping company_id to known US ticker symbol.

    Returns:
        Partial state dict with raw_sec_facts, data_collection_errors,
        and completed_nodes.
    """
    company_identifiers: list[str] = state.get("company_identifiers") or []
    extra_config: dict[str, Any] = state.get("config") or {}
    lg_config = config or {}
    configurable: dict[str, Any] = lg_config.get("configurable") or {}

    # Caller may supply known tickers via config to avoid guessing
    known_tickers: dict[str, str] = configurable.get("tickers") or extra_config.get("tickers") or {}

    raw_facts: list[dict[str, Any]] = []
    errors: list[str] = []

    if not company_identifiers:
        logger.warning("[sec_filings] No company_identifiers in state — skipping")
        return {
            "raw_sec_facts": raw_facts,
            "data_collection_errors": errors,
            "completed_nodes": ["sec_filings"],
        }

    if not _SEC_EDGAR_AVAILABLE:
        msg = "[sec_filings] SECEdgarConnector not available (edgar library not installed)"
        logger.error(msg)
        errors.append(msg)
        return {
            "raw_sec_facts": raw_facts,
            "data_collection_errors": errors,
            "completed_nodes": ["sec_filings"],
        }

    connector = SECEdgarConnector()
    current_year = _current_year()

    for company_id in company_identifiers:
        ticker = known_tickers.get(company_id) or _guess_ticker(company_id)
        if not ticker:
            msg = f"[sec_filings] {company_id}: no ticker symbol — skipping (not a US public company)"
            errors.append(msg)
            logger.info(msg)
            continue

        try:
            filing_data = connector.fetch_filing(ticker=ticker, year=current_year - 1, form_type="10-K")
            fact = _build_sec_fact(company_id=company_id, ticker=ticker, filing_data=filing_data)
            raw_facts.append(fact)
            logger.debug("[sec_filings] %s (ticker=%s): fetched 10-K for %d", company_id, ticker, current_year - 1)
        except CompanyNotFoundError:
            msg = f"[sec_filings] {company_id} (ticker={ticker}): company not found in SEC EDGAR"
            errors.append(msg)
            logger.warning(msg)
        except ValueError as exc:
            # Connector raises ValueError for invalid ticker/year/form_type
            msg = f"[sec_filings] {company_id} (ticker={ticker}): {exc}"
            errors.append(msg)
            logger.warning(msg)
        except Exception as exc:
            msg = f"[sec_filings] {company_id} (ticker={ticker}): exception — {exc}"
            errors.append(msg)
            logger.error(msg)

    return {
        "raw_sec_facts": raw_facts,
        "data_collection_errors": errors,
        "completed_nodes": ["sec_filings"],
    }


def _current_year() -> int:
    """Return the current calendar year."""
    return date.today().year


def _guess_ticker(company_id: str) -> str | None:
    """Attempt to derive a US stock ticker from a company identifier.

    Returns the ticker if the identifier looks like a valid US ticker
    (1–5 uppercase letters, optionally prefixed by a colon namespace
    such as "NYSE:AAPL"). Returns None for company names that are
    clearly not tickers (contain spaces, are too long, etc.).
    """
    # Strip namespace prefix like "NYSE:" or "NASDAQ:"
    cleaned = re.sub(r"^[A-Z]+:", "", company_id.upper().strip())

    # Valid US ticker: 1–5 uppercase letters, no digits or special chars
    if re.fullmatch(r"[A-Z]{1,5}", cleaned):
        return cleaned

    return None


def _build_sec_fact(
    company_id: str,
    ticker: str,
    filing_data: dict[str, Any],
) -> dict[str, Any]:
    """Build a standardised SEC fact dict from the connector's response."""
    return {
        "company_id": company_id,
        "form_type": str(filing_data.get("form_type", "10-K")),
        "period_of_report": str(filing_data.get("period_of_report", "")),
        "revenue": _to_float(filing_data.get("revenue")),
        "net_income": _to_float(filing_data.get("net_income")),
        "employees": _to_int(filing_data.get("employees")),
        "filing_url": filing_data.get("filing_url"),
        "ticker": ticker,
    }


def _to_float(value: Any) -> float | None:
    """Safely convert a value to float, returning None on failure."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> int | None:
    """Safely convert a value to int, returning None on failure."""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
