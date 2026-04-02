# STORY-222: Replace Static Relevance Ranking with Source Intelligence Scoring

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-061 Adaptive Research Planning and Source Intelligence |
| **Created** | 2026-03-11 |
| **Risk** | Medium |
| **Assigned** | - |

---

## Audit Verdict

`src/solstein/research/ai_research_orchestrator.py` uses `_rank_by_relevance()` with static keyword matching and hardcoded domain boosts. Ranking does not include explicit source reliability priors, cross-source diversity penalties, or field-specific trust calibration.

---

## Problem Statement

Search result ranking is currently too shallow, so top slots can be occupied by low-trust or redundant pages, reducing extraction quality and wasting scrape budget.

---

## Impact

| Dimension | Effect |
|-----------|--------|
| **Reliability** | High-confidence values can originate from weak sources |
| **Performance** | Query budget consumed by pages likely to fail or add no new evidence |
| **Maintainability** | Hardcoded boosts are brittle and hard to tune by market |
| **Business Quality** | Financial and strategic claims can be under-corroborated |

---

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|------------------|
| `src/solstein/research/ai_research_orchestrator.py` | Modify | Replace `_rank_by_relevance` scoring contract |
| `tests/unit/research/test_ai_research_orchestrator.py` | Create/Modify | Ranking tests for reliability/diversity behavior |
| `docs/research/AI_RESEARCH_GUIDE.md` | Modify | Document source intelligence policy |

---

## Dependencies

### Hard Dependencies (Must Complete First)
- None

### Soft Dependencies (Preferred Order)
- STORY-225 - benchmark harness should consume ranking telemetry

---

## Architectural Requirements

- **REQ-1**: Ranking score must include relevance, reliability prior, freshness, and diversity terms.
- **REQ-2**: Reliability priors must be externalized to a versioned policy table, not hardcoded in function body.
- **REQ-3**: Ranking output must preserve score components for auditability.
- **REQ-4**: Deterministic tie-breaking must be enforced for reproducible runs.

---

## Acceptance Criteria

- [ ] `_rank_by_relevance()` replaced by a composable scoring function with explicit components.
- [ ] Top-5 results include at least one official domain and one independent domain in benchmark cases.
- [ ] Score component breakdown is attached to selected source metadata.
- [ ] Unit tests cover ranking behavior under conflicting sources and duplicate domains.
- [ ] Benchmark delta report shows validated-source yield improvement against baseline.

---

## Definition of Done

### Tests Required
- [ ] Unit tests for weighted score components
- [ ] Unit tests for diversity penalty behavior
- [ ] Regression tests with fixed fixture queries

### Documentation Required
- [ ] Update research guide with scoring model and policy fields
- [ ] Add tuning notes for reliability priors

### Code Review Gate
- [ ] Reviewer confirms deterministic ordering for equal scores
- [ ] Reviewer confirms no hardcoded domain logic outside policy table

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Mis-weighted priors reduce relevance | Medium | Medium | Introduce benchmark A/B validation before default rollout |
| Added scoring complexity slows search | Low | Medium | Keep scoring O(n), avoid network in scoring path |

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-03-11 | @opencode | Created |

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
