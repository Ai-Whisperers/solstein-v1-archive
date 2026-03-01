# EPIC-034: Exception Handling Transparency

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Critical |
| **Owner** | Platform Team |
| **Created** | 2026-03-01 |

## Context

Forensic audit found 20+ locations where exceptions are caught and `None` is returned with NO logging. enhanced_client.py:296 returns None on ANY exception. yfinance wrapper returns None on any failure. This creates "silent failures" where the pipeline appears healthy but produces no data.

## Stories

| Story | Title | Priority |
|-------|-------|----------|
| STORY-129 | Eliminate Silent None Returns in enhanced_client.py | P1 |
| STORY-130 | Add Structured Logging to All Adapter Exception Handlers | P1 |
| STORY-131 | Add Null Safety Guards for Division Operations | P1 |
| STORY-132 | Create Exception Handling Standards Document | P2 |

## Dependencies

- EPIC-014 (observability)
- EPIC-021 (LLM stack)

## Notes

Silent failures are worse than loud failures. At least with a loud failure you know something is wrong. Silent failures corrupt data and erode trust.
