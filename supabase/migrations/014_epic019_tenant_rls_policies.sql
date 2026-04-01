-- Migration 014: EPIC-019 Tenant Row Level Security Policies
-- STORY-064: Replace permissive anon policies with tenant-scoped RLS
--
-- This migration:
--   1. Creates a helper function to extract tenant_id from JWT claims
--   2. Adds tenant_id columns to all tenant-scoped tables
--   3. Backfills existing rows with the default migration tenant
--   4. Drops old permissive anon policies
--   5. Creates tenant-scoped policies for the authenticated role
--
-- NOTE: The Supabase service_role bypasses RLS by default, so no
-- explicit bypass policy is needed for background jobs.

-- ============================================================
-- 0. Constants
-- ============================================================
-- Default tenant UUID used for backfilling pre-existing rows.
-- Must match DEFAULT_TENANT_ID in solstein.domain.models.
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'default_tenant_const') THEN
        PERFORM set_config('epic019.default_tenant', '00000000-0000-0000-0000-000000000000', false);
    END IF;
END $$;

-- ============================================================
-- 1. Helper function: extract tenant_id from Supabase JWT
-- ============================================================
-- Supabase stores custom claims in app_metadata. The JWT middleware
-- (STORY-068) sets tenant_id in app_metadata during signup/invite.
-- This function reads it from the JWT so RLS policies can reference it.

CREATE OR REPLACE FUNCTION public.get_user_tenant_id()
RETURNS TEXT
LANGUAGE sql
STABLE
SECURITY DEFINER
AS $$
    SELECT COALESCE(
        (auth.jwt() -> 'app_metadata' ->> 'tenant_id'),
        (auth.jwt() -> 'user_metadata' ->> 'tenant_id')
    );
$$;

COMMENT ON FUNCTION public.get_user_tenant_id() IS
    'EPIC-019: Extracts tenant_id from Supabase JWT app_metadata or user_metadata. Used by RLS policies.';

-- ============================================================
-- 2. Add tenant_id columns to all tenant-scoped tables
-- ============================================================

-- companies
ALTER TABLE public.companies
    ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255);
UPDATE public.companies
    SET tenant_id = '00000000-0000-0000-0000-000000000000'
    WHERE tenant_id IS NULL;
CREATE INDEX IF NOT EXISTS ix_companies_tenant_id ON public.companies(tenant_id);

-- scoring_records
ALTER TABLE public.scoring_records
    ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255);
UPDATE public.scoring_records
    SET tenant_id = '00000000-0000-0000-0000-000000000000'
    WHERE tenant_id IS NULL;
CREATE INDEX IF NOT EXISTS ix_scoring_records_tenant_id ON public.scoring_records(tenant_id);

-- signal_records (child of scoring_records, but needs tenant_id for direct RLS)
ALTER TABLE public.signal_records
    ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255);
UPDATE public.signal_records
    SET tenant_id = '00000000-0000-0000-0000-000000000000'
    WHERE tenant_id IS NULL;
CREATE INDEX IF NOT EXISTS ix_signal_records_tenant_id ON public.signal_records(tenant_id);

-- market_snapshots
ALTER TABLE public.market_snapshots
    ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255);
UPDATE public.market_snapshots
    SET tenant_id = '00000000-0000-0000-0000-000000000000'
    WHERE tenant_id IS NULL;
CREATE INDEX IF NOT EXISTS ix_market_snapshots_tenant_id ON public.market_snapshots(tenant_id);

-- audit_trails
ALTER TABLE public.audit_trails
    ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255);
UPDATE public.audit_trails
    SET tenant_id = '00000000-0000-0000-0000-000000000000'
    WHERE tenant_id IS NULL;
CREATE INDEX IF NOT EXISTS ix_audit_trails_tenant_id ON public.audit_trails(tenant_id);

-- research_runs
ALTER TABLE public.research_runs
    ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255);
UPDATE public.research_runs
    SET tenant_id = '00000000-0000-0000-0000-000000000000'
    WHERE tenant_id IS NULL;
CREATE INDEX IF NOT EXISTS ix_research_runs_tenant_id ON public.research_runs(tenant_id);

-- research_stages (child, but RLS needs direct tenant_id)
ALTER TABLE public.research_stages
    ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255);
UPDATE public.research_stages
    SET tenant_id = '00000000-0000-0000-0000-000000000000'
    WHERE tenant_id IS NULL;
CREATE INDEX IF NOT EXISTS ix_research_stages_tenant_id ON public.research_stages(tenant_id);

