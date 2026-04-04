# STORY-317: Deploy FastAPI API server with uvicorn

| Field | Value |
|-------|-------|
| **Epic** | EPIC-079 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | STORY-316 |

## Description

Deploy the FastAPI server using uvicorn. Verify it responds to health check at /health.

## Acceptance Criteria

- [ ] FastAPI server responds to GET /health with HTTP 200
- [ ] Server handles concurrent requests without error
