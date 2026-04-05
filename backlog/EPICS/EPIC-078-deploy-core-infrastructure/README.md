# EPIC-078: Deploy Core Infrastructure

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 |
| **Phase** | P3 — Run as Real Service |
| **Effort** | M (3–5 days) |
| **Stories** | 5 ([STORY-311](STORIES/STORY-311.md) through [STORY-315](STORIES/STORY-315.md)) |
| **Created** | 2026-04-01 |
| **Updated** | 2026-04-05 (added metadata, DoD) |

## Context

The platform requires PostgreSQL 15 (with pgvector), Redis 7, and SearXNG to function. These services exist in docker-compose but may not be deployed or configured for production use. Without them, all enrichment, scoring, and pipeline functionality is unavailable.

## Stories

| Story | Title | Status | Notes |
|-------|-------|--------|-------|
| [STORY-311](STORIES/STORY-311.md) | Deploy PostgreSQL 15 with pgvector extension (docker-compose or managed) | 🔴 READY | Deps: none |
| [STORY-312](STORIES/STORY-312.md) | Run all Alembic migrations on deployed database | 🔴 READY | Deps: [STORY-311](STORIES/STORY-311.md) |
| [STORY-313](STORIES/STORY-313.md) | Deploy Redis 7 for Celery broker and result backend | 🔴 READY | Deps: none |
| [STORY-314](STORIES/STORY-314.md) | Deploy SearXNG instance for web search | 🔴 READY | Deps: none |
| [STORY-315](STORIES/STORY-315.md) | Create .env.production with all required env vars, secrets rotated | 🔴 READY | Deps: [STORY-311](STORIES/STORY-311.md)–[STORY-314](STORIES/STORY-314.md) |

## Success Criteria

- PostgreSQL accepts connections with pgvector extension enabled
- All Alembic migrations run without error
- Redis accepts Celery connections
- SearXNG returns results for test queries
- `.env.production` contains all required vars with no placeholder values

## Definition of Done

- [ ] [STORY-311](STORIES/STORY-311.md): `psql -c "SELECT extversion FROM pg_extension WHERE extname='vector'"` returns a version
- [ ] [STORY-312](STORIES/STORY-312.md): `alembic current` shows latest revision with no pending migrations
- [ ] [STORY-313](STORIES/STORY-313.md): `redis-cli ping` returns PONG on deployed instance
- [ ] [STORY-314](STORIES/STORY-314.md): SearXNG `/search?q=test` returns JSON results
- [ ] [STORY-315](STORIES/STORY-315.md): `.env.production` has no `<PLACEHOLDER>` values

## Dependencies

None — infrastructure can be deployed independently.
