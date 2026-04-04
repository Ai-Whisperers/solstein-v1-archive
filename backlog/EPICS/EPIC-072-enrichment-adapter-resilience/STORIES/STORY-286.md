# STORY-286: All enrichment adapters: return partial data with low confidence instead of raising ValueError

| Field | Value |
|-------|-------|
| **Epic** | EPIC-072 |
| **Priority** | P0 |
| **Size** | S |
| **Status** | 🔴 READY |
| **Dependencies** | None |

## Description

CRITICAL: Multiple enrichment adapters raise ValueError when partial data is unavailable instead of returning a partial result with low confidence. This causes entire enrichment runs to fail for companies with incomplete metadata. All adapters must return a result object (possibly empty) rather than raising.

## Acceptance Criteria

- [ ] No enrichment adapter raises ValueError during normal operation
- [ ] All adapters return `EnrichmentResult` with `confidence = 0.0` and empty fields when all sources fail
- [ ] Partial results have `confidence` proportional to data completeness
- [ ] Errors are logged at WARNING level, not propagated as exceptions
- [ ] Existing tests updated to test the no-raise contract
