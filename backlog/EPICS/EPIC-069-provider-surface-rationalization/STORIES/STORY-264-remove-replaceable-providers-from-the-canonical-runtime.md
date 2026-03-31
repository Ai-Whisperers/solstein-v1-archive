# STORY-264: Remove Replaceable Providers from the Canonical Runtime

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P0 - Ship Blocker |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-069 Provider Surface Rationalization |
| **Created** | 2026-03-31 |
| **Risk** | Medium |

---

## Problem Statement

`docs/quality-and-fixes/COMPREHENSIVE-UPDATE.md` already identifies replaceable provider surfaces, but the code still carries them in active paths. `src/solstein/research/graph/nodes/news_node.py` still uses Google Custom Search semantics, and the runtime still preserves legacy support for surfaces that should be narrowed before debugging quality.

## Acceptance Criteria

- [ ] The canonical legacy runtime no longer depends on deprecated or replaceable provider surfaces without explicit justification.
- [ ] Provider removals are reflected in registry construction and runtime docs.
- [ ] Tests prove the canonical path still works after provider reduction.
- [ ] Any retained exception is documented with cost/coverage rationale.

## Tasks

- [ ] Choose the canonical search/news/market-data surfaces.
- [ ] Remove deprecated providers from the runtime build path.
- [ ] Update tests and docs to match the new provider set.
