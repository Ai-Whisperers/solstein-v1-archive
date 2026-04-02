# STORY-208: Add Confidence Score Preservation from Metric_Lineage

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P1 — High |
| **Size** | S (< 1 day) |
| **Epic** | EPIC-059 Input Validation & Graceful Degradation |
| **Created** | 2026-03-01 |
| **Risk** | Low — wiring existing data; no logic change |
| **Assigned** | — |
| **Depends On** | STORY-204 (Confidence Extraction) |

---

## Audit Verdict

**CONFIRMED CAPABILITY** — `Company.signal_confidences` is populated (STORY-204) but not used by scorers.

Current state:
- Confidence data extracted: ✅ (STORY-204)
- Confidence data stored: ✅ (Company model field)
- Confidence data used by scorer: ❌ (ScoringEngine ignores it)

Result: Metadata about data quality exists but is invisible to scoring logic.

---

## Problem Statement

The scoring engine weights all inputs equally, regardless of confidence. A revenue figure with 0.95 confidence is treated identically to one with 0.50 confidence.

Example:
- Company A: revenue=100M (confidence=0.95) → Score includes this heavily
- Company B: revenue=100M (confidence=0.50) → Score includes this equally

Both should not score identically if one input is half as confident.

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Scoring Accuracy | 🟡 Medium — Low-confidence inputs weighted equally |
| Data Quality Signals | 🟡 Medium — Quality metadata ignored |
| Score Explainability | 🟡 Medium — Can't explain confidence variance |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `src/solstein/analytics/scoring.py` | Scorer classes | Use `signal_confidences` for weighting |
| `src/solstein/presentation/narrative_generator.py` | Report generation | Include confidence in narratives |

---

## Dependencies

- **Hard**: STORY-204 (Company.signal_confidences population)
- **Blocks**: Nothing; enhances scoring

---

## Architectural Requirements

**REQ-1**: Scoring engine multiplies signal strength by confidence:
```
weighted_signal = signal_value * confidence_score
```

**REQ-2**: Narrative generator includes confidence in explanations:
```
"Revenue is $100M (78% confident)"
```

**REQ-3**: Default confidence 0.50 for data without metadata (neutral, not low).

---

## Acceptance Criteria

- [ ] `ScoringEngine.score()` uses `company.signal_confidences` values
- [ ] Low-confidence signals (0.50) contribute less to score than high-confidence (0.95)
- [ ] Narrative includes confidence: "Revenue: $100M (78% confident)"
- [ ] Default 0.50 confidence used for data without metadata
- [ ] Unit test: Two companies with same data but different confidence → different scores

---

## Definition of Done

- [ ] Confidence weighting integrated into scorers
- [ ] Narratives explain confidence
- [ ] Unit tests verify weighting behavior
- [ ] Score distribution stable (Phoenix/Salt/Lead percentages within 5%)

---

## Implementation Notes

### Weighting Pattern

```python
def score(self, company: Company) -> ScoreResult:
    revenue_signal = company.financials.revenue / MAX_REVENUE
    revenue_confidence = company.signal_confidences.get("revenue", 0.50)
    
    weighted_revenue = revenue_signal * revenue_confidence
    
    growth_signal = company.financials.growth_rate / MAX_GROWTH
    growth_confidence = company.signal_confidences.get("growth_rate", 0.50)
    
    weighted_growth = growth_signal * growth_confidence
    
    total_score = weighted_revenue * 0.5 + weighted_growth * 0.5
    # ...
```

### Files to Create/Modify

- `src/solstein/analytics/scoring.py` - Add confidence weighting
- `src/solstein/presentation/narrative_generator.py` - Include in narratives
- `tests/unit/test_scoring.py` - Test weighting behavior

### Risk Mitigation

- Score distribution could change significantly → Baseline before implementing, accept 5% variance
- Weighting could cause extreme score drops → Use confidence as multiplier, not replacement
- Old data without confidence → Default to 0.50 (neutral)

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | Confidence metadata extracted but unused by scorer |

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
