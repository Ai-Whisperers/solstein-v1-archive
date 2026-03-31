# Validation Schema Strictness Audit - 2026-03-31

## Scope and Goal

Audit current validation schema structure and runtime enforcement strictness across:

- Python API boundary schemas (`src/solstein/api/schemas/*.py` and request models in routers)
- TypeScript contract schemas (`tooling/contracts-ts/src/**/*.ts`)

Goal: identify strictness gaps, fix what is safe now, and document unresolved items requiring deeper follow-up.

## Audit Method

- Direct codebase inspection with grep/read/LSP tooling.
- Parallel exploration agents were launched but failed due external access restrictions in this environment.
- External reference sweep (librarian) completed and confirmed Zod strictness best practices (strict object handling, safe parsing at boundaries, coercion caveats).

## Current State Before Fixes

### 1) Python request schemas accepted unknown fields in multiple boundary models

By default, Pydantic models without `extra="forbid"` can silently accept/drop unexpected keys, which weakens API contract enforcement.

### 2) SearchRequest validation order bug risk

`SearchRequest` validated `field` against `model_type` inside a field validator, which can execute before `model_type` is finalized. This can lead to allowlist checks being applied against the wrong model type.

### 3) TS connector fact contracts were permissive on unknown keys

`tooling/contracts-ts/src/external/facts.ts` used `.passthrough()` for both input and canonical schemas, allowing contract drift to pass through boundary validation.

### 4) Legacy validation schema module exists but is not wired into active API handlers

`src/solstein/api/schemas/validation.py` contains strict domain request models, but current routing paths mostly use other schemas or inline models.

## Fixes Applied

### A) Hardened Python API request schema strictness

- `src/solstein/api/schemas/validation.py`
  - Added `StrictRequestModel` with `ConfigDict(extra="forbid", str_strip_whitespace=True)`.
  - Applied to `SearchRequest`, `PaginationParams`, `CompanyFilterRequest`, `MarketAnalysisRequest`, `ScoreUpdateRequest`, and `CompanyCreateRequest`.
  - Moved model-type field allowlist enforcement in `SearchRequest` to a model-level validator so cross-field validation runs on a fully parsed model.

- `src/solstein/api/schemas/enrichment.py`
  - `EnrichmentRequest` and `BatchEnrichmentRequest` now enforce:
    - `extra="forbid"`
    - `str_strip_whitespace=True`
  - Replaced mutable list default for `sources` with `default_factory`.

- `src/solstein/api/routers/auth.py`
  - Hardened boundary request models:
    - `LoginRequest` and `RefreshRequest` now forbid extra fields.
    - Added explicit password length bounds for login.
    - Added refresh token length bounds.

### B) Hardened TypeScript connector fact contracts

- `tooling/contracts-ts/src/external/facts.ts`
  - Changed base input envelope from `.passthrough()` to `.strict()`.
  - Changed canonical `ConnectorFactSchema` from `.passthrough()` to `.strict()`.
  - Updated transform output to explicit canonical fields only (prevents leaking permissive input fields into canonical output).

## Verification Results

### TypeScript contracts

- `npm --prefix tooling/contracts-ts ci` -> passed
- `npm --prefix tooling/contracts-ts run check` -> passed
- `npm --prefix tooling/contracts-ts run build` -> passed

### Python runtime checks

- `python3 -m compileall` on modified Python modules -> passed (syntax-level validation).

### Python test execution

- `pytest` and `python3 -m pytest` unavailable initially (`pytest` not installed in this runtime image).
- Full Python behavioral test pass could not be executed in this environment and must be run in the project test environment/CI.

### LSP diagnostics

- LSP reports unresolved imports (`pydantic`, `fastapi`, `loguru`, etc.) due this runtime's language server environment not being configured with project dependencies.
- TS modified file diagnostics (`facts.ts`) returned clean.

## Remaining Issues Requiring Further Analysis

1. Request models still defined inline in several active routers without shared strict base policy:
   - `src/solstein/api/routers/companies.py`
   - `src/solstein/api/routers/simulation.py`
   - `src/solstein/api/routers/async_jobs.py`
   - `src/solstein/api/routers/review.py`
   - `src/solstein/api/routers/scoring.py`

2. `src/solstein/api/schemas/validation.py` appears underused by active API routes.
   - This should be either (a) wired into handlers, or (b) retired/migrated to avoid split-brain validation policy.

3. Python connector boundary in `src/solstein/infrastructure/fact_payloads.py` intentionally uses `extra="allow"`.
   - This may be required for connector-specific metadata, but it is not strict and should be evaluated with connector owners before tightening.

4. FastAPI/Pydantic strictness policy is currently fragmented across modules.
   - Recommend introducing a shared boundary base model (single source of strict config) and applying it incrementally to all request schemas.

## Recommended Next Steps (Priority Order)

1. Apply strict request model policy to remaining inline router request models.
2. Add/extend contract tests that explicitly assert unknown field rejection at API boundaries.
3. Decide lifecycle for `api/schemas/validation.py` (wire or deprecate).
4. Perform connector-by-connector compatibility review before changing Python fact payload `extra="allow"`.
5. Run full Python test suite in CI/test container with dependencies installed to validate behavioral compatibility.