-- research_artifacts
ALTER TABLE public.research_artifacts
    ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255);
UPDATE public.research_artifacts
    SET tenant_id = '00000000-0000-0000-0000-000000000000'
    WHERE tenant_id IS NULL;
CREATE INDEX IF NOT EXISTS ix_research_artifacts_tenant_id ON public.research_artifacts(tenant_id);

-- source_documents
ALTER TABLE public.source_documents
    ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255);
UPDATE public.source_documents
    SET tenant_id = '00000000-0000-0000-0000-000000000000'
    WHERE tenant_id IS NULL;
CREATE INDEX IF NOT EXISTS ix_source_documents_tenant_id ON public.source_documents(tenant_id);

-- metric_observations
ALTER TABLE public.metric_observations
    ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255);
UPDATE public.metric_observations
    SET tenant_id = '00000000-0000-0000-0000-000000000000'
    WHERE tenant_id IS NULL;
CREATE INDEX IF NOT EXISTS ix_metric_observations_tenant_id ON public.metric_observations(tenant_id);

-- evidence_readiness
ALTER TABLE public.evidence_readiness
    ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255);
UPDATE public.evidence_readiness
    SET tenant_id = '00000000-0000-0000-0000-000000000000'
    WHERE tenant_id IS NULL;
CREATE INDEX IF NOT EXISTS ix_evidence_readiness_tenant_id ON public.evidence_readiness(tenant_id);

-- research_contradictions
ALTER TABLE public.research_contradictions
    ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255);
UPDATE public.research_contradictions
    SET tenant_id = '00000000-0000-0000-0000-000000000000'
    WHERE tenant_id IS NULL;
CREATE INDEX IF NOT EXISTS ix_research_contradictions_tenant_id ON public.research_contradictions(tenant_id);

-- enrichment_audit_trail
ALTER TABLE public.enrichment_audit_trail
    ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255);
UPDATE public.enrichment_audit_trail
    SET tenant_id = '00000000-0000-0000-0000-000000000000'
    WHERE tenant_id IS NULL;
CREATE INDEX IF NOT EXISTS ix_enrichment_audit_trail_tenant_id ON public.enrichment_audit_trail(tenant_id);

-- enrichment_cache
ALTER TABLE public.enrichment_cache
    ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255);
UPDATE public.enrichment_cache
    SET tenant_id = '00000000-0000-0000-0000-000000000000'
    WHERE tenant_id IS NULL;
CREATE INDEX IF NOT EXISTS ix_enrichment_cache_tenant_id ON public.enrichment_cache(tenant_id);

-- enrichment_jobs
ALTER TABLE public.enrichment_jobs
    ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255);
UPDATE public.enrichment_jobs
    SET tenant_id = '00000000-0000-0000-0000-000000000000'
    WHERE tenant_id IS NULL;
CREATE INDEX IF NOT EXISTS ix_enrichment_jobs_tenant_id ON public.enrichment_jobs(tenant_id);

-- outbox_records (infrastructure, but tenant-scoped for isolation)
ALTER TABLE public.outbox_records
    ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255);
UPDATE public.outbox_records
    SET tenant_id = '00000000-0000-0000-0000-000000000000'
    WHERE tenant_id IS NULL;
CREATE INDEX IF NOT EXISTS ix_outbox_records_tenant_id ON public.outbox_records(tenant_id);

-- release_gate_audit (not tenant-scoped — system-wide audit, skip)
-- tenants table itself (not tenant-scoped — it IS the tenant registry, skip)
-- contradiction_transitions (child of contradictions, inherits via FK, skip)

-- ============================================================
-- 3. Drop old permissive anon policies
-- ============================================================

-- companies
DROP POLICY IF EXISTS "Allow basic anon read" ON public.companies;
DROP POLICY IF EXISTS "Allow basic anon insert" ON public.companies;
DROP POLICY IF EXISTS "Allow basic anon update" ON public.companies;

-- research tables
DROP POLICY IF EXISTS "Allow basic anon read" ON public.research_runs;
DROP POLICY IF EXISTS "Allow basic anon read" ON public.research_stages;
DROP POLICY IF EXISTS "Allow basic anon read" ON public.research_artifacts;
DROP POLICY IF EXISTS "Allow basic anon read" ON public.source_documents;
DROP POLICY IF EXISTS "Allow basic anon read" ON public.metric_observations;
DROP POLICY IF EXISTS "Allow basic anon read" ON public.evidence_readiness;
DROP POLICY IF EXISTS "Allow basic anon read" ON public.research_contradictions;

