# STORY-315: Create .env.production with all required env vars

| Field | Value |
|-------|-------|
| **Epic** | EPIC-078 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | STORY-311, STORY-312, STORY-313, STORY-314 |

## Description

Create `.env.production` with all required environment variables filled in with real values (no placeholders). Rotate any example/placeholder credentials before copying to production.

## Acceptance Criteria

- [ ] `.env.production` contains all vars from `.env.example`
- [ ] No placeholder values (change-me, example.com, etc.)
- [ ] File is gitignored (never committed)
- [ ] Application starts with no configuration errors
