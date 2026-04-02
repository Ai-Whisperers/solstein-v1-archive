# STORY-229: Apply Freshness Windows and Evidence-Aware Export Trust Tiers

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-062 Scraping Resilience and Field Evidence Ledger |
| **Created** | 2026-03-11 |
| **Risk** | Medium |
| **Assigned** | - |

---

## Audit Verdict

Current cache reuse and carry-forward rely on completeness and staleness checks, but output trust signaling is not explicit in exports. Consumers cannot quickly distinguish corroborated vs thin evidence records.

---

## Problem Statement

Exports should communicate evidence quality and freshness explicitly so downstream analysis can weigh records correctly and prioritize review.

---

## Impact

| Dimension | Effect |
|-----------|--------|
| **Reliability** | Stale or weakly evidenced records may be over-trusted |
| **Business Quality** | Portfolio decisions may overweight low-trust entries |
| **Maintainability** | Manual review burden increases without trust tiers |

---

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|------------------|
| `src/solstein/research/ai_research_orchestrator.py` | Modify | Add per-field freshness policy and trust-tier computation |
| `scripts/generate_excel_dashboard.py` | Modify | Surface trust tier and quality reasons in dashboard metadata |
| `data/research_results/research_results.json` | Modify schema | Include export-quality summary per company |
| `tests/integration/test_export_trust_tiers.py` | Create | Validate trust-tier mapping and freshness behavior |

---

## Dependencies

### Hard Dependencies (Must Complete First)
- STORY-228

---

## Architectural Requirements

- **REQ-1**: Freshness policy must be field-class aware (static vs volatile).
- **REQ-2**: Trust tier must consider evidence count, source reliability, contradiction flags, and staleness.
- **REQ-3**: Export payload must include trust tier and reasons for downgrade.
- **REQ-4**: Excel/JSON outputs must preserve quality tier visibility for human review.

---

## Acceptance Criteria

- [ ] Trust tiers (`gold`, `silver`, `bronze`, `review-required`) computed and persisted for each company.
- [ ] Volatile fields are refreshed according to policy even when static profile fields are reused.
- [ ] Export metadata includes tier reasons and stale field summary.
- [ ] Dashboard displays trust tier without breaking current sheets.
- [ ] Integration tests verify tier downgrades for stale single-source financial claims.

---

## Definition of Done

### Tests Required
- [ ] Integration tests for freshness policy behavior
- [ ] Integration tests for trust-tier assignment matrix
- [ ] Snapshot test for export metadata compatibility

### Documentation Required
- [ ] Trust-tier rubric and examples
- [ ] Freshness policy table by field class

### Code Review Gate
- [ ] Reviewer confirms tier computation is deterministic and explainable
- [ ] Reviewer confirms no backward-incompatible export break without migration note

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Tier thresholds too strict/lenient | Medium | Medium | Start with configurable thresholds and benchmark feedback loop |
| Export consumers break on new metadata | Low | Medium | Keep additive schema changes and version output |

---

## Change Log

| Date | Author | Change |
|------|--------|--------|
| 2026-03-11 | @opencode | Created |

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
