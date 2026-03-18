# Solstein Node Gate Enforcement Strategy - 2026-03-18

## Intent

Establish a mechanistic enforcement model for node/stage execution so high-abstraction features behave deterministically under Ivan's architecture, without endless patch loops.

## Executive Diagnosis

Solstein has solid gate primitives, but enforcement is fragmented by execution path.

- Strong gates and artifacts exist in research pipeline flow:
  - `src/solstein/research/pipeline.py`
  - `src/solstein/research/pipeline_stages.py`
  - `src/solstein/data/report_release_gate.py`
- Run lifecycle and checkpoint semantics exist:
  - `src/solstein/research/contracts.py`
  - `src/solstein/research/checkpoints.py`
- Agent node workflow is modular but weakly guarded (state in/out not contract-enforced):
  - `src/solstein/agents/coordinator_agent.py`
  - `src/solstein/agents/workflow_nodes/base.py`
  - `src/solstein/agents/workflow_nodes/*.py`

Result: policy can differ by entrypoint. This is the core driver of patch/rebreak cycles.

## Root Cause (Deep)

1. Gate semantics are implemented, but not centralized as a single contract consumed by all orchestrators.
2. Node boundaries are state-shaped, not invariant-shaped (minimal pre/postcondition checks).
3. Release gate is rich, but not used as a unified decision ledger across all flows.
4. Lifecycle persistence exists for research runs, but not fully reflected in all node-oriented paths.
5. Rollout guard primitives exist but are not wired to live gate telemetry.

## Mechanistic Enforcement Model

### 1) Canonical Gate Decision Envelope (single schema)

Define one envelope used by node gates, stage gates, and export gates:

```python
{
  "run_id": str,
  "gate": str,
  "scope": "node" | "stage" | "release",
  "decision": "pass" | "warn" | "block",
  "reason_codes": list[str],
  "artifact_hash": str,
  "config_hash": str,
  "timestamp": str,
}
```

Why: one schema prevents drift between coordinator path and research pipeline path.

### 2) Hard vs Soft Gate Matrix

Hard gates (must block):

- Invalid run-state transition (`research/contracts.py`).
- Stale refresh metadata (`report_release_gate.py`).
- Provenance boundary violations (`report_release_gate.py`).
- Unresolved critical claim contradictions (`report_release_gate.py`).
- Source volume below hard threshold (`pipeline_stages.py` SourceVolumeGate).

Soft gates (warn, never silent):

- Completeness below target but above hard minimum.
- Evidence readiness drift.
- Adjudication override present (must be logged with decision id).

### 3) Node Guard Wrapper (for coordinator nodes)

Wrap each `WorkflowNode.execute` with a guard layer:

- Precondition checks: required state keys/types.
- Postcondition checks: expected outputs present and shape-valid.
- Monotonic progression check: no backward lifecycle transitions.
- Decision emission: always emit gate envelope, even when pass.

Why: moves node path from best-effort to deterministic contract behavior.

### 4) Unified Gate Journal (per run)

Persist all gate envelopes into one append-only journal per `run_id`.

- Include source path (`node`/`stage`/`release`) and reason codes.
- Store alongside checkpoints and stage report in output dir.

Why: enables replay, auditing, and non-ambiguous root-cause analysis.

### 5) Rollout Guard Wiring

Wire `src/solstein/core/rollout_guard.py` to gate telemetry:

- `gate_fail_ratio` from journal reason counts.
- `confidence_drift` from scored artifacts over rolling windows.
- `export_error_ratio` from API export paths.

If thresholds breach, auto-switch from strict to protected mode or pause rollout according to policy.

## Non-Negotiable Invariants

1. **No unlogged gate decision**
   - Every gate evaluation emits a gate envelope.
   - Test: assert gate journal count matches evaluated gates in stage report.

2. **No scoring/export with unresolved critical contradictions**
   - Enforce `critical_claim_contradiction` block unless adjudication override exists.
   - Test: seed unresolved contradiction and assert blocking in scoring + export paths.

3. **No invalid run-state transitions**
   - Only transitions from `_RUN_STATE_TRANSITIONS` allowed.
   - Test: replay transition matrix and fail on illegal edge.

4. **No provenance-required field without provenance metadata**
   - Boundary provenance violations hard-block release.
   - Test: populate required fields without provenance and assert gate block.

5. **No silent node-state schema drift**
   - Node pre/post validators must fail-fast on missing/extra critical keys.
   - Test: malformed state fixtures per node should produce block decision + reason code.

## Where-To-Enforce Matrix

- `src/solstein/agents/workflow_nodes/base.py`
  - Add guard wrapper hooks and mandatory decision emission.
- `src/solstein/agents/coordinator_agent.py`
  - Require guarded node execution and run-level gate journal attachment.
- `src/solstein/research/pipeline.py`
  - Keep stage gates; emit canonical envelopes and append to same journal.
- `src/solstein/data/report_release_gate.py`
  - Keep reason taxonomy as canonical blocking language.
- `src/solstein/core/rollout_guard.py`
  - Consume journal metrics to enforce rollout decisions.

## Migration Sequence (No Rewrite)

Phase 1 - Contract Foundation

1. Introduce canonical gate envelope model and serializer.
2. Add gate journal writer in output dir.
3. Add adapter function to map existing `ReportGateResult` to envelope.

Phase 2 - Node Guarding

1. Add pre/postcondition validators for each workflow node.
2. Emit gate envelopes from node wrapper.
3. Fail fast on invariant violation; keep reason codes stable.

Phase 3 - Stage/Release Convergence

1. Emit canonical envelopes from stage gates and quality gate.
2. Ensure scoring/export API routes log gate decisions with same schema.

Phase 4 - Rollout Automation

1. Wire journal-derived metrics into `evaluate_rollout`.
2. Enforce threshold actions (warn/protect/rollback) via config profile.

## Immediate Correctness Follow-up

Potential architecture drift to review first:

- `src/solstein/research/pipeline_stages.py` contains `ExportStage._run_async` body that appears to implement gather-style async enrichment flow.

Action:

1. Validate intent of this method placement.
2. Move/refactor only if confirmed drift, preserving behavior and tests.

## Anti-Patterns to Avoid

- Adding more ad-hoc `if` checks without journaled reason codes.
- Creating separate gate reason taxonomies per module.
- Introducing bypass flags without explicit audit trail.
- Relying on log lines as gate evidence instead of structured artifacts.
- Mixing hard and soft gates with no severity model.

## Definition of Done

- One gate envelope schema used across node/stage/release paths.
- One gate journal per run with deterministic replay.
- Invariant tests fail on contract violations.
- Rollout guard decisions derive from gate telemetry, not manual judgement.
