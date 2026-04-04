# STORY-311: Deploy PostgreSQL 15 with pgvector extension

| Field | Value |
|-------|-------|
| **Epic** | EPIC-078 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | None |

## Description

Deploy PostgreSQL 15 with the pgvector extension enabled. Can use docker-compose (local) or managed PostgreSQL (production). Verify the extension is available.

## Acceptance Criteria

- [ ] PostgreSQL 15 running and accepting connections
- [ ] `CREATE EXTENSION vector` succeeds (pgvector installed)
- [ ] Connection URL documented in `.env.example`
- [ ] Health check confirms DB connectivity
