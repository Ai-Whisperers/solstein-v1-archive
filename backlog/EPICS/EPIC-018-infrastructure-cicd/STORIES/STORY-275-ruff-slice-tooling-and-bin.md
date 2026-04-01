# STORY-275: Ruff Bounded Slice — .claude/, tests/unit/ import sorting, bin/ bare excepts, src/ stragglers

| Field | Value |
|-------|-------|
| Status | 🟢 Ready |
| Priority | P2 |
| Size | XS |
| Epic | [EPIC-018: Infrastructure-as-Code & CI/CD](../README.md) |
| Created | 2026-04-01 |
| Depends On | [STORY-273](STORY-273-ruff-slice-scripts-legacy.md), [STORY-274](STORY-274-ruff-slice-alembic-versions.md) |
| Risk | Low–Medium |

---

## Problem Statement

After STORY-273 and STORY-274 are complete, the remaining non-`src/` Ruff debt is distributed across four small locations. This story cleans all of them in one pass, bringing `ruff check .` to **0 errors** on canonical `develop`.

---

## Empirical Debt (2026-04-01)

Verified by `ruff check . --output-format concise`:

| Location | Count | Rules | Auto-fix? |
|----------|-------|-------|-----------|
| `.claude/commands/__init__.py` | 9 | F401 ×7, UP035 | ✅ |
| `.claude/validation/test_sample.py:62` | 1 | SIM115 | ❌ |
| `tests/unit/test_docs_health_dashboard.py` | 1 | I001 | ✅ |
| `tests/unit/test_docs_quality_gate.py` | 1 | I001 | ✅ |
| `tests/unit/test_stale_docs.py` | 1 | I001 | ✅ |
| `tests/unit/test_story079_checkpointing.py` | 1 | I001 | ✅ |
| `src/solstein/research/research_agents.py:9` | 1 | I001 | ✅ |
| `bin/agents/hostinger-safe.py` | 3 | E722 × 3 | ❌ |
| **Total** | **18** | | 15 auto / 3 manual |

---

## Scope

All four locations above. This is the final slice before a clean repo-wide gate.

---

## Acceptance Criteria

- [ ] `ruff check .claude/ tests/unit/ src/solstein/research/ --output-format concise` exits 0.
- [ ] `ruff check bin/ --output-format concise` exits 0.
- [ ] No new `pyproject.toml` entries.
- [ ] SIM115 in `.claude/validation/test_sample.py` fixed with `with open(...)` context manager.
- [ ] E722 bare excepts in `bin/agents/hostinger-safe.py` replaced with `except Exception` (minimum safe replacement; add `as e` and a log if the surrounding code already has a logger, otherwise `except Exception: pass` with a comment is acceptable given the agent guard context).
- [ ] Repo-wide `ruff check .` exits 0 after this story.

---

## Implementation Notes

### Auto-fixable (run first)
```bash
ruff check .claude/ tests/unit/ src/solstein/research/ --fix
```

### Manual fix 1: SIM115 in `.claude/validation/test_sample.py:62`
```python
# Before:
f = open(path)
data = f.read()
f.close()

# After:
with open(path) as f:
    data = f.read()
```
Read the surrounding context before applying — adapt to the actual code shape.

### Manual fix 2: E722 in `bin/agents/hostinger-safe.py` (lines 31, 49, 76)
```python
# Before:
except:
    pass

# After (minimum safe):
except Exception:
    pass
```
If the block already has access to a logger, prefer:
```python
except Exception as e:
    logger.warning("...: %s", e)
```
Do not add a logger import if one does not already exist — keep the fix minimal.

### Verification
```bash
ruff check . --output-format concise
# Expected: "Found 0 errors."
```

---

## Definition of Done

- [ ] `ruff check .` passes with 0 errors on canonical `develop`
- [ ] Commit message: `lint: ruff clean final slice — .claude/ tests/unit/ bin/ src/research/`
- [ ] `planning/QUEUE.md` updated: ruff-gate cleanup complete, STORY-061 CI unblocked
- [ ] STORY-272 closed as DONE
- [ ] STORY-061 dependency note updated to reflect clean lint signal

---

## Successor Work

Once this story is done:
- STORY-272 is COMPLETE — ruff gate signal is restored on `develop`
- STORY-061 (CI pipeline) can proceed without the "lint signal not trustworthy" caveat
- STORY-062 (pre-commit hooks) can be wired with confidence that `ruff check .` is a valid gate
