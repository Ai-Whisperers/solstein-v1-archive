# STORY-207: Add None-Safety to GrowthScorer.score()

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P1 — High |
| **Size** | M (1–2 days) |
| **Epic** | EPIC-059 Input Validation & Graceful Degradation |
| **Created** | 2026-03-01 |
| **Risk** | Low — defensive checks; no logic change |
| **Assigned** | — |
| **Depends On** | STORY-206 (Company Validation) |

---

## Audit Verdict

**CONFIRMED DEFECT** — The `GrowthScorer` in `src/solstein/analytics/scoring.py` silently handles None values from incomplete data.

Current behavior:
```python
growth_score = (company.financials.growth_rate or 0) * 0.5  # None → 0 silently
# If growth_rate is None, it becomes 0, reducing the score by 50%
```

Silent None handling masks data quality issues. When data is incomplete, the scorer should:
1. Return a score with reduced confidence
2. Log a warning explaining why
3. Not silently substitute default values

---

## Problem Statement

The scorer contains defensive code that hides data quality problems:
- `company.growth_rate or 0` → Silent None handling
- `company.revenue or 0` → Hides missing financial data  
- No warnings logged
- Confidence not adjusted for missing data

Result: A company with no data gets a low score indistinguishable from a company with poor data.

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Transparency | 🔴 Critical — Silent failures hide incomplete data |
| Scoring Accuracy | 🟡 Medium — Low scores not explained |
| Debuggability | 🟡 Medium — Hard to trace why score is low |
| Data Quality Signals | 🟠 High — Missing data not flagged |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `src/solstein/analytics/scoring.py` | `GrowthScorer.score()` | Replace silent or with explicit None checks and warnings |

---

## Dependencies

- **Hard**: STORY-206 (Company Validation)
- **Blocks**: STORY-209

---

## Architectural Requirements

**REQ-1**: When a critical field is None:
1. Log a warning: `"Company {name}: {field} is None, reducing confidence"`
2. Return a score with lowered confidence
3. Document in score narrative why confidence is low

**REQ-2**: If too many fields are None (>50%), return minimum score (1.0) with warning.

**REQ-3**: No silent `or 0` substitutions — explicit handling for every None.

---

## Acceptance Criteria

- [ ] `GrowthScorer.score(company_with_none_growth_rate)` logs warning
- [ ] Score returned is lower than for company with data
- [ ] Confidence in score is reduced when fields are None
- [ ] If >50% of fields are None, score is 1.0 and warning is logged
- [ ] Unit test: Load company with None fields → verify warning logged
- [ ] Unit test: Score with None vs. with data → verify score difference

---

## Definition of Done

- [ ] All None handling is explicit with warnings
- [ ] Confidence reduced for incomplete data
- [ ] Unit tests verify warning logging
- [ ] No silent `or 0` substitutions remain
- [ ] Score narratives explain low confidence

---

## Implementation Notes

### Pattern

```python
def score(self, company: Company) -> ScoreResult:
    score = 0.0
    confidence = 1.0
    warnings = []
    
    if company.financials.growth_rate is None:
        logger.warning(f"Company {company.name}: growth_rate is None")
        warnings.append("growth_rate data missing")
        confidence -= 0.2  # Reduce confidence
    else:
        score += company.financials.growth_rate * 0.5
    
    if company.financials.revenue is None:
        logger.warning(f"Company {company.name}: revenue is None")
        warnings.append("revenue data missing")
        confidence -= 0.2
    else:
        score += min(company.financials.revenue / MAX_REVENUE, 1.0) * 0.3
    
    # ... similar for other fields
    
    return ScoreResult(
        score=score,
        confidence=max(confidence, 0.0),
        warnings=warnings
    )
```

### Files to Create/Modify

- `src/solstein/analytics/scoring.py` - Replace silent None handling
- `tests/unit/test_scoring.py` - Add None handling tests

### Risk Mitigation

- Logging could be too verbose → Use debug level
- Confidence reduction could lower scores too much → Use 0.1–0.2 per missing field
- Existing code might break → Test against real data first

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | Silent None handling masks data quality issues |

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
