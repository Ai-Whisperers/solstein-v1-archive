# EPIC-012: Type Safety & Code Quality

| Field | Value |
|-------|-------|
| Priority | **P2** |
| Status | 🔴 Open |
| Stories | 3 |
| Created | 2026-02-28 |
| Depends On | [EPIC-007](../EPIC-007-ddd-migration/README.md) (Value Objects replace some Any types) |

## Context

The type system exists in this codebase in the same way a speed limit exists on a highway with no enforcement: technically present, routinely ignored.

90 instances of `: Any` type annotations appear across 32 files. The domain model (`domain/models.py`) alone has 10+. At least 10 files use Python's stdlib `logging` module instead of the project-standard `loguru`, producing inconsistent log format and missing structured context. Primitive types carry domain meaning without domain constraints — `revenue: float` accepts `-5.0` without complaint.

These are not cosmetic issues. Unchecked type annotations mean mypy cannot catch type errors that would otherwise surface at compile time. Inconsistent logging means structured log queries return incomplete results.

## Scope

| Story | Title | Severity |
|-------|-------|----------|
| [STORY-041](STORIES/STORY-041-eliminate-any-types.md) | Eliminate `: Any` Type Annotations | HIGH |
| [STORY-042](STORIES/STORY-042-migrate-stdlib-logging.md) | Migrate stdlib logging to loguru | MEDIUM |
| [STORY-043](STORIES/STORY-043-resolve-primitive-obsession.md) | Resolve Primitive Obsession in Domain Types | MEDIUM |

## Definition of Done

- [ ] Zero `: Any` annotations in domain and application layers (infrastructure layer may retain justified exceptions)
- [ ] All modules use loguru for logging
- [ ] Primitive types no longer carry unconstrained domain meaning

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This epic currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently schedule this epic, treat it as triage-required backlog inventory instead of self-startable work.

### Develop-Relevant Evidence

- `docs/reference/ENGINEERING_GUARDRAILS.md` and `docs/sessions/DEV_LOG_2026-03.md` now document a real `basedpyright` baseline rollout on `develop`.
- `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md` already names `basedpyright`, strict Pydantic boundaries, and ratcheted strictness as the intended follow-through rather than a full-repo flag flip.
- Future work here should assume the repo already has a strict-type ratchet and should extend it deliberately by surface, not replace it with one-off mypy or mock type claims.

### Next Agent Action

- Reconcile this epic against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before selecting a story.
- Do not start implementation from this README alone unless the queue or a fresh planning decision activates the epic.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Prefer narrow, machine-checkable progress over broad narrative backlog churn.

### Minimum Verification For Future Agents

- If this epic is reactivated, update the queue or controlling planning artifact first.
- Then execute one story at a time with the relevant tests, gates, and generated references for the touched surface.
