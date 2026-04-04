# STORY-316: Build and test Solstein Docker image

| Field | Value |
|-------|-------|
| **Epic** | EPIC-079 |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | STORY-315 |

## Description

Build the Solstein Docker image and verify it starts without errors. Run smoke tests inside the container.

## Acceptance Criteria

- [ ] Docker image builds without error
- [ ] Container starts and all imports succeed
- [ ] No missing env vars at startup
