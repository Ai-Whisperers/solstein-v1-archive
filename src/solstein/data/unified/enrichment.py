"""Data enrichment methods for unified company loader.

Extracted from unified_loader.py as part of EPIC-021 file splitting.
Handles enrichment from SEC EDGAR, Companies House, and News Signals.
"""

from __future__ import annotations

import time
import asyncio
from datetime import datetime, timezone

from loguru import logger

from solstein.domain.models import ConfidenceLevel
from solstein.data.enrichment_orchestrator import EnrichmentConfig, EnrichmentOrchestrator, EnrichmentSource

from .company import UnifiedCompany
from .error_tracking import format_enrichment_error, build_error_context
from .sec_edgar_helpers import (
    _handle_sec_edgar_error,
    _store_additional_metrics,
    _track_enrichment_timestamp,
    _validate_and_fill_employees,
    _validate_and_fill_growth_rate,
    _validate_and_fill_profit_margin,
    _validate_and_fill_revenue,
)


def is_valid_number(val):
    """Helper function to check if value is valid number (not NaN/Inf)."""
    if not isinstance(val, (int, float)):
        return False
    if val != val:  # NaN check
        return False
    if val == float("inf") or val == float("-inf"):
        return False
    return True


def enrich_from_connectors(loader, company: UnifiedCompany) -> UnifiedCompany:
    """Enrich company data from all available connectors.

    Uses EnrichmentOrchestrator to:
    - Skip enrichment if data already complete
    - Determine optimal source order
    - Handle confidence-aware overwriting
    - Ensure immutability (returns new object)
    - Track enrichment costs and errors

    Calls SEC EDGAR, Companies House, and News Signal Detector in sequence.
    Only fills NULL fields - never replaces existing data.
    """
    orchestrator = EnrichmentOrchestrator(EnrichmentConfig())

    company = fill_identifiers_from_lookup(loader, company)

    if orchestrator.should_skip_enrichment(company):
        logger.debug(f"Skipping enrichment for {company.name} - data already complete or no identifiers")
        return company

    enriched = orchestrator.create_enrichment_copy(company)

    sources = orchestrator.get_enrichment_order(enriched)
    fields = orchestrator.get_fields_to_enrich(enriched)

    if not sources or not fields:
        logger.debug(f"No enrichment needed for {enriched.name}")
        return enriched

    for source in sources:
        try:
            if source == EnrichmentSource.SEC_EDGAR:
                enriched = fill_nulls_from_sec_edgar(loader, enriched)
            elif source == EnrichmentSource.COMPANIES_HOUSE:
                enriched = fill_nulls_from_companies_house(loader, enriched)
            elif source == EnrichmentSource.NEWS_SIGNALS:
                enriched = attach_news_signals(loader, enriched)
        except (ValueError, RuntimeError, TypeError, AttributeError) as e:
            logger.error(f"Enrichment from {source} failed for {enriched.name}: {e}")
            enriched = orchestrator.rollback_on_error(company, enriched, str(e))
            break

    return enriched


def fill_identifiers_from_lookup(loader, company: UnifiedCompany) -> UnifiedCompany:
    if not hasattr(loader, "lookup_service") or not loader.lookup_service:
        return company

    if not company.name:
        return company

    missing_fields = [
        field for field in ("ticker", "company_number", "isin", "geography_code") if not getattr(company, field, None)
    ]
    if not missing_fields:
        return company

    try:
        service = loader.lookup_service
        if not hasattr(service, "resolve_identifiers_enveloped"):
            return company

        response = asyncio.run(service.resolve_identifiers_enveloped(company.name, headquarters=company.headquarters))
        company.metric_justifications["identifier_lookup_status"] = str(response.status)
        company.metric_justifications["identifier_lookup_attempts"] = str(response.metadata.get("attempts"))

        payload = response.payload or {}
        if payload:
            company.metric_observations["identifier_lookup"] = [payload]

        for field in missing_fields:
            candidate = payload.get(field)
            if not candidate:
                continue
            try:
                setattr(company, field, candidate)
                if "identifier_lookup_service" not in company.metric_sources.get(field, []):
                    company.metric_sources.setdefault(field, []).append("identifier_lookup_service")
            except (ValueError, RuntimeError, TypeError, AttributeError) as field_error:
                error_context = build_error_context(ticker=company.ticker, company_number=company.company_number)
                error_msg = format_enrichment_error(
                    "Identifier Lookup",
                    error_context,
                    f"Invalid {field} value '{candidate}': {field_error}",
                )
                company.enrichment_errors.append(error_msg)

        if payload and "identifier_lookup" not in company.enrichment_sources:
            company.enrichment_sources.append("identifier_lookup")

        if response.status in {"degraded", "failure"} and response.error:
            error_context = build_error_context(ticker=company.ticker, company_number=company.company_number)
            error_msg = format_enrichment_error("Identifier Lookup", error_context, response.error)
            company.enrichment_errors.append(error_msg)

        return company
    except (ValueError, RuntimeError, TypeError, AttributeError) as e:
        error_context = build_error_context(ticker=company.ticker, company_number=company.company_number)
        error_msg = format_enrichment_error("Identifier Lookup", error_context, str(e))
        company.enrichment_errors.append(error_msg)
        return company


