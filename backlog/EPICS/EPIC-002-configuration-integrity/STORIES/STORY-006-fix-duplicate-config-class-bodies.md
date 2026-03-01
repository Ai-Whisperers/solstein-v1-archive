# STORY-006: Fix Duplicate Class Body Definitions in config.py

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P0 |
| Severity | CRITICAL |
| Epic | [EPIC-002: Configuration Integrity](../README.md) |
| Created | 2026-02-28 |
| Dependencies | None |

---

## The Audit Verdict

> `config.py` defines `DatabaseConfig` and at least 6 LLM provider configuration fields twice within the same class bodies. Python's class loading silently discards the first definition. Validators attached to those first definitions are dead code — they will never execute regardless of what configuration values are provided.

## Problem Statement

Duplicate field definitions in Python classes cause the second definition to silently replace the first. Any Pydantic validators, `Field()` constraints, or default value logic attached to the first definition of a field are permanently discarded without warning. Engineers reading the code will believe these validators are active. They are not. The effective configuration schema is a subset of what the source code appears to define.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Correctness** | Validation logic believed to be running is silently dead |
| **Reliability** | Configuration values that should be validated pass through unchecked |
| **Developer Confusion** | The effective configuration schema does not match what the code appears to define — engineers are maintaining ghost code |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/config.py` | Modify | Merge all duplicate class definitions; preserve all validators from both copies |

## Architectural Requirements

*What the system must satisfy. No implementation instructions. No code. Only what — never how.*

- **REQ-1**: Each configuration field must appear exactly once in its containing class
- **REQ-2**: Where both duplicate definitions contained validators, all validators from both must be retained in the merged definition
- **REQ-3**: The merged field set must be a strict superset of what was validated in either duplicate definition — no validator may be lost in the merge
- **REQ-4**: Each Pydantic validator must have an inline comment stating what it validates and why

## Acceptance Criteria

- [ ] Grep for each formerly-duplicated field name returns exactly one definition in config.py
- [ ] All validators present in either duplicate copy exist in the merged result
- [ ] Application starts and all configuration fields are populated as expected
- [ ] No Python `SyntaxWarning` or `UserWarning` about duplicate definitions appears in any log

## Definition of Done

**Tests Required:**
- [ ] Unit test: load config with each formerly-duplicated field and assert validator behavior is applied
- [ ] Unit test: confirm all expected validators fire by providing invalid input and asserting `ValidationError`

**Documentation Required:**
- [ ] Each validator commented with its purpose and the consequence of removing it

**Code Review Gate:**
- [ ] Reviewer confirms no field name appears more than once in any class definition in config.py
- [ ] Reviewer confirms the total number of validators in the merged file equals or exceeds the total from both original copies

## Notes

This is the root story of the entire backlog's critical path. Every other P0 story depends — directly or transitively — on this one. It has no dependencies of its own and can be started immediately. The fix itself is straightforward; the risk is in ensuring no validator is lost during the merge.
