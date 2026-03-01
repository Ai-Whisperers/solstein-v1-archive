# STORY-094: Add Celery Beat Service to docker-compose

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Critical |
| **Epic** | EPIC-026: Service Topology |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-093 (worker service must exist for Beat to have something to dispatch to) |

## The Audit Verdict
> `docker-compose.yml` — no `beat` service. Beat scheduler for 12 periodic data collection tasks has no containerized home.

## Problem Statement

Without a Beat service in docker-compose, the 12 scheduled research tasks (SEC EDGAR daily, news hourly, GitHub every 6h, etc.) never execute on any schedule. The platform becomes read-only: it can query data but never refresh it. Every competitive intelligence insight is frozen at seed time.

Beat is a singleton — exactly one beat process must run per deployment. This is a critical constraint that Docker Compose does not enforce by default. Running Beat inside the worker container is a common anti-pattern that causes double-scheduling when workers scale horizontally. The correct pattern is a dedicated Beat service with `replicas: 1` enforced at the orchestration level.

Getting this wrong doesn't produce errors. It produces duplicate task dispatches, which produce duplicate data, which produce incorrect scores. The failure mode is data corruption, not a crash.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Reliability** | Zero scheduled data collection in containerized deployments — platform is read-only |
| **Operational** | Beat-inside-worker is a known duplicate-scheduling footgun when workers scale |
| **Data Integrity** | Duplicate Beat processes produce duplicate task dispatches and duplicate data writes |
| **Developer Experience** | Schedule testing requires running Beat separately — a step easily forgotten |

## Affected Files

| File | Issue |
|------|-------|
| `docker-compose.yml` | Missing `beat` service definition |

## Architectural Requirements
- A `beat` service in docker-compose using the same image as `api`
- Command override using the appropriate scheduler backend (file-based `celery.beat.PersistentScheduler` or database-backed `django_celery_beat.schedulers:DatabaseScheduler` — match whatever the codebase currently uses)
- Exactly ONE beat replica — this constraint must be documented in the compose file as a comment and enforced via `deploy.replicas: 1` in the production override
- `depends_on`: `db` (with health check condition), `redis` (with health check condition)
- Restart policy: `unless-stopped`
- Beat schedule state must be persisted (volume mount for file-based scheduler, or database table for DB scheduler) so restarts don't re-fire all tasks
- Beat PID file or distributed lock to prevent accidental duplicate starts (e.g., if someone runs `docker compose up --scale beat=2` by mistake)
- Beat log must show each task dispatch with timestamp and task arguments

## Acceptance Criteria
- [ ] `docker compose up` starts Beat and it fires scheduled tasks on their configured intervals
- [ ] Beat is a singleton — starting two beat containers produces a warning/error, not silent double-scheduling
- [ ] All 12 Beat schedule entries execute within their configured windows in a 24h test period
- [ ] Beat logs show each task dispatch with timestamp
- [ ] Beat schedule state survives container restart (no re-fire of all tasks on restart)

## Definition of Done
- **Tests Required**: 1-hour integration test: verify all tasks with ≤1h intervals fire exactly once. Singleton violation test: start two beat containers, verify one fails or warns.
- **Documentation Required**: Document the singleton constraint prominently. Document which scheduler backend is used and why.
- **Code Review Gate**: Reviewer verifies singleton constraint is enforced. Reviewer confirms schedule persistence mechanism.

## Notes
- The singleton constraint is the most important requirement. Everything else is standard compose configuration. If this constraint is violated, the platform silently produces duplicate data — a failure mode that is much harder to detect and fix than a crash.
- If the codebase uses file-based Beat scheduler, the schedule file (`celerybeat-schedule`) must be volume-mounted. If it uses the database scheduler, the corresponding tables must exist (covered by Alembic migrations).
- Consider adding a startup probe that verifies Beat successfully loaded all 12 schedule entries before reporting healthy.
