-- Migration 008: Enrichment Tables
-- Creates tables for enrichment audit trail, cache, and jobs

-- Enrichment audit trail
CREATE TABLE IF NOT EXISTS public.enrichment_audit_trail (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(255) NOT NULL,
    company_name VARCHAR(500),
    
    operation VARCHAR(50) NOT NULL,  -- 'enrich_start', 'enrich_success', 'enrich_failure', 'cache_hit', 'cache_miss'
    source VARCHAR(255),  -- 'SEC_EDGAR', 'Companies_House', 'News_Signals'
    status VARCHAR(50) NOT NULL,  -- 'SUCCESS', 'FAILURE', 'SKIPPED'
    
    duration_ms NUMERIC,
    
    fields_enriched JSONB,  -- List of fields that were enriched
    error_message TEXT,
    
    user_id VARCHAR(255),
    client_id VARCHAR(255),
    
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for enrichment audit
CREATE INDEX IF NOT EXISTS ix_enrichment_audit_company_id ON public.enrichment_audit_trail(company_id);
CREATE INDEX IF NOT EXISTS ix_enrichment_audit_company_timestamp ON public.enrichment_audit_trail(company_id, timestamp);
CREATE INDEX IF NOT EXISTS ix_enrichment_audit_operation ON public.enrichment_audit_trail(operation);
CREATE INDEX IF NOT EXISTS ix_enrichment_audit_operation_timestamp ON public.enrichment_audit_trail(operation, timestamp);
CREATE INDEX IF NOT EXISTS ix_enrichment_audit_timestamp ON public.enrichment_audit_trail(timestamp);

-- Enrichment cache
CREATE TABLE IF NOT EXISTS public.enrichment_cache (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(255) NOT NULL UNIQUE,
    
    enriched_data JSONB NOT NULL,  -- Full UnifiedCompany serialized as JSON
    sources_used JSONB,  -- List of sources used for enrichment
    fields_enriched JSONB,  -- List of fields that were enriched
    
    cached_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ttl_seconds INTEGER DEFAULT 86400,  -- 24 hours default
    expires_at TIMESTAMPTZ NOT NULL,
    
    hits INTEGER DEFAULT 0,  -- Number of cache hits
    last_accessed_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for enrichment cache
CREATE INDEX IF NOT EXISTS ix_enrichment_cache_company_id ON public.enrichment_cache(company_id);
CREATE INDEX IF NOT EXISTS ix_enrichment_cache_expires ON public.enrichment_cache(expires_at);
CREATE INDEX IF NOT EXISTS ix_enrichment_cache_cached_at ON public.enrichment_cache(cached_at);

-- Enrichment jobs (async job tracking)
CREATE TABLE IF NOT EXISTS public.enrichment_jobs (
    id VARCHAR(255) PRIMARY KEY,  -- Celery task_id
    
    company_id VARCHAR(255) NOT NULL,
    company_name VARCHAR(500),
    job_type VARCHAR(50) NOT NULL,  -- 'single', 'batch'
    
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',  -- 'PENDING', 'RUNNING', 'SUCCESS', 'FAILED'
    progress INTEGER DEFAULT 0,  -- 0-100 for batch jobs
    
    sources JSONB,
    batch_size INTEGER,
    
    result_data JSONB,  -- Full result
    error_message TEXT,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_ms NUMERIC,
    
    user_id VARCHAR(255),
    
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for enrichment jobs
CREATE INDEX IF NOT EXISTS ix_enrichment_job_company_id ON public.enrichment_jobs(company_id);
CREATE INDEX IF NOT EXISTS ix_enrichment_job_status ON public.enrichment_jobs(status);
CREATE INDEX IF NOT EXISTS ix_enrichment_job_status_created ON public.enrichment_jobs(status, created_at);
CREATE INDEX IF NOT EXISTS ix_enrichment_job_company_created ON public.enrichment_jobs(company_id, created_at);
CREATE INDEX IF NOT EXISTS ix_enrichment_job_created_at ON public.enrichment_jobs(created_at);

-- Enable RLS
ALTER TABLE public.enrichment_audit_trail ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.enrichment_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.enrichment_jobs ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Allow basic anon read" ON public.enrichment_audit_trail FOR SELECT TO anon USING (true);
CREATE POLICY "Allow basic anon insert" ON public.enrichment_audit_trail FOR INSERT TO anon WITH CHECK (true);

CREATE POLICY "Allow basic anon read" ON public.enrichment_cache FOR SELECT TO anon USING (true);
CREATE POLICY "Allow basic anon insert" ON public.enrichment_cache FOR INSERT TO anon WITH CHECK (true);
CREATE POLICY "Allow basic anon update" ON public.enrichment_cache FOR UPDATE TO anon USING (true);

CREATE POLICY "Allow basic anon read" ON public.enrichment_jobs FOR SELECT TO anon USING (true);
CREATE POLICY "Allow basic anon insert" ON public.enrichment_jobs FOR INSERT TO anon WITH CHECK (true);
CREATE POLICY "Allow basic anon update" ON public.enrichment_jobs FOR UPDATE TO anon USING (true);

-- Update triggers for updated_at
CREATE TRIGGER set_timestamp_enrichment_cache
BEFORE UPDATE ON public.enrichment_cache
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

CREATE TRIGGER set_timestamp_enrichment_jobs
BEFORE UPDATE ON public.enrichment_jobs
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();
