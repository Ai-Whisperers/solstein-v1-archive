# EPIC-079: Deploy Application Stack

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 |
| **Phase** | P3 — Run as Real Service |
| **Effort** | M (3–5 days) |
| **Stories** | 5 ([STORY-316](STORIES/STORY-316.md) through [STORY-320](STORIES/STORY-320.md)) |
| **Created** | 2026-04-01 |
| **Updated** | 2026-04-05 (added metadata, DoD) |

## Context

The application must be deployed as a Docker container with FastAPI, Celery worker, and Celery Beat running. This epic covers building the Docker image, deploying the services, and verifying all health checks pass.

## Stories

| Story | Title | Status | Notes |
|-------|-------|--------|-------|
| [STORY-316](STORIES/STORY-316.md) | Build and test Solstein Docker image | 🔴 READY | Deps: STORY-315 |
| [STORY-317](STORIES/STORY-317.md) | Deploy FastAPI API server with uvicorn | 🔴 READY | Deps: [STORY-316](STORIES/STORY-316.md) |
| [STORY-318](STORIES/STORY-318.md) | Deploy Celery worker (4 queues: default, scoring, export, enrichment) | 🔴 READY | Deps: [STORY-316](STORIES/STORY-316.md) |
| [STORY-319](STORIES/STORY-319.md) | Deploy Celery Beat scheduler | 🔴 READY | Deps: [STORY-318](STORIES/STORY-318.md) |
| [STORY-320](STORIES/STORY-320.md) | Verify all health checks pass (DB, Redis, workers, LLM) | 🔴 READY | Deps: [STORY-317](STORIES/STORY-317.md)–[STORY-319](STORIES/STORY-319.md) |

## Success Criteria

- Docker image builds without error
- FastAPI server responds to `/health` with 200
- Celery workers register on all 4 queues
- Beat scheduler starts without error
- All health endpoints pass (DB, Redis, workers, LLM)

## Definition of Done

- [ ] [STORY-316](STORIES/STORY-316.md): `docker build` exits 0; image size < 2GB
- [ ] [STORY-317](STORIES/STORY-317.md): `GET /health` returns `{"status": "ok"}` with HTTP 200
- [ ] [STORY-318](STORIES/STORY-318.md): `celery inspect active_queues` shows all 4 queues registered
- [ ] [STORY-319](STORIES/STORY-319.md): Beat scheduler starts without `ERROR` in logs
- [ ] [STORY-320](STORIES/STORY-320.md): `/health` endpoint reports DB, Redis, and LLM as healthy

## Dependencies

- STORY-315 (.env.production) — required before building image
- STORY-311–314 ([EPIC-078](../EPIC-078-deploy-core-infrastructure/README.md)) — required for health checks to pass
