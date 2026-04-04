# STORY-415: Add scheduled evaluation harness for real-data benchmark set

| Field | Value |
|-------|-------|
| **Epic** | EPIC-053 |
| **Priority** | P1 |
| **Size** | M |
| **Status** | 🔴 Not Started |
| **Dependencies** | STORY-413 |
| **Previous number** | Was STORY-204 — renumbered 2026-04-03 due to collision with EPIC-058 |

## Description

Add a scheduled evaluation harness that runs weekly enrichment + scoring against a fixed real-company benchmark set. Output: weekly evaluation report with trend lines for coverage, confidence, and classification stability.

## Acceptance Criteria

- [ ] Benchmark set: 20+ real companies with known ground truth
- [ ] Harness runs weekly via Celery Beat
- [ ] Output: coverage trend, confidence trend, classification stability report
- [ ] Results stored with version history for comparison
- [ ] Tests use mocked enrichment to verify evaluation logic
