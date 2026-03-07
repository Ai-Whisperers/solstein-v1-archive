# EPIC-010: API Layer Hardening

| Field | Value |
|-------|-------|
| Priority | P1 |
| Status | 🔴 Open |
| Stories | STORY-036, STORY-037, STORY-038 |
| Created | 2026-02-28 |

---

## Summary

An API without response types is not an API — it is a promise.

The API layer has three fundamental problems:

1. **Business logic in routers**: Scoring calculations, classification thresholds, and statistical aggregations live in HTTP handler functions. This was covered partially in EPIC-007 (STORY-027), but the API layer itself needs additional hardening beyond service extraction.

2. **Untyped responses**: More than 12 endpoints return `dict[str, Any]` as their response type. This means the API contract is undocumented, unvalidated, and unenforceable. Clients must guess what fields to expect. The OpenAPI schema for these endpoints is useless. Breaking changes in response shape are invisible.

3. **No resource limits**: Bulk endpoints (export, statistics, batch enrichment) load entire datasets with no result limit. A single authenticated request can trigger a memory-exhausting response. There is no pagination, no maximum page size, and no server-side enforcement of result limits.

## What This Epic Delivers

| Before | After |
|--------|-------|
| Business logic in router handlers | Router handlers contain only: parse request → call service → format response |
| `dict[str, Any]` response types | Every endpoint declares a Pydantic response model |
| Unlimited bulk responses | All bulk endpoints support pagination with enforced limits |
| Useless OpenAPI schema | Complete, accurate OpenAPI schema generated from response models |

## Stories

| Story | Title | Priority | Severity | Dependencies |
|-------|-------|----------|----------|--------------|
| [STORY-036](STORIES/STORY-036-move-business-logic-from-routers.md) | Move Business Logic Out of Router Handlers | P1 | HIGH | STORY-027 |
| [STORY-037](STORIES/STORY-037-add-pagination.md) | Add Pagination to All Bulk Endpoints | P1 | HIGH | STORY-034 |
| [STORY-038](STORIES/STORY-038-add-typed-response-models.md) | Add Typed Response Models to All Endpoints | P1 | MEDIUM | STORY-036, STORY-023 |

## Definition of Done

- [ ] Router handlers contain no business logic — only HTTP handling
- [ ] Every endpoint declares a Pydantic `response_model`
- [ ] All bulk endpoints support pagination with a server-enforced maximum page size
- [ ] The OpenAPI schema (`/openapi.json`) contains complete response schemas for every endpoint
- [ ] A field removal from any response model causes a test failure

## Ordering Notes

STORY-036 depends on STORY-027 (domain services) from EPIC-007. STORY-037 depends on STORY-034 (database-level filtering) from EPIC-009. STORY-038 depends on STORY-036 (service extraction) and STORY-023 (Value Objects) — response models should reflect Value Objects, not raw primitives.

Recommended execution order: STORY-036 → STORY-038, with STORY-037 executable in parallel with STORY-036 once its dependency (STORY-034) is complete.

## Relationship to Other Epics

This epic overlaps with EPIC-007 (DDD Migration) through STORY-036/STORY-027 — the service extraction work. It overlaps with EPIC-009 (Data Layer Consolidation) through STORY-037/STORY-034 — pagination requires database-level filtering. These overlaps are intentional: the same architectural principle (separation of concerns) manifests differently in the domain layer, the data layer, and the API layer.
