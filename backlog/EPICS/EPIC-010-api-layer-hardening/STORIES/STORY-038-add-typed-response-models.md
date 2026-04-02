# STORY-038: Add Typed Response Models to All Endpoints

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | MEDIUM |
| Epic | [EPIC-010: API Layer Hardening](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-036](STORY-036-move-business-logic-from-routers.md) (service extraction), [STORY-023](../../EPIC-007-ddd-migration/STORIES/STORY-023-introduce-value-objects.md) (Value Objects) |

---

## The Audit Verdict

> More than 12 endpoints declare their response type as `dict[str, Any]` or have no response model at all. The API has no contract. Clients cannot know what fields to expect. The OpenAPI schema for these endpoints is useless.

## Problem Statement

Endpoints without typed response models provide no API contract guarantee. The server can return any shape and the client has no recourse. The OpenAPI schema generated for these endpoints shows `object` with no properties — which is technically accurate and practically useless.

The consequences compound:
- **No validation**: FastAPI only validates responses if a `response_model` is declared. Without it, any dict is returned as-is, including None values, extra fields, and inconsistent key names.
- **No documentation**: The OpenAPI/Swagger UI shows no response schema, so API consumers must reverse-engineer the response format from examples.
- **No change detection**: If a developer removes a field from a response, no test fails, no type checker warns, no CI gate catches it. The breaking change ships silently.
- **No serialisation control**: Without a Pydantic model, datetime fields may serialise differently depending on the JSON encoder, float precision is uncontrolled, and enum values may appear as strings or integers depending on the code path.

## Impact

| Dimension | Effect |
|-----------|--------|
| **API Contract** | No enforced response schema — the contract is "whatever the handler returns today" |
| **Documentation** | OpenAPI schema is incomplete — consumers cannot generate typed clients |
| **Client Reliability** | Clients cannot safely depend on response structure |
| **Testing** | Response shape changes are undetected by any automated test |
| **Serialisation** | Inconsistent field formatting across endpoints (datetime formats, number precision) |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| All router files in `src/solstein/api/routers/` | Modify | Add `response_model` to every route decorator |
| `src/solstein/api/schemas/` | Add | Response model Pydantic classes |
| New: `src/solstein/api/schemas/company_responses.py` | Add | Company-related response models |
| New: `src/solstein/api/schemas/enrichment_responses.py` | Add | Enrichment-related response models |
| New: `src/solstein/api/schemas/scoring_responses.py` | Add | Scoring-related response models |
| New: `src/solstein/api/schemas/export_responses.py` | Add | Export-related response models |

## Architectural Requirements

- **REQ-1**: Every endpoint must declare a `response_model` parameter in its route decorator — no endpoint may return an untyped response
- **REQ-2**: Response models must be Pydantic models — not `dict`, `Any`, `dict[str, Any]`, or untyped dict
- **REQ-3**: Response models must be defined in `api/schemas/` and be reusable across endpoints that share response shapes
- **REQ-4**: The OpenAPI schema (`/openapi.json`) must contain complete response schemas for every endpoint — a client should be able to generate a typed SDK from the schema
- **REQ-5**: Response models should use Value Objects from STORY-023 where appropriate (e.g., `Revenue` serialised with amount and currency, not a bare float)

## Acceptance Criteria

- [ ] Zero endpoints have `response_model=None` or `response_model=dict` or no response model at all
- [ ] The OpenAPI schema contains complete response schemas for every endpoint
- [ ] A field removal from a response model causes a test failure (schema contract test)
- [ ] All datetime fields serialise in ISO 8601 format across all endpoints
- [ ] All numeric fields have consistent precision across all endpoints
- [ ] `grep -rn "-> dict" src/solstein/api/routers/ --include="*.py"` returns zero results (no dict return types)

## Definition of Done

**Tests Required:**
- [ ] Schema contract test: generate OpenAPI schema and assert all endpoints have defined response models with properties
- [ ] Test: a response field removal from a Pydantic model triggers a validation error in tests
- [ ] Test: all response models can be instantiated with valid test data
- [ ] Test: response serialisation produces consistent datetime and numeric formats

**Documentation Required:**
- [ ] API schemas module documented with examples of response format
- [ ] OpenAPI schema verified to be complete and accurate (manual review)

**Code Review Gate:**
- [ ] Reviewer confirms every endpoint has a `response_model`
- [ ] Reviewer confirms response models are Pydantic classes, not dicts
- [ ] Reviewer confirms the OpenAPI schema reflects the actual response format

## Notes

This story depends on STORY-036 (service extraction) because response models should reflect the service method return types, not the internal data structures of router handlers. It depends on STORY-023 (Value Objects) because response models should serialise Value Objects meaningfully — `Revenue` should appear as `{"amount": 1000000, "currency": "USD"}`, not as `1000000.0`.

Start by auditing all endpoints to identify which currently have `response_model` and which do not. Generate the current OpenAPI schema and identify gaps. Then define response models for each endpoint group (company, enrichment, scoring, export) and wire them into the route decorators.

The response models may reveal inconsistencies in what different endpoints return for the same entity. If two endpoints return `Company` data with different fields, this story must resolve the inconsistency — not codify it into two different response models.

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
