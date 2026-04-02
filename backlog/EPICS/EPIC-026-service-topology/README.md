# EPIC-026: Service Topology

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Owner** | Platform Team |
| **Created** | 2026-03-01 |

## Context

The platform's `docker-compose.yml` defines three services: `api`, `db`, `redis`. The Celery worker and Beat scheduler are started via a manual shell script (`scripts/services/start_celery_workers.sh`) that nobody runs in containerized environments. The result: in any Docker-based deployment, the entire async job system simply does not run. Research tasks are never scheduled. Data is never collected. The platform silently degrades to a static snapshot of whatever was seeded at setup time.

This is not a configuration oversight — it is a missing architectural layer. Fixing it requires adding worker, beat, and monitoring services to the compose topology, and making the Dockerfile production-worthy with a multi-stage build.

## Stories

| Story | Title | Priority |
|-------|-------|----------|
| STORY-093 | Add Celery Worker Service to docker-compose | P1 |
| STORY-094 | Add Celery Beat Service to docker-compose | P1 |
| STORY-095 | Add Flower Monitoring Service to docker-compose | P1 |
| STORY-096 | Multi-Stage Dockerfile for Production | P1 |

## Dependencies
- EPIC-025 (Worker Reliability) — workers should be hardened before being formalized in topology
- EPIC-002 (Configuration Integrity) — env-driven config must work before multi-container wiring

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
