# STORY-178: Map `funding_raised` to `financials.total_funding_raised` in Company Loaders

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P1 — High |
| **Size** | S (< half a day) |
| **Epic** | EPIC-047 Data Loading Fidelity |
| **Created** | 2026-03-01 |
| **Risk** | Low — additive field mapping |
| **Assigned** | — |

---

## Audit Verdict

**CONFIRMED BUG** — verified by live comparison on 2026-03-01.

```
Raw JSON:      "funding_raised": 2000000.0     (€2M)
Company obj:   financials.total_funding_raised = None    ← not mapped
```

Report output: `"No funding data available"` — despite €2M being in the source file.

The `GrowthMomentumScorer` awards `+2.0` for funding > €50M and `+1.0` for funding > €10M. While Eneve's €2M doesn't trigger these thresholds, the issue affects any company with meaningful funding: a startup with €15M would receive `+1.0` growth momentum that it's currently not getting.

---

## Problem Statement

The raw JSON key `funding_raised` (a top-level field) is not mapped to `Company.financials.total_funding_raised`. The loader skips it because of a key name mismatch. As a result:
1. The Growth Momentum and Financial Health scorers don't see funding data
2. Report financial sections say "No funding data" for funded companies
3. `funding_rounds` (structured array) from JSON is also not mapped

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Business Accuracy | 🟠 High — underestimates funding-driven companies |
| Scoring Correctness | 🟠 High — funded companies score lower than they should |
| Report Quality | 🟠 High — financial reports incorrectly state "no funding data" |
| Security | ⬜ None |
| Performance | ⬜ None |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `src/solstein/data/loaders.py` | `CompetitorDataLoader._map_fields()` | Add funding mapping |
| `src/solstein/data/unified_loader.py` | Same | Add funding mapping |
| `tests/unit/test_loaders.py` | Existing | Add funding field test |

---

## Dependencies

- **Hard**: Must fix in both loaders
- **Soft**: STORY-171 (once migrated to UnifiedCompanyLoader, one fix suffices)
- **Supersedes**: Nothing

---

## Architectural Requirements

**REQ-1**: Map `funding_raised` (number, top-level) → `company.financials.total_funding_raised` (float, EUR).

**REQ-2**: Map `funding_rounds` (array) → `company.funding_rounds` if field exists on Company model.

**REQ-3**: Map `valuation` (number, top-level) → `company.financials.valuation` or `company.latest_valuation_eur` (check which attribute exists on Company model).

**REQ-4**: If `funding_raised` is present as both top-level AND inside `funding_rounds` total, use the top-level value (already summed) and don't double-count.

---

## Acceptance Criteria

- [ ] `loader.load_companies()[eneve_index].financials.total_funding_raised == 2_000_000.0`
- [ ] Financial growth report for Eneve shows `€2.0M total funding raised` (not "No funding data")
- [ ] `GrowthMomentumScorer` for a company with `funding_raised = 12_000_000` receives the `+1.0` funding bonus
- [ ] `valuation` mapped: `latest_valuation_eur == 50_000_000.0` for Eneve
- [ ] Unit test: load fixture with `funding_raised: 15000000` and assert `financials.total_funding_raised == 15_000_000.0`

---

## Definition of Done

- [ ] Funding mapping added to both loaders
- [ ] Valuation mapping added
- [ ] Financial growth report no longer shows "No funding data" for Eneve
- [ ] Unit tests covering funding and valuation mapping
- [ ] Manual score comparison: company with €15M funding gets higher score than without

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | Confirmed via Company object dump and report output "No funding data" |

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
