# STORY-224: Add Query Budget Allocator by Field Priority and Expected Value

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

The current query budget is largely static (`plan.queries[:6]`, fixed max sources), with no explicit expected-value model by field criticality or current confidence.

---

## Problem Statement

Without budget allocation policy, the system can over-invest in easily discoverable fields and under-invest in high-value unresolved fields (revenue, funding, valuation, headquarters).

---

## Impact

| Dimension | Effect |
|-----------|--------|
| **Reliability** | Important fields remain unresolved despite available budget |
| **Performance** | Extra queries provide low marginal value |
| **Business Quality** | Ranking/exports skewed by uneven data depth |

---

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|------------------|
| `src/solstein/research/ai_research_orchestrator.py` | Modify | Add budget allocator and integrate with planning loop |
| `src/solstein/research/market_catalogs.py` | Modify (optional) | Add market-level field priority profiles |
| `tests/unit/research/test_budget_allocator.py` | Create | Deterministic budget allocation tests |

---

## Dependencies

### Hard Dependencies (Must Complete First)
- STORY-223 - iterative loop needed to consume dynamic budgets

---

## Architectural Requirements

- **REQ-1**: Budget allocator must compute per-field query quotas from criticality, missingness, and confidence.
- **REQ-2**: Allocator must be deterministic for identical inputs.
- **REQ-3**: Allocation policy must be configurable by market/industry profile.
- **REQ-4**: Allocator must emit explainable decision metadata.

---

## Acceptance Criteria

- [ ] Query allocation reflects field priority profile and residual uncertainty.
- [ ] Median queries per company reduced by >=20% with no completeness regression.
- [ ] Allocation decisions logged in run metadata for each cycle.
- [ ] Unit tests validate deterministic output for fixed inputs.
- [ ] Policy can be adjusted without code changes to algorithm core.

---

## Definition of Done

### Tests Required
- [ ] Unit tests for allocation calculation edge cases
- [ ] Integration test with iterative loop to verify budget enforcement

### Documentation Required
- [ ] Document field priority profile schema
- [ ] Add tuning guide for budget parameters

### Code Review Gate
- [ ] Reviewer confirms allocator cannot exceed hard budget caps
- [ ] Reviewer confirms clear metadata for each allocation decision

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Misconfigured field priorities | Medium | Medium | Provide safe defaults and schema validation |
| Too strict caps reduce completeness | Low | Medium | Add guardrail to re-balance budget if core fields remain empty |

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-03-11 | @opencode | Created |
