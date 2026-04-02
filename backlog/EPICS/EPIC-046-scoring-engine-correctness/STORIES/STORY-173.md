# STORY-173: Derive `threat_level` from Composite Score and Classification After Scoring

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P0 — Critical |
| **Size** | S (< 1 day) |
| **Epic** | EPIC-046 Scoring Engine Correctness |
| **Created** | 2026-03-01 |
| **Risk** | Low — surgical addition of 4 lines |
| **Assigned** | — |

---

## Audit Verdict

**CONFIRMED BUG** — verified by live execution on 2026-03-01.

```python
# src/solstein/analytics/scoring.py — GrowthScorer.calculate_scores()
# Lines 110–133 (approximate):
profile.growth_score = growth_score
profile.financial_health_score = fin_score
profile.competitive_position_score = comp_score
profile.composite_score = round(composite, 2)
profile.classification = classify_company(composite_score)
# ← MISSING: profile.threat_level is never set here
return profile
```

Live evidence:
```
Eneve composite_score = 8.37  → classification = Phoenix  → threat_level = "Low"  ← WRONG
```

`threat_level` retains whatever value was in the input JSON. For Eneve, the input had `threat_level: "Low"` and it was never overridden.

---

## Problem Statement

`threat_level` is one of the primary outputs shown in dashboards, reports, and export files. PE/VC analysts use it to triage which companies require immediate attention. A `Phoenix`-classified company (composite score ≥ 7.0) represents a high competitive threat by definition, yet the system reports "Low" threat level — the exact opposite of the correct signal.

The bug exists because `GrowthScorer.calculate_scores()` sets `classification` but never derives `threat_level` from it. The classification and threat_level are not independent — one should always follow from the other.

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Business Accuracy | 🔴 Critical — primary analyst-facing signal is wrong |
| Reliability | 🔴 Critical — outputs are self-contradictory (Phoenix + Low threat) |
| Security | ⬜ None |
| Performance | ⬜ None |
| Maintainability | 🟡 Medium — two related fields maintained independently |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `src/solstein/analytics/scoring.py` | ~133 (after classification line) | Add 4 lines |
| `src/solstein/analytics/constants.py` | New section | Add mapping dict |
| `tests/unit/analytics/test_scoring_correctness.py` | New | Test all mappings |

---

## Dependencies

- **Hard**: STORY-176 (authoritative mapping in constants) — implement simultaneously or derive inline
- **Soft**: STORY-173 is prerequisite for EPIC-048 (report quality) to show correct threat_level
- **Supersedes**: Nothing

---

## Architectural Requirements

**REQ-1**: `threat_level` must be derived deterministically from `composite_score` AND `classification` — no randomness, no external input.

**REQ-2**: The mapping must live in `src/solstein/analytics/constants.py` (see STORY-176) — not hardcoded in `scoring.py`.

**REQ-3**: The mapping rules (from domain expert analysis):

| Classification | Composite Score | `threat_level` |
|----------------|----------------|----------------|
| Phoenix | ≥ 9.0 | `CRITICAL` |
| Phoenix | ≥ 7.0 | `HIGH` |
| Salt (competitive) | 6.0–6.9 | `MEDIUM` |
| Salt (neutral) | 4.0–5.9 | `LOW` |
| Lead | ≤ 4.0 | `LOW` |

**REQ-4**: `threat_level` must be set to a `ThreatLevel` enum value (not a raw string) to leverage type safety.

---

## Acceptance Criteria

- [ ] Eneve: composite=8.37 → classification=Phoenix → threat_level=HIGH
- [ ] A company with composite=9.5 → classification=Phoenix → threat_level=CRITICAL
- [ ] A company with composite=5.5 → classification=Salt → threat_level=LOW
- [ ] A company with composite=6.5 → classification=Salt → threat_level=MEDIUM
- [ ] A company with composite=3.0 → classification=Lead → threat_level=LOW
- [ ] `threat_level` is a `ThreatLevel` enum value, not a raw string
- [ ] Input JSON `threat_level` field is ignored (overwritten by scorer)
- [ ] Unit tests cover all 5 mapping cases above

---

## Implementation Note

```python
# constants.py — add:
CLASSIFICATION_THREAT_MAPPING = {
    ("Phoenix", 9.0): ThreatLevel.CRITICAL,
    ("Phoenix", 7.0): ThreatLevel.HIGH,
    ("Salt", 6.0): ThreatLevel.MEDIUM,
    ("Salt", 0.0): ThreatLevel.LOW,
    ("Lead", 0.0): ThreatLevel.LOW,
}

def derive_threat_level(classification: str, composite_score: float) -> ThreatLevel:
    if classification == "Phoenix":
        return ThreatLevel.CRITICAL if composite_score >= 9.0 else ThreatLevel.HIGH
    elif classification == "Salt" and composite_score >= 6.0:
        return ThreatLevel.MEDIUM
    return ThreatLevel.LOW

# scoring.py — add after classification line:
profile.threat_level = derive_threat_level(profile.classification, composite)
```

---

## Definition of Done

- [ ] `threat_level` correctly set for all 3 companies in `data/input/competitor_data.json`
- [ ] Unit test: `test_threat_level_derived_from_classification_and_score`
- [ ] `generate-report` output shows correct threat_level (visual verification)
- [ ] Code review: reviewer checks that old `threat_level` from input is always overwritten

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | Eneve scored Phoenix/8.37 but threat_level=Low confirmed via live run |

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
