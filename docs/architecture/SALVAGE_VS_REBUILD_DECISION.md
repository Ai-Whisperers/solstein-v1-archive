# Salvage vs Rebuild Decision: Legacy Runtime

**STORY-258 / EPIC-067** | Decision Date: 2026-03-31

## Executive Summary

**Decision: SALVAGE + Targeted Hardening.**

The legacy sequential pipeline (`pipeline.py` + `pipeline_stages.py`) is the only
behaviorally complete runtime in the Solstein codebase. It handles all 10 stages
end-to-end with real data transformations and is the sole production caller for
all CLI commands and API endpoints. The graph runtime has 4 placeholder nodes
that produce no real output, no confirmed non-test production caller, and a
dual-maintenance burden of 4,029 LOC across both surfaces.

The recommendation is to keep the legacy pipeline as the canonical runtime,
delete the graph runtime after salvage milestones are met, and only revisit
a rebuild if specific red-flag triggers fire.

## Evidence Base

This decision is grounded in three evidence sources produced during EPIC-067
through EPIC-070:

**STORY-271 Runtime Depth Ledger** (`docs/audit/RUNTIME_DEPTH_AND_DUPLICATION_LEDGER_2026-03-31.md`):
Measured 4,029 total runtime LOC across legacy (1,944) and graph (2,085) surfaces.
Identified 1,859 LOC of duplicate enrichment families, 1,193 LOC of placeholder/mock
services, and 4 graph nodes returning empty outputs.

**STORY-263 Provider Scorecard** (`docs/architecture/provider-scorecard.md`):
Assessed all provider adapters. Unified adapters score 0.65-0.80 confidence vs.
legacy 0.3-0.7. All providers are wired to the legacy pipeline. No provider
requires the graph runtime.

**EPIC-070 Golden Run Evidence** (STORY-267/268/269):
75 golden contract and regression tests pass on the legacy pipeline. Full-market
run with 5 benchmark companies demonstrates 86.7% average completeness. All
known placeholder patterns are detected and blocked by guard functions.

## Decision Criteria

All 6 salvage conditions are met:

| # | Condition | Threshold | Status |
|---|-----------|-----------|--------|
| 1 | Legacy pipeline complete end-to-end | 100% of stages produce real output | MET |
| 2 | Placeholder surfaces bounded | Mock/stub LOC < 30% of total runtime | MET (29.6%) |
| 3 | Golden runs pass on legacy | 0 regressions in EPIC-070 tests | MET (75 tests pass) |
| 4 | Callers consolidated | 1 canonical entrypoint | MET (`run_market_intelligence()`) |
| 5 | Provider parity exists | Unified adapters cover all surfaces | MET |
| 6 | Debt removal timeline exists | Roadmap to delete duplicate LOC | MET (STORY-265/264 DONE) |

## Salvage Path

Completed milestones (EPIC-067/069/070):

1. STORY-265: Collapsed duplicate adapter pairs (-336 LOC)
2. STORY-264: Removed replaceable providers from canonical runtime
3. STORY-255: Froze graph runtime, declared legacy canonical (ADR-009)
4. STORY-256: Deleted runtime aliases and feature-flag branching
5. STORY-257: Repaired legacy entrypoints to share one registry + one converter
6. STORY-267/268/269: Golden contract tests + full-market regression gates

Remaining hardening work (future epics):

- Replace 4 placeholder graph nodes with real logic or delete them entirely
- Wire tenant control-plane services or quarantine mock implementations
- Add export artifact validation to golden runs
- Delete graph runtime files once all value is migrated to legacy path

## Rebuild Triggers

If any of these conditions are observed, escalate to a rebuild decision:

| # | Red Flag | Trigger Condition |
|---|----------|-------------------|
| 1 | Graph placeholders persist | Still empty after 2 more sprints |
| 2 | Duplicate providers re-emerge | New adapter pairs created without deleting old |
| 3 | Features bypass legacy for graph | New code routes through graph runtime instead of legacy |
| 4 | Golden runs regress | EPIC-070 test suite fails on legacy pipeline |
| 5 | Mock services in API routes | Placeholder tenant/control-plane code serves user requests |
| 6 | Entrypoint fragmentation | New CLI/API paths use a different orchestration surface |

Monitoring plan: Run `pytest tests/golden_runs/ -x` on every PR. Track
placeholder LOC quarterly via the runtime ledger script.

## Risk Mitigation

1. **Graph code frozen** (ADR-009, STORY-255): No new development on graph runtime
2. **Adapter freeze** (STORY-266): CI check blocks new compatibility adapters
3. **Golden run regression gate** (STORY-267/268): 75 tests catch any pipeline degradation
4. **Placeholder guards** (STORY-269): 28 tests detect empty/mock success paths
5. **Monthly review**: Re-evaluate rebuild triggers at each sprint retrospective

## Architecture Decision Record

This document serves as the Architecture Decision Record (ADR) for the
salvage-vs-rebuild question. It supersedes the interim freeze in ADR-009
(STORY-255) by providing the full evidence-backed decision.

**Decision**: Salvage the legacy runtime. Delete graph runtime after
placeholder value is migrated. Rebuild only if red-flag triggers fire.

**Consequences**: All new features target the legacy pipeline. Graph
runtime code remains frozen and will be progressively deleted. The
golden-run test suite becomes the regression gate for all runtime changes.
