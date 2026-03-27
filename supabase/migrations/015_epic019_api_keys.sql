-- Migration 015: EPIC-019 STORY-065 API Key Management Tables
-- Creates tables for tenant-scoped API keys and usage logging.

-- API keys table
CREATE TABLE IF NOT EXISTS public.api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    key_prefix VARCHAR(16) NOT NULL,
    key_hash VARCHAR(64) NOT NULL UNIQUE,
    scope VARCHAR(50) NOT NULL DEFAULT 'read_only',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    revoked_at TIMESTAMPTZ,

    CONSTRAINT ck_api_key_scope CHECK (scope IN ('read_only', 'read_write', 'admin'))
);

CREATE INDEX IF NOT EXISTS ix_api_keys_tenant_id ON public.api_keys(tenant_id);
CREATE INDEX IF NOT EXISTS ix_api_keys_key_hash ON public.api_keys(key_hash);
CREATE INDEX IF NOT EXISTS ix_api_keys_tenant_active ON public.api_keys(tenant_id, is_active);

-- API key usage logging table
CREATE TABLE IF NOT EXISTS public.api_key_usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    api_key_id UUID NOT NULL REFERENCES public.api_keys(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL,
    endpoint VARCHAR(500) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_api_key_usage_key_timestamp ON public.api_key_usage_logs(api_key_id, timestamp);
CREATE INDEX IF NOT EXISTS ix_api_key_usage_tenant_timestamp ON public.api_key_usage_logs(tenant_id, timestamp);

-- Enable RLS on both tables
ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.api_key_usage_logs ENABLE ROW LEVEL SECURITY;

-- Tenant-scoped RLS policies for api_keys
CREATE POLICY "tenant_select" ON public.api_keys
    FOR SELECT TO authenticated
    USING (tenant_id::text = public.get_user_tenant_id());

CREATE POLICY "tenant_insert" ON public.api_keys
    FOR INSERT TO authenticated
    WITH CHECK (tenant_id::text = public.get_user_tenant_id());

CREATE POLICY "tenant_update" ON public.api_keys
    FOR UPDATE TO authenticated
    USING (tenant_id::text = public.get_user_tenant_id());

CREATE POLICY "tenant_delete" ON public.api_keys
    FOR DELETE TO authenticated
    USING (tenant_id::text = public.get_user_tenant_id());

-- Tenant-scoped RLS policies for usage logs
CREATE POLICY "tenant_select" ON public.api_key_usage_logs
    FOR SELECT TO authenticated
    USING (tenant_id::text = public.get_user_tenant_id());

CREATE POLICY "tenant_insert" ON public.api_key_usage_logs
    FOR INSERT TO authenticated
    WITH CHECK (tenant_id::text = public.get_user_tenant_id());
