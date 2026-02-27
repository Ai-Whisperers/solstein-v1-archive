-- Migration 007: Add missing columns to companies table
-- Adds all fields needed to store full company data from JSON

ALTER TABLE public.companies
    -- Company identifiers
    ADD COLUMN IF NOT EXISTS company_id VARCHAR(255) UNIQUE,
    
    -- Basic info
    ADD COLUMN IF NOT EXISTS description TEXT,
    ADD COLUMN IF NOT EXISTS website VARCHAR(500),
    ADD COLUMN IF NOT EXISTS headquarters VARCHAR(100),
    ADD COLUMN IF NOT EXISTS founded_year INTEGER,
    
    -- Positioning
    ADD COLUMN IF NOT EXISTS threat_level VARCHAR(50),
    
    -- Tech maturity
    ADD COLUMN IF NOT EXISTS ai_maturity VARCHAR(50),
    ADD COLUMN IF NOT EXISTS saas_maturity INTEGER,
    ADD COLUMN IF NOT EXISTS ai_score INTEGER,
    ADD COLUMN IF NOT EXISTS ai_signal_level VARCHAR(50),
    ADD COLUMN IF NOT EXISTS ai_key_capabilities TEXT,
    ADD COLUMN IF NOT EXISTS ai_in_production VARCHAR(10),
    
    -- Financials (latest)
    ADD COLUMN IF NOT EXISTS revenue_eur_m NUMERIC,
    ADD COLUMN IF NOT EXISTS revenue_confidence VARCHAR(50),
    ADD COLUMN IF NOT EXISTS growth_rate_pct NUMERIC,
    ADD COLUMN IF NOT EXISTS growth_confidence VARCHAR(50),
    ADD COLUMN IF NOT EXISTS profit_margin_pct NUMERIC,
    ADD COLUMN IF NOT EXISTS ebitda_margin_pct NUMERIC,
    ADD COLUMN IF NOT EXISTS recurring_revenue_pct NUMERIC,
    ADD COLUMN IF NOT EXISTS revenue_per_employee_eur_k NUMERIC,
    
    -- Revenue timeline (stored as JSON for full history)
    ADD COLUMN IF NOT EXISTS revenue_timeline JSONB,
    ADD COLUMN IF NOT EXISTS revenue_cagr_3yr NUMERIC,
    ADD COLUMN IF NOT EXISTS revenue_cagr_5yr NUMERIC,
    
    -- Funding
    ADD COLUMN IF NOT EXISTS funding_rounds JSONB,
    ADD COLUMN IF NOT EXISTS total_funding_raised_eur NUMERIC,
    ADD COLUMN IF NOT EXISTS latest_valuation_eur NUMERIC,
    ADD COLUMN IF NOT EXISTS lead_investors JSONB,
    ADD COLUMN IF NOT EXISTS funding_war_chest TEXT,
    
    -- Employees
    ADD COLUMN IF NOT EXISTS employee_count INTEGER,
    ADD COLUMN IF NOT EXISTS employee_cagr_3yr NUMERIC,
    ADD COLUMN IF NOT EXISTS open_positions INTEGER,
    
    -- Raw profitability metrics (from source)
    ADD COLUMN IF NOT EXISTS profitability_raw_metrics JSONB,
    
    -- Data quality
    ADD COLUMN IF NOT EXISTS data_availability TEXT,
    ADD COLUMN IF NOT EXISTS data_source VARCHAR(255),
    
    -- Scores (calculated)
    ADD COLUMN IF NOT EXISTS composite_score NUMERIC;

-- Create indexes for new columns
CREATE INDEX IF NOT EXISTS idx_companies_company_id ON public.companies(company_id);
CREATE INDEX IF NOT EXISTS idx_companies_name ON public.companies(name);
CREATE INDEX IF NOT EXISTS idx_companies_founded_year ON public.companies(founded_year);
CREATE INDEX IF NOT EXISTS idx_companies_ai_score ON public.companies(ai_score);
CREATE INDEX IF NOT EXISTS idx_companies_revenue_eur_m ON public.companies(revenue_eur_m);
CREATE INDEX IF NOT EXISTS idx_companies_employee_count ON public.companies(employee_count);
CREATE INDEX IF NOT EXISTS idx_companies_created_at ON public.companies(created_at);