-- scoring tables
DROP POLICY IF EXISTS "Allow basic anon read" ON public.scoring_records;
DROP POLICY IF EXISTS "Allow basic anon insert" ON public.scoring_records;
DROP POLICY IF EXISTS "Allow basic anon update" ON public.scoring_records;
DROP POLICY IF EXISTS "Allow basic anon read" ON public.signal_records;
DROP POLICY IF EXISTS "Allow basic anon insert" ON public.signal_records;
DROP POLICY IF EXISTS "Allow basic anon update" ON public.signal_records;

-- market_snapshots
DROP POLICY IF EXISTS "Allow basic anon read" ON public.market_snapshots;
DROP POLICY IF EXISTS "Allow basic anon insert" ON public.market_snapshots;
DROP POLICY IF EXISTS "Allow basic anon update" ON public.market_snapshots;

-- audit_trails
DROP POLICY IF EXISTS "Allow basic anon read" ON public.audit_trails;
DROP POLICY IF EXISTS "Allow basic anon insert" ON public.audit_trails;
DROP POLICY IF EXISTS "Allow basic anon update" ON public.audit_trails;

-- enrichment tables
DROP POLICY IF EXISTS "Allow basic anon read" ON public.enrichment_audit_trail;
DROP POLICY IF EXISTS "Allow basic anon insert" ON public.enrichment_audit_trail;
DROP POLICY IF EXISTS "Allow basic anon read" ON public.enrichment_cache;
DROP POLICY IF EXISTS "Allow basic anon insert" ON public.enrichment_cache;
DROP POLICY IF EXISTS "Allow basic anon update" ON public.enrichment_cache;
DROP POLICY IF EXISTS "Allow basic anon read" ON public.enrichment_jobs;
DROP POLICY IF EXISTS "Allow basic anon insert" ON public.enrichment_jobs;
DROP POLICY IF EXISTS "Allow basic anon update" ON public.enrichment_jobs;

-- outbox
DROP POLICY IF EXISTS "Allow basic anon read" ON public.outbox_records;

-- ============================================================
-- 4. Create tenant-scoped RLS policies for authenticated role
-- ============================================================
-- Pattern: Each table gets SELECT, INSERT, UPDATE, DELETE policies.
-- SELECT/UPDATE/DELETE use USING (tenant_id = get_user_tenant_id())
-- INSERT uses WITH CHECK (tenant_id = get_user_tenant_id())

