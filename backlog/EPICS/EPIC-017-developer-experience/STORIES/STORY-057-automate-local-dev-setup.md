# STORY-057: Automate Local Development Environment Setup

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P2 |
| Severity | HIGH |
| Epic | [EPIC-017: Developer Experience](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-059: Dockerize Application](../../EPIC-018-infrastructure-cicd/STORIES/STORY-059-dockerize-application.md), [STORY-008: Startup Validation](../../EPIC-002-configuration-integrity/STORIES/STORY-008.md) |

---

## The Audit Verdict
> The AGENTS.md lists `python scripts/setup_db.py` and manual environment variable configuration as setup steps. There is no single command that brings up a working local environment. The number of undocumented steps between cloning the repository and making a successful API call is unknown.

## Problem Statement
An undocumented, multi-step setup process means every new engineer rediscovers the same configuration pitfalls. Time spent debugging local setup is time not spent on productive work. Each developer's local environment is slightly different because each followed a slightly different path through the undocumented setup. Bugs that are "works on my machine" are environment bugs caused by inconsistent setup.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Onboarding** | New engineers spend unquantified time on local setup — the first day is lost to configuration archaeology |
| **Consistency** | Every developer's local environment is slightly different — "works on my machine" is a regular occurrence |
| **Productivity** | Environment differences cause bugs that are not reproducible in CI and consume debugging time |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `Makefile` | Modify | Add `make setup` target that orchestrates the full setup |
| `docker-compose.dev.yml` | Add | Local services (PostgreSQL, Redis) with health checks |
| `scripts/setup_local.sh` or equivalent | Add | Setup orchestration script |

## Architectural Requirements
*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: A single command (`make setup` or equivalent) must bring up all required local services (PostgreSQL, Redis) and configure the application
- **REQ-2**: The command must generate a `.env.local` template with all required variables and sensible local development defaults
- **REQ-3**: The setup must be idempotent — running it twice must not break a working setup
- **REQ-4**: The setup command must verify its own success: confirm database connectivity, Redis connectivity, and that the API starts successfully
- **REQ-5**: The setup must work from a fresh clone with only Docker and `make` as prerequisites

## Acceptance Criteria
- [ ] A fresh clone + `make setup` produces a running local environment
- [ ] The setup is idempotent (run twice → still works, no errors, no duplicate data)
- [ ] The setup command verifies success and reports which steps succeeded or failed
- [ ] Only Docker and `make` are required as prerequisites on the host machine

## Definition of Done

**Tests Required:**
- [ ] Tested on a clean machine (or clean Docker environment) with only Docker installed
- [ ] Idempotency verified: run `make setup` twice, confirm no errors

**Documentation Required:**
- [ ] Setup troubleshooting guide for common failures (port conflicts, Docker resource limits, etc.)

**Code Review Gate:**
- [ ] Reviewer confirms the setup script verifies its own success
- [ ] Reviewer confirms idempotency (no destructive operations without guards)

## Notes
This story depends on STORY-059 (Dockerfile) for the Docker-based local services and STORY-008 (startup validation) for the self-verification step. The `make setup` target should be the single documented entry point — if a developer reads nothing else, they should be able to run `make setup` and get a working environment. The `.env.local` template should contain sensible defaults that work with the docker-compose.dev.yml services (e.g., `DATABASE_URL=postgresql://solstein:solstein@localhost:5432/solstein_dev`).
