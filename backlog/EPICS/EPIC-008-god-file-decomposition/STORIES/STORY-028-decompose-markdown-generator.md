# STORY-028: Decompose the Markdown Generator God File

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | HIGH |
| Epic | [EPIC-008: God File Decomposition](../README.md) |
| Created | 2026-02-28 |
| Dependencies | None |

---

## The Audit Verdict

> `exporters/markdown/generator.py` is 1,223 lines containing 4 classes and over 100 methods. It is the largest file in the codebase. It renders company profiles, generates competitive analysis sections, formats financial tables, produces executive summaries, and assembles final documents — all in one file.

## Problem Statement

A 1,223-line module with 4 classes and 100+ methods is unmaintainable by any reasonable standard. It has grown to this size because the rendering pipeline was built incrementally — each new section type was added to the existing file rather than to a new, focused module.

The result is a file where:
- Modifying the executive summary format requires scrolling past 800 lines of unrelated rendering code
- Testing financial table formatting requires importing the entire document assembly machinery
- Merge conflicts are frequent because every rendering change touches the same file
- Code review is impractical — no reviewer can meaningfully assess a diff in a 1,223-line file without significant cognitive overhead

The file must be split by rendering responsibility, not by line count. Each resulting module should handle one type of output — profiles, financials, competitive analysis, executive summaries, or document assembly.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Maintainability** | Any rendering change requires navigating a 1,223-line file |
| **Testability** | No clear boundaries for unit tests — everything is coupled within one module |
| **Merge Conflicts** | High-traffic file generates frequent conflicts on multi-developer teams |
| **Code Review** | Diffs in a 1,223-line file are effectively unreviewable |
| **Onboarding** | New engineers cannot determine which part of the file handles which output section |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/exporters/markdown/generator.py` | Split | 1,223 lines → multiple focused modules |
| `src/solstein/exporters/markdown/__init__.py` | Modify | Re-export public interfaces from new modules |
| New: `src/solstein/exporters/markdown/profile_renderer.py` | Add | Company profile rendering (suggested — follow the actual code structure) |
| New: `src/solstein/exporters/markdown/financial_formatter.py` | Add | Financial table formatting |
| New: `src/solstein/exporters/markdown/competitive_section.py` | Add | Competitive analysis section rendering |
| New: `src/solstein/exporters/markdown/document_assembler.py` | Add | Final document assembly from sections |
| All callers of `generator.py` | Evaluate | Should require no changes if `__init__.py` re-exports correctly |

## Architectural Requirements

- **REQ-1**: `generator.py` must be split into modules each with a single, clearly named responsibility — the module name must describe what it renders
- **REQ-2**: No resulting module may exceed 400 lines
- **REQ-3**: Existing public interfaces must be preserved — callers importing from `exporters.markdown` must not require changes
- **REQ-4**: Each new module must have its own test file targeting that module's specific rendering responsibility
- **REQ-5**: The class-to-module mapping must be documented in a comment at the top of each new module explaining what it renders and what it delegates

## Acceptance Criteria

- [ ] `generator.py` does not exist as a 1,223-line monolith — it is either deleted or reduced to a thin facade that delegates to focused modules
- [ ] No resulting module exceeds 400 lines
- [ ] All existing export tests pass without modification
- [ ] Each new module has a corresponding test file
- [ ] Callers of `exporters.markdown.generator` do not require import changes (via `__init__.py` re-exports)

## Definition of Done

**Tests Required:**
- [ ] All pre-existing generator tests pass after decomposition (regression verification)
- [ ] New focused unit tests exist for each new module's rendering logic
- [ ] Test: each module can be imported and tested independently without importing the others

**Documentation Required:**
- [ ] Comment at the top of each new module explaining its single responsibility
- [ ] `__init__.py` documents the public API of the `exporters.markdown` package

**Code Review Gate:**
- [ ] Reviewer confirms each module has one clear responsibility
- [ ] Reviewer confirms no module exceeds 400 lines
- [ ] Reviewer confirms existing caller imports are unaffected

## Notes

The suggested module names (profile_renderer, financial_formatter, competitive_section, document_assembler) are starting points. Follow the actual code structure. Read the 4 classes in `generator.py` and let their responsibilities dictate the module boundaries. The goal is not to match these suggestions — it is to ensure each module has exactly one reason to change.

This story has no dependencies and can start immediately. It is also a good candidate for parallel execution with STORY-031 (GitHub agent decomposition).
