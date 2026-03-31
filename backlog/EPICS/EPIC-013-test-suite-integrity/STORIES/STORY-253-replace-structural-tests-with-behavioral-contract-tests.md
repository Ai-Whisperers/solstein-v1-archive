# STORY-253: Replace Structural Source-Inspection Tests with Behavioral Contract Tests

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-013 Test Suite Integrity |
| **Created** | 2026-03-31 |
| **Risk** | High |

---

## Problem Statement

The 2026-03-31 audit found that a material slice of the test suite passes by reading source files, ASTs, or string literals instead of exercising runtime behavior. This creates false confidence: code can satisfy tests while still failing when routes execute, artifacts are emitted, or task wiring is actually used.

## Acceptance Criteria

- [ ] Replace or supplement high-risk structural tests so they execute runtime behavior for the targeted surfaces.
- [ ] Targeted areas include export task wiring, metrics/auth route behavior, and other critical-path checks currently dominated by `Path.read_text()`, AST, or substring assertions.
- [ ] Any retained static test clearly documents why runtime execution is not practical and what concrete regression it still catches.
- [ ] The targeted suite would fail on a real runtime regression even if the source file still contains the expected strings.

## Tasks

- [ ] Inventory the worst-offending structural tests and rank them by production risk.
- [ ] Convert critical-path assertions to behavioral tests using live imports, route registration, task metadata, emitted artifacts, or response behavior.
- [ ] Keep static tests only where they are the correct level of verification, and mark them as intentional.
- [ ] Document the chosen boundary between structural and behavioral QA in test comments or contributing guidance.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This story was added from the 2026-03-31 audit because behavior-oriented export tests caught a regression that source-inspection tests did not.

### Next Agent Action

- Start with tests guarding export schema behavior, Prometheus/auth wiring, and async export task behavior.
- Prefer replacing brittle source-text assertions with executable checks over broad test-file churn.

### Required Working Style

- Keep the scope focused on meaningful regressions, not test-style cleanup for its own sake.
- Preserve fast feedback where possible, but not at the cost of replacing runtime truth with string matching.

### Minimum Verification For Future Agents

- Run the targeted converted tests and show they fail against the pre-fix regression shape.
- Document any static tests intentionally retained and why.
