# STORY-292: Register all new enrichment adapters in build_default_registry()

| Field | Value |
|-------|-------|
| **Epic** | EPIC-073 |
| **Priority** | P1 |
| **Size** | XS |
| **Status** | 🔴 READY |
| **Dependencies** | STORY-287, STORY-288, STORY-289, STORY-290, STORY-291 |

## Description

Register all 5 new enrichment adapters (SearXNG, GDELT, SEC EDGAR, GitHub, arXiv/patent) in the `build_default_registry()` function so they are used in pipeline enrichment runs.

## Acceptance Criteria

- [ ] All 5 adapters registered in `build_default_registry()`
- [ ] Adapters registered with appropriate priority/weight
- [ ] Registry test confirms all adapters are discoverable
- [ ] No circular imports introduced
