# STORY-239: Add Stale-Doc Detection and Ownership Alerts

| Field | Value |
|---|---|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-065 Documentation Lifecycle Automation and CI Enforcement |
| **Created** | 2026-03-11 |
| **Risk** | Low |

---

## Problem Statement

Stale documentation is not systematically identified, escalated, or reviewed.

## Acceptance Criteria

- [ ] Staleness policy is defined by document class and review interval.
- [ ] Automated stale-doc detector emits actionable report.
- [ ] Ownership mapping is used to route notifications.
- [ ] Escalation path exists for unowned documents.
- [ ] Exceptions to staleness policy use the same `owner`, `rationale`, and `expiry` model used in STORY-234 and STORY-238.

## Definition of Done

- [ ] Weekly stale-doc report is generated and stored.
- [ ] Alert routing is verified for at least one stale-doc scenario.
