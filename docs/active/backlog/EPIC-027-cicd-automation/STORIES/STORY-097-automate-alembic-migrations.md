# STORY-097: Automate Alembic Migrations Pre-Deploy

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Critical |
| **Epic** | EPIC-027: CI/CD Automation |
| **Created** | 2026-03-01 |
| **Dependencies** | EPIC-002 (Configuration Management) |

## The Audit Verdict

> `scripts/apply_supabase_migrations.py` exists but is NOT called in any GitHub Actions workflow. Migration before deploy is a manual step.

## Problem Statement

Database migrations in production currently require a human to SSH into the server, run a script, and hope they remembered to do it before the new API version starts serving traffic. This is not a deployment strategy. It is a prayer with a terminal prompt.

Every deploy without automated migration is a potential schema mismatch between the API version and the database schema. The new API expects a column that doesn't exist yet. The old API references a table that was renamed in the migration that nobody ran. On a Supabase/PostgreSQL backend, schema drift isn't a theoretical concern — it's the gap between "deploy succeeded" and "deploy actually works."

The migration script exists. It's sitting right there in `scripts/apply_supabase_migrations.py`, dutifully waiting for someone to invoke it. Nobody does, because it's not in the workflow. The workflow deploys the API. The script migrates the database. They have never been formally introduced.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Reliability** | Schema mismatch on every deploy until a human notices and runs the migration manually. The window between deploy and migration is a production incident in progress. |
| **Operational** | Deploy requires a manual checklist: "Did you run migrations? Are you sure? Check again." This is a process that exists because automation doesn't. |
| **Developer Experience** | Developers must coordinate deploys with migration runs. Timezone differences, vacations, and the universal human tendency to forget make this coordination unreliable. |
| **Security** | N/A — no direct security impact, though a schema mismatch causing 500 errors could be mistaken for an attack. |

## Affected Files

| File | Issue |
|------|-------|
| `.github/workflows/` | No workflow step runs migrations before deploy |
| `scripts/apply_supabase_migrations.py` | Exists but is never called by CI/CD |
| `Makefile` | No `migrate` target (addressed in STORY-098) |

## Architectural Requirements

- A `migrate` step in the deploy GitHub Actions workflow that executes before the API service restarts
- The migration step must use a single canonical migration mechanism — either `alembic upgrade head` or `apply_supabase_migrations.py`, not both. Pick one, delete the ambiguity.
- Migration step must run in a one-off container or job with database connectivity, not inside the API container during startup
- Migration failure MUST block deploy — the workflow exits non-zero, the API is not restarted, the old version continues serving on the old schema
- Migration must be idempotent — running `alembic upgrade head` on an already-current database is a no-op, not an error
- `make migrate` Makefile target added for local development and CI parity (detailed in STORY-098)
- Migration step must emit structured logs: migration revision name, direction (upgrade/downgrade), duration in seconds
- Rollback procedure documented: `alembic downgrade -1` with explicit steps in a runbook, tested in staging before production use
- Migration timeout: if a migration takes longer than a configured threshold (default: 5 minutes), the step fails rather than hanging indefinitely

## Acceptance Criteria

- [ ] `make migrate` runs Alembic upgrade head successfully against a local database
- [ ] GitHub Actions deploy workflow runs migration step before API restart step
- [ ] Migration failure causes the workflow to exit non-zero and skips the deploy step entirely
- [ ] Running migration twice on the same database revision is a no-op — no error, no duplicate operations
- [ ] Migration logs include which revisions were applied, with timestamps and duration
- [ ] Rollback procedure documented in `docs/runbooks/migration-rollback.md`

## Definition of Done

- **Tests Required**: Integration test — deploy with a pending migration, verify schema is updated before traffic reaches the new API version. Test migration idempotency by running the same migration twice.
- **Documentation Required**: Runbook for migration rollback (`alembic downgrade -1`). Updated deploy documentation reflecting the automated migration step.
- **Code Review Gate**: Reviewer verifies that the migration step is ordered BEFORE the service restart step in the workflow YAML. Reviewer verifies that migration failure halts the workflow.

## Notes

There is a subtle but important decision here: should migration run as part of the API container startup (e.g., an entrypoint script that runs `alembic upgrade head` before starting uvicorn) or as a separate CI/CD job? The separate job is correct. Running migrations in the entrypoint means every replica runs migrations on startup, which means migration locking contention with multiple replicas, and a failed migration takes down the API container rather than just failing the deploy step. Migrations are a deploy-time concern, not a runtime concern.

The existing `scripts/apply_supabase_migrations.py` needs to be evaluated: does it do anything beyond `alembic upgrade head`? If it handles Supabase-specific concerns (connection pooling through pgbouncer, Supabase auth for the migration user), it may be the canonical path. If it's just a wrapper around Alembic with no added value, use Alembic directly and delete the wrapper.
