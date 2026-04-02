# EPIC-061: Adaptive Research Planning and Source Intelligence

> **Priority**: P1 - High  
> **Stories**: 4 (STORY-222 through STORY-225)  
> **Effort**: L (2-3 weeks)  
> **Dependencies**: EPIC-050 (Web Acquisition Pipeline), EPIC-052 (Provenance, Confidence, and Quality Gates), EPIC-053 (Enrichment Observability and Evaluation Loop)  
> **Status**: 🔴 Not Started

---

## Problem

The current research orchestration can run end-to-end, but search and source selection still rely on shallow heuristics and one-shot planning.

Evidence in `src/solstein/research/ai_research_orchestrator.py`:

- `_rank_by_relevance()` uses keyword/domain boost rules with no calibration or diversity penalty.
- `research_company()` runs planned queries once and executes at most one adaptive pass.
- `_synthesize_data()` picks top-confidence values without robust cross-source adjudication.

This causes avoidable low-value scraping, weaker source quality in top results, and inconsistent completeness per company.

---

## Scope

| Category | Action |
|----------|--------|
| Search Decisioning | Replace one-shot planning with iterative, budgeted gap-closure loops |
| Source Ranking | Introduce deterministic source intelligence scoring with reliability priors |
| Query Budgeting | Allocate query budget by field uncertainty and business criticality |
| Decision Telemetry | Capture query/source decisions and outcomes for tuning |
| Evaluation | Add benchmark harness with measurable quality and efficiency KPIs |

---

## Stories

| Story | Title | Priority | Size | Status |
|-------|-------|----------|------|--------|
| STORY-222 | Replace static relevance ranking with source intelligence scoring | P1 | M | 🔴 Open |
| STORY-223 | Implement iterative uncertainty-driven research loop | P1 | L | 🔴 Open |
| STORY-224 | Add query budget allocator by field priority and expected value | P1 | M | 🔴 Open |
| STORY-225 | Build decision telemetry and benchmark runner for tuning | P1 | M | 🔴 Open |

---

## Target Integration Points

- `src/solstein/research/ai_research_orchestrator.py`
- `src/solstein/cli_ai_research.py`
- `scripts/run_incremental_market_pipeline.py`
- `data/research_results/research_memory.json`
- `data/research_results/research_results.json`

---

## Architectural Requirements

- **REQ-1**: Search planning must be iterative and stateful within a company run, not one-shot.
- **REQ-2**: Source ranking must combine relevance, reliability, freshness, and diversity signals.
- **REQ-3**: Query budget decisions must be explainable and persisted in run metadata.
- **REQ-4**: Adaptive search expansion must stop using deterministic stopping criteria.
- **REQ-5**: Every planning decision must emit telemetry suitable for offline tuning.

---

## Success Criteria

- Top-5 source set contains at least one official source and one independent source for >=80% of companies.
- Validated-source yield in top-5 increases by >=15 percentage points versus current baseline.
- Median queries per company decreases by >=20% without lowering target-field completeness.
- Target-field completeness increases by >=10 percentage points on benchmark set.
- Benchmark report is generated for every batch and stored with run artifacts.

---

## Risks

| Risk | Mitigation |
|------|------------|
| Overfitting source priors to one market | Version source scoring profiles by market and tune quarterly |
| Longer runtime from iterative loops | Add strict query/source caps and early-stop thresholds |
| More logic complexity in orchestrator | Keep planning and scoring helpers isolated and unit-tested |
| KPI drift unnoticed | Gate merges on benchmark delta reports in CI |

---

## Notes

This epic is the decision-quality layer of research. The objective is not "scrape more." The objective is to spend research budget where uncertainty is highest and return trusted, diverse evidence faster.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This epic currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently schedule this epic, treat it as triage-required backlog inventory instead of self-startable work.

### Next Agent Action

- Reconcile this epic against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before selecting a story.
- Do not start implementation from this README alone unless the queue or a fresh planning decision activates the epic.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Prefer narrow, machine-checkable progress over broad narrative backlog churn.

### Minimum Verification For Future Agents

- If this epic is reactivated, update the queue or controlling planning artifact first.
- Then execute one story at a time with the relevant tests, gates, and generated references for the touched surface.
