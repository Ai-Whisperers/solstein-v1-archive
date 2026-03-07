# STORY-087: Implement Celery Dead Letter Queue and Retry Policy

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | HIGH |
| Epic | [EPIC-018: Infrastructure-as-Code & CI/CD](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-015](../../EPIC-004-architecture-cleanup/STORIES/STORY-015-single-worker-tasks-file.md) (single worker tasks file) |

---

## The Audit Verdict

> Celery background jobs have no dead letter queue. A failed research job is retried according to default Celery retry behaviour, then silently dropped if all retries are exhausted. There is no queue for inspecting failed jobs, no alerting on job failure, and no mechanism to requeue a failed job after the underlying cause is fixed.

## Problem Statement

In a research platform where each job represents hours of enrichment work and potentially billable computation, silently dropping failed jobs is unacceptable. Failed jobs must be inspectable, re-queueable, and alertable.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Reliability** | Failed research jobs are silently lost — no operator visibility into job failures |
| **Business** | Billable computation is wasted when failed jobs cannot be retried after root cause is fixed |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/worker_tasks.py` (canonical after STORY-015) | Modify | Add retry policies and DLQ routing |
| Celery configuration | Modify | Add dead letter queue (DLQ) definition |
| New job management endpoint | Add | Ability to inspect and requeue failed jobs |

## Architectural Requirements

*What — never how. No code.*

- **REQ-1**: A dead letter queue must be defined — failed jobs that exhaust retries must land in the DLQ, not be silently dropped
- **REQ-2**: Each task must have an explicit retry policy: maximum retry count, backoff interval (exponential with jitter), and retry-eligible exception types
- **REQ-3**: DLQ depth must be exposed as a Prometheus metric (integrates with STORY-051)
- **REQ-4**: An administrative endpoint must allow operators to: list DLQ jobs, inspect job payloads and failure reasons, and requeue selected jobs
- **REQ-5**: A DLQ job count exceeding a configurable threshold must trigger an alert (integrate with alerting from STORY-051)

## Acceptance Criteria

- [ ] A permanently-failing job lands in the DLQ after exhausting retries
- [ ] The DLQ is queryable and shows job payload + failure reason
- [ ] A DLQ job can be requeued without code deployment
- [ ] DLQ depth is a Prometheus metric

## Definition of Done

**Tests Required:**
- [ ] Integration test: job that always fails lands in DLQ after N retries
- [ ] Integration test: requeue from DLQ re-runs the job
- [ ] Metric test: DLQ depth metric increments correctly

**Documentation Required:**
- [ ] DLQ architecture documented
- [ ] Operator runbook for DLQ inspection and requeue procedures

**Code Review Gate:**
- [ ] Reviewer confirms no task silently drops after exhausting retries
- [ ] Reviewer confirms retry policies use exponential backoff with jitter

## Notes

This story addresses a silent failure mode that is invisible until a client asks "where is my research?" and the answer is "it failed three days ago and nobody noticed." The DLQ makes failure visible, inspectable, and recoverable — which is the minimum bar for a platform handling paid research operations.
