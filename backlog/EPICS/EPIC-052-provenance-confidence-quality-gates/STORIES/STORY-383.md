# STORY-383: Fix `research_dual_write.py` — remove hardcoded `strict_provenance=False` from production pipeline path

| Field | Value |
|-------|-------|
| **Epic** | EPIC-052 — Provenance, Confidence, and Quality Gates |
| **Priority** | P0 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Created** | 2026-04-03 |
| **Source** | Third-pass contamination audit |

## Problem

The production async research pipeline path (outbox worker → `research_dual_write.py` →
`pipeline.py`) has its quality gate **permanently disabled**.

Two sites in `src/solstein/infrastructure/research_dual_write.py`:

**Line 424** — `PersistRunPayload` construction:
```python
return PersistRunPayload(
    ...
    strict_provenance=False,   # hardcoded — bypasses quality gate for every run
    ...
)
```

**Line 340** — fallback when `strict_provenance` is absent from the outbox payload:
```python
strict_provenance = strict_obj if isinstance(strict_obj, bool) else False
```

Combined with `pipeline.py:82–84`:
```python
def _run_quality_gate(context: PipelineContext, strict_provenance: bool) -> None:
    if not strict_provenance:
        return   # gate entirely skipped
```

Every run dispatched through the outbox worker path skips provenance validation. Direct API
calls to `pipeline.py` default to `strict_provenance=True` (line 72), but the worker path
overrides this at construction time.

## Root Cause

`strict_provenance=False` was likely set during initial development to unblock the pipeline
while provenance infrastructure was incomplete. It was never reverted after EPIC-052 stories
added the gate code.

## Fix

1. **Line 424**: Remove `strict_provenance=False`. Derive the value from the source request
   payload, configuration, or default to `True`.
2. **Line 340**: Change the fallback from `False` to `True`:
   ```python
   strict_provenance = strict_obj if isinstance(strict_obj, bool) else True
   ```
3. Verify that the quality gate runs end-to-end for a test research run through the outbox
   worker path.
4. If existing integration tests fail because of strict provenance, fix the tests to use
   properly tagged test data (not suppress the gate).

## Acceptance Criteria

- [ ] `PersistRunPayload` no longer hardcodes `strict_provenance=False`
- [ ] The fallback at line 340 defaults to `True` (gate enabled) when not specified
- [ ] A research run through the outbox path with un-provenanced data is blocked by the gate
- [ ] A research run through the outbox path with fully-provenanced data passes the gate
- [ ] No existing tests suppress gate behavior via `strict_provenance=False` workaround

## Files

- `src/solstein/infrastructure/research_dual_write.py` — lines 340, 424
- `src/solstein/research/pipeline.py` — line 82 (gate function — verify it runs)
- Tests that exercise the outbox/worker path end-to-end

## Notes

This story must be resolved before STORY-369 (gate contract tests) can provide meaningful
coverage of the production async path.
