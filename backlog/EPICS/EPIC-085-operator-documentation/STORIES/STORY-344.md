# STORY-344: Write deployment guide (docker-compose → working system in 10 min)

| Field | Value |
|-------|-------|
| **Epic** | EPIC-085 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | STORY-320 (all health checks pass) |

## Description

Write a deployment guide at `docs/operations/deployment.md` that walks an operator from a fresh clone to a working system in under 10 minutes using docker-compose.

## Acceptance Criteria

- [ ] Guide covers: prerequisites, clone, configure .env, docker-compose up, verify
- [ ] Each step has the exact command to run
- [ ] Time estimate per step included
- [ ] Tested by a fresh operator — total time < 10 minutes
