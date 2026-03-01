# STORY-019: Eliminate Duplicate Unified Adapter Pairs

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | HIGH |
| Epic | [EPIC-006: Unification of Duplicates](../README.md) |
| Created | 2026-02-28 |
| Dependencies | None |

---

## The Audit Verdict

> `adapters/enrichment/` contains 6 duplicate adapter pairs: `funding.py` + `funding_unified.py`, `linkedin.py` + `linkedin_unified.py`, `news.py` + `news_unified.py`, `patents.py` + `patents_unified.py`, `website.py` + `website_unified.py`, `web_search.py` + `web_search_unified.py`. An adapter migration was started and never finished.

## Problem Statement

Twelve adapter files exist where six should. An adapter migration was initiated — each original adapter received a `_unified` counterpart — and then abandoned mid-execution. Both versions may be imported by different callers with no indication of which is correct. The result is that a bug fix applied to `funding.py` may not affect callers that import `funding_unified.py`, and vice versa.

The `_unified` suffix itself is a problem: migration-era naming conventions should not persist in production code. A file called `funding_unified.py` tells you it was created during a migration, not what it does.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Maintainability** | Bug fixes may be applied to the wrong version of an adapter |
| **Correctness** | Different callers may use different versions of the same adapter, producing different behaviour |
| **Cognitive Load** | Engineers must determine which version is canonical before making any change |
| **Code Volume** | 12 files where 6 should exist — double the surface area for review and testing |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/adapters/enrichment/funding.py` | Evaluate | Original adapter — may be canonical |
| `src/solstein/adapters/enrichment/funding_unified.py` | Evaluate | Unified version — may be canonical |
| `src/solstein/adapters/enrichment/linkedin.py` | Evaluate | Original adapter |
| `src/solstein/adapters/enrichment/linkedin_unified.py` | Evaluate | Unified version |
| `src/solstein/adapters/enrichment/news.py` | Evaluate | Original adapter |
| `src/solstein/adapters/enrichment/news_unified.py` | Evaluate | Unified version |
| `src/solstein/adapters/enrichment/patents.py` | Evaluate | Original adapter |
| `src/solstein/adapters/enrichment/patents_unified.py` | Evaluate | Unified version |
| `src/solstein/adapters/enrichment/website.py` | Evaluate | Original adapter |
| `src/solstein/adapters/enrichment/website_unified.py` | Evaluate | Unified version |
| `src/solstein/adapters/enrichment/web_search.py` | Evaluate | Original adapter |
| `src/solstein/adapters/enrichment/web_search_unified.py` | Evaluate | Unified version |
| All callers of these adapters | Modify | Must import the canonical version |

## Architectural Requirements

- **REQ-1**: For each adapter pair, one canonical version must be chosen and all callers migrated to import it exclusively
- **REQ-2**: The non-canonical version must be deleted — not renamed, not archived, not moved to a `deprecated/` directory
- **REQ-3**: The canonical version must be named without a `_unified` suffix; migration-era naming must not persist in production code
- **REQ-4**: An adapter interface (`Protocol` or `ABC`) must be defined that all enrichment adapter implementations must satisfy, ensuring consistency across adapters

## Acceptance Criteria

- [ ] Six adapter files exist in `adapters/enrichment/` — one per external system
- [ ] No files with a `_unified` suffix exist anywhere in the codebase
- [ ] All callers import the canonical adapter
- [ ] An `EnrichmentAdapter` Protocol or ABC exists and all adapters satisfy it
- [ ] `grep -r "_unified" src/solstein/adapters/` returns zero results

## Definition of Done

**Tests Required:**
- [ ] Existing adapter tests pass against the canonical version
- [ ] Integration test for each retained adapter confirming it satisfies the adapter interface
- [ ] Test: importing a deleted adapter name raises `ImportError`

**Documentation Required:**
- [ ] Comment in the adapter interface module documenting the consolidation and interface contract

**Code Review Gate:**
- [ ] Reviewer confirms all 6 non-canonical files are deleted
- [ ] Reviewer confirms the adapter interface is satisfied by all remaining adapters (mypy verification)

## Notes

Start by auditing the callers: `grep -r "from solstein.adapters.enrichment" . --include="*.py"` will reveal which version each caller imports. The version with more active callers is likely canonical, but verify by diffing the implementations — the `_unified` versions may contain bug fixes or improvements not present in the originals.
