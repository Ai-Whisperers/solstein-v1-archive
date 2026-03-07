# Contributing to Solstein

**This is a proprietary platform. All contributions are internal.**

---

## Development Philosophy

> *"We don't spray perfume on coal. We put pressure on it until it becomes a diamond."*

This applies to code as much as to companies. We do not patch over problems. We fix the root cause.

---

## Before You Start

1. Read the [Developer Guide](docs/guides/developer.md) for setup instructions
2. Understand the [Architecture Decision Records](docs/architecture/decisions.md) — know *why* things are built the way they are before changing them
3. Run the full test suite and confirm it passes: `pytest tests/`

---

## Workflow

### Branching

```
main          ← stable, deployable
feature/xxx   ← new features (FD-XXX ticket format)
fix/xxx       ← bug fixes
docs/xxx      ← documentation only
```

### Commit Format

Use conventional commits:

```
feat: add competitive overlap endpoint
fix: resolve double-prefix bug in market router
docs: add API reference for /market/analysis
test: add golden dataset regression for Rocket classification
refactor: move settings into function scope for testability
```

---

## Code Standards

- **Python 3.10+** — use type hints everywhere
- **Ruff** for linting and formatting: `make lint && make format`
- **Pydantic** for all data validation and configuration
- **No silent failures** — every exception must be caught, logged, or raised
- **No hardcoded paths** — all paths go through `settings.data.data_dir`

---

## Testing Requirements

Every new feature must include tests in the appropriate layer:

| What you built | Test in |
|----------------|---------|
| Domain model | `tests/unit/test_models.py` |
| Scoring logic | `tests/unit/test_scoring.py` |
| API endpoint | `tests/test_fastapi.py` |
| Celery task | `tests/integration/test_worker.py` |
| Classification rule | `tests/data_quality/test_ai_insights.py` |

### Rules

- Use `pytest.approx()` for floating-point assertions — not `>= 8.0`
- Use the shared `mock_company` fixture from `conftest.py` — do not create local duplicates
- Every API test must use the `client` fixture (which provides auth + repo mocks)
- Zero `pass` tests — if a test is not ready, use `pytest.skip(reason="...")`

---

## Adding a New Scoring Dimension

1. Add fields to `src/solstein/core/scoring_config.py`
2. Implement `_calculate_<dimension>_score()` in `GrowthScorer`
3. Attach result to `Company` in `calculate_scores()`
4. Add unit test with exact expected value
5. Add golden dataset test protecting the classification boundary
6. Update the [API Reference](docs/api/reference.md) if the score appears in a response
7. Add an ADR in [Architecture Decisions](docs/architecture/decisions.md)

---

## Documentation

All documentation uses the scroll theme:

```markdown
<div align="center">
<img src="path/to/assets/scroll_top.png" width="100%" alt="— Title —" />
</div>

# 📜 Document Title

...content...

<div align="center">
<img src="path/to/assets/scroll_bottom.png" width="100%" alt="— End —" />
</div>
```

Relative paths from each directory:
- `docs/LORE/`, `docs/PITCH/`, `docs/guides/`, `docs/api/`, `docs/architecture/` → `../assets/scroll_top.png`
- Root `README.md` → `docs/assets/scroll_top.png`

---

## Review Checklist

Before opening a PR:

- [ ] Tests pass: `pytest tests/`
- [ ] Linting passes: `make lint`
- [ ] No `pass` tests introduced
- [ ] No hardcoded file paths
- [ ] Documentation updated if behavior changed
- [ ] CHANGELOG.md updated

---

*Solstein is built by AI Whisperers. Internal use only.*
