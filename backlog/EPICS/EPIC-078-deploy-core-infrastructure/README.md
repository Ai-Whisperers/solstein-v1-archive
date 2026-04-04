# EPIC-078: Deploy Core Infrastructure

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 — Phase P3: Infrastructure |
| **Phase** | P3 — Run as Real Service |
| **Created** | 2026-04-01 |

## Context

The platform requires PostgreSQL 15 (with pgvector), Redis 7, and SearXNG to function. These services exist in docker-compose but may not be deployed or configured for production use. Without them, all enrichment, scoring, and pipeline functionality is unavailable.

## Stories

| Story | Title | Status | Notes |
|-------|-------|--------|-------|
| [STORY-311](STORIES/STORY-311.md) | Deploy PostgreSQL 15 with pgvector extension (docker-compose or managed) | 🔴 READY | Deps: none |
| [STORY-312](STORIES/STORY-312.md) | Run all Alembic migrations on deployed database | 🔴 READY | Deps: STORY-311 |
| [STORY-313](STORIES/STORY-313.md) | Deploy Redis 7 for Celery broker and result backend | 🔴 READY | Deps: none |
| [STORY-314](STORIES/STORY-314.md) | Deploy SearXNG instance for web search | 🔴 READY | Deps: none |
| [STORY-315](STORIES/STORY-315.md) | Create .env.production with all required env vars, secrets rotated | 🔴 READY | Deps: STORY-311 through STORY-314 |

## Success Criteria

- PostgreSQL accepts connections with pgvector extension enabled
- All Alembic migrations run without error
- Redis accepts Celery connections
- SearXNG returns results for test queries
- `.env.production` contains all required vars with no placeholder values

## Dependencies

- None — infrastructure can be deployed independently
