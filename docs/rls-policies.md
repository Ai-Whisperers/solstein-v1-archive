# Row Level Security (RLS) Policy Documentation

## EPIC-019: Multi-Tenancy Data Isolation

### Overview

All tenant-scoped tables in Solstein enforce Row Level Security (RLS) at the database layer.
This ensures that no authenticated user can query, insert, update, or delete rows belonging
to another tenant, regardless of application-level bugs or misconfiguration.

### Architecture

RLS policies use a helper function `public.get_user_tenant_id()` which extracts the
`tenant_id` from the authenticated user's JWT claims (Supabase Auth). The function checks
`app_metadata.tenant_id` first, falling back to `user_metadata.tenant_id`.

### Policy Pattern

Every tenant-scoped table has four policies:

| Policy | Operation | Clause | Effect |
|--------|-----------|--------|--------|
| `tenant_select` | SELECT | `USING (tenant_id = get_user_tenant_id())` | User can only read own tenant rows |
| `tenant_insert` | INSERT | `WITH CHECK (tenant_id = get_user_tenant_id())` | User can only insert rows for own tenant |
| `tenant_update` | UPDATE | `USING (tenant_id = get_user_tenant_id())` | User can only update own tenant rows |
| `tenant_delete` | DELETE | `USING (tenant_id = get_user_tenant_id())` | User can only delete own tenant rows |

### Tables with RLS Enabled

| Table | Domain | Notes |
|-------|--------|-------|
| `companies` | Company | Core company data |
| `scoring_records` | Scoring | Company scoring results |
| `signal_records` | Scoring | Individual signals (child of scoring_records) |
| `market_snapshots` | Market | Market state snapshots |
| `audit_trails` | Audit | Company analysis audit trail |
| `research_runs` | Research | Top-level research runs |
| `research_stages` | Research | Pipeline stage tracking |
| `research_artifacts` | Research | Produced artifacts |
| `source_documents` | Research | Source URLs per company |
| `metric_observations` | Research | Individual metric values |
| `evidence_readiness` | Research | Evidence quality scores |
| `research_contradictions` | Research | Detected data conflicts |
| `enrichment_audit_trail` | Enrichment | Enrichment operation audit |
| `enrichment_cache` | Enrichment | Cached enrichment data |
| `enrichment_jobs` | Enrichment | Async enrichment jobs |
| `outbox_records` | Infrastructure | Transactional outbox events |

### Tables Without RLS

| Table | Reason |
|-------|--------|
| `tenants` | This IS the tenant registry; not scoped to a single tenant |
| `release_gate_audit` | System-wide audit records, not tenant-specific |
| `research_contradiction_transitions` | Child table; inherits tenant scope through FK to contradictions |

### Service Role Bypass

Background jobs (Celery workers, scheduled tasks) connect using the Supabase `service_role`
key, which bypasses RLS by default. This is a Supabase built-in behavior and requires no
explicit policy. See [Supabase RLS docs](https://supabase.com/docs/guides/auth/row-level-security).

### Migration Files

| File | Type | Description |
|------|------|-------------|
| `supabase/migrations/014_epic019_tenant_rls_policies.sql` | Supabase SQL | Full RLS policy migration |
| `alembic/versions/014_epic019_rls_helper_function.py` | Alembic Python | Helper function + ENABLE RLS |

### Default Tenant

Pre-existing rows are backfilled with `tenant_id = '00000000-0000-0000-0000-000000000000'`
(the default migration tenant). This ensures backward compatibility during the transition
to full multi-tenancy.
