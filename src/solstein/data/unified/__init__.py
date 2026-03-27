"""Data loaders package.

EPIC-021: Modularized data loading with specialized loaders.
"""

from .batch_outcomes import BatchEnrichmentOutcome, BatchEnrichmentStatus
from .company import UnifiedCompany
from .enrichment import (
    attach_news_signals,
    clear_enrichment_cache,
    enrich_batch,
    enrich_from_connectors,
    fill_nulls_from_companies_house,
    fill_nulls_from_sec_edgar,
    get_enrichment_metrics,
)
from .error_tracking import (
    add_error_severity,
    build_error_context,
    categorize_and_track_error,
    categorize_error,
    format_enrichment_error,
    safe_append_source,
    track_error_with_timestamp,
)
from .merger import (
    convert_to_unified,
    infer_ai_score_from_maturity,
    merge_companies,
    merge_financials,
)
from .unified import UnifiedCompanyLoader

__all__ = [
    # Main classes
    "BatchEnrichmentOutcome",
    "BatchEnrichmentStatus",
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
]
