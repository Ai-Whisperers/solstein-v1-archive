# ISSUE-11 Batch Enrichment Outcome Audit

Date: 2026-03-26

## Summary

`ISSUE-11` was not just a bad fallback line. The real defect was a boundary-contract failure:

- `enrich_batch()` returned `list[UnifiedCompany]`
- per-company failure was represented by appending the original `company`
- callers had to infer failure indirectly from mutable error fields
- the batch API then reconstructed status heuristically

That let the pipeline continue with objects that looked valid enough to score, report, or cache.

## What Changed

- Added an explicit Python outcome contract in `src/solstein/data/unified/batch_outcomes.py`
- Changed `src/solstein/data/unified/enrichment.py` so `enrich_batch()` returns `BatchEnrichmentOutcome`
- Updated `src/solstein/api/routers/enrichment_batch.py` to consume explicit outcome statuses instead of re-deriving failure from `enrichment_errors`
- Added `tests/unit/test_issue11_batch_enrichment_outcomes.py`
- Added TypeScript contract mirror in `tooling/contracts-ts/src/pipeline/batch-enrichment.ts`
- Added AST guard `no-batch-enrichment-fallback-company`

## Nested Debt Found During Fix

The strict type gate exposed a second live problem in the same path:

- `CacheService` was typed as `dict[str, object]`
- batch enrichment was caching `UnifiedCompany` objects directly

That mismatch is now fixed by caching serialized company payloads and reconstructing `UnifiedCompany` on cache reads.

## Additional Related Cleanup

Another instance of the same fallback class existed in `src/solstein/data/unified/unified.py`, where connector enrichment failure appended the original company directly. That path now returns a copied company with explicit failure metadata instead of reusing the original object reference.

## Why This Is Considered Fixed

The fix is not based on a comment or flag alone. It is based on four enforced changes:

1. Runtime behavior now returns explicit per-company outcomes
2. Batch API results consume explicit `success|partial|failure`
3. Regression tests cover failure and partial-enrichment outcomes
4. AST and TypeScript guardrails were added to stop the old pattern from re-entering

## Verification

- `make type-strict lint-ast ast-test docs-strict`
- `cd tooling/contracts-ts && npm run check`
- `DATABASE__URL=... SECURITY__SECRET_KEY=... GITHUB_TOKEN=... COMPANIES_HOUSE_API_KEY=... uv run pytest tests/unit/test_issue11_batch_enrichment_outcomes.py tests/unit/test_audit_regressions_march_2026.py::test_batch_enrichment_partial_status_uses_schema_valid_partial -q`

Result at fix time:

- engineering gate passed
- TypeScript contract check passed
- focused regression tests passed (`3 passed`)
