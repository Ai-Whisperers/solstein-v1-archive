-- Migration 007: Scoring Records
-- Creates tables for company scoring results and signals

-- Scoring results table
CREATE TABLE IF NOT EXISTS public.scoring_records (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(255) NOT NULL,
    company_name VARCHAR(500) NOT NULL,
    
    growth_score NUMERIC(5, 2) NOT NULL,
    financial_health_score NUMERIC(5, 2) NOT NULL,
    competitive_position_score NUMERIC(5, 2) NOT NULL,
    overall_score NUMERIC(5, 2) NOT NULL,
    
    classification VARCHAR(50) NOT NULL,
    
    scored_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    data_sources_used JSONB,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for scoring records
CREATE INDEX IF NOT EXISTS ix_scoring_company_id ON public.scoring_records(company_id);
CREATE INDEX IF NOT EXISTS ix_scoring_company_scored_at ON public.scoring_records(company_id, scored_at);
CREATE INDEX IF NOT EXISTS ix_scoring_overall_score ON public.scoring_records(overall_score);
CREATE INDEX IF NOT EXISTS ix_scoring_classification ON public.scoring_records(classification);
CREATE INDEX IF NOT EXISTS ix_scoring_scored_at ON public.scoring_records(scored_at);

-- Signal records table (child of scoring_records)
CREATE TABLE IF NOT EXISTS public.signal_records (
    id SERIAL PRIMARY KEY,
    scoring_record_id INTEGER NOT NULL REFERENCES public.scoring_records(id) ON DELETE CASCADE,
    
    signal_name VARCHAR(255) NOT NULL,
    signal_category VARCHAR(50) NOT NULL,
    signal_value NUMERIC,
    signal_text VARCHAR(2000),
    
    source_agent VARCHAR(100) NOT NULL,
    evidence JSONB,
    
    confidence NUMERIC(5, 2) NOT NULL,
    
    extracted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for signal records
CREATE INDEX IF NOT EXISTS ix_signal_scoring_record ON public.signal_records(scoring_record_id);
CREATE INDEX IF NOT EXISTS ix_signal_name ON public.signal_records(signal_name);
CREATE INDEX IF NOT EXISTS ix_signal_category ON public.signal_records(signal_category);
CREATE INDEX IF NOT EXISTS ix_signal_name_category ON public.signal_records(signal_name, signal_category);
CREATE INDEX IF NOT EXISTS ix_signal_extracted_at ON public.signal_records(extracted_at);

-- Enable RLS
ALTER TABLE public.scoring_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.signal_records ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Allow basic anon read" ON public.scoring_records FOR SELECT TO anon USING (true);
CREATE POLICY "Allow basic anon insert" ON public.scoring_records FOR INSERT TO anon WITH CHECK (true);
CREATE POLICY "Allow basic anon update" ON public.scoring_records FOR UPDATE TO anon USING (true);

CREATE POLICY "Allow basic anon read" ON public.signal_records FOR SELECT TO anon USING (true);
CREATE POLICY "Allow basic anon insert" ON public.signal_records FOR INSERT TO anon WITH CHECK (true);
CREATE POLICY "Allow basic anon update" ON public.signal_records FOR UPDATE TO anon USING (true);

-- Update trigger for updated_at
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON public.scoring_records
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();
