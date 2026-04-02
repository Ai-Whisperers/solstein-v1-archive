# STORY-136: Add Async HTTP Client Guidelines and Linting

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | Medium |
| **Epic** | EPIC-035: Async-First External Adapters |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-133, STORY-134, STORY-135 (migrations must complete before guidelines are finalized) |

---

## The Audit Verdict

> 12+ files use `requests` in async context. No guidelines exist for async HTTP. The pattern will recur.

---

## Problem Statement

The forensic audit identified 12 files using `requests` in async context. STORY-133 through STORY-135 fix the existing violations. This story addresses the root cause: there are no standards, no guidelines, and no automated enforcement preventing the same mistake from being made again next week.

The `requests` library is the most widely known Python HTTP client. It is the first result for "python http request" on every search engine. It is what developers reach for by default, because it is what they learned first and what every tutorial uses. In a codebase with no documented standard for HTTP clients, every new developer who writes an async function and needs to make an HTTP call will reach for `requests`. They will not know it is wrong. There is nothing to tell them.

The fix is not to trust that developers will remember. The fix is to make the wrong thing hard and the right thing obvious. That requires three things: a written standard that defines which HTTP client to use and when, a linting rule that catches violations automatically, and a code review checklist that makes HTTP client choice an explicit review concern. Together, these create a system where a `requests` import in an async file fails CI before it ever reaches a reviewer's eyes.

The written standard must also address the edge cases that will arise: when is `aiohttp` appropriate instead of `httpx`? What about synchronous scripts and CLI tools — is `requests` acceptable there? What about test files? The standard must be specific enough to answer these questions without requiring a committee meeting every time a developer needs to make an HTTP call.

---

## Impact

| Dimension | Impact |
|-----------|--------|
| **Maintainability** | Without a standard, the `requests`-in-async pattern will be reintroduced by any developer unfamiliar with the issue. The audit finding becomes a recurring problem rather than a one-time fix. |
| **Performance** | New blocking code introduced over time silently degrades pipeline performance. The degradation is invisible until it becomes severe enough to notice. |
| **Onboarding** | New developers have no guidance on HTTP client selection. They will make the same mistake the audit found, not out of negligence but out of ignorance. |
| **CI Reliability** | Without automated enforcement, the standard is only as strong as the most tired reviewer on the most rushed PR. |

---

## Affected Files

| File | Issue |
|------|-------|
| `docs/standards/async-http.md` | Does not exist — must be created |
| `.ruff.toml` or `pyproject.toml` (ruff config) | No linting rule for `requests` in async files — must be added |
| `docs/standards/code-review-checklist.md` | No HTTP client section — must be added or updated |
| `docs/guides/migration-requests-to-httpx.md` | Does not exist — must be created |

---

## Architectural Requirements

- A standards document must be created at `docs/standards/async-http.md` defining the authoritative HTTP client policy for the codebase
- The standards document must include a decision matrix covering: async API calls (httpx), async website scraping with complex requirements (aiohttp), synchronous scripts and CLI tools (requests acceptable), test files (mock preferred, httpx acceptable)
- The standards document must include explicit examples of correct and incorrect patterns — not code, but descriptions of what constitutes a violation and what constitutes compliance
- A linting rule must be configured in `ruff` (or an equivalent static analysis tool already in the CI pipeline) that flags `import requests` or `from requests import` in any file that also contains `async def`
- The linting rule must be integrated into the existing CI pipeline such that a violation causes CI to fail — not warn, fail
- The code review checklist must include an explicit HTTP client section requiring reviewers to verify that async functions do not use `requests`
- A migration guide must be created at `docs/guides/migration-requests-to-httpx.md` documenting the mechanical steps for converting `requests`-based code to `httpx.AsyncClient`, including exception type mapping and connection pooling considerations
- The migration guide must document the `asyncio.gather()` pattern for concurrent fetching, as this is the most commonly missed optimization when migrating from synchronous to async HTTP

---

## Acceptance Criteria

- [ ] `docs/standards/async-http.md` exists and is committed to the repository
- [ ] The standards document contains a decision matrix covering all common HTTP client use cases in this codebase
- [ ] The standards document contains explicit descriptions of correct and incorrect patterns (no code — descriptions only, per the scope of this story)
- [ ] A linting rule is configured that flags `requests` imports in files containing `async def`
- [ ] The linting rule is integrated into CI and causes CI failure (not warning) on violation
- [ ] A new async file with a `requests` import fails CI — verified by a test of the linting rule itself
- [ ] The code review checklist includes an HTTP client section
- [ ] `docs/guides/migration-requests-to-httpx.md` exists and is committed to the repository
- [ ] The migration guide documents exception type mapping between `requests` and `httpx`
- [ ] The migration guide documents the `asyncio.gather()` pattern for concurrent fetching

---

## Definition of Done

- **Tests Required**: A test of the linting rule itself — a synthetic file containing `import requests` and `async def` must trigger the linting rule. This can be a CI job or a unit test of the ruff configuration. All existing tests continue to pass.
- **Documentation Required**: `docs/standards/async-http.md` (the standard), `docs/guides/migration-requests-to-httpx.md` (the migration guide), updated code review checklist. These documents are the primary deliverable of this story.
- **Code Review Gate**: Reviewer must verify (a) the linting rule actually catches violations (demonstrated by the linting test), (b) the standards document is specific enough to answer common questions without ambiguity, (c) the migration guide covers exception type mapping and concurrent fetching patterns, (d) CI fails on violation.

---

## Notes

The linting rule is the most important deliverable in this story. Documentation that lives in `docs/` is read once during onboarding and forgotten. A CI failure is encountered every time a violation is introduced. The linting rule is the enforcement mechanism that makes the standard real rather than aspirational.

The specific implementation of the linting rule depends on what static analysis tooling is already in the CI pipeline. `ruff` is the preferred tool given the project's existing configuration. If `ruff` cannot express the required rule natively (detecting `requests` imports in files with `async def`), a custom pre-commit hook or a simple Python script in the CI pipeline is an acceptable alternative. The requirement is that the check runs automatically and fails CI — the implementation mechanism is secondary.

The standards document should be written for the developer who has never thought about async HTTP clients, not for the developer who already knows the answer. It should explain *why* `requests` is wrong in async context, not just *that* it is wrong. A developer who understands the event loop model will not make this mistake; a developer who has only been told "use httpx" will make it the moment they forget the rule.

This story depends on STORY-133 through STORY-135 being complete before finalization, because the migration guide should reference the actual patterns used in the codebase rather than hypothetical examples. The linting rule and standards document can be drafted in parallel with the migrations.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This story currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently list this story as active work, treat it as triage-required rather than immediately actionable.

### Next Agent Action

- Reconcile this story against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before starting.
- Do not begin implementation from this file alone unless the queue or a fresh planning decision reactivates it.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Preserve machine-checkable enforcement and avoid prose-only or speculative "AI slop" updates.

### Minimum Verification For Future Agents

- If this story is reactivated, update the queue or controlling planning artifact first.
- Then prove the work with the smallest relevant regression tests, gates, or generated artifacts for the touched boundary.
