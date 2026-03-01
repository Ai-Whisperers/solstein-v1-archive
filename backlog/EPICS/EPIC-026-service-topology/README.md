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
