# JSON to Database Roadmap

This document outlines how to move from JSON artifact management to a production relational data platform while preserving provenance, explainability, and stage-level auditability.

## Current state

Current pipeline outputs multiple JSON artifacts per run:

- `discovery_candidates.json`
- `extracted.json`
- `provenance_report.json`
- `contradictions_report.json`
- `evidence_readiness.json`
- `scored.json`
- `market_analysis.json`
- `stage_report.json`
- `run_summary.json`

This is good for transparency, but difficult for:

- cross-run joins,
- historical comparisons,
- query performance at scale,
- multi-user analytics access.

## Target relational model

Use PostgreSQL + SQLAlchemy + Alembic (Supabase Postgres as managed target).

### Table groups

1. Run orchestration tables

- `research_run`
  - run metadata: market, seed_company, started_at, completed_at, status
  - thresholds used: min_total_sources, min_readiness_score, max_contradictions
- `research_stage_event`
  - one row per stage execution (discovery/gather/gates/score/export)
  - metrics and status (JSONB payload for extensibility)

2. Entity tables

- `company`
  - canonical company master record
- `market`
  - market taxonomy / scope
- `company_market_membership`
  - many-to-many relation across runs/markets

3. Evidence/provenance tables

- `source_document`
  - URL, source_type, domain, observed_at, retrieved_at, document_hash
- `metric_observation`
  - company_id, metric_key, value, unit, currency, period, source_document_id
- `metric_reconciliation`
  - chosen_value, chosen_reason, method, confidence, unresolved_flag
- `metric_justification`
  - explicit explanation when direct source evidence is missing

4. Quality/gate tables

- `provenance_validation_result`
- `contradiction_record`
- `evidence_readiness_result`
- `gate_result`

5. Analytics tables

- `company_score`
- `market_analysis_snapshot`

6. Export tracking

- `export_artifact`
  - path/type/hash/created_at

## Relationship map

- One `research_run` has many `research_stage_event`.
- One `research_run` discovers many companies through `run_company` (bridge table).
- One `company` has many `metric_observation` rows.
- One `metric_observation` points to one `source_document`.
- One metric (company + metric_key + period) can have many observations and one reconciliation result.
- Contradictions link to the same metric reconciliation context.

## Staged migration plan

### Phase 1 - Dual write (low risk)

- Keep JSON outputs unchanged.
- Add DB writer in pipeline to mirror stage artifacts into relational tables.
- Validate parity between JSON and DB.

### Phase 2 - Query-first adoption

- Build API reads from DB for dashboards/drill-down endpoints.
- Keep JSON exports for audit and backward compatibility.

### Phase 3 - JSON as derived artifact

- Generate JSON exports from DB snapshots.
- DB becomes source of truth.

### Phase 4 - Performance hardening

- Partition large tables (`metric_observation`, `source_document`) by run date.
- Add materialized views for readiness/scoring rollups.

## Indexing strategy

Required indexes:

- `source_document(url_hash)` unique-ish dedupe index
- `metric_observation(company_id, metric_key, period_end)`
- `metric_observation(source_document_id)`
- `contradiction_record(company_id, metric_key, run_id)`
- `company_score(run_id, company_id)`
- `evidence_readiness_result(run_id, company_id)`

Consider GIN indexes on JSONB payload columns in stage/gate tables.

## Data integrity rules

- Every chosen reconciled metric must reference at least one observation.
- Every observation must reference exactly one source document.
- Missing-source metrics require mandatory justification text.
- Gate pass/fail thresholds must be persisted with run config.

## How to move pipeline code

Current files to evolve:

- `src/solstein/research/pipeline.py`
  - add repository layer writes at each stage
- `src/solstein/research/gather.py`
  - emit richer source metadata (`observed_at`, `retrieved_at`, source_type)
- `src/solstein/research/reconcile.py`
  - persist contradiction rows + chosen-value rationale
- `src/solstein/infrastructure/database_models.py`
  - extend with run/stage/evidence tables

## Example: normalized metric lineage

For one metric (revenue):

1. `source_document`: Yahoo quote + company report PDF
2. `metric_observation`: two observed revenue values
3. `contradiction_record`: divergence details if mismatch above threshold
4. `metric_reconciliation`: selected value + explanation
5. `evidence_readiness_result`: includes coverage and explainability scores

## Rollout acceptance criteria

- DB receives complete run-stage lineage for every execution.
- JSON and DB are consistent for key outputs.
- Gate decisions are reproducible from DB only.
- Drill-down UI can show full source-to-conclusion chain per metric.
