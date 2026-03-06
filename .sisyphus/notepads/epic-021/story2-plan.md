# EPIC-021 Story 2: Split data/unified_loader.py

## Current State
- `unified_loader.py`: 1,065 lines
- Contains: Helper functions, UnifiedCompany class, UnifiedCompanyLoader class

## Target Structure
```
data/
├── unified_loader.py        # Orchestration layer (~150 lines)
├── loaders/
│   ├── __init__.py
│   ├── unified.py           # UnifiedCompanyLoader main class (~200 lines)
│   ├── company.py           # UnifiedCompany model (~50 lines)
│   ├── merger.py            # Data merging logic (~150 lines)
│   ├── enrichment.py        # Enrichment methods (~200 lines)
│   └── error_tracking.py    # Error tracking helpers (~150 lines)
└── connectors/
    └── ... (existing)
```

## Migration Plan

### Phase 1: Create error_tracking.py
Move helper functions (lines 1-173):
- `format_enrichment_error()`
- `safe_append_source()`
- `categorize_error()`
- `add_error_severity()`
- `build_error_context()`
- `track_error_with_timestamp()`
- `categorize_and_track_error()`

### Phase 2: Create company.py
Move `UnifiedCompany` class (lines 174-182)

### Phase 3: Create merger.py
Move merge methods:
- `_merge_companies()` (lines 351-416)
- `_merge_financials()` (lines 417-478)
- `_convert_to_unified()` (lines 480-501)
- `_infer_ai_score_from_maturity()` (lines 503-524)

### Phase 4: Create enrichment.py
Move enrichment methods:
- `enrich_from_connectors()` (lines 525-568)
- `enrich_batch()` (lines 569-629)
- `get_enrichment_metrics()` (lines 630-637)
- `clear_enrichment_cache()` (lines 638-642)
- `fill_nulls_from_sec_edgar()` (lines 643-800)
- `fill_nulls_from_companies_house()` (lines 820-971)
- `attach_news_signals()` (lines 972-1062)

### Phase 5: Update unified_loader.py
Keep only:
- Imports from new modules
- `UnifiedCompanyLoader.__init__()`
- `load_unified_companies()`
- `_load_markdown_companies()`
- Backward compatibility exports

## Testing Strategy
1. Import tests for each new module
2. Golden tests for behavior preservation
3. Integration tests for cross-module calls
4. All existing tests must pass
