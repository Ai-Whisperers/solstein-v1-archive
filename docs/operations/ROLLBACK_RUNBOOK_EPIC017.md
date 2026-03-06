# EPIC-017 Rollback Runbook

## Purpose
Provide a deterministic, low-risk rollback procedure for EPIC-017 feature-flagged cutovers.

## Trigger Conditions
Execute rollback immediately when any of the following are true:
- gate fail ratio exceeds threshold
- confidence drift exceeds threshold
- export error ratio exceeds threshold
- classification mismatch rate exceeds agreed canary bound

## Fast Rollback (Flags Only)
Use safe rollback profile:

```bash
export FEATURE_NEW_CLASSIFIER=false
export FEATURE_NEW_READINESS_GATE=false
export FEATURE_NEW_UNIFIED_LOADER=false
```

Or print commands from helper:

```bash
export PYTHONPATH=src
uv run python scripts/rollback_epic017_flags.py
```

## Verification After Rollback
1. Run shadow-mode scoring test:
   - `uv run pytest tests/unit/test_scoring_router_shadow_mode.py -q`
2. Run readiness snapshot test:
   - `uv run pytest tests/unit/test_report_gate_snapshot.py -q`
3. Run core guard tests:
   - `uv run pytest tests/unit/test_rollout_guard.py -q`

## Incident Notes
Capture:
- timestamp of rollback
- triggering metrics and thresholds
- impacted exports/endpoints
- follow-up owner and ETA for re-enable decision

## Re-enable Policy
Do not re-enable flags until:
- root cause documented
- tests pass in CI
- canary burn-in run completes without threshold breaches
