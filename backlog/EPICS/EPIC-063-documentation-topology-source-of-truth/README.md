# EPIC-063: Documentation Topology and Source-of-Truth Governance

> **Priority**: P1 - High
> **Stories**: 4 ([STORY-230](STORIES/STORY-230-canonical-docs-topology-ownership-matrix.md) through [STORY-233](STORIES/STORY-233-archival-and-deprecation-metadata-policy.md))
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
| [STORY-230](STORIES/STORY-230-canonical-docs-topology-ownership-matrix.md) | Define canonical docs topology and ownership matrix | P1 | M | 🔴 Open |
| [STORY-231](STORIES/STORY-231-resolve-mirrored-backlog-trees.md) | Resolve mirrored backlog trees with one-way sync/migration plan | P1 | L | 🔴 Open |
| [STORY-232](STORIES/STORY-232-normalize-epic-directory-naming.md) | Normalize epic directory naming and remove topology anomalies | P1 | M | 🔴 Open |
| [STORY-233](STORIES/STORY-233-archival-and-deprecation-metadata-policy.md) | Establish archival/deprecation metadata policy for docs | P2 | M | 🔴 Open |

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
