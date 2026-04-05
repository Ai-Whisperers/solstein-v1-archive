# Solstein — Claude Code Bootstrap

> Auto-loaded by Claude Code at every session start.

## ⛔ FIRST ACTION — No exceptions

Read these two files before doing anything:

```
1. .hermes.md                        ← full protocol, prohibited actions, verified facts
2. backlog/EXECUTION_ORDER.md        ← 95 stories in order — pick first READY item
```

## Story Selection

Work the **first row with Status = READY** in `backlog/EXECUTION_ORDER.md`. Nothing else.

## Project

AI-powered competitive intelligence platform for Private Equity.
Python 3.10+, FastAPI, SQLAlchemy 2.0, PostgreSQL, Celery+Redis.

- Source: `src/solstein/`
- Tests: `tests/unit/` — baseline 3855 passing, floor 3800
- Canonical pipeline: `src/solstein/research/pipeline.py`
- Frozen (do not touch): `src/solstein/research/graph/` — see STORY-343 in queue
- Adapter registry: `src/solstein/adapters/registry.py:74`

## Commands

```bash
# Run tests (use .venv/bin/python3 — system python3 lacks pgvector)
PYTHONPATH=src .venv/bin/python3 -m pytest tests/unit/ -x -q --no-header

# Lint
PYTHONPATH=src .venv/bin/python3 -m ruff check src/ --fix

# Safe local baseline (excludes infra-dependent files)
PYTHONPATH=src .venv/bin/python3 -m pytest tests/unit/ -q \
  --ignore=tests/unit/test_async_boundary_regressions.py \
  --ignore=tests/unit/test_api_routers_coverage.py \
  --no-header 2>&1 | tail -3
```

## Git

- Branch: `develop` (all work here)
- Feature branches: `feature/STORY-NNN-description`
- Never push without green tests
- Commit format: `feat(STORY-NNN): <title>`
- Always update `backlog/EXECUTION_ORDER.md` Status in the same commit as the implementation
