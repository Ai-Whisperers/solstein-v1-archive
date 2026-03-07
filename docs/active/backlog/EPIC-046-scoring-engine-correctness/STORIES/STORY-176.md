# STORY-176: Define Authoritative `classification → threat_level` Mapping in Constants

| Field | Value |
|-------|-------|
| **Status** | 🟡 Open |
| **Priority** | P1 — High |
| **Size** | S (half a day) |
| **Epic** | EPIC-046 Scoring Engine Correctness |
| **Created** | 2026-03-01 |
| **Risk** | Low — additive; existing code untouched |
| **Assigned** | — |

---

## Audit Verdict

**DESIGN GAP** — confirmed by code analysis and live run.

The relationship between `classification` (Phoenix/Salt/Lead) and `threat_level` (LOW/MEDIUM/HIGH/CRITICAL) is defined nowhere in the codebase. `GrowthScorer` sets `classification` but not `threat_level` (STORY-173). The `threat_level` is whatever came from the input JSON. There is no single authoritative source of truth for how these two fields relate.

---

## Problem Statement

`classification` and `threat_level` are derived metrics that represent the same underlying competitive assessment at different granularities. They should be deterministically related:
- `Phoenix` (disruptive, high-growth) = High or Critical threat
- `Salt` (established, slow) = Low or Medium threat (depending on score range)
- `Lead` (underperforming) = Low threat

Without a constants-level definition of this mapping, every module that needs to derive one from the other will implement its own interpretation, leading to inconsistencies across CLI output, API responses, reports, and exports.

Currently: `scoring.py`, `report_generator`, and `domain/models.py` each have independent interpretations.

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Maintainability | 🟠 High — mapping scattered across modules |
| Consistency | 🟠 High — API and reports may show different threat_level for same company |
| Business Accuracy | 🟠 High — inconsistent signals erode analyst trust |
| Security | ⬜ None |
| Performance | ⬜ None |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `src/solstein/analytics/constants.py` | New section | Add mapping + `derive_threat_level()` |
| `src/solstein/analytics/scoring.py` | ~133 | Import and use `derive_threat_level()` |
| `src/solstein/domain/models.py` | Optional | Document enum relationship |
| `tests/unit/analytics/test_constants.py` | New | Test mapping exhaustiveness |

---

## Dependencies

- **Hard**: Implemented in same PR as STORY-173 (scoring sets threat_level using this mapping)
- **Soft**: EPIC-048 (report generation uses threat_level from scoring)
- **Supersedes**: Nothing

---

## Architectural Requirements

**REQ-1**: Define `CLASSIFICATION_THREAT_RULES` as a data structure in `constants.py` that maps `(classification, min_score)` tuples to `ThreatLevel` values, checked in priority order (highest score threshold first).

**REQ-2**: Export a `derive_threat_level(classification: str, composite_score: float) -> ThreatLevel` function from `constants.py` that is the single call site for this derivation anywhere in the codebase.

**REQ-3**: Add a module-level docstring to `constants.py` explaining that all scoring thresholds and classification mappings live here, not in individual scorer files.

**REQ-4**: No hard-coded threat-level strings anywhere in the codebase outside `constants.py` — enforce via a linting comment.

---

## Acceptance Criteria

- [ ] `from solstein.analytics.constants import derive_threat_level` works
- [ ] `derive_threat_level("Phoenix", 8.37)` returns `ThreatLevel.HIGH`
- [ ] `derive_threat_level("Phoenix", 9.2)` returns `ThreatLevel.CRITICAL`
- [ ] `derive_threat_level("Salt", 6.5)` returns `ThreatLevel.MEDIUM`
- [ ] `derive_threat_level("Salt", 5.0)` returns `ThreatLevel.LOW`
- [ ] `derive_threat_level("Lead", 3.5)` returns `ThreatLevel.LOW`
- [ ] `grep -rn "ThreatLevel.HIGH\|ThreatLevel.CRITICAL" src/` (outside constants.py) returns 0 results — all derivations use the function
- [ ] Unit test covers all 5 input combinations above plus an unknown classification (should return `ThreatLevel.LOW` as safe default)

---

## Definition of Done

- [ ] `derive_threat_level()` exported from `constants.py`
- [ ] All call sites in codebase updated to use it
- [ ] Unit tests covering all mapping cases
- [ ] Docstring on `constants.py` explaining its role as single source of truth

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | Mapping gap identified via threat_level=Low for Phoenix company |
