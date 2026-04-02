# EPIC-032: Complete Unified Adapter Migration

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Severity** | Critical |
| **Created** | 2026-03-01 |
| **Dependencies** | EPIC-006 (unification of duplicates), STORY-092 (merge task files) |
| **Stories** | STORY-121, STORY-122, STORY-123, STORY-124 |

---

## Executive Summary

A forensic audit of the data adapter layer revealed that the "unified adapter migration" was completed in name only. Six adapters were refactored to inherit from `BaseRefreshConnector` — a legitimate architectural improvement — but the refactor was executed without verifying functional parity. In the process, error handling wrappers, retry logic, input validation, and cross-referencing capabilities were silently dropped. The old adapter files were never deleted, so the codebase now carries both versions: the old ones that actually work and the new ones that are architecturally correct but functionally incomplete.

This epic exists to finish what was started. The unified adapters must be brought to full functional parity with their predecessors, and the old files must be deleted. Until that happens, the migration is a liability, not an improvement.

---

## Audit Verdict

> Six "unified" adapters gained `BaseRefreshConnector` inheritance but lost original client wrappers that handled error handling, retry, and transformation. The migration was architectural, not functional parity. Old versions still exist in parallel, creating maintenance confusion.

---

## Problem Statement

The adapter unification effort was motivated by a real problem: duplicate adapter files with divergent implementations were creating maintenance overhead. The solution — a shared `BaseRefreshConnector` base class — was architecturally sound. The execution was not.

When the unified adapters were written, the focus was on inheritance structure, not behavioral equivalence. The old adapters contained battle-tested logic: `AdditionalDataSources` wrappers that caught API errors, retry mechanisms tuned to specific provider rate limits, input validation that prevented wasted network calls, and cross-referencing logic that enriched data from multiple sources. None of this was documented. None of it was ported. It was simply left behind.

The result is a codebase in an indeterminate state. The unified adapters are the "official" versions by name, but the old adapters are the ones that actually handle production conditions. Developers who use the unified adapters get silent failures where the old adapters would have retried. They get cryptic HTTP errors where the old adapters would have returned structured domain errors. They get wasted API calls where the old adapters would have short-circuited on missing input.

Meanwhile, both versions coexist. The old files were never deleted because the migration was never verified as complete. Every bug fix applied to one version is silently not applied to the other. Every new developer who reads the codebase has to figure out which version is canonical. The answer, currently, is neither.

---

## Scope

This epic covers four stories that together complete the migration:

| Story | Title | Focus |
|-------|-------|-------|
| STORY-121 | Restore Error Handling in news_unified.py | Error handling, retry logic |
| STORY-122 | Restore Funding Adapter Wrapper | Error handling, news cross-reference |
| STORY-123 | Restore Website Adapter Validation | Input validation, early exit |
| STORY-124 | Delete Old Adapter Versions After Parity | Cleanup, import consolidation |

STORY-124 is a hard dependency on STORY-121, STORY-122, and STORY-123. Old files must not be deleted until unified parity is verified.

---

## Impact

| Dimension | Impact |
|-----------|--------|
| **Reliability** | Unhandled API errors in unified adapters crash the research pipeline under production load conditions |
| **Data Quality** | Lost cross-referencing capability in funding adapter reduces signal richness |
| **Maintainability** | 12 adapter files where 6 would suffice; fixes applied to wrong version go unnoticed |
| **Developer Experience** | No clear canonical version; onboarding requires archaeology to understand which adapter to use |
| **Error Observability** | Raw exceptions instead of structured domain errors make debugging significantly harder |

---

## Affected Files

| File | Issue |
|------|-------|
| `data/news_unified.py` | Missing error handling wrapper and retry logic |
| `data/news.py` | Old version — to be deleted after STORY-121 |
| `data/funding_unified.py` | Missing `news_api_key` parameter and error wrapper |
| `data/funding.py` | Old version — to be deleted after STORY-122 |
| `data/website_unified.py` | Missing early validation for empty website URL |
| `data/website.py` | Old version — to be deleted after STORY-123 |
| `data/linkedin.py` | Old version — to be deleted after parity confirmed |
| `data/patents.py` | Old version — to be deleted after parity confirmed |
| `data/web_search_news.py` | Old version — to be deleted after parity confirmed |

---

## Architectural Requirements

- All unified adapters must achieve full behavioral parity with their old counterparts before old files are removed
- Error handling must produce structured domain errors, not raw HTTP or library exceptions
- Retry logic must be provider-specific (different backoff profiles for NewsAPI vs. Crunchbase vs. generic HTTP)
- Input validation must occur before any network call is initiated
- Cross-referencing capabilities must be preserved as first-class features, not optional add-ons
- All imports across the codebase must reference unified adapter versions exclusively
- A developer-facing migration guide must document the consolidation and the canonical adapter interface

---

## Definition of Done (Epic Level)

- [ ] All four stories completed and accepted
- [ ] Zero references to old adapter filenames in `src/` (verified by grep)
- [ ] All adapter-related tests pass against unified versions only
- [ ] Migration guide published to `docs/`
- [ ] No regression in research pipeline integration tests

---

## Notes

The irony of this epic is that the original unification effort was correct in intent. `BaseRefreshConnector` is the right abstraction. The problem is that architectural correctness was treated as a proxy for functional correctness, and it isn't. A class that inherits from the right base but drops error handling is worse than the class it replaced — it looks right while behaving wrong.

STORY-124 (deletion of old files) should not be rushed. It is the final gate, not a cleanup task. Deleting the old adapters before parity is verified would remove the reference implementation that the unified adapters are supposed to match.

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
