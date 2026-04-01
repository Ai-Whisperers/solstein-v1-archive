# STORY-200: Quality Gate Before Scoring and Export

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P0 - Ship Blocker |
| **Size** | L (5-8 days) |
| **Epic** | EPIC-052 Provenance, Confidence, Quality Gates |
| **Created** | 2026-04-01 |

## Problem Statement
The scoring engine and export pipeline accept any data regardless of quality. Low-confidence or unprovenanced data silently influences classifications.

## Acceptance Criteria
- [ ] Quality gate check runs before scoring: rejects companies with <50% field coverage
- [ ] Quality gate check runs before export: flags low-confidence classifications
- [ ] Gate results are logged with specific reasons for rejection/flagging
- [ ] Existing `ReportReleaseGate` is extended (not replaced)
- [ ] Tests: gate blocks bad data, passes good data, logs reasons
