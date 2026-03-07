# STORY-133: Replace requests with httpx in GitHub Agent

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-035: Async-First External Adapters |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

---

## The Audit Verdict

> `github_agent.py:56,58` — `requests.get()` in `async def gather()` [BLOCKS EVENT LOOP].

---

## Problem Statement

The GitHub agent is declared as an `async def` function. It uses `async def gather()` as its entry point, which signals to every caller — and to the FastAPI event loop — that this function is non-blocking and safe to run concurrently. That signal is a lie.

Inside `gather()`, at lines 56 and 58, the agent calls `requests.get()`. The `requests` library is synchronous. It does not yield control to the event loop while waiting for a network response. It blocks the calling thread entirely. In an async context, that thread *is* the event loop. So every GitHub API call freezes the entire application until the response arrives.

A research pipeline that should take 30 seconds with proper async concurrency takes 5 minutes because each GitHub API call serializes the entire pipeline. While the GitHub agent waits for a response, no other coroutine can run — not the news fetcher, not the funding adapter, not the scoring engine. Everything queues behind a single HTTP request to GitHub's API. This is not async code; it's sync code wearing async lipstick.

The fix is straightforward: replace `requests` with `httpx.AsyncClient`. The `httpx` library provides an API nearly identical to `requests` but with proper async support. The migration is mechanical. The performance impact is immediate.

---

## Impact

| Dimension | Impact |
|-----------|--------|
| **Performance** | Every GitHub API call serializes the entire research pipeline. A 30-second pipeline becomes 5 minutes. |
| **Scalability** | Cannot handle concurrent research jobs — each job blocks the event loop for all others. |
| **Resource Usage** | Event loop blocked during I/O wait; FastAPI workers are underutilized while waiting on network. |
| **Correctness** | Code presents itself as async but behaves synchronously — a contract violation with every caller. |

---

## Affected Files

| File | Issue |
|------|-------|
| `agents/github_agent.py` | Lines 56, 58: `requests.get()` called inside `async def gather()` — blocks event loop |
| `agents/github_agent.py` | Any retry logic using `requests` exceptions must be updated to `httpx` exception types |
| `tests/` (GitHub agent tests) | Mocks targeting `requests` must be updated to mock `httpx` |

---

## Architectural Requirements

- The `requests` library must be replaced with `httpx.AsyncClient` for all HTTP calls in `github_agent.py`
- All HTTP calls must use the `await` keyword — no synchronous HTTP calls permitted in any `async def` function
- `httpx.AsyncClient` must be used as an async context manager to ensure connection pooling and proper resource cleanup
- Timeout configuration must be migrated from `requests`-style parameters to `httpx.Timeout` objects
- Retry logic must be updated to catch `httpx` exception types (`httpx.TimeoutException`, `httpx.HTTPStatusError`, etc.) rather than `requests` exceptions
- The public interface of the GitHub agent (function signatures, return types) must remain unchanged — this is an internal implementation change only
- Connection pooling must be configured appropriately for GitHub API rate limits and concurrency requirements
- The agent must not create a new `httpx.AsyncClient` per request — client instantiation must be managed at the appropriate scope to enable connection reuse

---

## Acceptance Criteria

- [ ] No `import requests` or `from requests` statements remain in `github_agent.py`
- [ ] All HTTP calls in `github_agent.py` use `await` with `httpx.AsyncClient`
- [ ] `httpx.AsyncClient` is used as an async context manager (`async with httpx.AsyncClient() as client:`)
- [ ] Timeout configuration uses `httpx.Timeout` or equivalent `httpx`-native approach
- [ ] Retry logic catches `httpx` exception types, not `requests` exception types
- [ ] All existing unit tests pass with mocks updated to target `httpx` instead of `requests`
- [ ] A performance benchmark demonstrates that 10 concurrent GitHub API requests execute in parallel rather than serially
- [ ] The agent's public interface (function signatures, return types, raised exceptions visible to callers) is unchanged

---

## Definition of Done

- **Tests Required**: Load test demonstrating 10 concurrent GitHub API requests complete in parallel (total time ≈ single request time, not 10× single request time). Unit tests updated to mock `httpx`. All existing tests pass.
- **Documentation Required**: Inline comments updated where `requests`-specific behavior was previously documented. No new external documentation required.
- **Code Review Gate**: Reviewer must verify (a) no `requests` imports remain, (b) all HTTP calls use `await`, (c) `AsyncClient` is not instantiated per-request, (d) exception handling targets `httpx` types.

---

## Notes

The `requests` library is not inherently bad. It is excellent for synchronous code. The problem is using it in async code, where it becomes a silent event loop killer. The `httpx` library was designed specifically to address this: it provides a `requests`-compatible API with proper async support via `httpx.AsyncClient`.

The migration path is well-documented and the API surface is nearly identical. The primary gotchas are: (1) exception types differ between `requests` and `httpx` — any `except requests.exceptions.X` blocks must be updated; (2) `httpx.AsyncClient` should be reused across requests rather than instantiated per-call; (3) response methods like `.json()` are synchronous in `httpx` (unlike some async HTTP libraries), so no `await` is needed there.

This story is the highest-priority item in EPIC-035 because `github_agent.py` is explicitly called out in the audit with line numbers, and the GitHub agent is a core component of the research pipeline.
