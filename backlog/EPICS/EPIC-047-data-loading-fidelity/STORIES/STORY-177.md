# STORY-177: Fix `ai_score` Float Truncation in Company Loaders

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P1 — High |
| **Size** | S (< half a day) |
| **Epic** | EPIC-047 Data Loading Fidelity |
| **Created** | 2026-03-01 |
| **Risk** | Low — fix float coercion; no logic change |
| **Assigned** | — |

---

## Audit Verdict

**CONFIRMED BUG** — verified by live comparison of raw JSON vs Company object on 2026-03-01.

```
Raw JSON:      "ai_score": 7.5
Company obj:   company.ai_score = 7      ← truncated
```

The Company domain model declares `ai_score` as `int` or applies `int()` coercion during loading. All fractional AI scores are silently truncated.

---

## Problem Statement

`ai_score` is on a 0–10 scale. The difference between `7.0` and `7.5` is 7% relative error. The `PHOENIX_SCORE_THRESHOLD = 7.0` means a company with `ai_score=6.9` could be mis-classified if it was loaded as `7` (rounds up) from JSON `6.9`. Or a company with `ai_score=7.0` from JSON `7.4` loses meaningful signal about its AI strength.

The `ai_score` field is used in `CompetitivePositionScorer` and in report narratives — both are affected.

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Business Accuracy | 🟠 High — systematic 0–0.5 point error on all AI scores |
| Scoring Correctness | 🟡 Medium — affects competitive position sub-score |
| User Trust | 🟡 Medium — analysts who double-check raw data see discrepancy |
| Security | ⬜ None |
| Performance | ⬜ None |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `src/solstein/data/loaders.py` | `CompetitorDataLoader` ai_score handling | Fix type coercion |
| `src/solstein/data/unified_loader.py` | `UnifiedCompanyLoader` ai_score handling | Fix same bug here |
| `src/solstein/domain/models.py` | `Company.ai_score` field type | Change `int` → `float` if typed as int |
| `tests/unit/test_loaders.py` | Existing | Add float preservation test |

---

## Dependencies

- **Hard**: Must fix in BOTH `CompetitorDataLoader` AND `UnifiedCompanyLoader`
- **Soft**: STORY-171 (loader migration) — once migrated, only one loader needs the fix
- **Supersedes**: Nothing

---

## Architectural Requirements

**REQ-1**: `Company.ai_score` must be typed as `float`, not `int` or `Optional[int]`.

**REQ-2**: All loading paths must preserve the raw float value — no `int()` coercion, no rounding.

**REQ-3**: Validation: if `ai_score > 10` or `ai_score < 0`, log a warning and clamp to [0, 10].

---

## Acceptance Criteria

- [ ] `CompetitorDataLoader().load_companies()[0].ai_score == 7.5` for Eneve (was 7)
- [ ] `UnifiedCompanyLoader().load_companies()[0].ai_score == 7.5` for Eneve
- [ ] `Company(ai_score=7.5).ai_score == 7.5` (domain model preserves float)
- [ ] `Company(ai_score=7).ai_score == 7.0` (int input converted to float cleanly)
- [ ] Unit test: load fixture JSON with `ai_score: 7.5` and assert `== 7.5`
- [ ] Unit test: `ai_score: 0` stays `0.0`, `ai_score: 10` stays `10.0`

---

## Definition of Done

- [ ] Fix applied in both loaders and domain model
- [ ] Unit tests added
- [ ] Manual run: Eneve `ai_score` shows `7.5` not `7`

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | Confirmed via Company object attribute dump during live trace |
