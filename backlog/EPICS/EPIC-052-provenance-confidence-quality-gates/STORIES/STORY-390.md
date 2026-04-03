# STORY-390: Fix `domain/models.py` — change `industry` default from `"Energy Software"` to `None`

| Field | Value |
|-------|-------|
| **Epic** | EPIC-052 — Provenance, Confidence, and Quality Gates |
| **Priority** | P1 |
| **Size** | M |
| **Status** | 🔴 READY |
| **Created** | 2026-04-03 |
| **Source** | Third-pass contamination audit |

## Problem

`src/solstein/domain/models.py:178`:

```python
industry: str = "Energy Software"
```

When a `Company` is constructed without an explicit `industry` value — which occurs whenever:
- Enrichment returns no industry classification
- A record is loaded from a sparse source
- A converter does not populate the field

— the `Company` silently defaults to `"Energy Software"`. This hardcoded default propagates
through:

1. **Scoring models** — industry-specific signal weights are applied for the wrong sector
2. **Excel exports** — PE/VC analyst deliverables show `"Energy Software"` for companies in
   unrelated industries
3. **The `FinancialMetric` converter** — which reads `company.industry` for context
4. **Competitor migration** — `load_competitor_data.py` passes through the domain model

A company with no known industry is classified as `"Energy Software"` in production outputs.
This is a **false classification** that could influence investment decisions.

The same default likely exists in duplicate domain model files (the audit found the field
copied across multiple locations — exact count to be verified during implementation).

## Fix

1. Change `industry: str = "Energy Software"` to `industry: Optional[str] = None` in
   `src/solstein/domain/models.py`.
2. Update all downstream code that assumes `industry` is non-null:
   - Export column formatters that write `company.industry` directly — add null guard
   - Scoring signals that use industry for weighting — treat `None` as "unknown" sector
   - Converters that pass `industry` through — preserve `None` rather than substituting a default
3. Search for and fix all other files that duplicate this default (grep for `"Energy Software"`).
4. Add a validation warning (not error) when `industry` is `None` at export time, so the
   analyst knows the field is absent rather than seeing a false value.

## Acceptance Criteria

- [ ] `Company(name="Acme")` produces `industry=None`, not `"Energy Software"`
- [ ] Export does not write `"Energy Software"` for companies with unknown industry
- [ ] Export writes an empty cell or `"Unknown"` for companies with `industry=None`
- [ ] Scoring handles `industry=None` without error (treated as unknown sector)
- [ ] All files containing `"Energy Software"` as a hardcoded default are updated
- [ ] Tests that relied on `industry="Energy Software"` as a default are updated to be explicit

## Files

- `src/solstein/domain/models.py` — line 178 (primary fix)
- All files containing `"Energy Software"` as a hardcoded string (verify with grep)
- Export layer — null-safe industry column handling
- Scoring layer — `None` industry handling
- Any converter that currently substitutes `"Energy Software"` as a fallback

## Notes

Run `grep -r '"Energy Software"' src/` to find all occurrence sites before starting.
Expected: domain model + possibly converters, migrations, and test fixtures. Each must be
updated to use `None` for the unknown case. The test factory `CompanyFactory` likely also
needs updating — ensure factory uses `None` or a realistic industry value, not `"Energy Software"`.
