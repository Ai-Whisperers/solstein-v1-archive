# STORY-085: Wire api_prefix to All Route Definitions

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P2 |
| Severity | MEDIUM |
| Epic | [EPIC-010: API Layer Hardening](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-022](../STORIES/STORY-022-route-directory-consolidation.md) (route directory consolidation) |

---

## The Audit Verdict

> `config.py` defines `api_prefix = '/api/v1'` but this prefix is not applied to any route definition in `api/routers/`. All routes are accessible at `/companies`, `/enrichment`, etc. — not `/api/v1/companies`, `/api/v1/enrichment`. The versioning infrastructure exists in config but is disconnected from the actual routes.

## Problem Statement

An API versioning prefix defined in config but not applied to routes provides no versioning benefit. Clients cannot rely on a stable `/api/v1/` namespace. Adding versioning later, after clients have integrated with unversioned paths, is a breaking change.

## Impact

| Dimension | Effect |
|-----------|--------|
| **API Stability** | No versioned namespace exists — clients integrate against unversioned paths that cannot be maintained alongside future versions |
| **Breaking Changes** | Adding versioning after client integration forces all clients to update simultaneously |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/api/main.py` | Modify | Apply `settings.api_prefix` to the router registration |
| `src/solstein/api/routers/` | Modify | Verify all routers are registered under the prefix |

## Architectural Requirements

*What — never how. No code.*

- **REQ-1**: All private API routes must be accessible under the configured `api_prefix` (e.g., `/api/v1/companies`)
- **REQ-2**: The prefix must be read from configuration — not hardcoded in router definitions
- **REQ-3**: The OpenAPI schema must reflect the versioned paths
- **REQ-4**: Public routes (`/health`, `/docs`) must remain unversioned

## Acceptance Criteria

- [ ] GET /api/v1/companies returns the same response as GET /companies did before
- [ ] GET /companies returns HTTP 404 (old path no longer exists)
- [ ] OpenAPI schema shows `/api/v1/` prefixed paths

## Definition of Done

**Tests Required:**
- [ ] Integration test: versioned paths accessible, unversioned paths 404
- [ ] OpenAPI contract test: all private routes have /api/v1/ prefix

**Documentation Required:**
- [ ] API versioning strategy documented
- [ ] Client migration guide for path updates

**Code Review Gate:**
- [ ] Reviewer confirms prefix is read from config, not hardcoded
- [ ] Reviewer confirms public routes remain unversioned

## Notes

This is a low-risk, high-clarity story. The config already defines the prefix — the work is purely wiring it to the router registration in `main.py`. The longer this is deferred, the more clients integrate against unversioned paths, and the more painful the eventual migration becomes.

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
