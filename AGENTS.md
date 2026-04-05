# Solstein — Agent Bootstrap

> This file is automatically loaded by all agent runtimes (OpenCode, Claude Code, Codex, Gemini).
> It is the entry point. Do not skip it.

## ⛔ FIRST ACTION — No exceptions

Before doing anything else — before reading any code, before running any command, before answering
any question about what to work on — execute these two reads in order:

```
1. Read: .hermes.md          ← full protocol, prohibited actions, regression floor
2. Read: backlog/EXECUTION_ORDER.md   ← 95 stories in priority order, pick the first READY one
```

**There is no valid reason to skip these reads.** They are fast (< 2 minutes). Every session that
skips them has caused regressions or wasted work.

## Story Selection (one rule)

Work the **first row with Status = READY** in `backlog/EXECUTION_ORDER.md`.
Nothing else. No GitHub issues. No epic READMEs. No intuition about what seems important.

## What This Project Is

AI-powered competitive intelligence platform for Private Equity.
Python 3.10+, FastAPI, SQLAlchemy 2.0, PostgreSQL, Celery+Redis.

- Source: `src/solstein/`
- Tests: `tests/unit/` (3855 passing baseline — do not regress below 3800)
- Backlog: `backlog/EPICS/` (90 epics) — read via `EXECUTION_ORDER.md`, not directly
- Agent protocol: `.hermes.md`

## Test Command

```bash
PYTHONPATH=src .venv/bin/python3 -m pytest tests/unit/ -q \
  --ignore=tests/unit/test_async_boundary_regressions.py \
  --ignore=tests/unit/test_api_routers_coverage.py \
  --no-header 2>&1 | tail -3
```

Use `.venv/bin/python3`, not system `python3` — system python lacks pgvector.
