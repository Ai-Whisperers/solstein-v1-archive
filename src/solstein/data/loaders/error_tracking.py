"""Error tracking utilities for data enrichment.

Extracted from unified_loader.py as part of EPIC-021 file splitting.
Provides consistent error formatting, categorization, and tracking.
"""

from __future__ import annotations

from datetime import datetime, timezone


def format_enrichment_error(source: str, context: str, error: str) -> str:
    """Format enrichment error messages consistently.

    Args:
        source: Data source (e.g., 'SEC EDGAR', 'Companies House', 'News Signals')
        context: Context info (e.g., ticker, company_number, company name)
        error: Error message or exception

    Returns:
        Formatted error string: 'SOURCE [context]: error'
    """
    if context:
        return f"{source} [{context}]: {str(error)[:200]}"  # Truncate to 200 chars
    return f"{source}: {str(error)[:200]}"


def safe_append_source(sources: list[str], source: str) -> None:
    """Safely append to enrichment_sources, preventing duplicates.

    Args:
        sources: List of enrichment sources
        source: Source to append (e.g., 'SEC EDGAR')
    """
    if source not in sources:
        sources.append(source)


def categorize_error(error_type: str, error: Exception | str) -> str:
    """Categorize error into API_ERROR, DATA_ERROR, VALIDATION_ERROR, or UNKNOWN.

    Args:
        error_type: Type of error (e.g., 'API', 'DATA', 'VALIDATION')
        error: The error object or message

    Returns:
        Error category string
    """
    str(error).lower()

    if error_type.upper() == "API":
        return "API_ERROR"
    elif error_type.upper() == "DATA":
        return "DATA_ERROR"
    elif error_type.upper() == "VALIDATION":
        return "VALIDATION_ERROR"
    else:
        return "UNKNOWN"


def add_error_severity(error_msg: str, severity: str) -> str:
    """Add severity prefix to error message.

    Args:
        error_msg: The error message
        severity: Severity level (CRITICAL, WARNING, INFO)

    Returns:
        Error message with severity prefix
    """
    severity_upper = severity.upper()
    if severity_upper not in ("CRITICAL", "WARNING", "INFO"):
        severity_upper = "INFO"
    return f"[{severity_upper}] {error_msg}"


def build_error_context(
    ticker: str | None = None,
    company_number: str | None = None,
    year: int | None = None,
    attempt_count: int | None = None,
) -> str:
    """Build error context string from enrichment parameters.

    Args:
        ticker: Stock ticker symbol
        company_number: UK company number
        year: Year being enriched
        attempt_count: Number of attempts made

    Returns:
        Context string for error messages
    """
    parts = []
    if ticker:
        parts.append(f"ticker={ticker}")
    if company_number:
        parts.append(f"company_number={company_number}")
    if year:
        parts.append(f"year={year}")
    if attempt_count:
        parts.append(f"attempt={attempt_count}")
    return ", ".join(parts) if parts else "unknown context"


def track_error_with_timestamp(company, error_msg: str, field: str | None = None) -> None:
    """Track error with timestamp and optional field association.

    Args:
        company: Company object to track error on
        error_msg: Error message
        field: Optional field name if error is field-specific
    """
    # Append to main error list
    company.enrichment_errors.append(error_msg)

    # Track timestamp
    error_key = f"error_{len(company.enrichment_errors)}"
    company.enrichment_error_timestamps[error_key] = datetime.now(timezone.utc)

    # Track per-field if specified
    if field:
        if field not in company.enrichment_errors_per_field:
            company.enrichment_errors_per_field[field] = []
        company.enrichment_errors_per_field[field].append(error_msg)

    # Increment error count
    company.enrichment_error_count += 1

    # Limit error accumulation to 50 most recent
    if len(company.enrichment_errors) > 50:
        company.enrichment_errors = company.enrichment_errors[-50:]
        company.enrichment_error_timestamps = dict(list(company.enrichment_error_timestamps.items())[-50:])


def categorize_and_track_error(company, error_msg: str, category: str) -> None:
    """Track error with category for metrics.

    Args:
        company: Company object to track error on
        error_msg: Error message
        category: Error category (API_ERROR, DATA_ERROR, VALIDATION_ERROR, UNKNOWN)
    """
    track_error_with_timestamp(company, error_msg)

    # Track category count
    if category not in company.enrichment_error_categories:
        company.enrichment_error_categories[category] = 0
    company.enrichment_error_categories[category] += 1
