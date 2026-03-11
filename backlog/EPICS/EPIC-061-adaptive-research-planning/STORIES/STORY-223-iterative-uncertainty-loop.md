# STORY-223: Implement Iterative Uncertainty-Driven Research Loop

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | L (1-2 weeks) |
| **Epic** | EPIC-061 Adaptive Research Planning and Source Intelligence |
| **Created** | 2026-03-11 |
| **Risk** | High |
| **Assigned** | - |

---

## Audit Verdict

`research_company()` currently executes one planned query bundle and one optional adaptive pass. It does not iterate based on residual uncertainty after new evidence arrives.

---

## Problem Statement

The pipeline cannot dynamically reallocate effort as field certainty changes, so it often over-searches low-value areas and under-searches unresolved critical fields.

---

## Impact

| Dimension | Effect |
|-----------|--------|
| **Reliability** | Critical fields remain unresolved while budget is exhausted |
| **Performance** | Query/spider budget is spent inefficiently |
| **Maintainability** | Adaptive logic becomes ad hoc instead of policy-driven |

---

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|------------------|
| `src/solstein/research/ai_research_orchestrator.py` | Modify | Replace one-shot adaptive phase with iterative loop |
| `src/solstein/cli_ai_research.py` | Modify | Expose optional budget controls |
| `tests/integration/test_ai_research_loop.py` | Create | End-to-end loop behavior tests |

---

## Dependencies

### Hard Dependencies (Must Complete First)
- STORY-222 - requires improved source ranking

### Soft Dependencies (Preferred Order)
- STORY-224 - budget allocator should be integrated with loop scheduler

---

## Architectural Requirements

- **REQ-1**: Research must iterate in bounded cycles: search -> extract -> validate -> synthesize -> reassess.
- **REQ-2**: Next-query decisions must be based on missing and low-confidence target fields.
- **REQ-3**: Loop must support deterministic stop conditions (max cycles, min gain, max budget).
- **REQ-4**: Each cycle must record decision and result telemetry.

---

## Acceptance Criteria

- [ ] One-shot adaptive branch replaced by bounded iterative cycle engine.
- [ ] Stop conditions prevent unbounded retries and guarantee termination.
- [ ] Loop increases target-field completeness by >=10 points on benchmark set.
- [ ] Loop does not exceed configured per-company query and source budgets.
- [ ] Metadata includes per-cycle summary and field-state deltas.

---

## Definition of Done

### Tests Required
- [ ] Integration tests for convergence and stop conditions
- [ ] Failure-path test where blocked sources trigger graceful loop exit
- [ ] Performance test ensuring bounded runtime under configured budget

### Documentation Required
- [ ] Add cycle model diagram to research docs
- [ ] Document stop-condition policy and defaults

### Code Review Gate
- [ ] Reviewer confirms no loop can exceed configured max iterations
- [ ] Reviewer confirms cycle telemetry is complete and structured

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Iterative loop increases runtime | Medium | High | Enforce strict budgets and min-gain stop rule |
| More complexity in orchestrator | High | Medium | Extract cycle scheduler into isolated helper module |

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-03-11 | @opencode | Created |
