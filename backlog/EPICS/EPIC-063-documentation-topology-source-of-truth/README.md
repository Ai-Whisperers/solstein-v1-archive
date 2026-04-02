# EPIC-063: Documentation Topology and Source-of-Truth Governance

> **Priority**: P1 - High
> **Stories**: 4 (STORY-230 through STORY-233)
> **Effort**: L (2-3 weeks)
> **Dependencies**: EPIC-043 (Repository Cleanup and Organization)
> **Status**: 🔴 Not Started

---

## Problem

The documentation system currently operates with duplicated backlog trees and partial drift between mirrored files.
This creates conflicting references and unclear ownership.

Audit evidence:

- 229 mirrored markdown files between `docs/active/backlog` and `backlog/EPICS`
- 3 mirrored files with drift
- unclear canonical owner for epic/story planning artifacts

---

## Scope

| Category | Action |
|---|---|
| Topology | Define canonical documentation tree and ownership model |
| Source-of-Truth | Standardize backlog epic/story canonical location |
| Migration Planning | Plan deterministic move/sync behavior for mirrored content |
| Governance | Add explicit rules for where new planning docs are authored |

---

## Stories

| Story | Title | Priority | Size | Status |
|---|---|---|---|---|
| STORY-230 | Define canonical docs topology and ownership matrix | P1 | M | 🔴 Open |
| STORY-231 | Resolve mirrored backlog trees with one-way sync/migration plan | P1 | L | 🔴 Open |
| STORY-232 | Normalize epic directory naming and remove topology anomalies | P1 | M | 🔴 Open |
| STORY-233 | Establish archival/deprecation metadata policy for docs | P2 | M | 🔴 Open |

---

## Target Integration Points

- `docs/`
- `docs/active/backlog/`
- `backlog/EPICS/`
- `docs/DOCUMENTATION_INDEX.md`
- `docs/ORGANIZATION_SUMMARY.md`

---

## Architectural Requirements

- **REQ-1**: Exactly one canonical source-of-truth must exist for epic/story markdown artifacts.
- **REQ-2**: Documentation ownership must be explicit at directory level.
- **REQ-3**: Any mirror or migration flow must be deterministic and scriptable.
- **REQ-4**: Deprecated docs must include status metadata and successor references.

---

## Success Criteria

- Canonical docs topology document approved and published.
- Source-of-truth rule enforced for all newly created epic/story docs.
- All topology anomalies have an explicit migration disposition (keep, move, archive).
- Deprecation metadata standard adopted and documented.

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
