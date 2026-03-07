"""Data loaders package.

EPIC-021: Modularized data loading with specialized loaders.
"""

from .company import UnifiedCompany
from .unified import UnifiedCompanyLoader
from .error_tracking import (
    format_enrichment_error,
    safe_append_source,
    categorize_error,
    add_error_severity,
    build_error_context,
    track_error_with_timestamp,
    categorize_and_track_error,
)
from .merger import (
    merge_companies,
    merge_financials,
    convert_to_unified,
    infer_ai_score_from_maturity,
)
from .enrichment import (
    enrich_from_connectors,
    enrich_batch,
    get_enrichment_metrics,
    clear_enrichment_cache,
    fill_nulls_from_sec_edgar,
    fill_nulls_from_companies_house,
    attach_news_signals,
)

__all__ = [
    # Main classes
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
