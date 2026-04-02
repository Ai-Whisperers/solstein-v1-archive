# STORY-063: Define the Tenant Model and Domain Object Scoping

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P1 |
| Severity | HIGH |
| Epic | [EPIC-019: Multi-Tenancy & Data Isolation](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [EPIC-020](../../EPIC-020-supabase-auth-migration/README.md) (Supabase Auth) |

---

## The Audit Verdict

> No `tenant_id`, `org_id`, or equivalent exists anywhere in `domain/models.py` (613 lines), `infrastructure/database_models.py` (768 lines), or any middleware. The platform is architecturally single-tenant by omission, not by design.

## Problem Statement

Without a tenant model, every database table is a shared namespace. Adding multi-tenancy after the fact is the most expensive architectural retrofit possible. The earlier this is defined, the lower the total migration cost.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Business** | No more than one firm can be onboarded without data contamination risk |
| **Architecture** | Every future feature must be retrofitted with tenant awareness retroactively if not done now |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/domain/models.py` | Modify | Add Tenant entity |
| `src/solstein/infrastructure/database_models.py` | Modify | Add tenant_id FK to all major tables |
| New Alembic migration file | Add | Migration to add tenant_id columns and backfill default tenant |

## Architectural Requirements

*What — never how. No code.*

- **REQ-1**: A `Tenant` entity must exist in the domain layer with: id, name, subscription tier, created_at, is_active
- **REQ-2**: Every table that holds business data (Company, FinancialData, Signal, Analysis, ResearchJob, EnrichmentAudit) must have a non-nullable `tenant_id` foreign key
- **REQ-3**: The `tenant_id` must be propagated through the entire domain object graph — no business entity may exist without a tenant owner
- **REQ-4**: A database migration must add `tenant_id` to all existing tables and backfill a default tenant for existing data
- **REQ-5**: The tenant model must be extensible for future per-tenant configuration (rate limits, data source access, feature flags)

## Acceptance Criteria

- [ ] `Tenant` entity exists in domain/models.py
- [ ] All major database tables have a `tenant_id` column
- [ ] A migration file exists and runs successfully
- [ ] Constructing a `Company` without a `tenant_id` raises a domain exception

## Definition of Done

**Tests Required:**
- [ ] Migration test: alembic upgrade head succeeds on a clean database
- [ ] Unit test: domain entity construction without tenant_id is rejected

**Documentation Required:**
- [ ] Entity relationship diagram updated to show tenant ownership

**Code Review Gate:**
- [ ] Reviewer confirms no business entity can be constructed without a tenant_id
- [ ] Reviewer confirms migration backfills a default tenant for existing data

## Notes

This is the foundational story for multi-tenancy. Every subsequent story in EPIC-019 depends on the tenant model defined here. Get the entity shape right — changing it later cascades across every RLS policy, every API endpoint, and every background job.

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
