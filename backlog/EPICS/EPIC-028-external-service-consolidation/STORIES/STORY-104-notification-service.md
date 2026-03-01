# STORY-104: Add Slack and Email Notification Service

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | Medium |
| **Epic** | EPIC-028: External Service Consolidation |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Audit Verdict

> Zero email, Slack, or webhook integration exists anywhere in the codebase. Research jobs complete silently. Users have no way to know when a 10-minute research pipeline finishes or fails.

## Problem Statement

A research pipeline that takes 5-15 minutes to complete and reports its result only via API polling is a product that users don't trust. They poll, get PENDING, stop polling, assume it failed, and run it again. The absence of a notification layer is not just an inconvenience — it's a source of duplicate work, user frustration, and wasted LLM costs from re-triggered pipelines. The fix is a notification service that fires on research completion, research failure, DLQ accumulation, and scheduled source degradation.

## Impact

| Dimension | Impact |
|-----------|--------|
| **User Experience** | Users unaware of job completion |
| **Operational** | No alerting on system failures |
| **Cost** | Duplicate pipeline runs from impatient re-triggers |

## Affected Files

| File | Issue |
|------|-------|
| New: `src/solstein/notifications/` | Does not exist |
| `src/solstein/worker_tasks.py` | No notification hooks |

## Architectural Requirements

- Notification service abstraction: `NotificationChannel` interface with `send(event, payload)` method
- Slack implementation: webhook-based, configurable per-tenant webhook URL, message templated per event type
- Email implementation: SMTP or Sendgrid, configurable sender, HTML template per event type
- Event types: `research.completed`, `research.failed`, `source.degraded`, `dlq.threshold_exceeded`, `export.ready`
- Per-user notification preferences (opt-in per event type) stored in PostgreSQL
- Notification delivery is async (Celery task) — never blocks research pipeline
- Notification failures do NOT propagate to the triggering operation (fire-and-forget)
- Retry: 3 attempts on notification delivery failure, then log and abandon (not DLQ'd — notifications are best-effort)

## Acceptance Criteria

- [ ] Slack message sent on research job completion with company name, duration, and score summary
- [ ] Email sent on research job failure with error summary and retry link
- [ ] Notification delivery is async — pipeline completion latency is unchanged
- [ ] Notification failure does not fail the research pipeline
- [ ] Per-user preferences respected (opted-out users receive no notifications)

## Definition of Done

- **Tests Required**: Integration test: trigger research job, verify Slack message arrives
- **Documentation Required**: Notification configuration guide
- **Code Review Gate**: Reviewer verifies notification dispatch is async and failure is non-propagating

## Notes

Users need to know when their jobs complete.
