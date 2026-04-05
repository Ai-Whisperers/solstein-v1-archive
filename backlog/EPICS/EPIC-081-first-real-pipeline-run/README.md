# EPIC-081: First Real Pipeline Run for ENEVE

| Field | Value |
|-------|-------|
| **Status** | ⏳ Blocked |
| **Priority** | P1 |
| **Phase** | P4 — End-to-End Pipeline Execution |
| **Effort** | L (1–2 weeks) |
| **Stories** | 7 ([STORY-324](STORIES/STORY-324.md) through [STORY-330](STORIES/STORY-330.md)) |
| **Created** | 2026-04-01 |
| **Updated** | 2026-04-05 (added metadata, explicit BLOCKED state, DoD) |

## Context

All previous epics lay the groundwork. This epic executes the first real pipeline run for ENEVE's Dutch Energy market, validates that each stage produces real output, and saves a golden run as a regression baseline.

> ⚠️ **All stories BLOCKED** until the following epics complete:
> - Phase P1: [EPIC-071](../EPIC-071-enrich-market-catalog-real-data/README.md) + [EPIC-072](../EPIC-072-enrichment-adapter-resilience/README.md) + [EPIC-073](../EPIC-073-wire-connectors-into-pipeline/README.md) + [EPIC-074](../EPIC-074-revenue-financial-data-validation/README.md)
> - Phase P2: [EPIC-075](../EPIC-075-fix-scoring-missing-data/README.md) + [EPIC-076](../EPIC-076-capability-overlap-enhancement/README.md) + [EPIC-077](../EPIC-077-ai-maturity-scoring-enhancement/README.md)
> - Phase P3: [EPIC-078](../EPIC-078-deploy-core-infrastructure/README.md) + [EPIC-079](../EPIC-079-deploy-application-stack/README.md) + [EPIC-080](../EPIC-080-configure-llm-providers/README.md)

## Stories

| Story | Title | Status | Notes |
|-------|-------|--------|-------|
| [STORY-324](STORIES/STORY-324.md) | Execute discovery stage: verify 20+ companies discovered with metadata | ⏳ BLOCKED | Deps: EPIC-071, EPIC-073, STORY-287 |
| [STORY-325](STORIES/STORY-325.md) | Execute gather stage: verify 15+ companies enriched with financial data | ⏳ BLOCKED | Deps: EPIC-072, [STORY-324](STORIES/STORY-324.md) |
| [STORY-326](STORIES/STORY-326.md) | Execute scoring stage: verify composite scores in 2.0-9.0 range (no zeros) | ⏳ BLOCKED | Deps: EPIC-075, [STORY-325](STORIES/STORY-325.md) |
| [STORY-327](STORIES/STORY-327.md) | Execute analysis stage: verify LLM insights are real (not templates) | ⏳ BLOCKED | Deps: EPIC-080, [STORY-326](STORIES/STORY-326.md) |
| [STORY-328](STORIES/STORY-328.md) | Execute export stage: generate Excel + PDF with complete landscape | ⏳ BLOCKED | Deps: [STORY-327](STORIES/STORY-327.md) |
| [STORY-329](STORIES/STORY-329.md) | Validate: at least 3 Phoenix, 10 Salt, 5 Lead in results | ⏳ BLOCKED | Deps: [STORY-328](STORIES/STORY-328.md) |
| [STORY-330](STORIES/STORY-330.md) | Save golden run results as regression baseline for future runs | ⏳ BLOCKED | Deps: [STORY-329](STORIES/STORY-329.md) |

## Success Criteria

- 20+ companies discovered in Dutch Energy market
- 15+ companies enriched with financial data from real sources
- Composite scores in 2.0-9.0 range (no zeros or near-zeros)
- LLM analysis produces real insights (not templates)
- Excel + PDF export complete and readable
- At least 3 Phoenix, 10 Salt, 5 Lead classifications
- Golden run saved as regression baseline

## Definition of Done

- [ ] [STORY-324](STORIES/STORY-324.md): discovery log shows ≥ 20 companies with `website` populated
- [ ] [STORY-325](STORIES/STORY-325.md): ≥ 15 companies have non-null `revenue` or `employees` after gather
- [ ] [STORY-326](STORIES/STORY-326.md): all composite scores in 2.0–9.0 range; zero scores = 0
- [ ] [STORY-327](STORIES/STORY-327.md): LLM analysis output ≠ "No description available"
- [ ] [STORY-328](STORIES/STORY-328.md): Excel and PDF export files exist and are non-empty
- [ ] [STORY-329](STORIES/STORY-329.md): classification breakdown has ≥ 3 Phoenix, ≥ 10 Salt, ≥ 5 Lead
- [ ] [STORY-330](STORIES/STORY-330.md): golden run saved to `tests/golden_runs/` as regression baseline

## Dependencies

- [EPIC-071](../EPIC-071-enrich-market-catalog-real-data/README.md) through [EPIC-080](../EPIC-080-configure-llm-providers/README.md) must all be complete
