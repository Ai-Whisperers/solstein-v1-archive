-- Migration 002: Relationalize Financials
-- Extract core financial metrics from JSONB into dedicated numeric columns for performance

ALTER TABLE public.companies
ADD COLUMN revenue NUMERIC,
ADD COLUMN growth_rate NUMERIC,
ADD COLUMN profit_margin NUMERIC,
ADD COLUMN valuation NUMERIC,
ADD COLUMN employees INTEGER;

-- Backfill data from JSONB block
UPDATE public.companies
SET 
  revenue = (financials->>'revenue')::NUMERIC,
  growth_rate = (financials->>'growth_rate')::NUMERIC,
  profit_margin = (financials->>'profit_margin')::NUMERIC,
  valuation = (financials->>'valuation')::NUMERIC,
  employees = (financials->>'employees')::INTEGER
WHERE financials IS NOT NULL AND financials::text != '{}';

-- Create an index to support fast queries on revenue
CREATE INDEX idx_companies_revenue ON public.companies(revenue);
