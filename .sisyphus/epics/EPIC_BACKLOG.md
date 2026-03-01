# Solstein ENEVE Epic Backlog
> Generated: 2026-03-01 | Based on ENEVE run analysis & critique

## Status Legend
- 🔴 NOT STARTED
- 🟡 IN PROGRESS  
- 🟢 COMPLETE
- ⛔ BLOCKED

---

## EPIC-001: Fix Classification Thresholds — Applied Consistently
**Status**: 🟡 IN PROGRESS  
**Priority**: P0 CRITICAL  
**Root Cause**: `run_eneve_199.py` summary block hardcodes Phoenix (≥7.0) / Salt (4.0-7.0) / Lead (≤4.0) instead of reading from constants

### Stories
- [ ] STORY-001-1: Fix `run_eneve_199.py` summary to import and use `PHOENIX_SCORE_THRESHOLD`, `LEAD_SCORE_THRESHOLD` from constants.py
- [ ] STORY-001-2: Add threshold validation test that asserts summary counts match constants
- [ ] STORY-001-3: Update README classification table (still shows ≥7.0 as Phoenix)

### Acceptance Criteria
- Summary output shows Phoenix (≥7.5) not Phoenix (≥7.0)
- All threshold references in run scripts use constants, not literals
- Unit test verifies classification boundary correctness

---

## EPIC-002: Fix Score Inflation / Distribution Problem
**Status**: 🔴 NOT STARTED  
**Priority**: P0 CRITICAL  
**Root Cause**: Scoring algorithm gives very few penalty paths; all 199 synthetic companies score 5.90+; no Lead companies (0%)

### Stories
- [ ] STORY-002-1: Audit scoring paths — find minimum reachable score for worst-case inputs
- [ ] STORY-002-2: Add penalty multipliers for negative growth rates (< 0%)
- [ ] STORY-002-3: Add heavy penalties for unprofitable + low revenue companies
- [ ] STORY-002-4: Add stress test: deliberately bad company must score < 3.0
- [ ] STORY-002-5: Validate score distribution: Phoenix 15-20%, Salt 60-75%, Lead 10-25%
- [ ] STORY-002-6: Fix base_score floor — shouldn't allow 5.9 minimum with bad inputs

### Acceptance Criteria
- Worst-case inputs produce score < 3.0
- At least 10% of synthetic companies classify as Lead
- At least 60% of synthetic companies classify as Salt
- No more than 20% classify as Phoenix

---

## EPIC-003: Fix Fake Enrichment Reporting
**Status**: 🔴 NOT STARTED  
**Priority**: P0 CRITICAL  
**Root Cause**: System claims enrichment happened but nothing real was fetched; `enrichment_sources: []`, `enrichment_quality_metrics: {}`

### Stories
- [ ] STORY-003-1: Add `data_source_type` field to CompanyProfile: "real" | "synthetic" | "mixed"
- [ ] STORY-003-2: Label synthetic enrichment sources as "Synthetic-Generator" not vague API refs
- [ ] STORY-003-3: Remove fake `enrichment_source_count: 3` for synthetic companies
- [ ] STORY-003-4: Add `data_lineage` dict tracking which fields came from which source
- [ ] STORY-003-5: Update Excel export to show Data Source column per company
- [ ] STORY-003-6: Validate: real companies have enrichment_sources populated

### Acceptance Criteria
- Every company has `data_source_type` field
- Synthetic companies show `data_source_type: "synthetic"`
- No fake enrichment_source_count claimed for synthetic data
- Excel dashboard shows data source transparency column

---

## EPIC-004: Fix Pipeline Execution Order
**Status**: 🔴 NOT STARTED  
**Priority**: P1 HIGH  
**Root Cause**: Dashboard/Excel sometimes generated before scoring completes; log lines confirm order issues

### Stories
- [ ] STORY-004-1: Add explicit pipeline stage logging with timestamps (STAGE 1: Load → STAGE 2: Enrich → STAGE 3: Score → STAGE 4: Export)
- [ ] STORY-004-2: Add pipeline progress bar using tqdm or simple % counter
- [ ] STORY-004-3: Verify Excel export is always LAST step after all scoring complete
- [ ] STORY-004-4: Add pipeline timing report in summary (time per stage)

