# STORY-093: Add Celery Worker Service to docker-compose

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Critical |
| **Epic** | EPIC-026: Service Topology |
| **Created** | 2026-03-01 |
| **Dependencies** | EPIC-025 (Worker Reliability) — workers should be hardened before containerizing |

## The Audit Verdict
> `docker-compose.yml` — defines `api`, `db`, `redis` only. No `worker` service. Workers started manually via `scripts/services/start_celery_workers.sh --concurrency=4`.

## Problem Statement

In any containerized or cloud deployment, the Celery worker does not run. The research pipeline — the entire point of the platform — never executes. The shell script exists for local development convenience and has been mistaken for a production deployment strategy.

This is the infrastructure equivalent of commenting out your main function. The API starts, health checks pass, monitoring shows green — and exactly zero data collection happens. The platform serves stale data with complete confidence, and nobody is the wiser until someone notices the SEC EDGAR data is three weeks old.

The fix is not complex: add a `worker` service to docker-compose that uses the same image as the API but overrides the command. This is day-one Docker Compose knowledge, but nobody did it.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Reliability** | Zero async task execution in any containerized deployment — total research pipeline failure |
| **Operational** | Platform appears healthy (API responds, health checks pass) while silently doing nothing useful |
| **Data Integrity** | All data is stale; freshness guarantees are completely unmet |
| **Developer Experience** | Works locally (shell script), fails silently in Docker — the worst class of environment-specific bug |

## Affected Files

| File | Issue |
|------|-------|
| `docker-compose.yml` | Missing `worker` service definition |
| `scripts/services/start_celery_workers.sh` | Shell script used as workaround; not viable for containerized deployments |

## Architectural Requirements
- A `worker` service in docker-compose using the same image as `api`
- Command override: `celery -A solstein.celery_app worker --loglevel=info --concurrency=4 -Q default,scoring,export,enrichment`
- All environment variables inherited from a shared `env_file` or `environment` block (DRY — no duplication with api service)
- `depends_on`: `db` (with health check condition), `redis` (with health check condition)
- Health check: `celery -A solstein.celery_app inspect ping` with appropriate interval, timeout, and retries
- Restart policy: `unless-stopped`
- Separate log stream from api service (distinct container name enables log filtering)
- Production compose override (`docker-compose.prod.yml`) documents `replicas: 2` scale-out pattern
- Worker memory limit should be set to prevent OOM from consuming host resources

## Acceptance Criteria
- [ ] `docker compose up` starts a working Celery worker without manual shell script
- [ ] Worker connects to Redis broker and processes tasks from all 4 queues (default, scoring, export, enrichment)
- [ ] Worker health check passes within 30s of container start
- [ ] Worker logs are separated from API logs (distinct container name)
- [ ] `start_celery_workers.sh` is updated with a header comment noting it is for local dev only, not production

## Definition of Done
- **Tests Required**: Integration test: `docker compose up`, enqueue a test task via API, verify task completes and result is written to PostgreSQL.
- **Documentation Required**: Update deployment README with the new service topology. Document the queue assignment strategy.
- **Code Review Gate**: Reviewer verifies all 4 queues are registered in the worker command. Reviewer confirms environment variable sharing pattern avoids duplication.

## Notes
- The worker service must use the same image as `api` — do not create a separate Dockerfile. The command override is the only differentiator. This is critical for STORY-096 (multi-stage Dockerfile).
- Queue names (`default`, `scoring`, `export`, `enrichment`) must match the queue routing configuration in `celery_config.py`. If they don't match, tasks will be enqueued to queues that no worker is listening on.
- Consider adding a `worker_send_task_events = True` config to enable Flower monitoring (STORY-095) from day one.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This story currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently list this story as active work, treat it as triage-required rather than immediately actionable.

### Next Agent Action

- Reconcile this story against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before starting.
- Do not begin implementation from this file alone unless the queue or a fresh planning decision reactivates it.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Preserve machine-checkable enforcement and avoid prose-only or speculative "AI slop" updates.

### Minimum Verification For Future Agents

- If this story is reactivated, update the queue or controlling planning artifact first.
- Then prove the work with the smallest relevant regression tests, gates, or generated artifacts for the touched boundary.
