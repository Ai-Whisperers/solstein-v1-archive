# STORY-382: Fix `test_modes.py` — change `SOLSTEIN_TEST_MODE` default from `"mixed"` to `"strict_real"`

| Field | Value |
|-------|-------|
| **Epic** | EPIC-052 — Provenance, Confidence, and Quality Gates |
| **Priority** | P0 |
| **Size** | XS |
| **Status** | 🔴 READY |
| **Created** | 2026-04-03 |
| **Source** | Third-pass contamination audit |

## Problem

`src/solstein/core/test_modes.py:16` sets the unguarded default:

```python
mode = os.getenv("SOLSTEIN_TEST_MODE", "mixed").strip().lower()
```

And at line 26:
```python
allow_synthetic = mode in {"synthetic", "mixed"}
```

When `SOLSTEIN_TEST_MODE` is not set (the common case in production), `mode = "mixed"` and
`allow_synthetic = True`. Any gate or guard that consults `get_test_mode().allow_synthetic`
will permit synthetic records through without any explicit configuration.

Additionally, lines 23–24 silently fall back to `"mixed"` for unrecognised values:
```python
if mode not in {"synthetic", "mixed", "strict_real"}:
    mode = "mixed"
```

This means a misconfigured env var also lands in synthetic-allowed mode rather than failing
loudly.

## Root Cause

`test_modes.py` lives in `src/solstein/core/` — a production module. Its default was chosen
for developer convenience (tests pass without configuration) but creates a latent production
risk: any deployment that forgets to set the env var runs with `allow_synthetic=True`.

## Fix

1. Change the default in `os.getenv(...)` from `"mixed"` to `"strict_real"`.
2. Change the invalid-value fallback from `"mixed"` to `"strict_real"` (or raise `ValueError`).
3. Update any test that relies on the default being `"mixed"` to explicitly set
   `SOLSTEIN_TEST_MODE=mixed` via `monkeypatch.setenv`.

```python
# After fix — line 16
mode = os.getenv("SOLSTEIN_TEST_MODE", "strict_real").strip().lower()

# After fix — lines 23-24 (strict fail-safe)
if mode not in {"synthetic", "mixed", "strict_real"}:
    raise ValueError(f"Unknown SOLSTEIN_TEST_MODE: {mode!r}. Must be one of: synthetic, mixed, strict_real")
```

## Acceptance Criteria

- [ ] `get_test_mode()` called without `SOLSTEIN_TEST_MODE` returns `allow_synthetic=False`
- [ ] `get_test_mode()` with `SOLSTEIN_TEST_MODE=mixed` returns `allow_synthetic=True` (unchanged)
- [ ] `get_test_mode()` with an unrecognised value raises `ValueError` (not silently falls back)
- [ ] All existing tests that depend on synthetic-allowed behaviour explicitly set the env var
- [ ] No production code path calls `get_test_mode()` without the env var being documented

## Files

- `src/solstein/core/test_modes.py` — primary change (lines 16, 23–24)
- Any test that calls `get_test_mode()` without `monkeypatch.setenv("SOLSTEIN_TEST_MODE", ...)`

## Notes

Consider moving `test_modes.py` entirely out of `src/` in a follow-up story. A module named
`test_modes` in a production source tree is a structural smell.
