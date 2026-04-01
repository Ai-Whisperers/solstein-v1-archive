# Next Session Runbook

## Goal
Start productive implementation in <30 minutes with no re-discovery.

## Read Order (Do Not Skip)
1. `docs/sessions/SESSION_IMPLEMENTATION_DOSSIER_2026-03-02.md`
2. `docs/research/MASTER_INTEGRATION_PLAN.md`
3. `docs/continuation/IMPLEMENTATION_BACKLOG.md`
4. `docs/continuation/ARCHITECTURE_GUARDRAILS.md`
5. `docs/continuation/VERIFICATION_COOKBOOK.md`

## First 20 Minutes Checklist
- Confirm branch and baseline SHA.
- Re-run quick compile checks for repaired modules.
- Re-run CLI smoke checks for research commands.
- Pick one backlog item only (default: synthetic hard gate).
- Define acceptance tests before editing.

## Baseline Commands
```bash
export PYTHONPATH=src
uv run python -m py_compile src/solstein/research/ai_research_orchestrator.py src/solstein/cli.py src/solstein/cli_ai_research.py src/solstein/cli_research.py src/solstein/research/__init__.py
uv run python -m solstein.cli ai-research --help
uv run python -m solstein.cli research-companies --help
```

## Default First Implementation Slice
- Implement hard synthetic-data gate in report generation path.
- Add tests for pass/fail threshold behavior and error messaging.
- Add evidence to dossier under verification section.

## Session-End Requirements
- Update dossier with exact files changed.
- Paste commands run and pass/fail outcomes.
- Record new risks and follow-up backlog items.
- Keep docs index links current.
