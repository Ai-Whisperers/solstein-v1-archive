# EPIC-061: Adaptive Research Planning and Source Intelligence

> **Priority**: P1 - High  
> **Stories**: 4 ([STORY-222](STORIES/STORY-222-source-intelligence-scoring.md) through [STORY-225](STORIES/STORY-225-decision-telemetry-benchmark.md))  
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
| [STORY-222](STORIES/STORY-222-source-intelligence-scoring.md) | Replace static relevance ranking with source intelligence scoring | P1 | M | 🔴 Open |
| [STORY-223](STORIES/STORY-223-iterative-uncertainty-loop.md) | Implement iterative uncertainty-driven research loop | P1 | L | 🔴 Open |
| [STORY-224](STORIES/STORY-224-query-budget-allocator.md) | Add query budget allocator by field priority and expected value | P1 | M | 🔴 Open |
| [STORY-225](STORIES/STORY-225-decision-telemetry-benchmark.md) | Build decision telemetry and benchmark runner for tuning | P1 | M | 🔴 Open |

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