-- ----- companies -----
CREATE POLICY "tenant_select" ON public.companies
    FOR SELECT TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_insert" ON public.companies
    FOR INSERT TO authenticated
    WITH CHECK (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_update" ON public.companies
    FOR UPDATE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_delete" ON public.companies
    FOR DELETE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

-- ----- scoring_records -----
CREATE POLICY "tenant_select" ON public.scoring_records
    FOR SELECT TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_insert" ON public.scoring_records
    FOR INSERT TO authenticated
    WITH CHECK (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_update" ON public.scoring_records
    FOR UPDATE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_delete" ON public.scoring_records
    FOR DELETE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

-- ----- signal_records -----
CREATE POLICY "tenant_select" ON public.signal_records
    FOR SELECT TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_insert" ON public.signal_records
    FOR INSERT TO authenticated
    WITH CHECK (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_update" ON public.signal_records
    FOR UPDATE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_delete" ON public.signal_records
    FOR DELETE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

-- ----- market_snapshots -----
CREATE POLICY "tenant_select" ON public.market_snapshots
    FOR SELECT TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_insert" ON public.market_snapshots
    FOR INSERT TO authenticated
    WITH CHECK (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_update" ON public.market_snapshots
    FOR UPDATE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_delete" ON public.market_snapshots
    FOR DELETE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

-- ----- audit_trails -----
CREATE POLICY "tenant_select" ON public.audit_trails
    FOR SELECT TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_insert" ON public.audit_trails
    FOR INSERT TO authenticated
    WITH CHECK (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_update" ON public.audit_trails
    FOR UPDATE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_delete" ON public.audit_trails
    FOR DELETE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

-- ----- research_runs -----
CREATE POLICY "tenant_select" ON public.research_runs
    FOR SELECT TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_insert" ON public.research_runs
    FOR INSERT TO authenticated
    WITH CHECK (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_update" ON public.research_runs
    FOR UPDATE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_delete" ON public.research_runs
    FOR DELETE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

-- ----- research_stages -----
CREATE POLICY "tenant_select" ON public.research_stages
    FOR SELECT TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_insert" ON public.research_stages
    FOR INSERT TO authenticated
    WITH CHECK (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_update" ON public.research_stages
    FOR UPDATE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_delete" ON public.research_stages
    FOR DELETE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

-- ----- research_artifacts -----
CREATE POLICY "tenant_select" ON public.research_artifacts
    FOR SELECT TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_insert" ON public.research_artifacts
    FOR INSERT TO authenticated
    WITH CHECK (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_update" ON public.research_artifacts
    FOR UPDATE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_delete" ON public.research_artifacts
    FOR DELETE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

-- ----- source_documents -----
CREATE POLICY "tenant_select" ON public.source_documents
    FOR SELECT TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_insert" ON public.source_documents
    FOR INSERT TO authenticated
    WITH CHECK (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_update" ON public.source_documents
    FOR UPDATE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_delete" ON public.source_documents
    FOR DELETE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

-- ----- metric_observations -----
CREATE POLICY "tenant_select" ON public.metric_observations
    FOR SELECT TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_insert" ON public.metric_observations
    FOR INSERT TO authenticated
    WITH CHECK (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_update" ON public.metric_observations
    FOR UPDATE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_delete" ON public.metric_observations
    FOR DELETE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

-- ----- evidence_readiness -----
CREATE POLICY "tenant_select" ON public.evidence_readiness
    FOR SELECT TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_insert" ON public.evidence_readiness
    FOR INSERT TO authenticated
    WITH CHECK (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_update" ON public.evidence_readiness
    FOR UPDATE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_delete" ON public.evidence_readiness
    FOR DELETE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

-- ----- research_contradictions -----
CREATE POLICY "tenant_select" ON public.research_contradictions
    FOR SELECT TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_insert" ON public.research_contradictions
    FOR INSERT TO authenticated
    WITH CHECK (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_update" ON public.research_contradictions
    FOR UPDATE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_delete" ON public.research_contradictions
    FOR DELETE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

-- ----- enrichment_audit_trail -----
CREATE POLICY "tenant_select" ON public.enrichment_audit_trail
    FOR SELECT TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_insert" ON public.enrichment_audit_trail
    FOR INSERT TO authenticated
    WITH CHECK (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_update" ON public.enrichment_audit_trail
    FOR UPDATE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_delete" ON public.enrichment_audit_trail
    FOR DELETE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

-- ----- enrichment_cache -----
CREATE POLICY "tenant_select" ON public.enrichment_cache
    FOR SELECT TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_insert" ON public.enrichment_cache
    FOR INSERT TO authenticated
    WITH CHECK (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_update" ON public.enrichment_cache
    FOR UPDATE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_delete" ON public.enrichment_cache
    FOR DELETE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

-- ----- enrichment_jobs -----
CREATE POLICY "tenant_select" ON public.enrichment_jobs
    FOR SELECT TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_insert" ON public.enrichment_jobs
    FOR INSERT TO authenticated
    WITH CHECK (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_update" ON public.enrichment_jobs
    FOR UPDATE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_delete" ON public.enrichment_jobs
    FOR DELETE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

-- ----- outbox_records -----
CREATE POLICY "tenant_select" ON public.outbox_records
    FOR SELECT TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_insert" ON public.outbox_records
    FOR INSERT TO authenticated
    WITH CHECK (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_update" ON public.outbox_records
    FOR UPDATE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

CREATE POLICY "tenant_delete" ON public.outbox_records
    FOR DELETE TO authenticated
    USING (tenant_id = public.get_user_tenant_id());

-- ============================================================
-- 5. Ensure RLS is enabled on all tables (idempotent)
-- ============================================================
-- These are no-ops if already enabled, but listed for completeness.

ALTER TABLE public.companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scoring_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.signal_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.market_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_trails ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.research_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.research_stages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.research_artifacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.source_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.metric_observations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.evidence_readiness ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.research_contradictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.enrichment_audit_trail ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.enrichment_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.enrichment_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.outbox_records ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- 6. Service role bypass note
-- ============================================================
-- In Supabase, the `service_role` key bypasses RLS by default.
-- Background jobs (Celery workers, etc.) should use the service_role
-- key when connecting, which gives them full access to all rows.
-- No explicit policy is needed for this — it is a Supabase built-in.
--
-- See: https://supabase.com/docs/guides/auth/row-level-security
