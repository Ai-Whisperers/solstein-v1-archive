# Test Failure Analysis Report — 2026-02-26

**Author**: Gestalt (AI Agent)  
**Context**: Post-merge analysis after accepting Ivan/Nyx commits (phases 10-13, enrichment API, docs overhaul)  
**Local HEAD**: `62fcc52` (merge commit, 1 ahead of origin)  
**Baseline**: 1190 tests collected (excluding 2 collection-blocked files)

---

## Executive Summary

After merging 25 Nyx/Ivan commits and applying Gestalt's loader fix, the test suite stands at:

| Layer | Passed | Failed | Errors | Skipped |
|-------|--------|--------|--------|---------|
| **Data Quality** | 48 | 0 | 0 | 0 |
| **Unit** | 775 | 77 | 6 | 0 |
| **Integration** | 164 | 45 | 24 | 3 |
| **Collection-blocked** | — | — | 2 | — |
| **TOTAL** | **987** | **122** | **32** | **3** |

**Pass rate**: ~86% (987 of 1144 runnable tests)

---

## Fix Applied This Session

### FIX-001: `loaders.py` JSON Schema Mismatch (CRITICAL — RESOLVED)

**File**: `src/solstein/data/loaders.py`  
**Error**: `'int' object has no attribute 'get'` on all 3 companies → 0 loaded → cascade to 9+ test files  
**Root Cause**: Ivan's `competitor_data.json` uses a flat/simplified schema. The loader expected deeply nested objects for `employees`, `ai`, `scorecard`, `funding`, `geographic`, and `profitability`. Ivan provided flat primitives at root level.

**Mismatches found and fixed (6 total)**:

| Field | Loader Expected | Ivan's JSON | Fix |
|-------|----------------|-------------|-----|
| `employees` | `{"latest_headcount": 150, ...}` | `150` (int) | Type-check: if int, use directly |
| `ai` | `{"ai_score": X, "signal_level": Y}` | `"ai_score": 7.5` at root | Fallback to root-level keys |
| `ai_score` | `int` (Company model) | `7.5` (float) | Cast `int(ai_score)` before Company() |
| `scorecard` | `{"dimensions": {...}, "composite_score": N}` | `"classification": "Phoenix"` at root | Fallback to root-level keys |
| `funding` | `{"rounds": [], "total_raised_text": "..."}` | `"funding_raised": 2000000.0` at root | Direct numeric fallback |
| `geographic` | `{"major_offices": [...]}` | `"geographic_presence": ["DE","FR"]` at root | Check flat list first |

**Additional fixes**:
- `industry`, `website`, `founded_year`, `headquarters` — were hardcoded, now read from JSON
- `profit_margin` — ratio-to-percentage conversion (0.15 → 15.0%) for flat format

**Result**: All 3 companies now load. Deterministic scoring tests (9 tests) now pass.

---

## Remaining Failures by Root Cause

### Category 1: Missing `pytest-asyncio` Package (50+ tests)

**Impact**: ~50 tests across 8 files  
**Error**: `async def functions are not natively supported. You need to install pytest-asyncio`  
**Fix**: `pip install pytest-asyncio` (or `uv add pytest-asyncio --dev`)

**Affected files**:
- `tests/unit/test_resilience.py` (11 tests)
- `tests/unit/test_additional_agents.py` (22 tests)
- `tests/unit/test_monitoring.py` (8 tests)
- `tests/unit/test_production_hardening.py` (8 tests)
- `tests/unit/test_worker.py` (1 test)
- `tests/unit/test_worker_coverage.py` (1 test)
- `tests/unit/test_analytics_activities.py` (3 tests)
- `tests/unit/test_analytics_misc_coverage.py` (2 tests)
- `tests/unit/test_api_base_coverage.py` (4 tests)
- `tests/unit/test_markdown_extractor_coverage.py` (2 tests)
- `tests/integration/test_coordinator_to_api.py` (4 tests)
- `tests/integration/test_resilience_scenarios.py` (11 tests)
- `tests/integration/test_unified_adapters.py` (15 tests)

**Note**: These tests use `@pytest.mark.asyncio` decorator but `pytest-asyncio` is not in the installed dependencies. This is an **environment setup issue**, not a code bug. The `pyproject.toml` should include `pytest-asyncio` in `[project.optional-dependencies]` or `[tool.uv.dev-dependencies]`.

---

### Category 2: Missing `httpx_mock` Fixture (6 errors)

**Impact**: 6 test errors in 1 file  
**Error**: `fixture 'httpx_mock' not found`  
**Fix**: `pip install pytest-httpx` (or `uv add pytest-httpx --dev`)

**Affected file**:
- `tests/unit/data/test_companies_house_connector.py` (6 tests)

---

### Category 3: Missing `edgar` Package (3 failures + 3 integration)

