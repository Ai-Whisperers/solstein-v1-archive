# EPIC-008: God File Decomposition

| Field | Value |
|-------|-------|
| Priority | P1 |
| Status | 🔴 Open |
| Stories | STORY-028, STORY-029, STORY-030, STORY-031 |
| Created | 2026-02-28 |

---

## Summary

A 1,223-line file is not a module — it is a liability.

Four files exceed the threshold of sustainable complexity. They have grown to their current size because they lack clear responsibility boundaries. Each file does multiple jobs, and no engineer can hold all of those jobs in mind simultaneously.

## The Offenders

| File | Lines | Classes | Methods | What It Does (All Of It) |
|------|-------|---------|---------|--------------------------|
| `exporters/markdown/generator.py` | 1,223 | 4 | 100+ | Company profiles, competitive analysis, financial tables, executive summaries, document assembly |
| `data/unified_loader.py` | 1,142 | - | - | File traversal, data parsing, schema validation, currency conversion, conflict detection, result aggregation |
| `api/routers/enrichment.py` | 793 | - | - | Enrichment initiation, status polling, result retrieval, data validation, statistical aggregation, business rules |
| `agents/github_agent.py` | 771 | 1 | - | API auth, repo listing, commit analysis, contributor profiling, tech detection, activity scoring, result aggregation |

These files are the most modified, most conflicted, and hardest to reason about in the entire codebase. Every modification to any part of the rendering pipeline requires navigating all 1,223 lines of `generator.py`. Every data loading change requires understanding all 1,142 lines of `unified_loader.py`.

## Decomposition Principles

Decomposition is not about hitting a line count target. It is about ensuring each module has a single, clear responsibility that can be understood, tested, and modified independently.

The guiding questions for each decomposition:
1. Can this module be described in one sentence without using "and"?
2. Can this module be tested without instantiating unrelated functionality?
3. Can a new engineer understand this module's purpose from its filename alone?

If the answer to any of these is "no," the module has too many responsibilities.

## Stories

| Story | Title | Priority | Severity | Dependencies |
|-------|-------|----------|----------|--------------|
| [STORY-028](STORIES/STORY-028-decompose-markdown-generator.md) | Decompose the Markdown Generator God File | P1 | HIGH | None |
| [STORY-029](STORIES/STORY-029-decompose-unified-loader.md) | Decompose the Unified Loader God File | P1 | HIGH | STORY-020 |
| [STORY-030](STORIES/STORY-030-decompose-enrichment-router.md) | Decompose the Enrichment Router God File | P1 | HIGH | STORY-027 |
| [STORY-031](STORIES/STORY-031-decompose-github-agent.md) | Decompose the GitHub Agent God File | P1 | MEDIUM | None |

## Definition of Done

- [ ] No module in the codebase exceeds 400 lines (routers: 200 lines)
- [ ] Each module has a single clear responsibility describable in one sentence
- [ ] All existing tests continue to pass after decomposition
- [ ] Each new module has its own test file
- [ ] Public interfaces are preserved — callers do not require changes

## Ordering Notes

STORY-028 (markdown generator) and STORY-031 (GitHub agent) have no dependencies and can start immediately. STORY-029 (unified loader) depends on STORY-020 (loader consolidation) — you must choose the canonical loader before decomposing it. STORY-030 (enrichment router) depends on STORY-027 (domain service extraction) — extracting business logic to services will naturally reduce the router's size before further decomposition.

Recommended execution order:
1. STORY-028 and STORY-031 in parallel (no dependencies)
2. STORY-020 → STORY-029 (consolidate, then decompose)
3. STORY-027 → STORY-030 (extract services, then decompose router)

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
