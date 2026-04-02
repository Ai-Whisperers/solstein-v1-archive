# EPIC-031: Shared Library & Architecture

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Owner** | Platform Team |
| **Created** | 2026-03-01 |

## Context

The platform has accumulated several architectural debts in its utility and shared layer: retry/backoff logic reimplemented independently in multiple adapter files despite a central `core/retry_policy.py` existing; circular import risk between `core/`, `api/`, and `domain/` layers because `core/` is imported by both and lacks a strict layering boundary; the CLI (`scripts/solstein_cli.py`) calls the domain layer directly rather than the API; two root bypass scripts (`run_research.py`, `run_market_pipeline.py`) normalize domain bypassing as a workflow; `data/unified_loader.py` (500+ lines) mixes data loading, transformation, and hardcoded config; and datetime handling is inconsistent across modules (mix of naive and aware datetimes, no enforced timezone policy). This epic cleans up these structural debts before they become load-bearing walls.

## Stories

| Story | Title | Priority |
|-------|-------|----------|
| STORY-116 | Centralize All Retry/Backoff in core/retry_policy.py | P2 |
| STORY-117 | Fix Circular Import Risk — Introduce shared/ Package | P2 |
| STORY-118 | Formalize CLI as Proper Package Entrypoint | P2 |
| STORY-119 | Split unified_loader.py into Separate Modules | P2 |
| STORY-120 | Enforce UTC Timezone Policy Across All Modules | P2 |

## Dependencies

- EPIC-007 (DDD Migration)
- EPIC-027/STORY-100 (Delete bypass scripts)

## Notes

These are structural improvements that make the codebase more maintainable. They don't deliver user-facing features but prevent future bugs and reduce onboarding friction.

## Autonomous Continuation Notes

### Queue Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` before selecting an EPIC-031 story.
- `planning/QUEUE.md` marks this epic `READY`.
- The queue notes that these stories can run in parallel with `EPIC-065/STORY-245`.
- `EPIC-066` stays blocked until this epic materially starts and `STORY-245` is done.

### Next Agent Action

- Pick one story at a time from `STORY-116` through `STORY-120`; do not blend multiple structural refactors into one change unless the dependency is real.
- Preferred order for lowest integration risk: `STORY-116` -> `STORY-117` -> `STORY-118` -> `STORY-119` -> `STORY-120`.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md` and `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`.
- Structural cleanup must not be prose-led. Each fix should add a durable guardrail such as a regression test, AST rule, boundary check, or generated reference update.
- Avoid AI-slop refactors: no broad renames or file moves without a directly verifiable architectural payoff.

### Minimum Verification For Future Agents

- Use the maintained engineering checks relevant to the touched surface: `make lint-ast`, `make ast-test`, `make type-strict`, and targeted regression tests.
- If a story changes package boundaries, verify imports and runtime entrypoints still work instead of relying on stylistic cleanup alone.
