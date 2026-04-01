# STORY-274: Ruff Bounded Slice — alembic/versions/ Migration Files

| Field | Value |
|-------|-------|
| Status | 🟢 Ready |
| Priority | P2 |
| Size | XS |
| Epic | [EPIC-018: Infrastructure-as-Code & CI/CD](../README.md) |
| Created | 2026-04-01 |
| Depends On | [STORY-272](STORY-272-restore-ruff-gate-signal-on-develop.md) |
| Risk | Low |

---

## Problem Statement

The `alembic/versions/` directory contains **21 Ruff errors** across four migration files. All are auto-fixable. Alembic migration files are generated boilerplate — they never get unit tested directly and are run by Alembic, not imported by application code. The fixes are mechanical (import sorting, deprecated typing imports, unused imports) with zero functional risk.

---

## Empirical Debt (2026-04-01)

Verified by `ruff check alembic/versions/ --output-format concise`:

| File | Errors | Rules |
|------|--------|-------|
| `086d0b4872a0_merge_multiple_heads.py` | 7 | UP035, I001, F401 ×2, UP007 ×3 |
| `012_epic025_strategic_indexes.py` | 6 | UP035, I001, F401, UP007 ×3 |
| `014_epic019_rls_helper_function.py` | 4 | UP035, UP007 ×3 |
| `015_epic019_api_keys_table.py` | 4 | UP035, UP007 ×3 |

| Rule | Count | Description |
|------|-------|-------------|
| UP007 | 12 | `Optional[X]` / `Union[X,Y]` → `X \| Y` syntax |
| UP035 | 4 | `typing.Sequence` → `collections.abc.Sequence` |
| I001 | 2 | Import block un-sorted |
| F401 | 3 | Unused imports (`sqlalchemy`, `alembic.op`) |

All 21 errors are auto-fixable with `ruff check --fix`.

---

## Scope

**In scope:** `alembic/versions/` only.

**Out of scope:** `alembic/env.py` — not currently failing; do not touch.

---

## Acceptance Criteria

- [ ] `ruff check alembic/versions/ --output-format concise` exits 0.
- [ ] No new entries added to `pyproject.toml`.
- [ ] No changes to migration SQL logic — only import and type annotation syntax.
- [ ] Repo-wide `ruff check .` count is re-run and recorded in story notes.

---

## Implementation Notes

```bash
# Fix everything (all 21 are auto-fixable)
ruff check alembic/versions/ --fix

# Verify
ruff check alembic/versions/ --output-format concise
# Expected: no output, exit 0

# Record new repo-wide count
ruff check . --output-format concise | tail -2
```

**Important**: Alembic migration files contain generated stubs (`op`, `sa`) that are imported at the top but may appear unused — these are the F401 violations. Verify that removing them does not break `alembic upgrade`/`alembic downgrade` by checking whether `op` or `sa` appear in function bodies, not just the top-level import. If they are truly unused in the file, removal is safe.

---

## Definition of Done

- [ ] `ruff check alembic/versions/` passes (0 errors)
- [ ] Commit message: `lint: ruff clean alembic/versions/ bounded slice`
- [ ] Repo-wide error count recorded below

### Post-completion count (fill in after merge)
> Repo-wide `ruff check .` count after this story: ___
