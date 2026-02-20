-- Solstein Data Storage Schema
-- Initialization for the 1.0 Enterprise Migration

CREATE TABLE public.companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(100) NOT NULL,
    tier VARCHAR(50) NOT NULL,
    
    -- Scored Metrics
    growth_score NUMERIC(5, 2),
    financial_health_score NUMERIC(5, 2),
    competitive_position_score NUMERIC(5, 2),
    
    -- Core Traits
    classification VARCHAR(50),
    scoring_breakdown JSONB DEFAULT '{}'::jsonb,
    financials JSONB DEFAULT '{}'::jsonb,
    
    -- Audit Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for efficient filtering
CREATE INDEX idx_companies_tier ON public.companies(tier);
CREATE INDEX idx_companies_industry ON public.companies(industry);
CREATE INDEX idx_companies_classification ON public.companies(classification);

-- Add an update trigger for updated_at
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON public.companies
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Enable RLS for future multi-tenancy (Optional, good practice)
ALTER TABLE public.companies ENABLE ROW LEVEL SECURITY;

-- Allow read/write access to authenticated service role / anon keys for now
CREATE POLICY "Allow basic anon read" ON public.companies FOR SELECT TO anon USING (true);
CREATE POLICY "Allow basic anon insert" ON public.companies FOR INSERT TO anon WItH CHECK (true);
CREATE POLICY "Allow basic anon update" ON public.companies FOR UPDATE TO anon USING (true);
