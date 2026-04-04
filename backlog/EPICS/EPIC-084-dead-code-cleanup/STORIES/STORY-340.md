# STORY-340: Delete data/real_data_integration.py (broken import)

| Field | Value |
|-------|-------|
| **Epic** | EPIC-084 |
| **Priority** | P1 |
| **Size** | XS |
| **Status** | 🔴 READY |
| **Dependencies** | None |

## Description

Delete `data/real_data_integration.py` which has a broken import of `web_research_pipeline` that does not exist. File is unreachable (no callers) and causes import errors.

## Acceptance Criteria

- [ ] File deleted
- [ ] No remaining imports of `real_data_integration` anywhere in codebase
- [ ] Dead code CI detector confirms no orphaned references
