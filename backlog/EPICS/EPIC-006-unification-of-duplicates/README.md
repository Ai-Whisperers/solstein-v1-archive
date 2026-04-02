# EPIC-006: Unification of Duplicates

| Field | Value |
|-------|-------|
| Priority | P1 |
| Status | 🔴 Open |
| Stories | STORY-019, STORY-020, STORY-021, STORY-022 |
| Created | 2026-02-28 |

---

## Summary

This is technical debt from an incomplete migration. Someone started unifying adapters, loaders, middleware, and routes — and then stopped. The result is worse than not starting at all: the codebase now contains both the old and new versions of everything, with no documentation indicating which is canonical.

In every case, the system's behaviour depends on which import path is taken. That is not architecture — it is a coin flip.

## Scope

### Adapter Pair Duplication
`adapters/enrichment/` contains 6 adapter pairs where both the original (`funding.py`) and the migration version (`funding_unified.py`) coexist. The full list:

| Original | Unified Version |
|----------|----------------|
| `funding.py` | `funding_unified.py` |
| `linkedin.py` | `linkedin_unified.py` |
| `news.py` | `news_unified.py` |
| `patents.py` | `patents_unified.py` |
| `website.py` | `website_unified.py` |
| `web_search.py` | `web_search_unified.py` |

The migration was never completed. Which version the system uses depends on which import wins at runtime.

### Three Parallel Data Loading Systems
Three data loading systems exist in parallel:
- `data/loaders.py` (771 lines, deprecated but still imported)
- `data/unified_loader.py` (1,142 lines, intended replacement)
- `data/company_research.py` (412 lines, orphaned, not imported in main paths)

Approximately 2,300 lines of competing loader logic. The "deprecated" loader is still actively called, meaning deprecation is aspirational, not actual.

### Duplicate Middleware Implementations
Two middleware implementations exist:
- `api/middleware.py` (a file)
- `api/middleware/` (a directory)

Both define `LoggingMiddleware`. The middleware ordering is wrong — error logging middleware runs before authentication middleware, meaning unauthenticated requests are logged as if they were authorised.

### Split Route Directories
Two route directories exist:
- `api/routers/` (10 route files)
- `api/routes/` (1 file: `refresh.py`)

The refresh route lives in a separate directory with no explanation. This is either an incomplete migration or a forgotten file — neither is acceptable.

## Stories

| Story | Title | Priority | Severity |
|-------|-------|----------|----------|
| [STORY-019](STORIES/STORY-019-eliminate-unified-adapter-pairs.md) | Eliminate Duplicate Unified Adapter Pairs | P1 | HIGH |
| [STORY-020](STORIES/STORY-020-consolidate-loader-systems.md) | Consolidate Three Parallel Data Loader Systems | P1 | HIGH |
| [STORY-021](STORIES/STORY-021-consolidate-middleware.md) | Merge Duplicate Middleware Implementations | P1 | HIGH |
| [STORY-022](STORIES/STORY-022-consolidate-route-directories.md) | Consolidate Duplicate Route Directories | P1 | MEDIUM |

## Definition of Done

- [ ] One adapter per external system — no `_unified` suffixed files remain
- [ ] One data loader system — the other two are deleted
- [ ] One middleware stack with correct ordering — duplicate `LoggingMiddleware` eliminated
- [ ] One route directory — `api/routes/` does not exist
- [ ] All existing tests pass after unification
- [ ] Each unification is accompanied by a Protocol or ABC defining the canonical interface

## Ordering Notes

STORY-020 (loader consolidation) should be completed before EPIC-008's STORY-029 (loader decomposition). You must decide what the canonical loader is before you decompose it. STORY-021 (middleware) is independent and can be executed in parallel with other stories. STORY-022 (routes) is the simplest item and can be completed in under an hour.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This epic currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently schedule this epic, treat it as triage-required backlog inventory instead of self-startable work.

### Next Agent Action

- Reconcile this epic against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before selecting a story.
- Do not start implementation from this README alone unless the queue or a fresh planning decision activates the epic.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Prefer narrow, machine-checkable progress over broad narrative backlog churn.

### Minimum Verification For Future Agents

- If this epic is reactivated, update the queue or controlling planning artifact first.
- Then execute one story at a time with the relevant tests, gates, and generated references for the touched surface.
