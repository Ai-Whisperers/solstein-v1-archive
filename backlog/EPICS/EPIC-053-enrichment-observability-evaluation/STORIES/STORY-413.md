# STORY-413: Add enrichment KPI instrumentation and dashboards

| Field | Value |
|-------|-------|
| **Epic** | EPIC-053 |
| **Priority** | P1 |
| **Size** | M |
| **Status** | 🔴 Not Started |
| **Dependencies** | EPIC-014 (Observability), EPIC-052 (Quality Gates) |
| **Previous number** | Was STORY-202 — renumbered 2026-04-03 due to collision with EPIC-058 |

## Description

Add enrichment quality KPI instrumentation to emit batch-level metrics for coverage, freshness, confidence, and source health. Dashboard available within 5 minutes of enrichment batch completion.

## Acceptance Criteria

- [ ] Metrics emitted per batch: field_coverage_pct, avg_confidence, source_failure_rate, batch_duration
- [ ] Metrics accessible via monitoring dashboard
- [ ] Historical trend data retained for 90 days
- [ ] Dashboard shows per-source breakdown
- [ ] Unit tests for metric emission logic