def enrich_batch(loader, companies: list[UnifiedCompany], batch_size: int = 10) -> list[UnifiedCompany]:
    """Batch enrich companies with caching and performance tracking (Phase B).

    Args:
        loader: UnifiedCompanyLoader instance
        companies: List of companies to enrich
        batch_size: Number of companies to process per batch (default: 10)

    Returns:
        List of enriched companies
    """
    enriched_companies = []
    total_batches = (len(companies) + batch_size - 1) // batch_size

    logger.info(f"✅ Starting batch enrichment: {len(companies)} companies in {total_batches} batches of {batch_size}")

    for batch_num, i in enumerate(range(0, len(companies), batch_size), 1):
        batch = companies[i : i + batch_size]
        batch_start = time.time()

        logger.debug(f"Processing batch {batch_num}/{total_batches} ({len(batch)} companies)")

        for company in batch:
            try:
                # Check cache first
                cache_key = f"enriched_{company.id}_{company.ticker or company.company_number}"
                cached_result = loader.cache.get(cache_key)

                if cached_result:
                    logger.debug(f"Cache hit for {company.name}")
                    enriched_companies.append(cached_result)
                    loader.metrics.record_enrichment(0, True)  # 0ms for cache
                    continue

                # Enrich company
                enriched = enrich_from_connectors(loader, company)
                enriched_companies.append(enriched)

                # Cache result
                loader.cache.set(cache_key, enriched)
                loader.metrics.record_enrichment(0, True)

            except (ValueError, RuntimeError, TypeError, AttributeError) as e:
                logger.warning(f"Batch enrichment failed for {company.name}: {e}")
                company._enrichment_failed = True  # flag for callers to detect failure
                enriched_companies.append(company)  # Use original if enrichment fails
                loader.metrics.record_enrichment(0, False)

        batch_duration = (time.time() - batch_start) * 1000  # Convert to ms
        logger.info(f"Batch {batch_num}/{total_batches} completed in {batch_duration:.2f}ms")

    # Log final metrics
    metrics_summary = loader.metrics.get_summary()
    logger.info(
        f"✅ Batch enrichment complete: {metrics_summary['successful']} successful, {metrics_summary['failed']} failed, avg {metrics_summary['avg_duration_ms']:.2f}ms per company"
    )

    return enriched_companies


def get_enrichment_metrics(loader) -> dict:
    """Get current enrichment metrics (Phase B).

    Returns:
        Dictionary of enrichment performance metrics
    """
    return loader.metrics.get_summary()


def clear_enrichment_cache(loader) -> None:
    """Clear all cached enrichment results (Phase B)."""
    loader.cache.clear()
    logger.info("✅ Enrichment cache cleared")


def fill_nulls_from_sec_edgar(loader, company: UnifiedCompany) -> UnifiedCompany:
    """
    Fill NULL financial fields from SEC EDGAR for US companies.

    EPIC-020: Refactored to use sec_edgar_helpers module.
    """
    logger.info(f"[CONNECTOR-SEC-START] SEC EDGAR enrichment STARTED for {company.name} (ticker={company.ticker})")

    # Skip if no SEC connector available
    if not loader.sec_connector:
        return company

    # Skip if no ticker
    if not company.ticker or not company.ticker.strip():
        return company

    # Skip if no financials object
    if not company.financials:
        return company

    try:
        # Try to fetch 10-K for current year first, then previous years
        current_year = datetime.now().year
        filing_data = None

        for year_offset in range(0, 3):  # Try current year and 2 previous years
            try:
                year = current_year - year_offset
                filing_data = loader.sec_connector.fetch_filing(
                    ticker=company.ticker.upper().strip(), year=year, form_type="10-K"
                )
                if filing_data:
                    break
            except ValueError:
                continue
            except RuntimeError:
                continue

        if not filing_data:
            logger.debug(f"No SEC EDGAR data found for {company.name} ({company.ticker})")
            error_context = build_error_context(ticker=company.ticker)
            error_msg = format_enrichment_error("SEC EDGAR", error_context, "No data found after retrying 3 years")
            company.enrichment_errors.append(error_msg)
            return company

        # Fill NULL fields using helper functions
        _validate_and_fill_revenue(company, filing_data)
        _validate_and_fill_growth_rate(company, filing_data)
        _validate_and_fill_employees(company, filing_data)
        _validate_and_fill_profit_margin(company, filing_data)

        # Store additional metrics
        _store_additional_metrics(company, filing_data)

        # Track enrichment timestamp
        _track_enrichment_timestamp(company)

        logger.info(
            f"[CONNECTOR-SEC-END] SEC EDGAR enrichment COMPLETED for {company.name}. Revenue: {company.financials.revenue}"
        )
        return company

    except ValueError as e:
        _handle_sec_edgar_error(company, e, "enrichment failed")
        return company

    except RuntimeError as e:
        _handle_sec_edgar_error(company, e, "API error")
        return company


