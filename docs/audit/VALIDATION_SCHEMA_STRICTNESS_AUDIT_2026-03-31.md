# Validation Schema Strictness Audit - 2026-03-31

## Goal

Review validation schema structure and strict enforcement at runtime, fix safe issues immediately, and document unresolved items that need broader follow-up.

## Scope Reviewed

- `src/solstein/api/schemas/validation.py`
- `src/solstein/api/schemas/enrichment.py`
- `src/solstein/api/schemas/semantic_search.py`
- `src/solstein/api/routers/auth.py`
- `src/solstein/api/routers/exports.py`
- `tooling/contracts-ts/src/external/facts.ts`

## Context Gathering Notes

- Two explore background tasks failed due external access restrictions in this environment.
- One librarian background task succeeded and confirmed strict Zod best practices:
  - prefer strict object mode at boundaries
  - avoid permissive unknown-key passthrough by default
  - use safe parse patterns for external input flows

## Issues Found

1. Python request models accepted unknown keys in multiple boundary schemas (`extra` policy not strict).
2. `SearchRequest` used cross-field logic in a field validator, risking model-type/field allowlist validation order issues.
3. Semantic search request documented exactly-one-of (`query` vs `company_id`) but did not enforce it.
4. TypeScript connector fact contracts were permissive (`.passthrough()`), enabling boundary drift.
5. Several active request boundaries still rely on broad/non-hardened models (see unresolved section).

## Fixes Applied

### Python API schemas

- `src/solstein/api/schemas/validation.py`
  - Added `StrictRequestModel` with `ConfigDict(extra="forbid", str_strip_whitespace=True)`.
  - Applied strict base to:
    - `SearchRequest`
    - `PaginationParams`
    - `CompanyFilterRequest`
    - `MarketAnalysisRequest`
    - `ScoreUpdateRequest`
    - `CompanyCreateRequest`
  - Moved field/model-type allowlist check to a model validator to avoid field-order coupling.

- `src/solstein/api/schemas/enrichment.py`
  - `EnrichmentRequest` and `BatchEnrichmentRequest` now use strict extras policy (`extra="forbid"`).
  - Added `str_strip_whitespace=True` for request normalization.
  - Replaced mutable list default in `EnrichmentRequest.sources` with `default_factory`.

- `src/solstein/api/schemas/semantic_search.py`
  - Added strict config (`extra="forbid"`, `str_strip_whitespace=True`).
  - Added exactly-one-of invariant for `query` and `company_id`.

### Router request models

- `src/solstein/api/routers/auth.py`
  - Hardened `LoginRequest`, `SignupRequest`, `RefreshRequest` with `extra="forbid"`.
  - Added explicit bounds on password and refresh token lengths.
  - Kept credential/token payloads untrimmed (no whitespace mutation for secrets).

- `src/solstein/api/routers/exports.py`
  - Hardened `ExportRequest` with `extra="forbid"` and input string normalization.

### TypeScript contracts

- `tooling/contracts-ts/src/external/facts.ts`
  - Changed base and canonical schemas from `.passthrough()` to `.strict()`.
  - Updated transform to emit explicit canonical fields only.

## Verification

- TypeScript
  - `npm --prefix tooling/contracts-ts ci` -> passed
  - `npm --prefix tooling/contracts-ts run check` -> passed
  - `npm --prefix tooling/contracts-ts run build` -> passed

- Python
  - `python3 -m compileall src/solstein/api/schemas/validation.py src/solstein/api/schemas/enrichment.py src/solstein/api/schemas/semantic_search.py src/solstein/api/routers/auth.py src/solstein/api/routers/exports.py` -> passed
  - `pytest` is not available in this runtime image, so behavioral test execution could not be completed here.

- LSP
  - TS diagnostics for modified contract file are clean.
  - Python LSP reports unresolved imports (`pydantic`, `fastapi`, etc.) in this environment due missing language-server dependency resolution.

## Unresolved / Needs Deeper Analysis

1. Active request boundaries still needing strictness review and likely hardening:
   - `src/solstein/api/routers/companies.py` (create path currently takes broad domain `Company` model)
   - `src/solstein/api/routers/simulation.py`
   - `src/solstein/api/routers/async_jobs.py`
   - `src/solstein/api/routers/review.py`
   - `src/solstein/api/routers/scoring.py`

2. `src/solstein/api/schemas/validation.py` remains underused by active endpoints and should be either:
   - wired to the actual route boundaries, or
   - deprecated in favor of a single boundary schema strategy.

3. Python connector boundary (`src/solstein/infrastructure/fact_payloads.py`) currently uses permissive extra handling by design (`extra="allow"`), which may be intentional for connector-specific metadata and needs connector-owner review before tightening.

## Recommended Next Steps

1. Introduce a shared strict request-model base for all API request bodies.
2. Migrate broad request bodies (`Company`, raw dict-list payloads) to dedicated boundary schemas.
3. Add explicit tests asserting rejection of unknown fields and invalid cross-field combinations.
4. Re-run full Python test suite in CI/test container with project deps installed.
