# STORY-171: Migrate All CLI Commands from Deprecated `CompetitorDataLoader` to `UnifiedCompanyLoader`

| Field | Value |
|-------|-------|
| **Status** | 🟡 Open |
| **Priority** | P1 — High |
| **Size** | M (1–2 days) |
| **Epic** | EPIC-045 CLI Runtime Correctness |
| **Created** | 2026-03-01 |
| **Risk** | Medium — behavioral differences between old and new loader must be validated |
| **Assigned** | — |

---

## Audit Verdict

**CONFIRMED TECHNICAL DEBT** — verified by live execution on 2026-03-01.

```
DeprecationWarning: CompetitorDataLoader is deprecated. Use UnifiedCompanyLoader from solstein.data.unified_loader
```

This warning fires on every `generate-report` and `generate-all-reports` invocation. The `CompetitorDataLoader` class has been superseded but the CLI was never updated.

---

## Problem Statement

`CompetitorDataLoader` (in `src/solstein/data/loaders.py`) is the old loader used by all existing CLI commands that work correctly. `UnifiedCompanyLoader` (in `src/solstein/data/unified_loader.py`) is the intended replacement that adds:
- Support for additional input formats
- Integration with the enrichment connector registry
- Consistent field normalization (resolves STORY-177, STORY-178)
- No deprecation warnings

Every `generate-report` and `generate-all-reports` run emits a deprecation warning, signaling that the CLI is using code scheduled for removal. Once `CompetitorDataLoader` is removed, all CLI commands will break simultaneously.

---

## Impact

| Dimension | Severity |
|-----------|----------|
| Reliability | 🟠 High — time-bomb: will break when deprecated class is removed |
| Maintainability | 🟠 High — two loader paths diverging, bugs fixed in only one |
| User Experience | 🟡 Medium — DeprecationWarning noise in output |
| Security | ⬜ None |
| Performance | ⬜ None |

---

## Affected Files

| File | Lines | Change Type |
|------|-------|-------------|
| `src/solstein/cli.py` | Multiple `CompetitorDataLoader` usages | Replace with `UnifiedCompanyLoader` |
| `src/solstein/data/loaders.py` | `CompetitorDataLoader` class | Eventually delete after migration |
| `tests/unit/test_cli.py` | Existing tests | Update loader mock |

---

## Dependencies

- **Hard**: `UnifiedCompanyLoader` must fully support `competitor_data.json` format
- **Soft**: STORY-177 (ai_score fix), STORY-178 (funding mapping) — these fixes should land in `UnifiedCompanyLoader`
- **Supersedes**: Nothing

---

## Architectural Requirements

**REQ-1**: `UnifiedCompanyLoader` must produce identical `Company` objects as `CompetitorDataLoader` for all existing test fixtures — behavioral parity is required before migration.

**REQ-2**: Migration must be done in a single PR with a feature flag if parity cannot be guaranteed: `USE_UNIFIED_LOADER=true` env var to enable, `false` to keep old behavior.

**REQ-3**: After migration, `CompetitorDataLoader` must be marked with `# TODO: STORY-171 — remove in next cleanup sprint` to signal safe deletion.

**REQ-4**: All data fixes (STORY-177: ai_score truncation, STORY-178: funding mapping) must be implemented in `UnifiedCompanyLoader`, not in `CompetitorDataLoader`, to avoid maintaining two paths.

---

## Acceptance Criteria

- [ ] All CLI commands that previously used `CompetitorDataLoader` now use `UnifiedCompanyLoader`
- [ ] No `DeprecationWarning` emitted on any CLI run
- [ ] `generate-report "Eneve"` produces identical output (same scores, same files) before and after migration
- [ ] `generate-all-reports` runs cleanly for all 3 companies in `competitor_data.json`
- [ ] All existing CLI unit tests pass without modification (or updated to mock `UnifiedCompanyLoader`)
- [ ] A new test `tests/unit/test_loader_parity.py` compares output of both loaders against fixture data

---

## Definition of Done

- [ ] All `CompetitorDataLoader` usages in `cli.py` replaced
- [ ] `CompetitorDataLoader` class annotated as deprecated-for-removal
- [ ] Parity test passing
- [ ] DeprecationWarning no longer emitted on any command

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| `UnifiedCompanyLoader` misses a field that `CompetitorDataLoader` handled | Medium | High | Parity test catches this before merge |
| `UnifiedCompanyLoader` not yet stable | Medium | Medium | Use feature flag approach |

---

## Change Log

| Date | Author | Note |
|------|--------|------|
| 2026-03-01 | Analysis Run | DeprecationWarning observed on every generate-report run |
