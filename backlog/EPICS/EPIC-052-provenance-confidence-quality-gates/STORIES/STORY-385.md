# STORY-385: Fix `converters/company.py` — change `data_source_type` fallback from `"real"` to `"unknown"`

| Field | Value |
|-------|-------|
| **Epic** | EPIC-052 — Provenance, Confidence, and Quality Gates |
| **Priority** | P0 |
| **Size** | XS |
| **Status** | 🔴 READY (benefits from STORY-384 landing first) |
| **Created** | 2026-04-03 |
| **Source** | Third-pass contamination audit |

## Problem

`src/solstein/data/converters/company.py:341–344`:

```python
data_source_type=raw_data.get(
    "data_source_type",
    "synthetic" if raw_data.get("is_synthetic", False) else "real",
),
```

When `data_source_type` is absent from the input dict — the common case for any record loaded
from the DB (which currently has no `data_source_type` column; see STORY-384) — the converter
assumes the data is `"real"`. This is the most optimistic possible assumption: it grants full
gate passage to records with no provenance information.

The correct defensive posture: absent provenance → `"unknown"` (blocked by the gate added in
STORY-366). Only data that explicitly carries `data_source_type="real"` should pass as real.

## Fix

```python
# Before
data_source_type=raw_data.get(
    "data_source_type",
    "synthetic" if raw_data.get("is_synthetic", False) else "real",
),

# After
data_source_type=raw_data.get(
    "data_source_type",
    "synthetic" if raw_data.get("is_synthetic", False) else "unknown",
),
```

One-character change in the string literal. The `is_synthetic` path is preserved — only the
untagged fallback changes from trusted (`"real"`) to untrusted (`"unknown"`).

## Acceptance Criteria

- [ ] `convert_to_domain_company({})` returns a `Company` with `data_source_type="unknown"`
- [ ] `convert_to_domain_company({"is_synthetic": True})` still returns `data_source_type="synthetic"`
- [ ] `convert_to_domain_company({"data_source_type": "real"})` still returns `data_source_type="real"`
- [ ] Existing converter tests updated to reflect `"unknown"` default
- [ ] No gate bypass is possible via an untagged input dict after this change

## Files

- `src/solstein/data/converters/company.py` — line 343 (one word: `"real"` → `"unknown"`)
- `tests/` — any test asserting `data_source_type="real"` as a default

## Notes

- This story is XS (one-word fix) but has wide impact: every DB-loaded company currently gets
  `"real"` by default. After this fix, they get `"unknown"` and are blocked by the gate.
- **Deploy sequentially**: STORY-384 (add DB column) → STORY-385 (fix converter default) →
  STORY-366 (gate blocks unknown). Deploying STORY-385 before STORY-366 will block all exports
  until the gate is updated to allow explicitly-tagged real records.
