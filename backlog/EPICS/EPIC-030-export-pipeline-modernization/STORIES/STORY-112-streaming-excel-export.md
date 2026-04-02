# STORY-112: Streaming Excel Export for Large Datasets

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-030: Export Pipeline Modernization |
| **Created** | 2026-03-01 |
| **Dependencies** | STORY-111 |

## The Audit Verdict

> `src/solstein/exporters/excel.py` — uses OpenPyXL, builds entire workbook in memory before writing. For datasets >10k rows, this causes OOM kills on the Celery worker.

## Problem Statement

OpenPyXL's default mode loads the entire workbook into memory. A portfolio analysis export covering 500 companies with full signal history can easily exceed 500MB in memory. On a Celery worker with a 512MB limit, this is an OOM kill — the task dies, appears as a failure, and the export is never delivered. OpenPyXL supports a write-only streaming mode that generates Excel row-by-row, keeping memory constant regardless of dataset size. This is not a nice-to-have; it is a correctness requirement for any export beyond a toy dataset.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Reliability** | OOM kills on real-scale exports |
| **Scalability** | Export size is bounded by worker RAM, not dataset size |

## Affected Files

| File | Issue |
|------|-------|
| `src/solstein/exporters/excel.py` | Loads entire workbook into memory |

## Architectural Requirements

- OpenPyXL write_only mode used for all Excel exports
- Memory usage is O(1) relative to dataset size (constant, not proportional to row count)
- Streaming write to a temporary file or io.BytesIO buffer, then upload to Supabase Storage (STORY-105)
- Excel export supports multi-sheet: Summary, Companies, Signals, Financials — each sheet streamed independently
- Column width auto-calculation disabled in streaming mode (document this limitation)
- Export tested with a 10,000-row synthetic dataset — memory usage documented in story notes
- Progress reporting: export task updates `progress_pct` in export_jobs table as each sheet completes

## Acceptance Criteria

- [ ] 10,000-row export completes without OOM
- [ ] Memory usage during export does not exceed 256MB
- [ ] Multi-sheet export (Summary, Companies, Signals, Financials) generates correctly
- [ ] Progress percentage updates in export_jobs table as sheets complete

## Definition of Done

- **Tests Required**: Memory profile test: export 10k rows, measure peak memory
- **Documentation Required**: Memory usage documentation
- **Code Review Gate**: Reviewer verifies no `.save()` call on a fully-materialized workbook

## Notes

Streaming is required for production-scale exports.

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
