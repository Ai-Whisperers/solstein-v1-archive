# STORY-029: Decompose the Unified Loader God File

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | HIGH |
| Epic | [EPIC-008: God File Decomposition](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-020](../../EPIC-006-unification-of-duplicates/STORIES/STORY-020-consolidate-loader-systems.md) (loader consolidation must happen first) |

---

## The Audit Verdict

> `data/unified_loader.py` is 1,142 lines. It handles file system traversal, data parsing, schema validation, currency conversion, conflict detection, and result aggregation — all in one file. Multiple hardcoded literals are embedded throughout.

## Problem Statement

The unified loader attempts to be the entire data ingestion pipeline in a single file. Its responsibilities span six distinct pipeline stages, each of which is complex enough to warrant its own module:

1. **File system traversal** — finding and resolving data files
2. **Data parsing** — reading and deserialising file contents
3. **Schema validation** — ensuring parsed data conforms to expected structures
4. **Currency conversion** — transforming financial figures to a common currency
5. **Conflict detection** — identifying and resolving conflicting data from multiple sources
6. **Result aggregation** — combining validated, converted data into the final output

No single engineer can hold all six of these concerns in mind simultaneously. A change to currency conversion logic requires navigating past file system traversal code. A bug in schema validation requires understanding the conflict detection flow. The file is an undifferentiated ball of pipeline logic.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Maintainability** | A data parsing change requires touching the same file as a currency conversion change |
| **Testability** | Individual pipeline stages cannot be tested in isolation |
| **Bug Isolation** | A validation bug and a file traversal bug are both in the same file |
| **Code Review** | Diffs in a 1,142-line file obscure the intent of changes |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/data/unified_loader.py` | Split | 1,142 lines → focused pipeline stage modules |
| New: `src/solstein/data/file_resolver.py` | Add | File system traversal and path resolution |
| New: `src/solstein/data/data_parser.py` | Add | Data deserialisation from files |
| New: `src/solstein/data/schema_validator.py` | Add | Schema conformance validation |
| New: `src/solstein/data/currency_transformer.py` | Add | Currency conversion and normalisation |
| New: `src/solstein/data/conflict_resolver.py` | Add | Multi-source conflict detection and resolution |
| New: `src/solstein/data/result_aggregator.py` | Add | Final data assembly |
| `src/solstein/data/__init__.py` | Modify | Re-export public loader interface |

## Architectural Requirements

- **REQ-1**: `unified_loader.py` must be split by pipeline responsibility into focused modules — each module handles one stage of the data ingestion pipeline
- **REQ-2**: No resulting module may exceed 400 lines
- **REQ-3**: Each module must be independently testable — a schema validator test should not require file system setup or currency conversion
- **REQ-4**: The public interface of the loader (what callers see) must remain unchanged — this is an internal decomposition, not an API change
- **REQ-5**: This decomposition must be coordinated with STORY-014 (date path fix) and STORY-013 (FX rate fix) — those bugs should be fixed in the canonical loader before decomposition is finalised, as fixing them after decomposition requires understanding the new module boundaries

## Acceptance Criteria

- [ ] No single module in `src/solstein/data/` exceeds 400 lines
- [ ] Each module has a clearly named single responsibility (one pipeline stage)
- [ ] All existing loader tests pass without modification
- [ ] Each new module has its own test file
- [ ] The public loader interface (what callers import and call) is unchanged

## Definition of Done

**Tests Required:**
- [ ] All pre-existing loader tests pass after decomposition
- [ ] New unit tests for each pipeline stage module (file resolution, parsing, validation, conversion, conflict detection, aggregation)
- [ ] Test: each module can be imported and tested independently

**Documentation Required:**
- [ ] Comment at the top of each module explaining its pipeline stage
- [ ] Data flow documentation: file_resolver → data_parser → schema_validator → currency_transformer → conflict_resolver → result_aggregator

**Code Review Gate:**
- [ ] Reviewer confirms each module handles exactly one pipeline stage
- [ ] Reviewer confirms the public interface is unchanged
- [ ] Reviewer confirms no module exceeds 400 lines

## Notes

This story MUST NOT start until STORY-020 (loader consolidation) is complete. The sequence is: choose the canonical loader, then decompose it. Attempting to decompose while two other loaders still exist will result in confusion about which loader is being decomposed and whether the other loaders need matching decomposition.

The suggested module names follow the pipeline stages identified in the audit. Adjust them based on the actual code structure — the names should describe what each module does, not what the audit suggested.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This story currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently list this story as active work, treat it as triage-required rather than immediately actionable.

### Next Agent Action

- Reconcile this story against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before starting.
- Do not begin implementation from this file alone unless the queue or a fresh planning decision reactivates it.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Preserve machine-checkable enforcement and avoid prose-only or speculative "AI slop" updates.

### Minimum Verification For Future Agents

- If this story is reactivated, update the queue or controlling planning artifact first.
- Then prove the work with the smallest relevant regression tests, gates, or generated artifacts for the touched boundary.
