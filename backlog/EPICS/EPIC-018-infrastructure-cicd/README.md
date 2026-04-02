# EPIC-018: Infrastructure-as-Code & CI/CD

| Field | Value |
|-------|-------|
| Priority | **P1** |
| Status | 🔴 Open |
| Stories | 4 |
| Created | 2026-02-28 |
| Depends On | [EPIC-002](../EPIC-002-configuration-integrity/README.md) (config must be clean before deployment pipeline) |

## Context

There is no CI pipeline. There is no Dockerfile. There is no infrastructure-as-code. Deployments are presumably manual. Configuration is managed by whoever set up the server at some point. The environment a developer runs locally may differ materially from production, and there is no automated mechanism to detect the difference.

The AGENTS.md documents `make check-all` and standard pytest commands, but there is no evidence these run automatically on every commit. There is no automated gate between "code merged" and "code deployed."

This is not a nice-to-have. Without a CI pipeline, every bug fix in this backlog can be deployed in a broken state and no automated system will notice.

## Scope

| Story | Title | Severity |
|-------|-------|----------|
| [STORY-059](STORIES/STORY-059-dockerize-application.md) | Dockerize Application with Multi-Stage Build | HIGH |
| [STORY-060](STORIES/STORY-060-iac-environment-configuration.md) | Define Environment Configuration via IaC | HIGH |
| [STORY-061](STORIES/STORY-061-ci-pipeline-quality-gates.md) | Build CI Pipeline with Quality Gates | HIGH |
| [STORY-062](STORIES/STORY-062-pre-commit-hooks.md) | Implement Pre-commit Hooks and Linting Automation | MEDIUM |

## Definition of Done

- [ ] Application runs in a Docker container built from a reproducible multi-stage Dockerfile
- [ ] All environment variables are managed via IaC — no manual server configuration
- [ ] Every commit triggers a CI pipeline that runs tests, type checks, and linting
- [ ] Pre-commit hooks prevent linting and type errors from reaching the repository

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
