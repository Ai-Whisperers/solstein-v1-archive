# EPIC-035: Async-First External Adapters

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Owner** | Platform Team |
| **Created** | 2026-03-01 |

## Context

Forensic audit found 12 files using synchronous requests library inside async functions. github_agent.py:56,58 has requests.get() in async def gather() — BLOCKS EVENT LOOP. This kills concurrency and makes the research pipeline unnecessarily slow.

## Stories

| Story | Title | Priority |
|-------|-------|----------|
| STORY-133 | Replace requests with httpx in GitHub Agent | P2 |
| STORY-134 | Replace requests with httpx in News and Funding Adapters | P2 |
| STORY-135 | Replace requests with httpx in Companies House and Website Agents | P2 |
| STORY-136 | Add Async HTTP Client Guidelines and Linting | P2 |

## Dependencies

- EPIC-021 (modern LLM stack)
- EPIC-028 (external service consolidation)

## Notes

This is not async code; it's sync code wearing async lipstick. Every blocking call serializes the entire pipeline.
