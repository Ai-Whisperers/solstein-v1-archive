# Ivan's Sequential Fixes — Verification Checklist
**Generated:** 2026-03-23
**Purpose:** Verify each of Ivan's fixes one-by-one, sequentially, to confirm they address root causes rather than just patch symptoms.

---

## Commit History (Most Recent First)

### Commit: b1601f5 (2026-03-23)
**Title:** Configuration integrity & classification boundaries
**Files Changed:** 6 | **Insertions:** 124 | **Deletions:** 16

#### Changes
- [ ] `src/solstein/config.py` — Configuration integrity updates
- [ ] `tests/unit/test_classification_boundaries.py` — NEW: Classification boundary regression tests

#### Issues Addressed
- [ ] Classification threshold enforcement

**Verification Steps:**
1. Read `config.py` and verify classification thresholds are enforced at startup
2. Run `test_classification_boundaries.py` and confirm all assertions pass
3. Check that configs that violate boundaries are rejected
4. Verify no silent failures in config loading

---

### Commit: 7aac536 (2026-03-20 21:34:19)
**Title:** Pipeline smoke test + process_raw/coordinator_agent correctness
**Author:** gesttaltt
**Files Changed:** 2 additions

#### Changes
- [ ] `tests/integration/test_pipeline_smoke.py` — NEW: End-to-end pipeline regression test
- [ ] `workflow_nodes/process_raw.py` — RawDataSource field mapping fixes
- [ ] `coordinator_agent.py` — AgentTaskResult field access fixes

#### Issues Addressed
- ❓ (Implicit from code context; severity unknown)

#### Detailed Changes

**test_pipeline_smoke.py (NEW)**
- [ ] Wires CoordinatorAgent with 5 mock sub-agents
- [ ] No real DB/API calls (isolation)
- [ ] Confirms full LangGraph workflow executes: gather → process_raw → logic_fusion → extract_signals
- [ ] Verifies result is AgentTaskResult (end-to-end regression gate)

**process_raw.py**
- [ ] **Root Issue:** Source objects from agent results were being re-wrapped with non-existent field accessors
  - [ ] Remove: `source_title`, `source_url`, `source_date`, `content_hash`, `word_count`, `language` (none exist on RawDataSource)
  - [ ] Fix: Pass RawDataSource objects through directly
  - [ ] Preserve: Legacy path for non-RawDataSource objects
- [ ] Verify field accessor changes don't break existing legacy data paths

**coordinator_agent.py**
- [ ] **Root Issue:** `result.signals` doesn't exist on AgentTaskResult
  - [ ] Replace: `result.signals` → `final_state.get('extracted_signals', [])`
  - [ ] Location: Log statement for signal count
- [ ] Verify the extracted_signals key is present in final_state before access

**Verification Steps:**
1. Run smoke test in isolation and confirm no errors
2. Trace RawDataSource object creation → process_raw → verify fields used are correct
3. Grep codebase for other uses of `.signals` on AgentTaskResult (check for similar bugs)
4. Verify legacy data path still works (if any test data uses old format)
5. Check coordinator_agent logs for signal count accuracy

---

### Commit: 8c3b34c (2026-03-20 21:31:25)
**Title:** Phase 3 infrastructure layer fixes
**Author:** gesttaltt
**Issues Addressed:** ISSUE-237, ISSUE-238, ISSUE-239, ISSUE-160, ISSUE-220

#### Changes

**market.py**
- [ ] **ISSUE-237:** `peer.company_id` → `peer.id`
- [ ] **ISSUE-238:** `target.company_id` → `target.id`
- [ ] **Root Cause:** Company domain model uses `.id`, not `.company_id`
- [ ] Verify: Find all accesses to `.company_id` on Company objects (should be `.id`)

**scoring.py**
- [ ] **ISSUE-239:** Guard `c.financials` before accessing `.revenue`, `.growth_rate`
- [ ] **Root Cause:** AttributeError when financials is None
- [ ] Fix Pattern: `if c.financials: access fields` or `c.financials?.revenue`
- [ ] Verify: Check all financials accesses are guarded

**drill_down.py + drill_down_service.py**
- [ ] **ISSUE-160:** `source.id` → `source.url` or `source.source_name`
- [ ] **Root Cause:** RawDataSource has no `id` field (has url, source_name)
- [ ] Verify: Confirm RawDataSource schema (no id field)
- [ ] Verify: All usages updated consistently

