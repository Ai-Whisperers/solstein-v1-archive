# STORY-133: Replace requests with httpx in GitHub Agent

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-035: Async-First External Adapters |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Audit Verdict

> github_agent.py:56,58 — requests.get() in async def gather() [BLOCKS EVENT LOOP].

## Problem Statement

The GitHub agent is an async function that uses the synchronous requests library. Every HTTP call blocks the entire event loop. While waiting for GitHub's API to respond, no other async task can run. A research pipeline that should take 30 seconds with proper async concurrency takes 5 minutes because each GitHub API call serializes the entire pipeline. This is not async code; it's sync code wearing async lipstick.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Performance** | Serializes entire pipeline |
| **Scalability** | Cannot handle concurrent requests |
| **Resource Usage** | Event loop blocked, workers underutilized |

## Affected Files

| File | Issue |
|------|-------|
| `agents/github_agent.py:56,58` | requests.get() in async function |

## Architectural Requirements

- requests replaced with httpx.AsyncClient
- All HTTP calls use async/await pattern
- Connection pooling via httpx.AsyncClient context manager
- Timeout configuration via httpx (not requests)
- Retry logic updated to work with httpx exceptions
- Unit tests updated to mock httpx instead of requests
- Performance benchmark: before/after concurrent request handling

## Acceptance Criteria

- [ ] No requests imports in github_agent.py
- [ ] All HTTP calls use await
- [ ] AsyncClient used with context manager
- [ ] Tests mock httpx
- [ ] Benchmark shows improved concurrency

## Definition of Done

- **Tests Required**: Load test: 10 concurrent GitHub requests
- **Documentation Required**: None
- **Code Review Gate**: Reviewer verifies no blocking calls remain

## Notes

Not async code; it's sync code wearing async lipstick.