**Impact**: 3 unit failures, 3 integration failures  
**Error**: `ModuleNotFoundError: No module named 'edgar'`  
**Fix**: `pip install edgar` (or `uv add edgar`)

**Affected files**:
- `tests/unit/data/test_sec_edgar_connector.py` — 3 tests that import `edgar` directly
- `tests/integration/test_connector_enrichment.py` — SEC Edgar enrichment tests

**Note**: The SEC Edgar connector (`src/solstein/data/connectors/sec_edgar_connector.py`) handles the missing module gracefully at runtime with a fallback. However, the tests that explicitly `import edgar` fail hard.

---

### Category 4: Missing `supabase` Package (2 failures)

**Impact**: 2 test failures  
**Error**: `ImportError: supabase package is not installed`  
**Fix**: `pip install supabase` (or `uv add supabase`)

**Affected file**:
- `tests/unit/test_core_config.py` — `test_get_supabase_client`, `test_get_supabase_client_missing_config`

---

### Category 5: Enrichment API Status Code Mismatch (8 failures)

**Impact**: 8 integration test failures  
**Error**: Tests assert `response.status_code == 400` but API returns `422`  
**Root Cause**: Ivan intentionally committed `e10261d` "fix: Return 422 status code for validation errors" — this is correct per FastAPI/HTTP spec (422 Unprocessable Entity for validation errors). Tests were not updated to match.

**Affected file**: `tests/integration/test_enrichment_api.py`

**Failing tests**:
- `TestSingleEnrichmentEndpoint::test_enrich_with_invalid_sources_returns_400`
- `TestBatchEnrichmentEndpoint::test_batch_enrich_empty_list_returns_400`
- `TestBatchEnrichmentEndpoint::test_batch_enrich_too_many_companies_returns_400`
- `TestBatchEnrichmentEndpoint::test_batch_enrich_invalid_batch_size_returns_400`
- `TestAuditTrailEndpoint::test_audit_trail_invalid_limit_returns_400`
- `TestInputValidation::test_invalid_json_returns_400`
- `TestInputValidation::test_invalid_data_type_returns_400`
- `TestInputValidation::test_oversized_request_returns_413`

**Fix**: Update test assertions from `== 400` to `== 422`. Also rename test methods from `*_returns_400` to `*_returns_422` for clarity.

---

### Category 6: Phase 11/12 Database Integration (24 errors)

**Impact**: 24 test errors  
**Error**: Tests require SQLAlchemy async session setup (PostgreSQL database connection)  
**Root Cause**: Infrastructure dependency — tests need a running PostgreSQL instance and proper `DATABASE_URL` environment variable.

**Affected file**: `tests/integration/test_phase_11_12_integration.py`

**Note**: These are not code bugs. They are integration tests that need database infrastructure to run. They should be marked with `@pytest.mark.requires_db` or similar to skip when no database is available.

---

### Category 7: Loader Test Assertions Outdated (7 failures)

**Impact**: 7 test failures across 2 files  
**Root Cause**: Tests have hardcoded expectations that no longer match the data or behavior.

**`tests/unit/test_loaders.py`** (3 failures):
- `test_loader_missing_file`: Expects `FileNotFoundError` but the loader now returns empty list (the actual `competitor_data.json` exists, so this test's temp dir strategy doesn't isolate properly)
- `test_loader_success`: Assertion count mismatch (expects specific count from mock, gets real data)
- `test_loader_invalid_json`: Similar isolation issue

