# STORY-414: Add quality-drift and source-outage alert policies

| Field | Value |
|-------|-------|
| **Epic** | EPIC-053 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 Not Started |
| **Dependencies** | STORY-413 |
| **Previous number** | Was STORY-203 — renumbered 2026-04-03 due to collision with EPIC-058 |

## Description

Add threshold-based alert policies that distinguish transient source failures from sustained quality drift. Alert on: source outage (>5 min), coverage drop > 20%, confidence degradation > 15%.

## Acceptance Criteria

- [ ] Alert fires within 15 minutes of source outage start
- [ ] Transient failures (< 5 min) do not trigger alerts
- [ ] Coverage drop alert threshold configurable per source
- [ ] Alerts distinguish outage vs degradation (different severity)
- [ ] Alert history queryable for post-incident review
