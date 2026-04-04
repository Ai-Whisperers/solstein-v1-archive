# EPIC-064: Markdown Integrity and Registry Correctness

> **Priority**: P0 - Ship Blocker
> **Stories**: 4 ([STORY-234](STORIES/STORY-234-repair-broken-relative-links.md) through [STORY-237](STORIES/STORY-237-reconcile-mirrored-drift-with-changelog.md))
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
| [STORY-234](STORIES/STORY-234-repair-broken-relative-links.md) | Repair broken relative links and establish baseline report | P0 | L | 🔴 Open |
| [STORY-235](STORIES/STORY-235-remove-placeholder-token-leakage.md) | Eliminate placeholder token leakage in active docs | P1 | M | 🔴 Open |
| [STORY-236](STORIES/STORY-236-correct-backlog-dashboard-metrics.md) | Correct backlog registry/dashboard metric inconsistencies | P0 | M | 🔴 Open |
| [STORY-237](STORIES/STORY-237-reconcile-mirrored-drift-with-changelog.md) | Reconcile mirrored drift and publish changelog of deltas | P1 | M | 🔴 Open |

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
