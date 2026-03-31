# STORY-265: Collapse Duplicate Adapter Pairs and Placeholder Services

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

The repo still contains paired provider implementations (`news` and `news_unified`, `funding` and `funding_unified`, `website` and `website_unified`, plus similar families) while `src/solstein/adapters/registry.py` branches between them via `feature_new_unified_loader` and `src/solstein/data/enrichment_service.py` preserves placeholder SEC, Companies House, and News provider methods. This keeps the team fixing wrappers instead of fixing the real surface.

## Acceptance Criteria

- [ ] Each provider capability has one canonical implementation in the active runtime.
- [ ] Placeholder provider methods are removed from active paths.
- [ ] Duplicate adapter pairs are either merged or explicitly retired.
- [ ] Contract tests cover the surviving canonical implementations.
- [ ] Orphan or unwired provider objects are inventoried and either retired or marked non-runtime.
- [ ] The implementation records before/after file counts and LOC for each collapsed family.
- [ ] The collapse plan names every feature flag, alias, and placeholder method currently keeping both provider families alive.

## Tasks

- [ ] Inventory duplicate provider families.
- [ ] Inventory orphan and unwired provider objects in the same families.
- [ ] Choose the canonical implementation per family.
- [ ] Remove placeholders from the active runtime.
- [ ] Record measured file/LOC reduction after collapse.
- [ ] Document how `build_default_registry()` changes source selection today and what code disappears once one family is canonical.
