"""Unified Company Data Model with Conflict Resolution.

Merges JSON and Markdown data sources with conflict resolution and data source tracking.
Priority: Markdown > JSON (when conflicts exist)

EPIC-021: Refactored from monolithic 1,065-line file to modular structure.
This module now serves as the orchestration layer, delegating to specialized modules.
"""

from __future__ import annotations

# Import all public APIs from modularized loaders package
from .unified import (
    BatchEnrichmentOutcome,
    UnifiedCompany,
    UnifiedCompanyLoader,
    # Error tracking
    format_enrichment_error,
    safe_append_source,
    categorize_error,
    add_error_severity,
    build_error_context,
    track_error_with_timestamp,
    categorize_and_track_error,
    # Merging
    merge_companies,
    merge_financials,
    convert_to_unified,
    infer_ai_score_from_maturity,
    # Enrichment
    enrich_from_connectors,
    enrich_batch,
    get_enrichment_metrics,
    clear_enrichment_cache,
    fill_nulls_from_sec_edgar,
    fill_nulls_from_companies_house,
    attach_news_signals,
)

# Backward compatibility: maintain unified_loader global instance
unified_loader = UnifiedCompanyLoader()

__all__ = [
    # Main classes
    "BatchEnrichmentOutcome",
    "UnifiedCompany",
    "UnifiedCompanyLoader",
    # Error tracking
    "format_enrichment_error",
    "safe_append_source",
    "categorize_error",
    "add_error_severity",
    "build_error_context",
    "track_error_with_timestamp",
    "categorize_and_track_error",
    # Merging
    "merge_companies",
    "merge_financials",
    "convert_to_unified",
    "infer_ai_score_from_maturity",
    # Enrichment
    "enrich_from_connectors",
    "enrich_batch",
    "get_enrichment_metrics",
    "clear_enrichment_cache",
    "fill_nulls_from_sec_edgar",
    "fill_nulls_from_companies_house",
    "attach_news_signals",
    # Global instance
    "unified_loader",
]
