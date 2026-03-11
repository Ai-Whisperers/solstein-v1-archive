# STORY-227: Add Extraction Contract with Unit Normalization and Contradiction Flags

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P0 - Ship Blocker |
| **Size** | L (1-2 weeks) |
| **Epic** | EPIC-062 Scraping Resilience and Field Evidence Ledger |
| **Created** | 2026-03-11 |
| **Risk** | High |
| **Assigned** | - |

---

## Audit Verdict

Extraction currently returns numeric values with inconsistent scale/currency interpretation. Validation checks numeric ranges, but does not enforce a unified unit contract across sources before synthesis.

---

## Problem Statement

Without canonical units and contradiction signaling, synthesized financial fields can look precise but be semantically wrong (for example millions vs billions).

---

## Impact

| Dimension | Effect |
|-----------|--------|
| **Reliability** | Financial outputs can be materially incorrect |
| **Business Quality** | Tiering and competitiveness scoring become unstable |
| **Compliance** | Auditability weak when value origins are ambiguous |

---

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|------------------|
| `src/solstein/research/ai_research_orchestrator.py` | Modify | Extend extraction payload contract and normalization pipeline |
| `tests/unit/research/test_numeric_normalization.py` | Create | Unit/currency normalization and contradiction tests |
| `docs/research/AI_RESEARCH_GUIDE.md` | Modify | Canonical numeric contract documentation |

---

## Dependencies

### Hard Dependencies (Must Complete First)
- STORY-226

---

## Architectural Requirements

- **REQ-1**: Numeric fields must include value, unit scale, currency, and normalization confidence.
- **REQ-2**: Ambiguous unit/currency extraction must be flagged explicitly, not silently coerced.
- **REQ-3**: Contradictory source claims must be recorded in synthesis metadata.
- **REQ-4**: Canonical output contract must define allowed numeric units and conversion rules.

---

## Acceptance Criteria

- [ ] Revenue/funding/valuation each carry normalized value and unit metadata.
- [ ] Ambiguous extractions are tagged and excluded from canonical winner selection by default.
- [ ] Contradiction flags emitted when two high-confidence sources disagree beyond threshold.
- [ ] Unit tests cover millions/billions/currency symbol and localized formatting cases.
- [ ] Benchmark report includes contradiction rate and normalized-field coverage metrics.

---

## Definition of Done

### Tests Required
- [ ] Unit tests for normalization conversion matrix
- [ ] Unit tests for contradiction detection logic
- [ ] Integration test for extraction-to-synthesis numeric contract

### Documentation Required
- [ ] Numeric normalization spec and examples
- [ ] Contract versioning note for downstream exporters

### Code Review Gate
- [ ] Reviewer confirms no untyped numeric passthrough remains for financial fields
- [ ] Reviewer confirms contradiction metadata is persisted and observable

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| False contradiction alerts | Medium | Medium | Tune thresholds by source reliability class |
| Overly strict normalization drops data | Medium | Medium | Add unknown-unit state and warn-mode rollout |

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-03-11 | @opencode | Created |
