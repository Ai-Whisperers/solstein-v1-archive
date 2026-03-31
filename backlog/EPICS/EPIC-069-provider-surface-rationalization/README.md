# EPIC-069: Provider Surface Rationalization

> **Priority**: P0 - Ship Blocker
> **Stories**: 4 (STORY-263 through STORY-266)
> **Effort**: L (2-3 weeks)
> **Dependencies**: EPIC-067 (Legacy Runtime Canonicalization), EPIC-068 (Boundary Schemas and Type Gates)
> **Status**: 🔴 Not Started

---

## Problem

Provider integration surfaces are fragmented across duplicate adapters, placeholder services, and contradictory strategic direction:

- `src/solstein/adapters/registry.py` still branches between unified and legacy enrichment stacks.
- Duplicate or paired adapters remain under `src/solstein/adapters/enrichment/` (`news.py` / `news_unified.py`, `funding.py` / `funding_unified.py`, `website.py` / `website_unified.py`, and peers).
- `src/solstein/research/graph/nodes/news_node.py` still centers Google Custom Search despite the consolidation direction in `docs/quality-and-fixes/COMPREHENSIVE-UPDATE.md`.
- `src/solstein/data/enrichment_service.py` still contains placeholder provider methods.

Until there is one canonical provider surface per capability, debugging source quality is guesswork.

---

## Scope

| Category | Action |
|---|---|
| Provider Matrix | Define canonical provider ownership, retry rules, TTL, ID semantics, and confidence semantics |
| Surface Reduction | Choose one canonical provider per capability in the legacy runtime |
| Placeholder and Orphan Removal | Remove provider placeholders and unwired/orphan provider objects from active code paths |
| Duplication Reduction | Measure and reduce file/LOC bloat caused by duplicate adapter families |
| Compatibility Ban | Delete compatibility wrappers at provider boundaries in ranked waves |

---

## Stories

| Story | Title | Priority | Size | Status |
|---|---|---|---|---|
| [STORY-263](STORIES/STORY-263-build-provider-scorecard-and-enforcement-matrix.md) | Build provider scorecard and enforcement matrix | P0 | M | 🔴 Open |
| [STORY-264](STORIES/STORY-264-remove-replaceable-providers-from-the-canonical-runtime.md) | Remove replaceable providers from the canonical runtime | P0 | M | 🔴 Open |
| [STORY-265](STORIES/STORY-265-collapse-duplicate-adapter-pairs-and-placeholder-services.md) | Collapse duplicate adapter pairs and placeholder services | P0 | M | 🔴 Open |
| [STORY-266](STORIES/STORY-266-ban-new-compatibility-patches-at-provider-boundaries.md) | Ban new compatibility patches at provider boundaries | P1 | M | 🔴 Open |

---

## Architectural Requirements

- **REQ-1**: Every external capability must have one canonical provider surface in the legacy runtime.
- **REQ-2**: Every provider must expose explicit ownership, retry class, cache TTL, identifier rules, and confidence semantics.
- **REQ-3**: Placeholder or unwired provider behavior may not remain in the canonical path.
- **REQ-4**: Duplicate provider families must report measured before/after file and LOC counts when collapsed.
- **REQ-5**: New provider additions must not introduce compatibility wrappers by default.

---

## Success Criteria

- A single provider scorecard exists and is used in implementation decisions.
- Replaceable or deprecated providers are removed from the canonical runtime path.
- Duplicate adapter families are collapsed to one canonical implementation per surface with measured file/LOC reduction.
- Orphan or unwired provider surfaces are either retired or explicitly documented as non-runtime inventory.
- Compatibility wrappers stop expanding at provider/API boundaries.
