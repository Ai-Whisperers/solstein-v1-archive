# Verification Cookbook

## Quick Integrity Checks
```bash
export PYTHONPATH=src
uv run python -m py_compile src/solstein/research/ai_research_orchestrator.py src/solstein/cli.py src/solstein/cli_ai_research.py src/solstein/cli_research.py src/solstein/research/__init__.py
uv run python -m solstein.cli --help
uv run python -m solstein.cli ai-research --help
uv run python -m solstein.cli research-companies --help
```

## LSP Diagnostics Targets
- `src/solstein/research/ai_research_orchestrator.py`
- `src/solstein/cli_ai_research.py`
- `src/solstein/cli_research.py`
- Any newly modified report/loader/worker files

## Test Matrix for Upcoming Work
- Synthetic gate tests: threshold boundary, fail-fast path, messaging.
- Citation checks: missing citation, broken citation, low-evidence refusal.
- Queue idempotency: duplicate enqueue, replay, concurrent workers, stale lock recovery.
- Gap detector: each gap type emits expected follow-up task.

## Evidence Logging Format (Paste into dossier)
- Command:
- Exit code:
- Key output:
- Files verified:
- Follow-up needed:

## Failure Protocol
1. Stop scope expansion.
2. Restore known-good local state logically (no destructive resets).
3. Fix root cause.
4. Re-run full relevant verification matrix.
5. Document failure and fix in dossier.
