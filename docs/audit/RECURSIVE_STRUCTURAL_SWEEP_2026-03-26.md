# Recursive Structural Sweep 2026-03-26

## Purpose

This addendum records the recursive structural sweep run after the March fix-and-guardrail rollout.

The goal was not another broad prose audit. The goal was to use the new strict surfaces to find issue classes the original source-reading audit did not track explicitly:

- import cycles
- module-boundary inversions
- post-audit regressions introduced by ongoing fixes

## Tooling Used

- `uv run basedpyright --warnings`
- `npm run ast-grep -- --error --report-style=short src/solstein`
- `uv run python scripts/ci/detect_import_cycles.py`
- `uv run python scripts/ci/enforce_module_boundaries.py`

## Verified Findings

The sweep added four new issues to the master audit:

- `ISSUE-268` static import cycle around `patents_unified` / `research.discovery` / `adapters.registry`
- `ISSUE-269` domain `value_objects` importing analytics scoring constants
- `ISSUE-270` infrastructure persistence importing `canonicalize_url` from the higher `research` layer
- `ISSUE-271` infrastructure reconciliation importing `canonical_json_dumps` from the higher `research` layer

## Important Negative Result

- `basedpyright` passed clean
- the current `ast-grep` rule set passed clean
- `check_imports.py` passed clean on import smoke coverage

This means the newly found issues are structural dependency-shape debt, not plain syntax/type/import failures.

## Why These Findings Matter

The repo now depends on generated docs, AST rules, and stricter boundary enforcement to avoid context drift and repeated re-auditing. Cycles and reversed-layer imports directly undermine that strategy even when runtime behavior still happens to work.

These issues therefore belong in both:

- the master audit as canonical defect history
- the backlog as explicit follow-up work

## Backlog Mapping

Tracked under:

- `backlog/EPICS/EPIC-066-architectural-boundaries-and-cycle-elimination/README.md`

Stories:

- `STORY-246` break the `patents_unified` / discovery / registry cycle
- `STORY-247` relocate shared canonicalization and hashing utilities to a lower shared boundary
- `STORY-248` decouple domain value objects from analytics-owned scoring constants
- `STORY-249` make cycle and boundary checks part of the maintained blocking engineering gate
