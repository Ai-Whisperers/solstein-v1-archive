# STORY-225: Build Decision Telemetry and Benchmark Runner for Tuning

| Field | Value |
|-------|-------|
| **Status** | 🔴 Open |
| **Priority** | P1 - High |
| **Size** | M (3-5 days) |
| **Epic** | EPIC-061 Adaptive Research Planning and Source Intelligence |
| **Created** | 2026-03-11 |
| **Risk** | Low |
| **Assigned** | - |

---

## Audit Verdict

Current metadata includes useful counters (`sources_found`, `sources_used`, adaptive flags) but does not persist full decision telemetry needed to tune planning and ranking safely.

---

## Problem Statement

Without benchmarkable telemetry, improvements to ranking, planning, and scraping cannot be validated objectively and regressions are hard to catch.

---

## Impact

| Dimension | Effect |
|-----------|--------|
| **Reliability** | Regression risk in ranking/planning changes |
| **Maintainability** | Tuning depends on anecdotal observations |
| **Performance** | No feedback loop for query-cost vs quality tradeoff |

---

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|------------------|
| `src/solstein/research/ai_research_orchestrator.py` | Modify | Emit structured decision events |
| `scripts/run_incremental_market_pipeline.py` | Modify | Add benchmark mode and output paths |
| `scripts/benchmark_research_pipeline.py` | Create | Batch evaluation harness and KPI report |
| `docs/research/AI_RESEARCH_IMPROVEMENTS.md` | Modify | KPI definitions and usage |

---

## Dependencies

### Hard Dependencies (Must Complete First)
- STORY-222, STORY-223, STORY-224

---

## Architectural Requirements

- **REQ-1**: Every research cycle must emit machine-readable decision events.
- **REQ-2**: Benchmark runner must compare baseline vs candidate metrics from identical input sets.
- **REQ-3**: KPI report must include completeness, source-yield, query-cost, and runtime percentiles.
- **REQ-4**: Benchmark outputs must be persistable as JSON artifacts for CI gating.

---

## Acceptance Criteria

- [ ] Benchmark script runs on a fixed company set and produces a deterministic report.
- [ ] KPI report includes at least: completeness by field, validated-source yield, median queries/company, P50/P95 runtime.
- [ ] Candidate run can be compared against baseline with delta summary.
- [ ] CI can fail on configurable quality regression thresholds.
- [ ] Telemetry schema is documented and versioned.

---

## Definition of Done

### Tests Required
- [ ] Unit tests for telemetry schema serialization
- [ ] Integration test for benchmark report generation

### Documentation Required
- [ ] Add benchmark operation guide
- [ ] Add KPI glossary and threshold recommendations

### Code Review Gate
- [ ] Reviewer confirms benchmark inputs are fixed and reproducible
- [ ] Reviewer confirms no PII leakage in telemetry payloads

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Benchmark dataset not representative | Medium | Medium | Use stratified market sample and refresh periodically |
| Telemetry volume growth | Medium | Low | Add retention policy and compact schema |

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
