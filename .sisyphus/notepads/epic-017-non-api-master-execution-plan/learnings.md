# EPIC-017 Non-API Master Execution Plan - Learnings

## 2026-03-06: Completed Wave 2 E1-E5 (Unified Loader Refactor)

### E1: Extract orchestration layer from unified_loader.py
- Created `src/solstein/data/loader_orchestrator.py` with `UnifiedLoaderOrchestrator`
- Separated concerns: discovery, normalization, merge/dedup, enrichment phases
- Added protocols for `DataSourceAdapter`, `EnrichmentConnector`, `Normalizer`, `ConflictResolver`
- Created `LoadConfig` and `LoadResult` dataclasses for structured I/O
- Added comprehensive test suite: 17 tests in `tests/unit/test_loader_orchestrator.py`

### E2: Extract normalization/parsing utilities
- Created `src/solstein/data/normalization.py` with safe parsing functions
- `parse_number()`, `parse_integer()`, `parse_decimal()` for numeric fields
- `normalize_string()`, `normalize_boolean()`, `normalize_list()`, `normalize_dict()` for type safety
- `normalize_date()` for ISO format dates
- `clean_company_name()`, `extract_domain_from_url()` for domain-specific cleaning
- `DataNormalizer` class for record-level normalization with field mapping
- Added 32 tests in `tests/unit/test_normalization.py`

### E3: Extract merge/conflict resolver adapter
- Created `src/solstein/data/conflict_resolution.py` with pluggable strategies
- `ConflictStrategy` enum: SOURCE_PRIORITY, RECENCY_WINS, MAXIMUM_VALUE, MINIMUM_VALUE, CONCATENATE, UNION, INTERSECTION
- `FieldConflict` dataclass for conflict representation
- `ResolutionResult` dataclass for resolution output
- Multiple resolver implementations:
  - `SourcePriorityResolver`: Uses source authority rankings
  - `RecencyResolver`: Prefers newer data, falls back to confidence
  - `NumericResolver`: Prefers max (revenue) or min (risk)
  - `StringResolver`: Concatenates or prefers longer
  - `ListResolver`: Union or intersection strategies
  - `CompositeResolver`: Field-specific strategy delegation
- Added 21 tests in `tests/unit/test_conflict_resolution.py`

### E4: Replace mutable defaults with safe factories
- Created `src/solstein/data/safe_defaults.py` with factory patterns
- `ensure_list()`, `ensure_dict()`, `ensure_set()`, `ensure_str()`, `ensure_int()`, `ensure_float()`, `ensure_bool()`
- `list_factory()`, `dict_factory()`, `set_factory()` for dataclass defaults
- `SafeDefault` descriptor for class-level safe mutable defaults
- `copy_with_safe_defaults()`, `merge_safe()` for safe dict operations
- Added 20 tests in `tests/unit/test_safe_defaults.py`

### E5: Add bounded concurrency for enrichment
- Implemented semaphore-based concurrency in `loader_orchestrator.py`
- `max_concurrent_enrichment` config option (default: 10)
- `asyncio.Semaphore` protects connector calls
- `asyncio.wait_for()` for timeout handling (default: 30s)
- Graceful error handling: timeouts and exceptions return `{}` instead of failing

### Test Results
- 125 new tests added for loader refactor
- All 125 tests passing
- Combined with Wave 0-1 tests: 173 EPIC-017 tests passing

### Files Created
- `src/solstein/data/loader_orchestrator.py` (296 lines)
- `src/solstein/data/normalization.py` (505 lines)
- `src/solstein/data/conflict_resolution.py` (402 lines)
- `src/solstein/data/safe_defaults.py` (268 lines)
- `tests/unit/test_loader_orchestrator.py` (267 lines)
- `tests/unit/test_normalization.py` (361 lines)
- `tests/unit/test_conflict_resolution.py` (314 lines)
- `tests/unit/test_safe_defaults.py` (232 lines)

### Next Steps
- E6: Add loader-level performance benchmarks
- F1-F5: Exception taxonomy (typed errors, error envelopes, lint checks)
- G1-G6: Testing hardening (coverage dashboard, golden tests)
- H1-H5: Provenance and confidence tracking
