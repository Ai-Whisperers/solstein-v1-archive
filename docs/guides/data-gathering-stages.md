# Data Gathering Stages (Deep Research Flow)

This document explains the full data-input flow used to build company intelligence JSON artifacts, including what happens at each stage, expected outputs, quality gates, and examples.

## Why this flow exists

For PE/shareholder-grade analysis, we need:

- deterministic data collection logic,
- explicit source traceability,
- contradiction visibility,
- explainable values for every important metric,
- machine-checkable quality gates before scoring is trusted.

## End-to-end stage map

Primary orchestration:

- `src/solstein/research/pipeline.py`
- script entrypoint: `scripts/discover_and_research_market.py`

Markdown ingestion path:

- `src/solstein/extractors/markdown_extractor.py`
- script entrypoint: `scripts/run_market_pipeline.py`

### Stage 0 - Seed + Scope

Inputs:

- `seed_company` (for example: `Eneve`, `ueno`)
- `market` (for example: `Dutch Energy Software`, `LATAM Financial Services`)
- optional keywords (`energy`, `bank`, `payments`, etc.)

Expected result:

- A clear scope for discovery and relevance ranking.

Output artifact:

- none yet; parameters flow into Stage 1.

### Stage 1 - Discovery

Code:

- `src/solstein/research/discovery.py`

What happens:

- Build candidate universe from market catalog + expansion rules.
- Rank candidates by seed similarity, market match, and keyword/tag overlap.
- Capture discovery reason and candidate source links.

Output artifact:

- `discovery_candidates.json`

Expected fields per candidate:

- `company_id`, `name`, `market`, `ticker`, `industry`, `region`
- `tags`, `seed_relevance`, `discovery_reason`, `source_links`

Example snippet:

```json
{
  "company_id": "volue-asa",
  "name": "Volue ASA",
  "market": "Dutch Energy Software",
  "ticker": "VOLUE.OL",
  "seed_relevance": 4.5,
  "discovery_reason": "keyword tag overlap, market region match",
  "source_links": [
    "https://www.volue.com/",
    "https://finance.yahoo.com/quote/VOLUE.OL/"
  ]
}
```

### Stage 2 - Gather / Enrichment

Code:

- `src/solstein/research/gather.py`

What happens:

- For each candidate, gather factual values (ticker-backed when available).
- Always emit source links and per-metric source mapping.
- For missing direct evidence, emit explicit justifications.
- Emit `metric_observations` for reconciliation/contradiction logic.

Output artifact:

- `extracted.json`

Expected fields per company profile:

- `source_links`
- `metric_sources`
- `metric_justifications`
- `metric_observations`
- core company + financial fields

### Stage 2.1 - Source Volume Gate (optional but recommended)

Code:

- `src/solstein/research/pipeline.py` (`min_total_sources`)

What happens:

- Count total unique sources across all discovered companies.
- Fail early if below threshold.

Output artifact:

- `stage_report.json` (with failed gate details)

CLI option:

- `--min-total-sources N`

Notes:

- This gate is critical for deep-research targets (for example: 300+ sources).

### Stage 3 - Provenance Validation

Code:

- `src/solstein/extractors/markdown_extractor.py`
- validator methods used by pipeline

What happens:

- Required metrics are checked: revenue, growth_rate, employees, profit_margin, funding, valuation.
- Each metric must have at least one source OR a justification.
- Profiles violating this rule are reported.

Output artifact:

- `provenance_report.json`

Gate behavior:

- if strict mode enabled, pipeline aborts when violations exist.

### Stage 4 - Contradiction Detection

Code:

- `src/solstein/research/reconcile.py`

What happens:

- Detect conflicting observations for same metric.
- Numeric conflicts: divergence above threshold.
- Emit contradiction details per company.

Output artifact:

- `contradictions_report.json`

Gate behavior:

- optional threshold gate: `--max-contradictions`.

### Stage 5 - Evidence Readiness Scoring

Code:

- `src/solstein/research/evidence.py`

What happens:

- Compute readiness metrics from source depth + explainability:
  - source count,
  - source domain diversity,
  - metric source coverage,
  - metric explainability,
  - unsupported metrics.
- Produce readiness level per company.

Output artifact:

- `evidence_readiness.json`

Gate behavior:

- optional threshold gate: `--min-readiness-score`.

### Stage 6 - Scoring and Market Analysis

Code:

- `src/solstein/analytics/scoring.py`

What happens:

- Calculate growth/financial/competitive/composite scores.
- Compute market-level analysis.

Output artifacts:

- `scored.json`
- `market_analysis.json`

### Stage 7 - Export + Trace Report

Code:

- `src/solstein/exporters/excel.py`
- stage tracker in `src/solstein/research/pipeline.py`

What happens:

- Create dashboard workbook.
- Write stage-by-stage report.

Output artifacts:

- `dashboard.xlsx`
- `stage_report.json`
- `run_summary.json`

## Stage report structure

`stage_report.json` captures execution trace for each stage:

- stage name,
- description,
- key counts/metrics,
- pass/fail status for gates.

This is the main audit trail for data-input flow quality.

## What "deep" means operationally

For deep evidence collection, set explicit minimums:

- `min_total_sources >= 300` for large market sweeps,
- `min_readiness_score` tuned by market,
- strict provenance enabled,
- contradiction threshold near zero for final investment packages.

## Recommended command templates

Discovery-first run with strong gates:

```bash
python scripts/discover_and_research_market.py \
  --seed-company "Eneve" \
  --market "Dutch Energy Software" \
  --output-dir "data/output/runs/<date>/eneve_deep" \
  --max-companies 80 \
  --keywords energy software grid trading \
  --min-total-sources 300 \
  --min-readiness-score 70 \
  --max-contradictions 0
```

Enable Supabase dual-write persistence for run/stage/artifact records:

```bash
# Ensure SUPABASE__DB_URL is configured in .env
python scripts/discover_and_research_market.py \
  --seed-company "ueno" \
  --market "LATAM Financial Services" \
  --output-dir "data/output/runs/<date>/ueno_deep" \
  --max-companies 40 \
  --min-total-sources 300 \
  --db-dual-write
```

Minimum Supabase environment variables:

- `SUPABASE__URL`
- `SUPABASE__KEY`
- `SUPABASE__ANON_KEY`
- `SUPABASE__DB_URL` (Postgres connection string used by SQLAlchemy dual-write)

Markdown strict pipeline:

```bash
python scripts/run_market_pipeline.py \
  --input-dir data/input/custom_market_runs/<date>/latam_market_bulk \
  --output-dir data/output/runs/<date>/latam_markdown_strict \
  --market-name "LATAM Financial Services" \
  --strict-provenance
```