### Acceptance Criteria
- Log shows clear STAGE markers with timestamps
- Excel export always generated after 100% of companies scored
- Pipeline timing visible in output

---

## EPIC-005: Financial Data Sanity Checks
**Status**: 🔴 NOT STARTED  
**Priority**: P1 HIGH  
**Root Cause**: Eneve shows €33K revenue/employee (should be €100K-€300K); unrealistic ratios pass scoring unchecked

### Stories
- [ ] STORY-005-1: Create `FinancialSanityValidator` class in `src/solstein/validation/`
- [ ] STORY-005-2: Revenue per employee check: warn if < €80K or > €3M/employee
- [ ] STORY-005-3: Profit margin sanity: warn if > 60% (unrealistic for software)
- [ ] STORY-005-4: Growth rate coherence: 3-year CAGR should be within ±20% of latest YoY
- [ ] STORY-005-5: Revenue scale check: companies < €500K revenue shouldn't score > 6.0 on financial health
- [ ] STORY-005-6: Log warnings for sanity violations (don't block pipeline)
- [ ] STORY-005-7: Add sanity violation count to Excel export summary sheet

### Acceptance Criteria
- FinancialSanityValidator identifies Eneve's €33K/employee ratio as suspicious
- Warnings logged without blocking pipeline
- Excel shows sanity warning count per company

---

## EPIC-006: Score Algorithm Audit & Penalty Fixes
**Status**: 🔴 NOT STARTED  
**Priority**: P0 CRITICAL  
**Root Cause**: All companies scoring 5.90-9.64; scoring algorithm has no effective floor via penalties

### Stories
- [ ] STORY-006-1: Audit GrowthScorer — calculate minimum possible score with worst inputs
- [ ] STORY-006-2: Audit FinancialHealthScorer — ensure negative revenue growth deeply penalized
- [ ] STORY-006-3: Audit CompetitiveScorer — legacy tech stack should cause significant penalty
- [ ] STORY-006-4: Create `ScoreAlgorithmAuditReport` that runs all scorers with min/max inputs
- [ ] STORY-006-5: Add negative growth rate penalty (-5% growth should subtract at least 1.5 points)
- [ ] STORY-006-6: Add zero-funding penalty (no funding rounds should subtract at least 0.5 points)
- [ ] STORY-006-7: Write unit tests for edge cases: zero revenue, negative growth, no funding

### Acceptance Criteria
- Audit report shows min score achievable (must be < 2.0)
- A company with -20% growth, no funding, old tech scores < 3.5
- Unit tests cover worst-case scoring scenarios

---

## EPIC-007: Synthetic Data Diversity
**Status**: 🔴 NOT STARTED  
**Priority**: P1 HIGH  
**Root Cause**: `generate_synthetic_companies.py` produces uniformly optimistic profiles; growth_rate 20-80%, no struggling companies

### Stories
- [ ] STORY-007-1: Add "Struggling" company archetype (negative growth -5% to -30%, low funding, poor margins)
- [ ] STORY-007-2: Add "Declining Legacy" archetype (old tech, high revenue but shrinking, no AI)
- [ ] STORY-007-3: Add "Early Stage Distressed" archetype (tiny revenue, burning cash, no growth)
- [ ] STORY-007-4: Adjust population distribution: 15% Phoenix, 65% Salt, 20% Lead archetypes
- [ ] STORY-007-5: Add seed-based reproducible generation (fix random seed globally)
- [ ] STORY-007-6: Generate 50+ realistic European energy software companies with proper names
- [ ] STORY-007-7: Validate generated dataset hits target distribution before run

### Acceptance Criteria
- Generated dataset contains companies with negative growth rates
- At least 30 companies have growth_rate < 5%
- At least 20 companies have growth_rate < 0%
- Score distribution falls within target range after algorithm changes

---

## EPIC-008: Output Directory Cleanup & Retention Policy
**Status**: 🔴 NOT STARTED  
**Priority**: P2 MEDIUM  
**Root Cause**: 139 Excel files in exports (2.20 MB graveyard); no cleanup mechanism; no run ID tracking

### Stories
- [ ] STORY-008-1: Create `scripts/cleanup_exports.py` with --keep-last N flag (default: 10)
- [ ] STORY-008-2: Add run ID (timestamp-based) to all output filenames
- [ ] STORY-008-3: Create `data/output/runs/` directory structure with per-run subdirectories
- [ ] STORY-008-4: Add auto-cleanup at start of each run (remove exports older than 30 days)
- [ ] STORY-008-5: Add export manifest JSON tracking all generated files per run

### Acceptance Criteria
- `python scripts/cleanup_exports.py --keep-last 5` removes old exports
- New runs use timestamped filenames
- Export manifest created per run

---

## EPIC-009: Excel Dashboard Quality
**Status**: 🔴 NOT STARTED  
**Priority**: P2 MEDIUM  
**Root Cause**: Excel exists but is basic — no charts, no summary statistics, no quality indicators, no visual hierarchy

### Stories
- [ ] STORY-009-1: Add "Summary" sheet: total companies, classification counts, avg scores, run date
- [ ] STORY-009-2: Add "Score Distribution" sheet with histogram data (0-1, 1-2, ..., 9-10 buckets)
- [ ] STORY-009-3: Add classification distribution pie chart data sheet
- [ ] STORY-009-4: Add "Data Quality" column in main sheet showing Synthetic/Real/Mixed
- [ ] STORY-009-5: Add conditional formatting: Phoenix rows gold, Salt rows silver, Lead rows red
- [ ] STORY-009-6: Add "Sanity Warnings" column showing financial sanity issue count
- [ ] STORY-009-7: Add auto-fit column widths and freeze top row

### Acceptance Criteria
- Excel has at minimum 3 sheets: Summary, Companies, ScoreDistribution
- Company rows color-coded by classification
- Summary sheet shows correct totals matching printed report

---

## EPIC-010: Confidence Score Transparency
**Status**: 🔴 NOT STARTED  
**Priority**: P2 MEDIUM  
**Root Cause**: Synthetic companies marked with "Confirmed" confidence; data lineage not tracked; no distinction between real vs synthetic confidence

### Stories
- [ ] STORY-010-1: Add `SYNTHETIC` as a valid ConfidenceLevel in confidence enum
- [ ] STORY-010-2: Prevent synthetic companies from ever receiving CONFIRMED or HIGH confidence
- [ ] STORY-010-3: Add `data_lineage` dict to CompanyProfile tracking field → source mapping
- [ ] STORY-010-4: Show confidence breakdown in Excel (one column per major confidence category)
- [ ] STORY-010-5: Add confidence summary to run report (avg confidence, % real vs synthetic)

### Acceptance Criteria
- No synthetic company has CONFIRMED confidence
- All synthetic companies show SYNTHETIC confidence level
- Excel shows confidence per company

---

## Summary

| Epic | Priority | Status | Stories |
|------|----------|--------|---------|
| EPIC-001 | P0 CRITICAL | 🟡 | 3 stories |
| EPIC-002 | P0 CRITICAL | 🔴 | 6 stories |
| EPIC-003 | P0 CRITICAL | 🔴 | 6 stories |
| EPIC-004 | P1 HIGH | 🔴 | 4 stories |
| EPIC-005 | P1 HIGH | 🔴 | 7 stories |
| EPIC-006 | P0 CRITICAL | 🔴 | 7 stories |
| EPIC-007 | P1 HIGH | 🔴 | 7 stories |
| EPIC-008 | P2 MEDIUM | 🔴 | 5 stories |
| EPIC-009 | P2 MEDIUM | 🔴 | 7 stories |
| EPIC-010 | P2 MEDIUM | 🔴 | 5 stories |

**Total**: 57 stories across 10 epics

---
*Last updated: 2026-03-01*
