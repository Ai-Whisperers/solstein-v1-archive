# STORY-100: Delete Root Bypass Scripts

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | High |
| **Epic** | EPIC-027: CI/CD Automation |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-098 (Makefile Targets) |

## The Audit Verdict

> `run_research.py` and `run_market_pipeline.py` in project root call the domain layer directly, bypassing the API entirely. `scripts/solstein_cli.py` does the same via Click commands.

## Problem Statement

These scripts exist because, at some point, using the API was harder than importing the domain layer and calling it directly. That's a legitimate frustration. The response — writing bypass scripts — was the wrong fix for a real problem. Instead of making the API easier to use, someone built a side door. Now the side door is load-bearing.

`run_research.py` and `run_market_pipeline.py` call the domain layer directly. They bypass authentication, rate limiting, request validation, structured logging, error handling middleware, and audit trails — everything the API exists to provide. Every time someone runs `python run_research.py` in production, they're executing business logic with no access control, no audit record, and no operational visibility. If the API is the front door with a lock, a camera, and a doorbell, these scripts are the window someone left open in the basement.

The CLI (`scripts/solstein_cli.py`) has the same problem: Click commands that import domain services directly. The CLI should be a thin HTTP client that calls the API, not a second application that shares the domain layer. Two code paths to the same business logic means two paths to maintain, two paths to test, two paths where bugs can diverge. When the API gets a fix and the CLI doesn't, users of the CLI experience the old bug. When the CLI adds a feature and the API doesn't, API users wonder why the CLI can do something the API can't.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Reliability** | Two code paths to the same operations. Bugs fixed in one path persist in the other. Behavior divergence between API and scripts is guaranteed over time. |
| **Operational** | No audit trail for script-based operations. If someone runs `run_research.py` and it corrupts data, there's no API log, no request ID, no trace to investigate. |
| **Developer Experience** | Confusing: "Do I use the API or the script?" New developers see both and don't know which is canonical. The answer is "the API," but the scripts' existence suggests otherwise. |
| **Security** | Scripts bypass all authentication and authorization middleware. Any user with SSH access can run any operation without access control. Rate limiting doesn't apply. Input validation doesn't apply. |

## Affected Files

| File | Issue |
|------|-------|
| `run_research.py` | Root-level script calling domain layer directly, bypassing API |
| `run_market_pipeline.py` | Root-level script calling domain layer directly, bypassing API |
| `scripts/solstein_cli.py` | Click CLI importing domain services directly instead of calling the API |

## Architectural Requirements

- `run_research.py` is DELETED from the repository. Not deprecated, not renamed, not moved. Deleted.
- `run_market_pipeline.py` is DELETED from the repository. Same treatment.
- `scripts/solstein_cli.py` is restructured: every Click command must invoke the API via HTTP requests with an auth token, not import domain services directly
- Before deletion, audit each script to identify operations that don't have API equivalents. Those operations need API endpoints first. Document the gap analysis in this story's notes.
- A `MIGRATION_GUIDE.md` is added to `scripts/` explaining:
  - What the old scripts did
  - What the equivalent CLI commands are
  - What the equivalent API endpoints are
  - How to obtain and configure an auth token for CLI use
- CI linting rule added: no Python files in project root except configuration files (`pyproject.toml`, `setup.py`, `setup.cfg`, `conftest.py`). Any `.py` file in project root fails CI.
- The CLI must support all operations the deleted scripts performed — if the scripts could trigger research and market pipeline runs, the CLI must be able to do the same, through the API
- CLI must pass authentication credentials (API key or JWT) on every request — no unauthenticated API calls from the CLI

## Acceptance Criteria

- [ ] `run_research.py` does not exist in the repository
- [ ] `run_market_pipeline.py` does not exist in the repository
- [ ] `find . -maxdepth 1 -name "run_*.py"` returns empty
- [ ] CLI commands invoke the API via HTTP, not the domain layer directly
- [ ] All CLI operations appear in API audit logs with the CLI user's identity
- [ ] CI fails if a `.py` file exists in project root (excluding config files)
- [ ] `MIGRATION_GUIDE.md` exists in `scripts/` documenting the transition

## Definition of Done

- **Tests Required**: All existing CLI functionality verified working through the API. Run each CLI command, verify the corresponding API endpoint is called, verify the result matches what the old script produced. Integration test: run CLI command, check API audit log for the corresponding request.
- **Documentation Required**: `MIGRATION_GUIDE.md` in `scripts/`. Updated `README.md` removing references to root-level scripts. CLI `--help` output updated to reflect API-backed commands.
- **Code Review Gate**: Reviewer verifies no direct domain imports remain in `scripts/`. Reviewer greps for `from solstein.domain` and `from solstein.application` in `scripts/` — zero matches. Reviewer verifies every CLI command makes an HTTP request to the API.

## Notes

**Gap analysis required before deletion.** Before deleting the scripts, enumerate every operation they perform and verify an API endpoint exists for it:

| Script Operation | API Endpoint | Status |
|-----------------|--------------|--------|
| `run_research.py` — trigger research for company | `POST /api/v1/research/{company_id}` | not-yet-verified |
| `run_research.py` — batch research for company list | `POST /api/v1/research/batch` | not-yet-verified |
| `run_market_pipeline.py` — trigger market data refresh | `POST /api/v1/market/refresh` | not-yet-verified |
| `run_market_pipeline.py` — trigger pipeline for sector | `POST /api/v1/market/pipeline/{sector}` | not-yet-verified |

If any operation lacks an API endpoint, that endpoint must be created BEFORE the script is deleted. Deleting the script before the API covers the operation means losing the capability entirely.

**On the CLI restructuring:** The CLI should use a configured `API_BASE_URL` and `API_TOKEN` (from environment or config file). It should format API responses for terminal display (tables, colors, progress bars for long-running jobs). It should NOT be a thin `curl` wrapper — it should be a proper CLI experience that happens to use the API as its backend. Think `gh` (GitHub CLI), not `curl | jq`.

**Expect resistance.** These scripts are convenient. They're fast. They skip auth. That's the point — they skip things that exist for good reasons. The migration path must be equally convenient, or the scripts will reappear under a different name within a sprint.

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
