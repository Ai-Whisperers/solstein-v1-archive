# Learnings

## 2026-03-05 Completion sweep
- Fixed missing ORM model import by adding `ReleaseGateAuditRecord` in `src/solstein/infrastructure/database_models.py` to satisfy repository import chain and unblock tests.
- Fixed runtime config mismatch by adding `allow_paid_escalation` and `paid_escalation_max_attempts` to `UnifiedCompanyLoaderConfig` in `src/solstein/data/enrichment_config.py`.
- Unified report readiness path by routing `assert_report_ready` and `assert_client_report_ready` through `ReportReleaseGate` in `src/solstein/data/report_readiness.py`.
- Enforced export gate in `scripts/run_eneve_199.py` so export now only proceeds on gate pass; otherwise it fails with explicit insufficiency reasons.
- Verified DoD commands with `uv run` under `PYTHONPATH=src`; synthetic/completeness tests pass and refresh/gating behavior is deterministic and auditable.
