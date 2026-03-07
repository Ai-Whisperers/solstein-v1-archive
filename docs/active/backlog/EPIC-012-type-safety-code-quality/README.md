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
