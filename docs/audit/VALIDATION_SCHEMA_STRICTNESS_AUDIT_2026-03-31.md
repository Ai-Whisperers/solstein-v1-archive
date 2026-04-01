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

## Current State Of Active Request Boundaries

### Already hardened in this audit cycle

- `src/solstein/api/routers/auth.py`
  - `LoginRequest`, `SignupRequest`, and `RefreshRequest` now forbid unknown fields.
  - Password and refresh-token lengths are bounded.
  - Secret-bearing fields are not whitespace-normalized.

- `src/solstein/api/routers/exports.py`
  - `ExportRequest` now forbids unknown fields.
  - String input normalization is applied at the boundary.

- `src/solstein/api/schemas/enrichment.py`
  - `EnrichmentRequest` and `BatchEnrichmentRequest` now forbid unknown fields.
  - These are consumed by `src/solstein/api/routers/enrichment_single.py` and `src/solstein/api/routers/enrichment_batch.py`.

- `src/solstein/api/schemas/semantic_search.py`
  - `SemanticSearchRequest` now forbids unknown fields.
  - Exactly one of `query` or `company_id` is enforced.

- `src/solstein/api/schemas/validation.py`
  - Strict request base exists and the `SearchRequest` cross-field validation ordering issue is fixed.
  - This remains only partially valuable until active handlers consistently adopt these models.

### Remaining active body boundaries still needing hardening

1. `src/solstein/api/routers/companies.py`
   - `POST /companies` takes `Company`, a broad domain model, directly at the API boundary.
   - Risk: boundary and domain concerns are collapsed, making extra-field policy and create-specific constraints harder to reason about.
   - Recommended fix: replace with a dedicated strict create schema and explicit mapping into the domain entity.

2. `src/solstein/api/routers/simulation.py`
   - `POST /run` takes `Scenario` directly.
   - Risk: domain model is used as transport schema without an explicit API boundary contract or strict shared policy.
   - Recommended fix: add a dedicated strict request schema or harden `Scenario` explicitly if it is intended to remain the boundary type.

3. `src/solstein/api/routers/async_jobs.py`
   - `AsyncEnrichmentRequest` and `AsyncBatchEnrichmentRequest` are inline `BaseModel` classes with no strict config.
   - `AsyncBatchEnrichmentRequest.companies` is `list[dict]`, the loosest active request shape found in the API layer.
   - Risk: silent payload drift can enter queued work and only fail later.
   - Recommended fix: add strict request models plus nested strict item schemas for company entries.

4. `src/solstein/api/routers/review.py`
   - `ApproveRequest` and `RejectRequest` are inline `BaseModel` classes with no strict config.
   - Risk: state-changing analyst workflow accepts non-hardened request bodies.
   - Recommended fix: add `extra="forbid"`, length bounds, and reviewer/rationale constraints.

5. `src/solstein/api/routers/scoring.py`
   - `AdjudicationRequest` is inline and non-strict.
   - Risk: adjudication is a state-changing boundary but accepts unconstrained strings and `Any` value payload.
   - Recommended fix: introduce strict enums/value families where possible and reject unknown keys.

## Future Hardening Backlog

### Fundamental hardenings to keep as reference

1. Standardize on one shared strict API request base model.
   - Every request-body schema should inherit the same explicit `extra` policy.
   - Apply normalization selectively; never trim or mutate secrets.

2. Separate transport schemas from domain models.
   - Avoid using `Company`, `Scenario`, or other business entities directly as HTTP request contracts.
   - Map from strict request DTOs into domain entities after validation.

3. Eliminate raw `dict` and `list[dict]` request payloads.
   - Replace with nested named schemas.
   - This is especially important for async ingestion and queued work.

4. Convert inline router request models into reusable schema modules where the endpoint is core or state-changing.
   - This keeps strictness policy centralized and easier to audit.

5. Add boundary-focused behavioral tests.
   - Unknown keys rejected.
   - Cross-field invariants rejected.
   - Secret fields preserved verbatim.
   - Nested batch payload items validated individually.

6. Review Python connector contracts separately from API contracts.
   - `src/solstein/infrastructure/fact_payloads.py` still allows extra fields intentionally.
   - Tightening should happen only after connector-specific metadata compatibility review.

### Suggested implementation order

1. `companies.py`
2. `async_jobs.py`
3. `simulation.py`
4. `scoring.py`
5. `review.py`

This order prioritizes the broadest and riskiest active request shapes first.

## Commit Traceability (Session + Remote)

- Session commit reviewed: `eed7ff2` (`audit: harden validation schema strictness at boundaries`).
  - Added this audit file and hardened strict boundary behavior in:
    - `src/solstein/api/schemas/validation.py`
    - `src/solstein/api/schemas/enrichment.py`
    - `src/solstein/api/schemas/semantic_search.py`
    - `src/solstein/api/routers/auth.py`
    - `src/solstein/api/routers/exports.py`
    - `tooling/contracts-ts/src/external/facts.ts`

- Latest remote commit reviewed: `68cd20e` (`docs: add external API inventory summary`).
  - Added `docs/reference/EXTERNAL_API_INVENTORY_2026-03-31.md`, which now acts as the external contract inventory for strict schema boundary planning.

- Baseline hardening context reviewed: `8562cb0` (`chore(lint): enforce full ruff compliance across src and tests`).
  - Not a boundary-schema change, but a broad code-quality pass affecting both `src/` and `tests/` and useful as the immediate pre-audit baseline.

- Documentation linkage for future implementers:
  - Validation boundary hardening details: this file.
  - External API contract inventory: `docs/reference/EXTERNAL_API_INVENTORY_2026-03-31.md`.
  - Dual-runtime migration reality: `docs/architecture/research-graph.md`.
