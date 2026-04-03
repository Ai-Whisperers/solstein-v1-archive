# STORY-388: Fix `instrumented.py` — propagate actual adapter confidence instead of hardcoding `1.0`

| Field | Value |
|-------|-------|
| **Epic** | EPIC-052 — Provenance, Confidence, and Quality Gates |
| **Priority** | P1 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Created** | 2026-04-03 |
| **Source** | Third-pass contamination audit |

## Problem

`src/solstein/adapters/instrumented.py:138`:

```python
confidence=1.0,
```

`InstrumentedDiscoveryAdapter` wraps all discovery adapters and records a `DiscoveryCandidate`
with `confidence=1.0` on every successful call. This value is hardcoded — the underlying
adapter's actual confidence estimate is discarded and replaced.

Downstream provenance and quality gates that rely on `confidence` scores see every
adapter-discovered record as maximum-confidence regardless of which source produced it and how
reliable that source actually is. This directly undermines the confidence calibration work
planned in STORY-199 (EPIC-052).

An adapter that is known to have 60% reliability will produce candidates marked `confidence=1.0`
after wrapping. The gate's `min_confidence=0.6` threshold (set in `pipeline.py:86`) becomes
meaningless when all records are hardcoded to pass.

## Fix

1. Inspect the underlying adapter's result for a `confidence` field.
2. Use the adapter's value if present; fall back to `1.0` only if the adapter provides none.

```python
# Before
confidence=1.0,

# After — example pseudocode (adjust to actual DiscoveryCandidate structure)
confidence=getattr(candidate_result, "confidence", None) or raw_result.get("confidence", 1.0),
```

The exact implementation depends on what the underlying adapter returns. If discovery
adapters don't currently return a confidence value, add a `confidence: float = 1.0` field
to their result type and default to `1.0` until calibrated values are available — but remove
the hardcoded override in `instrumented.py` so the field is propagated rather than replaced.

## Acceptance Criteria

- [ ] `InstrumentedDiscoveryAdapter` does not hardcode `confidence=1.0` when the underlying
  adapter returns a confidence value
- [ ] If the underlying adapter returns no confidence, `1.0` is used as the fallback (unchanged)
- [ ] `DiscoveryCandidate` has a `confidence` field that round-trips through the adapter wrapper
- [ ] Unit tests verify that a wrapped adapter with `confidence=0.6` produces a candidate
  with `confidence=0.6` (not `1.0`)

## Files

- `src/solstein/adapters/instrumented.py` — line 138
- Underlying adapter result types — verify/add `confidence` field
- `tests/unit/` — add test for confidence propagation

## Notes

This story is a prerequisite for meaningful confidence calibration (STORY-199). Until the
instrumentation layer stops overwriting confidence, calibration data is useless.
