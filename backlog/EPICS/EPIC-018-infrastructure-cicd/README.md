# EPIC-018: Infrastructure-as-Code & CI/CD

| Field | Value |
|-------|-------|
| Priority | **P1** |
| Status | 🔴 Open |
| Stories | 5 |
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
| [STORY-272](STORIES/STORY-272-restore-ruff-gate-signal-on-develop.md) | Restore Ruff Gate Signal Integrity on Current Develop | HIGH |

## Definition of Done

- [ ] Application runs in a Docker container built from a reproducible multi-stage Dockerfile
- [ ] All environment variables are managed via IaC — no manual server configuration
- [ ] Every commit triggers a CI pipeline that runs tests, type checks, and linting
- [ ] Pre-commit hooks prevent linting and type errors from reaching the repository
- [ ] Lint output is trustworthy on canonical `develop` and does not contain invalid suppression noise or backlog-invalidated "ruff clean" assumptions
