# STORY-210: Add Robustness Tests for Incomplete Data Inputs

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P1 — High |
| **Size** | M (1–2 days) |
| **Epic** | EPIC-059 Input Validation & Graceful Degradation |
| **Created** | 2026-03-01 |
| **Risk** | Low — test-only; establishes safety net |
| **Assigned** | — |
| **Depends On** | STORY-206, STORY-207, STORY-209 |

---

## Audit Verdict

**CONFIRMED MISSING** — No test suite verifies behavior with incomplete data.

Current testing:
- Tests use complete, well-formed data (fixtures)
- Incomplete data scenarios never tested
- Silent None handling never verified
- Validation error handling untested

Result: Robustness is assumed, not verified. Edge cases slip through.

---

## Problem Statement

The scoring pipeline has never been tested with incomplete data. All test fixtures use complete data with all fields populated. Real data validation revealed silent failures with missing fields.

Scenarios not tested:
- Company with None growth_rate
- Company with None revenue
- Company with all financial fields missing
- Mixed batch (some complete, some incomplete)
- Negative growth rates, revenue > reasonable max, etc.

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Code Safety | 🔴 Critical — No verification of incomplete data handling |
| Regression Detection | 🔴 Critical — Edge cases slip through |
| Confidence | 🟠 High — Production robustness unverified |

---

## Affected Files

| File | Lines | Change Type |
|-------|-------|-------------|
| `tests/integration/test_robustness_incomplete_data.py` | NEW | Full test suite for incomplete data |

---

## Dependencies

- **Soft**: All EPIC-059 stories (implementation must be done first)
- **Blocks**: Nothing; safety improvement

---

## Architectural Requirements

**REQ-1**: Test suite covers scenarios:
1. Company with None growth_rate (but valid revenue, ai_score, employees)
2. Company with None revenue
3. Company with all financial fields None
4. Company with negative growth rate
5. Company with growth rate > 100%
6. Mixed batch (50% complete, 50% incomplete)
7. Completely empty company (all fields None)

**REQ-2**: For each scenario, verify:
- Validation catches it (if configured to validate)
- Scoring produces a score (possibly with reduced confidence)
- Warning is logged
- Export still works (doesn't crash)

**REQ-3**: Test uses realistic incomplete data (simulates real format mismatches).

---

## Acceptance Criteria

- [ ] Test: Company with None growth_rate → validation detects, warning logged
- [ ] Test: Company with None revenue → validation detects, warning logged
- [ ] Test: Company with all fields None → validation detects, scoring skipped or default score
- [ ] Test: Negative growth rate → validation detects, warning logged
- [ ] Test: Growth rate > 100% → validation detects, warning logged
- [ ] Test: Mixed batch (50% complete) → all scored, invalid count logged
- [ ] All 6+ scenarios tested
- [ ] Warnings are logged (verified via logger.call_count)
- [ ] No crashes on edge cases

---

## Definition of Done

- [ ] Comprehensive robustness test suite created
- [ ] All edge cases tested
- [ ] Validation behavior verified for incomplete data
- [ ] Scoring behavior verified (score or skip)
- [ ] Warning logging verified
- [ ] Export tested with incomplete data
- [ ] Tests pass and are added to CI/CD

---

## Implementation Notes

### Test Structure

```python
def test_company_with_none_growth_rate():
    """Company with missing growth_rate should log warning and score lower."""
    company = Company(
        name="Test Inc",
        revenue=1000.0,
        growth_rate=None,  # Missing
        ai_score=7.0,
        employees=100
    )
    
    # Validate
    with pytest.raises(ValidationError, match="growth_rate"):
        validate_company(company)
    
    # Score with warning
    with pytest.warns(UserWarning, match="growth_rate"):
        score = scorer.score(company)
        assert score.confidence < 1.0
        assert score.score < normal_score  # Lower than complete data

def test_mixed_batch_50_percent_incomplete():
    """Pipeline handles mixed batches gracefully."""
    companies = [
        Company(name="Complete 1", revenue=1000, growth_rate=5, ai_score=7, employees=100),
        Company(name="Incomplete 1", revenue=None, growth_rate=5, ai_score=7, employees=100),
        Company(name="Complete 2", revenue=2000, growth_rate=3, ai_score=6, employees=200),
        Company(name="Incomplete 2", revenue=3000, growth_rate=None, ai_score=7, employees=300),
    ]
    
    scores = [scorer.score(c) for c in companies]
    
    assert len(scores) == 4
    assert scores[0].confidence > scores[1].confidence
    assert scores[2].confidence > scores[3].confidence

def test_export_with_incomplete_data():
    """Export doesn't crash with incomplete data."""
    companies = [
        Company(name="Complete", revenue=1000, growth_rate=5, ai_score=7, employees=100),
        Company(name="Incomplete", revenue=None, growth_rate=None, ai_score=None, employees=0),
    ]
    
    scores = [scorer.score(c) for c in companies]
    excel = export_to_excel(scores)
    
    assert excel is not None  # Doesn't crash
    assert excel.getRow(2).getValue("revenue") is not None  # Complete row
    # Incomplete row has empty/default values
```

### Files to Create/Modify

- `tests/integration/test_robustness_incomplete_data.py` - Full robustness suite (NEW)
- `tests/fixtures/incomplete_data_scenarios.py` - Realistic incomplete data fixtures (NEW)

### Risk Mitigation

- Tests might reveal bugs in incomplete data handling → Expected; fix bugs found
- Test data might not match real incomplete formats → Use actual failed conversions as fixtures
- Performance impact → Run in separate CI job if needed

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | No tests for incomplete data; edge cases unverified |

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
