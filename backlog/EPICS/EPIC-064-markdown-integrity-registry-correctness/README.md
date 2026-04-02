# EPIC-064: Markdown Integrity and Registry Correctness

> **Priority**: P0 - Ship Blocker
> **Stories**: 4 (STORY-234 through STORY-237)
> **Effort**: L (2-3 weeks)
> **Dependencies**: EPIC-063 (Documentation Topology and Source-of-Truth Governance)
> **Status**: 🔴 Not Started

---

## Problem

Markdown quality debt is materially impacting reliability of docs navigation and backlog operations.

Audit evidence:

- 140 broken relative links in scoped docs/backlog trees
- unresolved placeholder tokens in active documentation
- conflicting dashboard metrics and duplicate rows in `backlog/README.md`

---

## Scope

| Category | Action |
|---|---|
| Link Integrity | Repair broken relative links and prevent regressions |
| Placeholder Hygiene | Remove or contain unresolved template tokens in active docs |
| Registry Correctness | Correct backlog dashboard/index inconsistencies |
| Drift Control | Reconcile mirrored-file divergence before governance automation |

---

## Stories

| Story | Title | Priority | Size | Status |
|---|---|---|---|---|
| STORY-234 | Repair broken relative links and establish baseline report | P0 | L | 🔴 Open |
| STORY-235 | Eliminate placeholder token leakage in active docs | P1 | M | 🔴 Open |
| STORY-236 | Correct backlog registry/dashboard metric inconsistencies | P0 | M | 🔴 Open |
| STORY-237 | Reconcile mirrored drift and publish changelog of deltas | P1 | M | 🔴 Open |

---

## Architectural Requirements

- **REQ-1**: Link integrity checks must be deterministic and repeatable in CI.
- **REQ-2**: Active docs must be free of unresolved planning placeholders.
- **REQ-3**: Backlog metrics must be generated from a single calculation source.
- **REQ-4**: Mirror drift reconciliation must include auditability and change log evidence.

---

## Success Criteria

- Scoped broken relative links reduced to zero or explicitly allowlisted.
- Placeholder-token occurrences in active docs reduced to zero.
- Backlog dashboard metrics become single-source and reproducible.
- Drifted mirrored files reconciled with explicit disposition records.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This epic currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently schedule this epic, treat it as triage-required backlog inventory instead of self-startable work.

### Next Agent Action

- Reconcile this epic against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before selecting a story.
- Do not start implementation from this README alone unless the queue or a fresh planning decision activates the epic.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Prefer narrow, machine-checkable progress over broad narrative backlog churn.

### Minimum Verification For Future Agents

- If this epic is reactivated, update the queue or controlling planning artifact first.
- Then execute one story at a time with the relevant tests, gates, and generated references for the touched surface.
