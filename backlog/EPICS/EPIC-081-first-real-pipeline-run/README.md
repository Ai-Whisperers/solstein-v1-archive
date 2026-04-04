# EPIC-081: First Real Pipeline Run for ENEVE

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 — Phase P4: End-to-End |
| **Phase** | P4 — End-to-End Pipeline Execution |
| **Created** | 2026-04-01 |

## Context

All previous epics lay the groundwork. This epic executes the first real pipeline run for ENEVE's Dutch Energy market, validates that each stage produces real output, and saves a golden run as a regression baseline. All stories in this epic are blocked by Phase P1-P3 completion.

## Stories

| Story | Title | Status | Notes |
|-------|-------|--------|-------|
| [STORY-324](STORIES/STORY-324.md) | Execute discovery stage: verify 20+ companies discovered with metadata | ⏳ BLOCKED | Deps: STORY-277, 273, 287 |
| [STORY-325](STORIES/STORY-325.md) | Execute gather stage: verify 15+ companies enriched with financial data | ⏳ BLOCKED | Deps: STORY-282-286, STORY-324 |
| [STORY-326](STORIES/STORY-326.md) | Execute scoring stage: verify composite scores in 2.0-9.0 range (no zeros) | ⏳ BLOCKED | Deps: STORY-298-302, STORY-325 |
| [STORY-327](STORIES/STORY-327.md) | Execute analysis stage: verify LLM insights are real (not templates) | ⏳ BLOCKED | Deps: STORY-321, STORY-326 |
| [STORY-328](STORIES/STORY-328.md) | Execute export stage: generate Excel + PDF with complete landscape | ⏳ BLOCKED | Deps: STORY-327 |
| [STORY-329](STORIES/STORY-329.md) | Validate: at least 3 Phoenix, 10 Salt, 5 Lead in results | ⏳ BLOCKED | Deps: STORY-328 |
| [STORY-330](STORIES/STORY-330.md) | Save golden run results as regression baseline for future runs | ⏳ BLOCKED | Deps: STORY-329 |

## Success Criteria

- 20+ companies discovered in Dutch Energy market
- 15+ companies enriched with financial data from real sources
- Composite scores in 2.0-9.0 range (no zeros or near-zeros)
- LLM analysis produces real insights (not templates)
- Excel + PDF export complete and readable
- At least 3 Phoenix, 10 Salt, 5 Lead classifications
- Golden run saved as regression baseline

## Dependencies

- EPIC-071 (market catalog data)
- EPIC-072-074 (adapter resilience + connectors + validation)
- EPIC-075-077 (scoring accuracy)
- EPIC-078-080 (infrastructure + LLM)
