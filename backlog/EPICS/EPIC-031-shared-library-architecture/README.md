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
| [STORY-116](STORIES/STORY-116-centralize-retry-policy.md) | Centralize All Retry/Backoff in core/retry_policy.py | P2 |
| [STORY-117](STORIES/STORY-117-fix-circular-imports-shared-package.md) | Fix Circular Import Risk — Introduce shared/ Package | P2 |
| [STORY-118](STORIES/STORY-118-formalize-cli-entrypoint.md) | Formalize CLI as Proper Package Entrypoint | P2 |
| [STORY-119](STORIES/STORY-119-split-unified-loader.md) | Split unified_loader.py into Separate Modules | P2 |
| [STORY-120](STORIES/STORY-120-utc-timezone-policy.md) | Enforce UTC Timezone Policy Across All Modules | P2 |

## Dependencies

- EPIC-007 (DDD Migration)
- EPIC-027/STORY-100 (Delete bypass scripts)

## Notes

These are structural improvements that make the codebase more maintainable. They don't deliver user-facing features but prevent future bugs and reduce onboarding friction.
