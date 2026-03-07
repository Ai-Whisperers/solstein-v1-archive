# STORY-098: Add migrate, seed, deploy Makefile Targets

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Medium |
| **Epic** | EPIC-027: CI/CD Automation |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-097 (Automate Alembic Migrations) |

## The Audit Verdict

> `Makefile` has 20 targets. Missing: `migrate`, `seed`, `deploy`. Developer onboarding requires reading scripts and documentation to discover manual steps that should be single commands.

## Problem Statement

The Makefile is the developer's contract with the project. It's the first thing an experienced developer reads when joining a codebase, and the answers it gives shape their mental model of how the project works. When `make migrate` doesn't exist, a developer has two options: grep the codebase for migration commands (ambitious), or ask a colleague (fragile, undocumented, scales to exactly one timezone).

The same problem applies to seed data. Somewhere in the `scripts/` directory, there are seed scripts. They're not in the Makefile, so they're not discoverable. New developers either don't know they exist, run them incorrectly, or skip them entirely and work with an empty database — which produces a subtly different development experience than what production looks like. Every bug that exists only on an empty database and not in production is a waste of everyone's time.

The Makefile currently says: "You can test, lint, and format." It does not say: "You can migrate, seed, and deploy." A reasonable developer would conclude that migration, seeding, and deployment are someone else's problem. They are not. They are everyone's problem. The Makefile should make that obvious.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Reliability** | Inconsistent local environments lead to "works on my machine" bugs that don't reproduce because developer A seeded and developer B didn't. |
| **Operational** | Manual steps that should be automated remain invisible. The gap between "how CI deploys" and "how a developer runs locally" grows with every undocumented step. |
| **Developer Experience** | Onboarding friction. A new team member's first day should not involve a scavenger hunt through `scripts/` to figure out how to get a working database. |
| **Security** | N/A |

## Affected Files

| File | Issue |
|------|-------|
| `Makefile` | Missing `migrate`, `migrate-down`, `seed`, `seed-test`, `deploy`, `check-migrations` targets |

## Architectural Requirements

- `make migrate` — runs `alembic upgrade head`, reads `DATABASE_URL` from environment, fails loudly with a descriptive error if the database is unreachable (not a cryptic `sqlalchemy.exc.OperationalError` traceback)
- `make migrate-down` — runs `alembic downgrade -1`, requires explicit confirmation prompt when run interactively (not in CI), because downgrading a production database should involve at least one moment of deliberate intent
- `make seed` — runs the seed data pipeline, idempotent by design (running it twice does not create duplicate records), reports what was inserted and what was skipped
- `make seed-test` — seeds test fixtures only, isolated from production seed data, used by CI and local test runs
- `make deploy` — orchestrates the full deploy sequence: lint → test → migrate → restart services. In CI, delegates to the workflow. Locally, runs the steps in sequence with clear stage markers in output
- `make check-migrations` — verifies no unapplied migrations exist against the target database. Exits non-zero if migrations are pending. Useful as a CI gate and a pre-deploy sanity check
- All new targets documented in the Makefile header comment block, following the existing documentation style
- All targets fail with descriptive, human-readable error messages — not raw exit codes, not Python tracebacks, not silence
- Targets respect the existing Makefile conventions (variable naming, phony declarations, help formatting)

## Acceptance Criteria

- [ ] `make migrate` runs successfully from a clean checkout with a valid `DATABASE_URL`
- [ ] `make migrate` fails with a clear error message when `DATABASE_URL` is not set or the database is unreachable
- [ ] `make seed` is idempotent — running it twice on the same database does not create duplicate records
- [ ] `make seed` reports what was inserted ("Seeded 15 companies, 42 signals") and what was skipped ("3 companies already exist, skipped")
- [ ] `make check-migrations` exits non-zero if unapplied migrations exist, exits zero if database is current
- [ ] `make help` lists all new targets with descriptions
- [ ] All new targets are documented in the Makefile header comment block

## Definition of Done

- **Tests Required**: Developer onboarding test — a new team member (or a fresh environment) runs `make install && make migrate && make seed && make run` without reading any documentation beyond `make help`. If they need to read a README, the Makefile failed.
- **Documentation Required**: Makefile header updated. No separate documentation needed — the Makefile IS the documentation.
- **Code Review Gate**: Reviewer runs each new target from a clean environment. Reviewer verifies error messages are descriptive (not raw tracebacks). Reviewer verifies `make help` output is complete.

## Notes

There's a philosophical question about `make deploy`: should it actually deploy, or should it just verify deploy-readiness and delegate to CI? The answer depends on the team's workflow. If developers deploy from their laptops, `make deploy` should deploy. If deploys only happen through CI, `make deploy` should run the same checks CI runs (lint, test, check-migrations) and print "Ready to deploy — push to staging branch." The target should exist either way; the implementation depends on the team's deployment model.

`make migrate-down` deserves special attention. Downgrading is destructive. The confirmation prompt should include the migration name being reverted and a warning about potential data loss. In CI (non-interactive), the target should require an explicit `CONFIRM=yes` environment variable to proceed. The default behavior for `make migrate-down` without confirmation should be to print what would happen and exit without doing it.