**evidence/repositories/company.py**
- [ ] **ISSUE-220:** Cypher query values: `VERIFIED/DISPUTED` → `accepted/conflicting`
- [ ] **Root Cause:** ClaimStatus enum values don't match query constants
- [ ] Verify: Check ClaimStatus enum definition
- [ ] Verify: All Cypher queries use correct enum values

**research_dual_write.py**
- [ ] **Root Issue (implicit):** `session.commit()` inside `begin_nested()` savepoint
- [ ] Fix: Remove session.commit(); let with-transaction context manager handle it
- [ ] Verify: Confirm with-transaction properly commits/rolls back

**Verification Steps:**
1. Grep for `.company_id` on Company objects (should find zero or expected legacy cases)
2. Grep for financials access without guard (should find zero)
3. Grep for `source.id` where source is RawDataSource (should find zero)
4. Check ClaimStatus enum values match Cypher constants
5. Trace research_dual_write transaction flow; confirm savepoint+commit doesn't cause double-commit
6. Run integration tests for each module

---

### Commit: 550d7ef (2026-03-20 21:29:13)
**Title:** Phase 0–2 remediation — import crash, construction crashes, enforcement infra
**Author:** gesttaltt

#### Phase 0: Enforcement Infrastructure (NEW)

**scripts/ci/check_imports.py (NEW)**
- [ ] Import smoke checker using `pkgutil.walk_packages`
- [ ] Fails on `AttributeError`, `ImportError` (real import issues)
- [ ] Skips `ModuleNotFoundError` (missing infra dependencies acceptable)
- [ ] Verify: Run script and confirm imports are validated

**tests/unit/test_model_construction.py (NEW)**
- [ ] 13 domain model construction tests
- [ ] Acts as schema drift regression gate
- [ ] Verify: All tests pass; add more as schema changes occur

---

#### Phase 1: Unblock Import Graph (ISSUE-224, 105, 106, 107)

**domain/models.py**
- [ ] **ISSUE-224 (implicit):** Add `DataSourceType.WEB_SEARCH` enum member
- [ ] Root Issue: Enum was incomplete; code referenced missing value
- [ ] Verify: DataSourceType enum includes WEB_SEARCH

**workflow_nodes/process_raw.py**
- [ ] **ISSUE-105:** Remap RawDataSource field names:
  - [ ] `source_url` → `url`
  - [ ] `source_title` → `source_name`
  - [ ] `source_date` → `publication_date`
  - [ ] `extracted_at` → `retrieval_timestamp`
- [ ] Root Issue: Code was accessing wrong field names
- [ ] Verify: RawDataSource schema matches field names used

**workflow_nodes/logic_fusion.py**
- [ ] **ISSUE-106:** Remap AggregatedFact fields:
  - [ ] `field` → `fact_type`
  - [ ] `sources` → `sources_used`
  - [ ] Remove: `company_name`, `unit`, `extraction_method` (no longer exist)
- [ ] Root Issue: Field names don't match schema
- [ ] Verify: AggregatedFact schema matches field names used

**workflow_nodes/extract_signals.py**
- [ ] **ISSUE-107:** Remap SignalExtraction fields
  - [ ] Add required: `calculation_method="direct_extraction"`
- [ ] Root Issue: Field required but not provided
- [ ] Verify: SignalExtraction construction always includes calculation_method

**infrastructure/query_cache.py**
- [ ] Fix missing import: `from cache.py import get_cache`
- [ ] Root Issue: Import error breaks module loading
- [ ] Verify: Import succeeds; check relative import path

**Verification Steps (Phase 1):**
1. Run `scripts/ci/check_imports.py` — should succeed (no import errors)
2. Grep for old field names in workflow_nodes (should find zero)
3. Verify RawDataSource, AggregatedFact, SignalExtraction schemas match code
4. Trace import chain for query_cache.py; confirm get_cache is available
5. Run any integration tests that use these workflow nodes

---

#### Phase 2: Unblock Construction (ISSUE-152/153/154, 230/231, 250, 258, 265/266, 267)

**Report Generator Classes (Multiple files)**
- [ ] **ISSUE-152/153/154:** Add missing inheritance:
  - [ ] `BatchFinancialReportGenerator` ← `[base class]`
  - [ ] `BatchGenealogyReportGenerator` ← `[base class]`
  - [ ] `BatchProtocolReportGenerator` ← `[base class]`
