# ADR-010: Salvage Decision from Golden-Run Evidence

**STORY-270 / EPIC-070** | Decision Date: 2026-03-31

## Status

**ACCEPTED** — Salvage the legacy runtime. Delete graph runtime progressively.

## Context

EPIC-067 through EPIC-070 produced four categories of empirical evidence to
inform the salvage-vs-rebuild decision for the Solstein research pipeline:

1. **Runtime Depth Ledger** (STORY-271): 4,029 total runtime LOC across legacy
   (1,944) and graph (2,085) surfaces. 1,859 LOC of duplicate enrichment
   families. 4 graph nodes returning empty outputs.

2. **Provider Scorecard** (STORY-263): Unified adapters score 0.65-0.80
   confidence vs. legacy 0.3-0.7. All providers wired to legacy pipeline.
   No provider requires the graph runtime.

3. **Golden Contract Runs** (STORY-267): 30 provider-level contract tests
   validate success and degraded-mode semantics for Yahoo Finance, Patents,
   and Global Market adapters. ArtifactDiffer engine catches regressions.

4. **Full-Market Golden Runs** (STORY-268): 17 tests across 5 benchmark
   companies. 86.7% average completeness. 13 total facts extracted.
   Regression gates enforce minimum thresholds.

5. **Placeholder Guards** (STORY-269): 28 tests detect empty/mock success
   paths in all 4 graph placeholder nodes and the human review router.
   Router bypass bug fixed (empty confidence_scores no longer bypasses review).

6. **Salvage Decision Criteria** (STORY-258): 6 salvage conditions encoded
   as 13 executable tests, all passing. Decision document published at
   `docs/architecture/SALVAGE_VS_REBUILD_DECISION.md`.

## Decision

**SALVAGE the legacy runtime.** The measured evidence supports this:

### Measured Defect Rates

| Metric | Value | Threshold | Result |
|--------|-------|-----------|--------|
| Golden contract test failures | 0 / 30 | 0 | PASS |
| Full-market regression violations | 0 / 17 | 0 | PASS |
| Placeholder guard violations | 0 / 28 (after fix) | 0 | PASS |
| Salvage condition failures | 0 / 13 | 0 | PASS |
| Router bypass bug | Fixed (STORY-269) | No bypasses | PASS |
| Total test suite | 88 golden-run tests pass | 0 failures | PASS |

### Failure Classes Identified and Resolved

| # | Failure Class | Discovery | Resolution |
|---|---------------|-----------|------------|
| 1 | Empty confidence_scores bypass human review | STORY-269 placeholder guards | Fixed: `not confidence_scores` check in `_human_review_router` |
| 2 | Graph placeholder nodes produce no real output | STORY-271 ledger | Documented, guarded by 28 placeholder tests |
| 3 | Duplicate adapter pairs create maintenance burden | STORY-263 scorecard | Resolved: STORY-265 collapsed -336 LOC |
| 4 | Multiple entrypoints fragment orchestration | STORY-271 ledger | Resolved: STORY-257 consolidated to `run_market_intelligence()` |
| 5 | Feature-flag branching between runtimes | STORY-271 ledger | Resolved: STORY-256 deleted runtime aliases |

### Rebuild Triggers (None Currently Active)

All 6 rebuild triggers from `SALVAGE_VS_REBUILD_DECISION.md` were evaluated:

| # | Trigger | Current Status |
|---|---------|----------------|
| 1 | Graph placeholders persist after 2 sprints | NOT TRIGGERED — guarded, timeline active |
| 2 | Duplicate providers re-emerge | NOT TRIGGERED — adapter freeze CI check |
| 3 | Features bypass legacy for graph | NOT TRIGGERED — graph frozen (ADR-009) |
| 4 | Golden runs regress | NOT TRIGGERED — 88 tests pass |
| 5 | Mock services in API routes | NOT TRIGGERED — jobs endpoint disabled |
| 6 | Entrypoint fragmentation | NOT TRIGGERED — single canonical entrypoint |

## Next Backlog Wave

Based on the measured failure surfaces, the next backlog wave targets only
proven deficiency areas:

### Priority 1: Eliminate Graph Placeholders
- Replace or delete 4 placeholder graph nodes (conflict_resolution, scoring,
  analysis, export) — these are the only remaining non-functional code in
  the runtime
- Estimated: 2 stories, ~800 LOC affected

### Priority 2: Mock Service Quarantine
- Wire tenant control-plane services or quarantine mock implementations
  to prevent them from serving user requests
- Estimated: 1-2 stories

### Priority 3: Export Artifact Validation
- Add export artifact validation to golden runs to close the last
  uncovered surface in the pipeline
- Estimated: 1 story

### Priority 4: Graph Runtime Deletion
- Once placeholder value is migrated, delete graph runtime files entirely
- Estimated: 1 story, -2,085 LOC

## Consequences

1. All new features target the legacy pipeline exclusively
2. Graph runtime code remains frozen (ADR-009) and will be deleted after
   placeholder migration
3. The 88-test golden-run suite is the regression gate for all runtime changes
4. Rebuild triggers are monitored at each sprint retrospective
5. Next backlog wave is scoped to 5-6 stories on proven failure surfaces only

## References

- `docs/architecture/SALVAGE_VS_REBUILD_DECISION.md` (STORY-258)
- `docs/audit/RUNTIME_DEPTH_AND_DUPLICATION_LEDGER_2026-03-31.md` (STORY-271)
- `docs/architecture/provider-scorecard.md` (STORY-263)
- `docs/architecture/decisions.md` (ADR-009, STORY-255)
- `tests/golden_runs/` (STORY-267, 268, 269)
