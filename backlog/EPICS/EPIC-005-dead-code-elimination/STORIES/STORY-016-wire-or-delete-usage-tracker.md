# STORY-016: Wire or Delete the UsageTracker Class

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | MEDIUM |
| Epic | [EPIC-005: Dead Code Elimination](../README.md) |
| Created | 2026-02-28 |
| Dependencies | None |

---

## The Audit Verdict

> `llm/enhanced_client.py` lines 591–661 define a 70-line `UsageTracker` class with methods for recording token counts, cost estimates, and provider-level usage statistics. It is never imported anywhere. It is never instantiated. It tracks nothing. It is a ghost class.

## Problem Statement

`UsageTracker` was built — apparently with care — and then abandoned. It has methods for recording token usage, estimating costs, and producing provider-level statistics. None of these methods are called from anywhere in the codebase. Meanwhile, the business operates multiple LLM providers (Ollama, OpenAI, Groq, Fireworks) with no visibility into per-provider API spend, per-request token consumption, or aggregate cost trends.

This is a binary decision: either `UsageTracker` is wired into the LLM call path and begins tracking real usage, or it is deleted to stop misleading future developers into thinking usage tracking exists.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Operational Cost** | No LLM cost data available for budget management or provider selection |
| **Business** | Cannot attribute analysis costs to specific clients, jobs, or research pipelines |
| **Developer Confusion** | The class's existence implies usage tracking is implemented — it is not |
| **Dead Code Tax** | 70 lines of maintained-looking code that does nothing |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/llm/enhanced_client.py` | Modify | Lines 591–661: UsageTracker class — wire or delete |
| All LLM call sites | Modify (if wiring) | Must invoke UsageTracker at each LLM call |
| `src/solstein/llm/health_checker.py` | Evaluate | May need to interact with usage tracking |
| Logging/metrics infrastructure | Modify (if wiring) | Must persist or emit usage data |

## Architectural Requirements

- **REQ-1**: A decision must be made — wire `UsageTracker` into the LLM call path, or delete it entirely
- **REQ-2**: If wired, `UsageTracker` must record actual token counts and cost estimates at each LLM invocation across all providers
- **REQ-3**: If deleted, all related dead methods, imports, and references must be removed — no orphaned fragments
- **REQ-4**: If wired, usage data must be persisted or emitted to an observable store (structured log, Prometheus metric, database table, or similar)

## Acceptance Criteria

- [ ] `UsageTracker` is either:
  - (a) Called at every LLM invocation and usage data is observable via logs, metrics, or database queries, **OR**
  - (b) Entirely absent from the codebase — `grep -r "UsageTracker" .` returns zero results
- [ ] No orphaned class or dead methods exist in `enhanced_client.py`

## Definition of Done

**Tests Required:**
- [ ] If wired: unit test confirming a mock LLM call records usage in `UsageTracker` (token count, cost estimate, provider name)
- [ ] If deleted: `grep -r "UsageTracker" .` confirms complete absence from the codebase

**Documentation Required:**
- [ ] If wired: inline documentation describing the usage tracking data flow (where data is recorded, where it is stored, how to query it)
- [ ] If deleted: commit message documenting the decision to remove rather than wire

**Code Review Gate:**
- [ ] Reviewer confirms either full wiring or complete removal — no partial state

## Notes

The "wire" path is more valuable to the business but has a larger scope. If wiring is chosen, the minimum viable implementation is: record token count + estimated cost per LLM call to a structured log. Database persistence and dashboarding can follow in a separate story. The "delete" path is faster and eliminates the dead code immediately. Either outcome is acceptable — the current state of "exists but does nothing" is the only unacceptable outcome.

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
