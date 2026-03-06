# Model Migration Playbook (Company / FinancialMetric)

## Purpose
This playbook defines how to migrate model payloads safely while preserving backward compatibility for `Company` and `FinancialMetric`.

Scope covers payload shapes used by API, scripts, exports, and test fixtures.

## Current Compatibility Reality
`Company` currently supports two financial representations:

1. Nested model under `financials` (`FinancialMetric`)
2. Flattened fields on `Company` (`revenue`, `employees`, `growth_rate`, `profit_margin`, `funding`, `valuation`)

The model-level validator (`sync_financial_fields`) synchronizes these two representations.

## Canonical Direction
- Canonical runtime representation: `Company.financials`.
- Transitional input support: both nested and flattened payloads accepted.
- Transitional output support: both representations may exist until all consumers migrate.

## Migration Strategy

### Phase 0: Safety Harness (must exist before schema cleanup)
- Add dry-run validator script and unit tests.
- Validate legacy flat, nested, mixed, and incompatible payloads.
- Block migration changes if compatibility harness fails.

### Phase 1: Dual-Read / Dual-Write
- Keep accepting both payload shapes.
- Parse with `Company.model_validate`.
- Emit compatibility metadata in logs for old-shape payloads.

### Phase 2: Consumer Cutover
- Update all consumers to read `company.financials` first.
- Keep flattened reads as fallback only.
- Add release checks for remaining flat-shape consumers.

### Phase 3: Deprecation Window
- Keep flat-field acceptance for one release window after all consumers are migrated.
- Emit warning for flat-only payloads.
- Publish removal date in release notes.

### Phase 4: Removal
- Remove flat compatibility behavior only after:
  - all tests green,
  - dry-run compatibility checks are archived for prior versions,
  - no production consumers depend on flat shape.

## Compatibility Matrix

| Input shape | Example | Expected result |
|---|---|---|
| Flat legacy | `revenue`, `employees`, `growth_rate` at company root | Parses and syncs into `financials` |
| Nested canonical | `financials: {...}` only | Parses directly |
| Mixed | root + nested with conflicting values | Deterministic merge by model sync rules |
| Incompatible | wrong types (`revenue='oops'`) | Validation error with explicit reason |

## Dry-Run Validator Requirements
- Deterministic and read-only.
- No persistence side effects.
- Exit codes:
  - `0`: all scenarios pass
  - `1`: one or more scenarios fail
- Output sections:
  - scenario name
  - pass/fail
  - failure reason

## Test Obligations
- Unit tests must cover at minimum:
  1. Legacy flat payload parsing/round-trip
  2. Nested payload parsing/round-trip
  3. Mixed payload deterministic behavior
  4. Incompatible payload failure with clear message

## Rollback Rule
If migration work introduces parsing regressions, revert to previous model contract and re-run the dry-run validator before reattempting.

## Ownership
- Domain model owner: Analytics/Core maintainers
- Validation harness owner: EPIC-017 non-API stream