**`tests/unit/test_data_loaders_coverage.py`** (4 failures):
- `test_loader_missing_file`: Same issue
- `test_loader_success_and_cache`: `assert len(comps) == 8` but real data has 3 companies
- `test_loader_bad_json`: `assert len(comps) == 0` but real data loads 3 (test doesn't mock the file path)
- `test_loader_bad_competitor`: Same — test doesn't properly isolate from real data

**Fix**: These tests need proper mocking/tmp_path isolation. They're reading real `data/input/competitor_data.json` instead of test fixtures.

---

### Category 8: Data Quality Assertion Mismatches (3 failures)

**Impact**: 3 failures, tied to specific data expectations

**`tests/unit/test_geographic_specificity.py`** (1 failure):
- `test_eneve_has_seven_countries`: Expects exactly 7 countries for Eneve. Ivan's JSON has `"geographic_presence": ["Germany", "France", "UK", "Netherlands", "Belgium", "Austria", "Switzerland"]` — this is 7 countries, so this test should now pass after the loader fix. However the unified_loader may override this during merging.

**`tests/unit/test_ai_maturity_consistency.py`** (1 failure):
- `test_eneve_ai_maturity_consistency`: Expects specific AI maturity value. The loader now maps `ai_score=7` (truncated from 7.5) which gives `AIMaturity.MODERATE` (score >= 5 but < 8). The test may expect `STRONG`.

**`tests/unit/test_classification_confidence.py`** (1 failure):
- `test_classification_confidence_integration`: Expects specific classification confidence. Ivan's JSON has `"classification_confidence": 0.95` but the Company model may not expose this field.

**Fix**: Review each test's expectations against the actual data in `competitor_data.json`. Some may need updated thresholds.

---

### Category 9: News Signal Tests (1 failure)

**Impact**: 1 integration test failure  
**Error**: `TestNewsSignalEnrichment::test_news_signals_skips_without_name`  
**Root Cause**: NewsAPI key not configured (`NEWSAPI_KEY` env var missing)

**Affected file**: `tests/integration/test_connector_enrichment.py`

**Fix**: Infrastructure — set `NEWSAPI_KEY` in environment, or mark test as `@pytest.mark.requires_api_key`.

---

### Category 10: Collection-Blocked Test Files (2 errors)

**Impact**: 2 files cannot be collected by pytest (entire files skipped)

**`tests/unit/test_database_persistence.py`**:
- `import pytest_asyncio` at module level → `ModuleNotFoundError`
- Fix: Install `pytest-asyncio` or guard the import

**`tests/unit/test_facts_migration_smoke.py`**:
- `from alembic import command` → `ImportError: cannot import name 'command'`
- Fix: Install/configure `alembic` properly, or guard the import

---

## Summary of Required Actions

### Quick Wins (Environment Setup)

| Action | Tests Fixed | Command |
|--------|------------|---------|
| Install `pytest-asyncio` | ~52 | `uv add pytest-asyncio --dev` |
| Install `pytest-httpx` | 6 | `uv add pytest-httpx --dev` |
| Install `edgar` | 6 | `uv add edgar` |
| Install `supabase` | 2 | `uv add supabase` |

**Total: ~66 tests fixed by installing 4 packages**

### Code Changes Required

| Action | Tests Fixed | Effort |
|--------|------------|--------|
| Update enrichment API test assertions (400 → 422) | 8 | Low (find-replace) |
| Fix loader test isolation (proper mocking) | 7 | Medium |
| Review data quality test thresholds | 3 | Low |
| Mark DB-dependent tests with skip decorator | 24 | Low |
| Guard module-level imports in collection-blocked files | 2 | Low |

**Total: ~44 tests fixed by code changes**

### Infrastructure Required

| Action | Tests Fixed | Effort |
|--------|------------|--------|
| PostgreSQL + DATABASE_URL for phase 11/12 | 24 | Medium (CI/CD config) |
| NEWSAPI_KEY for news connector tests | 1 | Low (secrets config) |
| COMPANIES_HOUSE_API_KEY for Companies House | ~3 | Low (secrets config) |

---

## Gestalt's Loader Fix — Detailed Diff

The fix in `src/solstein/data/loaders.py` makes the `_convert_to_domain_company` method resilient to both schema formats:

**Pattern applied consistently across all 6 fields**:
```python
# Before (only handles nested dict):
employees_data = raw_data.get("employees", {})
employee_count_raw = employees_data.get("latest_headcount")

# After (handles both dict and primitive):
employees_data = raw_data.get("employees", {})
if isinstance(employees_data, (int, float)):
    employee_count = int(employees_data)
elif isinstance(employees_data, dict):
    employee_count_raw = employees_data.get("latest_headcount")
    employee_count = int(employee_count_raw) if employee_count_raw else None
```

**Why this approach**: The loader is the single point where raw JSON meets domain models. Making it format-resilient means we can accept data from multiple sources (research markdown extraction, Ivan's simplified JSON, or future API-generated data) without breaking.

---

## Recommendations for Ivan

1. **Package Dependencies**: Add `pytest-asyncio`, `pytest-httpx` to dev dependencies in `pyproject.toml`. These are required by tests you wrote but weren't in the dependency list.

2. **JSON Schema Documentation**: Consider creating a `data/schemas/competitor_data.schema.json` (JSON Schema) so both agents know the expected format. The current mismatch happened because the loader expected one format and the data used another.

3. **Test Isolation**: Several loader tests read from real `data/input/competitor_data.json` instead of using mocked/temp data. This makes them fragile — they break whenever the data file changes.

4. **Enrichment API Status Codes**: Your `422` for validation errors is correct (per FastAPI convention). The test assertions just need updating from `400` to `422`.

5. **Database Tests**: The phase 11/12 integration tests need a PostgreSQL setup. Consider adding `@pytest.mark.skipif` guards or a `conftest.py` fixture that checks for `DATABASE_URL` availability.

---

*Report generated: 2026-02-26T17:00:00Z*  
*Next action: Commit this report + loader fix, push to remote*
