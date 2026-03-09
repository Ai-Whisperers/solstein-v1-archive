# EPIC 047-050 Execution Map

## Scope

This map defines concrete implementation and verification targets for EPIC-047 through EPIC-050.

## EPIC-047 Data Loading Fidelity

- **Primary code**: `src/solstein/migrations/load_competitor_data.py`
  - Preserve decimal fidelity for `ai_score`.
  - Keep profitability and funding fields mapped without silent coercion.
  - Validate input shape (`competitors` root array) before processing.
- **Secondary code**: `src/solstein/data/converters/company_extractors.py`
  - Ensure growth-rate and source-count extraction parity where needed.
- **Tests**: `tests/unit/test_load_competitor_data_migration.py`
  - Decimal `ai_score` mapping test.
  - Funding/profitability mapping test.

## EPIC-048 Report Generation Quality

- **Primary code**: `src/solstein/cli.py`
  - Use base output directories for report commands so generator owns company subdirectory creation.
- **Primary code**: `src/solstein/exporters/markdown/report_sections.py`
  - Use consistent score formatting helper for score-facing fields.
- **Tests**: `tests/unit/test_cli.py`
  - Report command output-dir behavior (non-nested path intent).
  - Wrapped/invalid payload behavior for CLI data ingestion.

## EPIC-049 Infrastructure / Dev Environment

- **Primary code**: `scripts/start-dev.sh`
  - Verify Redis service availability.
  - Verify Python Redis module import in `.venv` before worker startup.
- **Validation**: script smoke checks and startup preflight assertions in shell execution.

## EPIC-050 OpenClaw API Integration (Initial Slice)

- **Primary code**: `src/solstein/data_sources/openclaw_evaluator.py`
  - API evaluation model and weighted ranking logic.
  - Top-candidate filtering by score threshold and limit.
- **Exports**: `src/solstein/data_sources/__init__.py`
- **Tests**: `tests/unit/test_openclaw_evaluator.py`
  - High-relevance scoring.
  - Rank ordering.
  - Candidate filtering.

## EPIC-051 Data Source Quality Scoring (Initial Slice)

- **Primary code**: `src/solstein/data_sources/quality/models.py`
  - `SourceQualityScores` data model.
  - `QualityScorer` weighted composite logic.
- **Exports**: `src/solstein/data_sources/quality/__init__.py`, `src/solstein/data_sources/__init__.py`
- **Tests**: `tests/unit/test_data_source_quality_scoring.py`
  - Weight correctness.
  - Input bounding.
  - Factor preservation.

## EPIC-053 Financial Data Expansion (Validation Slice)

- **Primary code**: `src/solstein/validation/financial_rules.py`
  - Canonical validation rules and payload validator.
  - Revenue, valuation, employee-count, and growth sanity checks.
- **Exports**: `src/solstein/validation/__init__.py`
- **Tests**: `tests/unit/test_financial_rules.py`
  - Reasonable payload passes.
  - Extreme growth / valuation multiple flagged.
  - Employee out-of-range flagged.

## Cross-Epic Verification

- `pytest tests/unit/test_load_competitor_data_migration.py`
- `pytest tests/unit/test_openclaw_evaluator.py`
- `pytest tests/unit/test_data_source_quality_scoring.py`
- `pytest tests/unit/test_financial_rules.py`
- `pytest tests/unit/test_cli.py -k "wrapped or unknown_object_payload or generate_report_default_output_dir or generate_llm_report_default_output_dir"`
- LSP diagnostics for touched files in `src/solstein` and `tests/unit`.
