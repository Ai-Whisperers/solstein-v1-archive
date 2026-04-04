# STORY-318: Deploy Celery worker (4 queues)

| Field | Value |
|-------|-------|
| **Epic** | EPIC-079 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | STORY-316 |

## Description

Deploy Celery worker registered on all 4 queues: default, scoring, export, enrichment.

## Acceptance Criteria

- [ ] Worker registered on: default, scoring, export, enrichment queues
- [ ] Worker processes a test task end-to-end