def fill_nulls_from_companies_house(loader, company: UnifiedCompany) -> UnifiedCompany:
    """
    Fill NULL fields from Companies House for UK companies.

    Note: Companies House primarily provides registration details rather than
    financial metrics. This function updates company metadata from Companies House.

    Args:
        loader: UnifiedCompanyLoader instance
        company: Company to enrich

    Returns:
        Enriched company
    """
    logger.debug(
        f"[CONNECTOR-CH] Companies House enrichment for {company.name} (company_number={company.company_number})"
    )

    # Skip if no Companies House connector available
    if not hasattr(loader, "companies_house_connector") or not loader.companies_house_connector:
        return company

    # Skip if no company number
    if not company.company_number or not company.company_number.strip():
        return company

    try:
        # Fetch company details from Companies House
        metrics = loader.companies_house_connector.get_company_metrics(company.company_number)

        # Update company metadata (not financials)
        if metrics.get("company_name") and not company.name:
            company.name = metrics["company_name"]

        if metrics.get("company_status"):
            company.metadata = company.metadata or {}
            company.metadata["company_status"] = metrics["company_status"]

        if metrics.get("sic_codes"):
            company.metadata = company.metadata or {}
            company.metadata["sic_codes"] = metrics["sic_codes"]

        logger.debug(f"[CONNECTOR-CH-END] Companies House enrichment completed for {company.name}")
        return company

    except (ValueError, RuntimeError, TypeError, AttributeError) as e:
        logger.warning(f"Companies House enrichment failed for {company.name}: {e}")
        error_context = build_error_context(company_number=company.company_number)
        error_msg = format_enrichment_error("Companies House", error_context, str(e))
        company.enrichment_errors.append(error_msg)
        return company


def attach_news_signals(loader, company: UnifiedCompany) -> UnifiedCompany:
    """
    Attach news signals to company data.

    Args:
        loader: UnifiedCompanyLoader instance
        company: Company to enrich

    Returns:
        Enriched company
    """
    logger.debug(f"[CONNECTOR-NEWS] News signals enrichment for {company.name}")

    # Skip if no news signal detector available
    if not hasattr(loader, "news_signal_detector") or not loader.news_signal_detector:
        return company

    try:
        detector = loader.news_signal_detector
        if not hasattr(detector, "detect_signals_enveloped"):
            logger.debug(f"[CONNECTOR-NEWS-SKIP] Enveloped detector method unavailable for {company.name}")
            return company

        response = asyncio.run(detector.detect_signals_enveloped(company.name))
        company.metric_justifications["news_signal_status"] = str(response.status)
        company.metric_justifications["news_signal_attempts"] = str(response.metadata.get("attempts"))

        signals = response.payload or []
        company.metric_justifications["news_signal_count"] = str(len(signals))
        if signals:
            signal_summaries = [
                {
                    "signal_type": getattr(signal, "signal_type", None),
                    "description": getattr(signal, "description", None),
                    "confidence": getattr(signal, "confidence", None),
                    "source": getattr(signal, "source", None),
                }
                for signal in signals
            ]
            company.metric_observations["news_signals"] = signal_summaries
            if "news_signals" not in company.enrichment_sources:
                company.enrichment_sources.append("news_signals")

        if response.status in {"degraded", "failure"} and response.error:
            error_context = build_error_context(
                ticker=company.ticker,
                company_number=company.company_number,
            )
            error_msg = format_enrichment_error(
                "News Signals",
                error_context,
                response.error,
            )
            company.enrichment_errors.append(error_msg)

        logger.debug(f"[CONNECTOR-NEWS-END] News signals enrichment completed for {company.name}")
        return company

    except (ValueError, RuntimeError, TypeError, AttributeError) as e:
        logger.warning(f"News signals enrichment failed for {company.name}: {e}")
        error_context = build_error_context(
            ticker=company.ticker,
            company_number=company.company_number,
        )
        error_msg = format_enrichment_error("News Signals", error_context, str(e))
        company.enrichment_errors.append(error_msg)
        return company
