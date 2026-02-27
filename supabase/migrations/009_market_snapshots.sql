-- Migration 009: Market Snapshots
-- Creates table for market analysis snapshots

CREATE TABLE IF NOT EXISTS public.market_snapshots (
    id SERIAL PRIMARY KEY,
    
    snapshot_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    total_companies_scored INTEGER NOT NULL,
    average_growth_score NUMERIC(5, 2) NOT NULL,
    average_financial_score NUMERIC(5, 2) NOT NULL,
    average_competitive_score NUMERIC(5, 2) NOT NULL,
    
    phoenix_count INTEGER NOT NULL,
    salt_count INTEGER NOT NULL,
    lead_count INTEGER NOT NULL,
    
    market_metadata JSONB,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for market snapshots
CREATE INDEX IF NOT EXISTS ix_market_snapshot_date ON public.market_snapshots(snapshot_date);
CREATE INDEX IF NOT EXISTS ix_market_snapshot_created_at ON public.market_snapshots(created_at);

-- Enable RLS
ALTER TABLE public.market_snapshots ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Allow basic anon read" ON public.market_snapshots FOR SELECT TO anon USING (true);
CREATE POLICY "Allow basic anon insert" ON public.market_snapshots FOR INSERT TO anon WITH CHECK (true);
CREATE POLICY "Allow basic anon update" ON public.market_snapshots FOR UPDATE TO anon USING (true);

-- Update trigger for updated_at
CREATE TRIGGER set_timestamp_market_snapshots
BEFORE UPDATE ON public.market_snapshots
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();
