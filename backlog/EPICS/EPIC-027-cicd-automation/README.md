# EPIC-027: CI/CD Automation

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Created** | 2026-03-01 |
| **Stories** | STORY-097, STORY-098, STORY-099, STORY-100 |
| **Dependencies** | EPIC-002 (Configuration Management), EPIC-025 (Worker Reliability) |

## Context

Seven GitHub Actions workflows exist: test, lint, coverage, secrets scanning, SBOM generation, release. On paper, that looks like a CI/CD pipeline. In practice, it's a CI pipeline with a deploy-shaped hole in the middle.

**What's missing:**

- **Automated Alembic migrations before deploy.** `scripts/apply_supabase_migrations.py` exists — lonely, uncalled by any workflow. Migration before deploy is a manual step performed by whoever remembers to do it. On a Supabase/PostgreSQL backend, schema drift between API version and database schema is not a theoretical risk; it's a Tuesday.

- **Seed data pipeline.** No `make seed`, no seed workflow, no way for a new developer to get a working local environment without asking someone "which script do I run to get test data?"

- **Staging environment.** Code passes CI and deploys directly to production. The first integration test is performed by real users with real data. This is bold. It is not, however, wise.

- **Post-deploy smoke tests.** After deploy, the system's health is verified by the absence of complaints. If no one complains within an hour, the deploy is considered successful. This is the "no news is good news" school of operations.

- **Makefile gaps.** The Makefile has 20 targets. It is missing `migrate`, `seed`, and `deploy`. The three things a developer does most often after `make test`.

- **Root-level bypass scripts.** `run_research.py` and `run_market_pipeline.py` sit in the project root, calling the domain layer directly — bypassing the API, its middleware, its auth, its logging, and its rate limiting. These scripts exist because the API was painful to use, and instead of fixing the API, someone wrote a shortcut. That shortcut is now a "workflow."

## Scope

This epic addresses the deploy pipeline end-to-end: from Makefile developer ergonomics through staging deploys with smoke tests, to eliminating the bypass scripts that undermine the API's purpose.

## Stories

| Story | Title | Priority | Status |
|-------|-------|----------|--------|
| [STORY-097](STORIES/STORY-097-automate-alembic-migrations.md) | Automate Alembic Migrations Pre-Deploy | P1 | 🔴 Not Started |
| [STORY-098](STORIES/STORY-098-makefile-targets.md) | Add migrate, seed, deploy Makefile Targets | P1 | 🔴 Not Started |
| [STORY-099](STORIES/STORY-099-staging-smoke-test-workflow.md) | Add Staging Deploy + Post-Deploy Smoke Test Workflow | P1 | 🔴 Not Started |
| [STORY-100](STORIES/STORY-100-delete-bypass-scripts.md) | Delete Root Bypass Scripts | P1 | 🔴 Not Started |

## Dependency Graph

```
EPIC-002 (Config) ──┐
                     ├──► STORY-097 (Migrations) ──► STORY-099 (Staging Deploy)
EPIC-025 (Workers) ──┘         │
                               ▼
                         STORY-098 (Makefile Targets)
                               │
                               ▼
                         STORY-100 (Delete Bypass Scripts)
```

## Success Criteria

- A push to `staging` branch triggers: build → migrate → deploy → smoke test → notify
- A migration failure blocks deploy — the old version stays up
- `make migrate && make seed && make run` works from a clean checkout
- No Python scripts in project root that bypass the API
- New developer onboarding requires zero tribal knowledge beyond `make help`

## Risks

| Risk | Mitigation |
|------|------------|
| Migration failures in CI block all deploys | Rollback procedure documented; `alembic downgrade -1` tested |
| Staging environment cost | Use minimal instance sizes; tear down on inactivity |
| Bypass script removal breaks existing workflows | Migration guide provided; CLI restructured to use API |
| Team resistance to removing "convenient" scripts | Demonstrate API-based CLI is equally convenient, with audit trail |

## Notes

The bypass scripts (`run_research.py`, `run_market_pipeline.py`) are a symptom, not a cause. They exist because the API was insufficient for operational workflows. STORY-100 must not just delete the scripts — it must ensure the API covers every operation those scripts performed. Deleting the crutch before fixing the leg is not progress.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This epic currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently schedule this epic, treat it as triage-required backlog inventory instead of self-startable work.

### Next Agent Action

- Reconcile this epic against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before selecting a story.
- Do not start implementation from this README alone unless the queue or a fresh planning decision activates the epic.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Prefer narrow, machine-checkable progress over broad narrative backlog churn.

### Minimum Verification For Future Agents

- If this epic is reactivated, update the queue or controlling planning artifact first.
- Then execute one story at a time with the relevant tests, gates, and generated references for the touched surface.
