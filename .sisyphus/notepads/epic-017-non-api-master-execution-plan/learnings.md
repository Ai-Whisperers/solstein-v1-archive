# Learnings

## 2026-03-05 Orchestrator Init
- EPIC-017 expanded to include stories 1-75 across A..P.
- Non-API scope only; provider integrations are out-of-scope (Jonathan-owned).
- High-risk areas: domain model duplication, scoring/config divergence, readiness split, loader monolith, broad exception patterns.

## 2026-03-05 Wave-0 N1 kickoff
- Added feature flags to Settings: FEATURE_NEW_CLASSIFIER, FEATURE_NEW_READINESS_GATE, FEATURE_NEW_UNIFIED_LOADER.
- Added central accessor module: src/solstein/core/feature_flags.py.
- Added unit tests in tests/unit/test_feature_flags.py for defaults and env overrides.
- Targeted pytest is currently blocked by pre-existing repo import error in tests/conftest.py chain (missing ReleaseGateAuditRecord symbol in infrastructure.database_models).

## 2026-03-05 M2 implementation
- Added `docs/architecture/MODEL_MIGRATION_PLAYBOOK.md` with phased dual-read/dual-write strategy and compatibility matrix for Company/FinancialMetric.
- Added deterministic dry-run validator: `scripts/validate_model_migration_dry_run.py` (exit 0 pass / 1 fail).
- Added unit suite: `tests/unit/test_model_migration_dry_run.py` covering legacy flat, nested, mixed, and incompatible payload scenarios.
- Observed current deterministic merge behavior for mixed payloads: nested `financials` values remain authoritative for overlapping fields.

## 2026-03-05 M4 progress
- Added contract tests in `tests/unit/test_model_contract_compat.py` for persisted JSON compatibility and API response shape stability.
- Verified four scenarios pass (`uv run pytest tests/unit/test_model_contract_compat.py -q`): legacy flat, nested canonical, mixed deterministic, and API key-set contract.

## 2026-03-05 N2 progress
- Added shadow classification comparison in `src/solstein/api/routers/scoring.py`.
- Response now includes `classification_shadow` with legacy vs canonical vs selected and mismatch flag.
- Feature flag `FEATURE_NEW_CLASSIFIER` controls selected classification path while keeping mismatch telemetry for dual-run.
- Added unit tests in `tests/unit/test_scoring_router_shadow_mode.py` for both flag states.

## 2026-03-05 N4 progress
- Added rollback decision utility `src/solstein/core/rollout_guard.py` with thresholds for gate-fail ratio, confidence drift, and export error ratio.
- Added tests `tests/unit/test_rollout_guard.py` covering no-rollback, single-trigger rollback, and multi-trigger rollback.

## 2026-03-05 N3/O3/D4/M5 progress
- Added deterministic canary utility: `src/solstein/core/canary_rollout.py` with stable SHA-based bucket selection.
- Added deterministic test mode resolver: `src/solstein/core/test_modes.py` with env-based mode/seed contract.
- Added machine-readable gate serialization (`to_dict`) in `src/solstein/data/report_release_gate.py` and snapshot builder in `src/solstein/data/report_readiness.py`.
- Added rollback profile + helper script (`src/solstein/core/rollback_profile.py`, `scripts/rollback_epic017_flags.py`) and runbook (`docs/operations/ROLLBACK_RUNBOOK_EPIC017.md`).
- Updated scorer to honor configurable composite weights (no hardcoded 0.4/0.3/0.3) and added dedicated regression test `tests/unit/test_scoring_composite_weights.py`.
- EPIC-017 focused unit test batch currently passing (26 tests).

## 2026-03-05 D5 export gate enforcement
- Enforced release gate in `src/solstein/api/routers/export.py` for both Excel and JSON exports.
- Added `tests/unit/test_export_release_gate.py` to ensure JSON export is blocked with `RELEASE_GATE_BLOCKED` and Excel export skips when gate fails.
- Export gate tests currently passing with expected warnings for missing type stubs/private usage.
