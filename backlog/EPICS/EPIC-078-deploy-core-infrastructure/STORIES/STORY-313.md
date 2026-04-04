# STORY-313: Deploy Redis 7 for Celery broker and result backend

| Field | Value |
|-------|-------|
| **Epic** | EPIC-078 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | None |

## Description

Deploy Redis 7 for use as the Celery message broker and result backend. Verify Celery can connect and publish/consume tasks.

## Acceptance Criteria

- [ ] Redis 7 running and accepting connections
- [ ] `redis-cli ping` returns PONG
- [ ] Celery test task successfully publishes and consumes via Redis
- [ ] Redis URL documented in `.env.example`
