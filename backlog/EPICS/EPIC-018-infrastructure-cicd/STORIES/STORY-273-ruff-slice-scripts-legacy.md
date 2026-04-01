# STORY-273: Ruff Bounded Slice — scripts/ Legacy Helpers

| Field | Value |
|-------|-------|
| Status | 🟢 Ready |
| Priority | P2 |
| Size | S |
| Epic | [EPIC-018: Infrastructure-as-Code & CI/CD](../README.md) |
| Created | 2026-04-01 |
| Depends On | [STORY-272](STORY-272-restore-ruff-gate-signal-on-develop.md) (suppression hygiene first) |
| Risk | Low |

---

## Problem Statement

The `scripts/` directory (excluding `scripts/ci/`, which was cleaned in the STORY-272 work branch) contains **168 Ruff errors** across legacy helper scripts. None of these errors are in production source paths (`src/`) or active test paths. All but two are auto-fixable by `ruff check --fix`.

The debt blocks the eventual goal of a clean repo-wide `ruff check .` gate.

---

## Empirical Debt (2026-04-01)

Verified by running `ruff check scripts/ --output-format concise`:

| Rule | Count | Auto-fix? | Description |
|------|-------|-----------|-------------|
| F541 | 84 | ✅ | f-string without placeholders (remove `f` prefix) |
| I001 | 31 | ✅ | Import block un-sorted |
| F401 | 18 | ✅ | Unused imports |
| UP006 | 11 | ✅ | `List`/`Dict` → `list`/`dict` in annotations |
| UP015 | 8 | ✅ | Unnecessary open mode argument |
| UP035 | 7 | ✅ | `typing.X` deprecated (use `collections.abc`) |
| F841 | 5 | ✅ | Assigned-but-unused local variables |
| SIM201 | 1 | ❌ | `not x == y` → `x != y` (manual, trivial) |
| UP045 | 1 | ✅ | Use `X \| None` instead of `Optional[X]` |
| F402 | 1 | ✅ | Import shadows existing name |
| C420 | 1 | ✅ | Dict comprehension → `dict.fromkeys` |
| **Total** | **168** | 166 auto | |

Highest-error files:
- `scripts/generate_eneve_report_enhanced.py` — 17 errors
- `scripts/generate_eneve_report.py` — 13 errors
- `scripts/codebase_analyzer.py` — 10 errors
- `scripts/generate_synthetic_companies.py` — 9 errors

---

## Scope

**In scope:** All files under `scripts/` (excluding `scripts/ci/` which is already clean).

**Out of scope:**
- `pyproject.toml` — no new global ignore entries; existing config is sufficient
- `src/` — not touched by this story
- `tests/` — not touched by this story
- `bin/` — separate story (E722 bare excepts require manual judgement)

---

## Acceptance Criteria

- [ ] `ruff check scripts/ --output-format concise` exits 0 (no errors).
- [ ] No new entries added to `pyproject.toml` `[tool.ruff.ignore]` or `[tool.ruff.per-file-ignores]`.
- [ ] The single SIM201 in `scripts/fix_silent_errors.py:56` is fixed manually (replace `not x == y` with `x != y`).
- [ ] No functional logic changes — only style/import fixes.
- [ ] Repo-wide `ruff check .` count is re-run and recorded in story notes after completion.

---

## Implementation Notes

### Recommended execution

```bash
# Step 1: auto-fix everything fixable
ruff check scripts/ --fix

# Step 2: verify one manual fix remains
ruff check scripts/ --output-format concise
# Expected: scripts/fix_silent_errors.py:56:8: SIM201

# Step 3: open scripts/fix_silent_errors.py line 56
# Change:  if not filepath.suffix == ".py":
# To:      if filepath.suffix != ".py":

# Step 4: final verification
ruff check scripts/ --output-format concise
# Expected: no output, exit 0

# Step 5: record new repo-wide count
ruff check . --output-format concise | tail -2
```

### Risk note
The `scripts/` directory contains legacy analysis, data-generation, and one-off diagnostic scripts. None are imported by `src/`. Changing f-strings, import order, and type annotations in these files carries no runtime risk.

---

## Definition of Done

- [ ] `ruff check scripts/` passes (0 errors)
- [ ] Commit message: `lint: ruff clean scripts/ legacy helpers bounded slice`
- [ ] Repo-wide error count recorded below

### Post-completion count (fill in after merge)
> Repo-wide `ruff check .` count after this story: ___

---

## Successor Stories

After this story is done, the remaining non-`src/` ruff debt is:
- `alembic/versions/` — 21 errors (STORY-274)
- `.claude/commands/` + `tests/unit/` + `src/solstein/research/` — ~14 errors (STORY-275)
- `bin/agents/hostinger-safe.py` — 3 × E722 bare excepts (STORY-275)