- [ ] Root Issue: Classes inherit from nothing; missing base functionality
- [ ] Verify: Find base report generator classes; confirm inheritance added

**data/funding_unified.py**
- [ ] **ISSUE-230:** `source_type="funding"` → `DataSourceType.CRUNCHBASE`
- [ ] Root Issue: Using string instead of enum
- [ ] Verify: All source_type assignments use DataSourceType enum

**data/web_search_unified.py**
- [ ] **ISSUE-231:** `source_type="web_search"` → `DataSourceType.EXA_SEARCH`
- [ ] Root Issue: Using string instead of enum
- [ ] Verify: All source_type assignments use DataSourceType enum

**data/merger.py**
- [ ] **ISSUE-250:** Add `allow_empty_primary=True` to FinancialMetric model_dump
- [ ] Root Issue: model_dump fails when primary metric is empty
- [ ] Verify: FinancialMetric can be dumped with no primary data

**data/sec_edgar_refresh.py**
- [ ] **ISSUE-258:** Guard `None start_date`/`end_date` with 3-year default window
- [ ] Root Issue: TypeError when dates are None
- [ ] Verify: Dates default to 3-year window if not provided

**infrastructure/business_metrics.py**
- [ ] **ISSUE-265:** `ai_data_quality_score` → `ai_score`
- [ ] **ISSUE-266:** `enrichment_updated_at` → `last_updated`
- [ ] Root Issue: Field names don't match schema
- [ ] Verify: BusinessMetrics model has ai_score, last_updated (not old names)

**api/routers/enrichment_batch.py**
- [ ] **ISSUE-267:** `status="partial_failure"` → `status="partial"`
- [ ] Root Issue: String value doesn't match enum
- [ ] Verify: Check status enum values; update all assignments

**Verification Steps (Phase 2):**
1. Run `tests/unit/test_model_construction.py` — all 13 tests should pass
2. Grep for old enum values (strings like "funding", "web_search") — should find zero
3. Grep for old field names (ai_data_quality_score, enrichment_updated_at, company_id) — should find zero
4. Trace each model construction; verify no TypeError or AttributeError
5. Run full test suite — should pass without construction errors

---

## Verification Strategy

### Sequential Verification (One Fix at a Time)
1. **Read** the fix commit message and understand the root issue
2. **Locate** the affected files in codebase
3. **Trace** the data flow from input → affected field → output
4. **Search** for similar issues in related code
5. **Test** the specific fix (unit test, integration test, or smoke test)
6. **Verify** no regressions in dependent code
7. **Mark** as ✅ VERIFIED or ⚠️ NEEDS INVESTIGATION

### Batch Verification (After All Individual Fixes)
1. Run full test suite
2. Run smoke tests
3. Run quality checks
4. Run import validation
5. Check for regressions

---

## Summary Table

| Commit | Date | Phase | Issues | Key Changes | Priority |
|--------|------|-------|--------|-------------|----------|
| b1601f5 | 2026-03-23 | Config | unverified | Classification boundaries | 🔴 HIGH |
| 7aac536 | 2026-03-20 | Pipeline | Implicit | RawDataSource field mapping | 🔴 HIGH |
| 8c3b34c | 2026-03-20 | Phase 3 | 237-239,160,220 | Market/scoring/drill_down/evidence | 🔴 HIGH |
| 550d7ef | 2026-03-20 | Phase 0-2 | 224,105-107,152-154,230-231,250,258,265-267 | Import + construction fixes | 🔴 HIGH |

---

## Next Steps

1. **Start with Phase 0-2 (550d7ef)** — Foundation layer, all other fixes depend on this
   - [ ] Verify import system works
   - [ ] Verify model construction tests pass
   - [ ] Verify field name remapping is complete

2. **Then Phase 3 (8c3b34c)** — Infrastructure layer
   - [ ] Verify no attribute errors on domain model access
   - [ ] Verify enum usage is consistent

3. **Then Pipeline (7aac536)** — Workflow integration
   - [ ] Verify end-to-end smoke test passes
   - [ ] Verify RawDataSource flow works

4. **Finally Config (b1601f5)** — Safety layer
   - [ ] Verify classification boundaries enforced
   - [ ] Verify no invalid configs accepted

---

**Created by:** Claude (Haiku 4.5)
**Status:** Ready for verification
**Last Updated:** 2026-03-23
