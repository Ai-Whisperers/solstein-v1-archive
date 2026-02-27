-- Migration 010: Audit Trail
-- Creates table for complete audit trail of company analysis

CREATE TABLE IF NOT EXISTS public.audit_trails (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(255) NOT NULL,
    gathering_batch_id VARCHAR(255) NOT NULL,
    company_name VARCHAR(500) NOT NULL,
    
    -- Analysis artifacts (Stored as JSON for transparency)
    raw_data JSONB,
    aggregated_facts JSONB,
    extracted_signals JSONB,
    
    -- Scores
    growth_score NUMERIC(5, 2),
    financial_health_score NUMERIC(5, 2),
    competitive_position_score NUMERIC(5, 2),
    classification VARCHAR(50),
    
    scoring_breakdown JSONB,
    
    -- Timing
    analysis_started_at TIMESTAMPTZ,
    analysis_completed_at TIMESTAMPTZ,
    analysis_duration_seconds NUMERIC,
    
    -- Data quality
    data_completeness NUMERIC(5, 2) DEFAULT 0.0,
    confidence_level VARCHAR(50) DEFAULT 'unknown',
    
    -- Errors and warnings
    errors JSONB DEFAULT '[]'::jsonb,
    warnings JSONB DEFAULT '[]'::jsonb,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for audit trails
CREATE INDEX IF NOT EXISTS ix_audit_company_id ON public.audit_trails(company_id);
CREATE INDEX IF NOT EXISTS ix_audit_company_batch ON public.audit_trails(company_id, gathering_batch_id);
CREATE INDEX IF NOT EXISTS ix_audit_gathering_batch ON public.audit_trails(gathering_batch_id);
CREATE INDEX IF NOT EXISTS ix_audit_classification ON public.audit_trails(classification);
CREATE INDEX IF NOT EXISTS ix_audit_created_at ON public.audit_trails(created_at);
CREATE INDEX IF NOT EXISTS ix_audit_analysis_completed ON public.audit_trails(analysis_completed_at);

-- Enable RLS
ALTER TABLE public.audit_trails ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Allow basic anon read" ON public.audit_trails FOR SELECT TO anon USING (true);
CREATE POLICY "Allow basic anon insert" ON public.audit_trails FOR INSERT TO anon WITH CHECK (true);
CREATE POLICY "Allow basic anon update" ON public.audit_trails FOR UPDATE TO anon USING (true);

-- Update trigger for updated_at
CREATE TRIGGER set_timestamp_audit_trails
BEFORE UPDATE ON public.audit_trails
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();
