# EPIC-084: Dead Code Cleanup

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 |
| **Phase** | P5 — Quality & Polish |
| **Effort** | S (1–2 days) |
| **Stories** | 4 ([STORY-340](STORIES/STORY-340.md) through [STORY-343](STORIES/STORY-343.md)) |
| **Created** | 2026-04-01 |
| **Updated** | 2026-04-05 (corrected wrong assumptions: STORY-340 and STORY-343 have active callers) |

## Context

Several files and directories contain dead or retired code. The safe deletions (STORY-341, STORY-342) can proceed immediately. Two stories (STORY-340, STORY-343) were originally written as simple deletions but are **incorrect** — both targets have active callers in production code and cannot be deleted without first refactoring those callers.

## Verified Codebase State (2026-04-05)

### STORY-340 — active caller found
`src/solstein/data/real_data_integration.py` is imported by `cli_research.py`:
```
src/solstein/cli_research.py:22: from solstein.data.real_data_integration import RealDataLoader
src/solstein/cli_research.py:50,115,233: RealDataLoader(...)
```
**Conclusion**: Cannot delete `real_data_integration.py` without first refactoring `cli_research.py` to remove the dependency. Story scope must include the caller fix.

### STORY-341 — confirmed safe
`src/solstein/adapters/enrichment/_retired/` has no callers:
```
grep -rn "from.*_retired" src/  → (no results)
```
Safe to delete as-is.

### STORY-342 — confirmed safe
`src/solstein/adapters/discovery/_retired/` has no callers:
```
grep -rn "from.*_retired" src/  → (no results)
```
Safe to delete as-is.

### STORY-343 — active caller found
`src/solstein/research/graph/` is imported by `api/routers/review.py`:
```
src/solstein/api/routers/review.py:168: from solstein.research.graph.executor import _get_default_executor
```
**Conclusion**: Cannot delete `research/graph/` without first fixing `review.py:168` to remove or reroute this import. Story scope must include the caller fix.

## Stories

| Story | Title | Status | Notes |
|-------|-------|--------|-------|
| [STORY-341](STORIES/STORY-341.md) | Delete adapters/enrichment/_retired/ directory (8 dead adapter files) | 🔴 READY | No callers — safe |
| [STORY-342](STORIES/STORY-342.md) | Delete adapters/discovery/_retired/ directory (dead Exa web search adapter) | 🔴 READY | No callers — safe |
| [STORY-340](STORIES/STORY-340.md) | Refactor cli_research.py to remove RealDataLoader dependency, then delete real_data_integration.py | 🔴 READY | ⚠️ Must fix cli_research.py first |
| [STORY-343](STORIES/STORY-343.md) | Fix review.py:168 import, then delete research/graph/ frozen runtime (per ADR-009/ADR-010) | ⏳ BLOCKED | ⚠️ Must fix review.py:168 first; needs team sign-off |

> ⚠️ **Execution order**: Run STORY-341 and STORY-342 first (safe deletions). STORY-340 requires caller fix before deletion. STORY-343 requires caller fix + team sign-off.

## Success Criteria

- `adapters/enrichment/_retired/` deleted; import scan clean
- `adapters/discovery/_retired/` deleted; import scan clean
- `cli_research.py` no longer imports from `real_data_integration`; `real_data_integration.py` deleted
- `api/routers/review.py:168` import removed or rerouted; `research/graph/` deleted after team sign-off
- Dead code CI detector confirms no new orphaned modules

## Definition of Done

- [ ] [STORY-341](STORIES/STORY-341.md): `_retired/enrichment/` directory gone; `grep -rn "_retired"` returns nothing
- [ ] [STORY-342](STORIES/STORY-342.md): `_retired/discovery/` directory gone; `grep -rn "_retired"` returns nothing
- [ ] [STORY-340](STORIES/STORY-340.md): `cli_research.py` imports removed; `real_data_integration.py` gone; tests pass
- [ ] [STORY-343](STORIES/STORY-343.md): `review.py:168` import gone; `research/graph/` gone; tests pass
- [ ] No test deleted or broken
- [ ] `pytest tests/unit/ -q` passes at ≥ pre-epic baseline

## Dependencies

- [STORY-343](STORIES/STORY-343.md) requires explicit team sign-off (ADR-009/010 reference frozen graph runtime)
