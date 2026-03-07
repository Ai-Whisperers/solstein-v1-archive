# STORY-119: Split unified_loader.py into Separate Modules

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P2 – Medium |
| **Severity** | High |
| **Epic** | EPIC-031: Shared Library & Architecture |
| **Created** | 2026-03-01 |
| **Dependencies** | None |

## The Audit Verdict

> `src/solstein/data/unified_loader.py` — 500+ lines mixing data loading, data transformation, source configuration, and hardcoded values (`'2026-02-23'` date, `'dutch_market'` market). A god file with four separate responsibilities and a P0 hardcoded date bug (STORY-009 scope).

## Problem Statement

`unified_loader.py` is the data layer's version of `enhanced_client.py` — a god file that accumulated responsibilities over time until it became the load-bearing wall that everything touches but nobody fully understands. Data loading logic lives next to transformation logic lives next to hardcoded configuration values lives next to a hardcoded date that will silently break on any date after 2026-02-23. Splitting this file is not cosmetic — it is making explicit the four different things this file does so each can be tested, modified, and reasoned about independently.

## Impact

| Dimension | Impact |
|-----------|--------|
| **Maintainability** | Changes to any of the four concerns touch the same file |
| **Testability** | God file untestable in isolation |
| **Reliability** | Hardcoded values buried inside make runtime failures unpredictable |

## Affected Files

| File | Issue |
|------|-------|
| `src/solstein/data/unified_loader.py` | 500+ lines, god file |

## Architectural Requirements

- Split into four modules:
  - `data/loaders/base_loader.py` — abstract data loading interface
  - `data/loaders/source_registry.py` — source configuration and registration (replaces hardcoded source list)
  - `data/transformers/signal_transformer.py` — data normalization and transformation logic
  - `data/loaders/unified_loader.py` — thin orchestration layer that composes the above
- Hardcoded date `'2026-02-23'` removed — replaced by dynamic `datetime.now(UTC).date()` or config-driven
- Hardcoded `'dutch_market'` removed — replaced by tenant/config-driven market scope
- All existing callers of `unified_loader.py` continue to work via the thin orchestration layer (backward-compatible interface)
- Each new module has its own test file

## Acceptance Criteria

- [ ] `unified_loader.py` is ≤100 lines (orchestration only)
- [ ] Hardcoded date `'2026-02-23'` does not exist in codebase
- [ ] Hardcoded `'dutch_market'` does not exist in codebase
- [ ] All existing callers of `unified_loader` continue to function
- [ ] Each split module has unit tests

## Definition of Done

- **Tests Required**: Unit tests for each new module
- **Documentation Required**: Module responsibility documentation
- **Code Review Gate**: Reviewer verifies interface backward compatibility

## Notes

This is god file decomposition for the data layer.
