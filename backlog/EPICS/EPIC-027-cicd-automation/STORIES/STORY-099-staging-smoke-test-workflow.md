# STORY-099: Add Staging Deploy + Post-Deploy Smoke Test Workflow

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Critical |
| **Epic** | EPIC-027: CI/CD Automation |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-097 (Automate Alembic Migrations), EPIC-025 (Worker Reliability) |

## The Audit Verdict

> `.github/workflows/` — 7 workflows present (test, lint, coverage, secrets, SBOM, release). No staging deploy workflow, no post-deploy smoke test.

## Problem Statement

Code passes CI tests — unit tests, linting, type checking — and then deploys directly to production. There is no staging environment. There is no integration test against a real database after deploy. There is no smoke test to verify the API is actually responding. The first signal that a deploy broke something is a user complaint, a monitoring alert, or — worst case — silence, because the broken endpoint wasn't one anyone used that day.

For a PE/VC intelligence platform where managing partners rely on the data for investment decisions, "deploy and pray" is not a release strategy. It's a liability. The CI tests verify that the code is correct in isolation. They do not verify that the code works when connected to a real database, a real Redis instance, real LLM providers, and real external services. That verification happens in staging — or it happens in production, which is another way of saying it happens to your users.

The absence of staging creates a second-order problem: developers become afraid of deploying. When every deploy is a production deploy, developers batch changes into larger, riskier releases. Larger releases are harder to debug when they fail. This is a well-documented death spiral in deployment practice, and the fix is boring: add a staging environment, add smoke tests, gate production on staging success.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Reliability** | Broken deploys are caught by users, not by automation. Mean time to detection is "whenever someone notices," which can be hours or days for low-traffic endpoints. |
| **Operational** | No automatic rollback trigger. A broken deploy stays broken until a human intervenes. Weekend deploys are particularly exciting. |
| **Developer Experience** | Fear of deploying leads to change batching, which increases risk per deploy, which increases fear. The cycle feeds itself. |
| **Security** | N/A directly, though a broken deploy that fails open (returning 200 with no auth check) is a security incident discovered by audit, not by automation. |

## Affected Files

| File | Issue |
|------|-------|
| `.github/workflows/` | No `staging-deploy.yml` workflow exists |
| `.github/workflows/` | No post-deploy smoke test in any workflow |

## Architectural Requirements

- A `staging-deploy.yml` GitHub Actions workflow triggered on push to `staging` branch or manual dispatch (`workflow_dispatch`)
- Workflow stages executed in strict order:
  1. Build container image
  2. Push image to container registry (tag: `staging-<sha>`)
  3. Run Alembic migrations against staging database (STORY-097 dependency)
  4. Deploy to staging environment (swap image tag)
  5. Run smoke tests against staging API URL
  6. Notify result (success or failure)
- Smoke test suite (minimum):
  - `GET /health` returns HTTP 200
  - `GET /api/v1/companies` returns HTTP 200 with valid JSON
  - One authenticated endpoint returns HTTP 200 (not 401, not 500) — verifies auth middleware is functional
  - Database connectivity verified (the health endpoint should check this, but verify explicitly)
- Smoke test failure triggers automatic rollback to the previous image tag — the staging environment reverts to the last known-good version
- Staging environment is fully isolated: separate PostgreSQL database, separate Redis instance, separate API URL, separate environment variables. No shared state with production.
- Workflow emits a notification (Slack webhook or similar) on both success and failure, with links to the workflow run and deploy details. Notification implementation links to STORY-104.
- Production deploy workflow must gate on the staging smoke test having passed for the same commit SHA — a commit that hasn't been verified in staging cannot deploy to production
- Staging environment should have representative (but anonymized) data — not an empty database, not a copy of production

## Acceptance Criteria

- [ ] `staging-deploy.yml` workflow exists and triggers on push to `staging` branch
- [ ] Workflow runs migrations before deploying the new image
- [ ] Smoke test suite runs after deploy and verifies health, API, and auth endpoints
- [ ] Smoke test failure triggers automatic rollback to previous image tag
- [ ] Production deploy workflow rejects deploys for commit SHAs that haven't passed staging smoke tests
- [ ] Workflow sends notification on completion (success or failure) with workflow URL
- [ ] Staging and production environments share zero infrastructure (separate DB, separate Redis, separate URL)

## Definition of Done

- **Tests Required**: Deploy a deliberately breaking change to staging (e.g., a migration that renames a column the API reads). Verify: migration runs, deploy completes, smoke test fails, rollback triggers, notification fires. This is the happy path for failure — the system catches it before production.
- **Documentation Required**: Staging environment architecture documented (what's shared, what's isolated). Smoke test suite documented (what's tested, what's not, and why).
- **Code Review Gate**: Reviewer verifies staging and production environments are fully isolated (no shared database connection strings, no shared Redis instances). Reviewer verifies smoke test failure triggers rollback, not just a warning.

## Notes

The staging environment doesn't need to be a full replica of production. It needs to be similar enough that a deploy that works in staging will work in production. In practice, this means: same database engine and version, same Redis version, same container runtime, same environment variable structure. It does not need: production-scale data, production-scale compute, production-level monitoring (though basic monitoring is nice).

The smoke test suite should be minimal and fast. The goal is not to re-run the full test suite against staging — that's what CI already did. The goal is to verify that the deployed artifact actually starts, connects to its dependencies, and serves traffic. Five HTTP requests that return 200 in under 10 seconds. If the smoke tests take more than 30 seconds, they're too comprehensive for this purpose.

The rollback mechanism needs careful design. Options: revert the image tag to the previous value (simple, works for container deployments), or keep the old version running alongside the new one and switch traffic (blue-green, more complex but safer). Start with the simple approach; graduate to blue-green when the deployment volume justifies it.

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
