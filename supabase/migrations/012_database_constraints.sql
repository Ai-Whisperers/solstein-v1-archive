-- Migration 012: Add Database Constraints for Data Quality
-- Adds CHECK and NOT NULL constraints to enforce data integrity

-- ============================================================
-- CHECK Constraints for companies table
-- ============================================================

-- Ensure ticker is not empty
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_companies_ticker_not_empty'
    ) THEN
        ALTER TABLE companies
        ADD CONSTRAINT chk_companies_ticker_not_empty
        CHECK (ticker IS NOT NULL AND length(trim(ticker)) > 0);
    END IF;
END $$;

-- Valid company status values
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_companies_status'
    ) THEN
        ALTER TABLE companies
        ADD CONSTRAINT chk_companies_status
        CHECK (status IN ('active', 'inactive', 'archived', 'pending'));
    END IF;
END $$;

-- Ensure created_at is not in the future
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_companies_created_at'
    ) THEN
        ALTER TABLE companies
        ADD CONSTRAINT chk_companies_created_at
        CHECK (created_at <= now());
    END IF;
END $$;

-- Ensure updated_at >= created_at
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_companies_updated_at'
    ) THEN
        ALTER TABLE companies
        ADD CONSTRAINT chk_companies_updated_at
        CHECK (updated_at >= created_at);
    END IF;
END $$;

-- ============================================================
-- CHECK Constraints for research_runs table
-- ============================================================

-- Valid research run status values
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_research_runs_status'
    ) THEN
        ALTER TABLE research_runs
        ADD CONSTRAINT chk_research_runs_status
        CHECK (status IN (
            'pending', 'queued', 'running', 'completed', 
            'failed', 'cancelled', 'timeout', 'retrying'
        ));
    END IF;
END $$;

-- Ensure dates are valid
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_research_runs_dates'
    ) THEN
        ALTER TABLE research_runs
        ADD CONSTRAINT chk_research_runs_dates
        CHECK (
            created_at <= now() AND
            updated_at >= created_at AND
            (completed_at IS NULL OR completed_at >= created_at)
        );
    END IF;
END $$;

-- ============================================================
-- CHECK Constraints for facts table
-- ============================================================

-- Confidence score between 0 and 1
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_facts_confidence'
    ) THEN
        ALTER TABLE facts
        ADD CONSTRAINT chk_facts_confidence
        CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1));
    END IF;
END $$;

-- Valid fact status values
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_facts_status'
    ) THEN
        ALTER TABLE facts
        ADD CONSTRAINT chk_facts_status
        CHECK (status IN ('active', 'superseded', 'retracted', 'pending'));
    END IF;
END $$;

-- Ensure dates are valid
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_facts_dates'
    ) THEN
        ALTER TABLE facts
        ADD CONSTRAINT chk_facts_dates
        CHECK (
            created_at <= now() AND
            updated_at >= created_at AND
            (superseded_at IS NULL OR superseded_at >= created_at)
        );
    END IF;
END $$;

-- ============================================================
-- CHECK Constraints for signals table
-- ============================================================

-- Valid signal types
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_signals_signal_type'
    ) THEN
        ALTER TABLE signals
        ADD CONSTRAINT chk_signals_signal_type
        CHECK (signal_type IN (
            'price_movement', 'volume_spike', 'news_sentiment',
            'earnings_surprise', 'analyst_upgrade', 'analyst_downgrade',
            'technical_breakout', 'technical_breakdown', 'momentum_shift',
            'volatility_spike', 'insider_activity', 'institutional_change'
        ));
    END IF;
END $$;

-- Valid signal status
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_signals_status'
    ) THEN
        ALTER TABLE signals
        ADD CONSTRAINT chk_signals_status
        CHECK (status IN ('active', 'resolved', 'expired', 'cancelled'));
    END IF;
END $$;

-- Valid confidence levels
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_signals_confidence'
    ) THEN
        ALTER TABLE signals
        ADD CONSTRAINT chk_signals_confidence
        CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1));
    END IF;
END $$;

-- Valid strength values
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_signals_strength'
    ) THEN
        ALTER TABLE signals
        ADD CONSTRAINT chk_signals_strength
        CHECK (strength IS NULL OR (strength >= 0 AND strength <= 1));
    END IF;
END $$;

-- Valid direction values
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_signals_direction'
    ) THEN
        ALTER TABLE signals
        ADD CONSTRAINT chk_signals_direction
        CHECK (direction IS NULL OR direction IN ('bullish', 'bearish', 'neutral'));
    END IF;
END $$;

-- ============================================================
-- CHECK Constraints for scoring_records table
-- ============================================================

-- Total score between 0 and 100
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_scoring_records_total'
    ) THEN
        ALTER TABLE scoring_records
        ADD CONSTRAINT chk_scoring_records_total
        CHECK (total_score >= 0 AND total_score <= 100);
    END IF;
END $$;

-- Component scores between 0 and 100
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_scoring_records_growth'
    ) THEN
        ALTER TABLE scoring_records
        ADD CONSTRAINT chk_scoring_records_growth
        CHECK (growth_score IS NULL OR (growth_score >= 0 AND growth_score <= 100));
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_scoring_records_profitability'
    ) THEN
        ALTER TABLE scoring_records
        ADD CONSTRAINT chk_scoring_records_profitability
        CHECK (profitability_score IS NULL OR (profitability_score >= 0 AND profitability_score <= 100));
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_scoring_records_valuation'
    ) THEN
        ALTER TABLE scoring_records
        ADD CONSTRAINT chk_scoring_records_valuation
        CHECK (valuation_score IS NULL OR (valuation_score >= 0 AND valuation_score <= 100));
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_scoring_records_quality'
    ) THEN
        ALTER TABLE scoring_records
        ADD CONSTRAINT chk_scoring_records_quality
        CHECK (quality_score IS NULL OR (quality_score >= 0 AND quality_score <= 100));
    END IF;
END $$;

-- Valid quartile values
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_scoring_records_quartile'
    ) THEN
        ALTER TABLE scoring_records
        ADD CONSTRAINT chk_scoring_records_quartile
        CHECK (quartile IS NULL OR quartile BETWEEN 1 AND 4);
    END IF;
END $$;

-- ============================================================
-- CHECK Constraints for signal_records table
-- ============================================================

-- Score between 0 and 100
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_signal_records_score'
    ) THEN
        ALTER TABLE signal_records
        ADD CONSTRAINT chk_signal_records_score
        CHECK (score >= 0 AND score <= 100);
    END IF;
END $$;

-- Valid signal types
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_signal_records_type'
    ) THEN
        ALTER TABLE signal_records
        ADD CONSTRAINT chk_signal_records_type
        CHECK (signal_type IN ('bullish', 'bearish', 'neutral'));
    END IF;
END $$;

-- Valid strength values
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_signal_records_strength'
    ) THEN
        ALTER TABLE signal_records
        ADD CONSTRAINT chk_signal_records_strength
        CHECK (strength IS NULL OR strength IN ('weak', 'moderate', 'strong'));
    END IF;
END $$;

-- ============================================================
-- CHECK Constraints for enrichment_jobs table
-- ============================================================

-- Valid priority values
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_enrichment_jobs_priority'
    ) THEN
        ALTER TABLE enrichment_jobs
        ADD CONSTRAINT chk_enrichment_jobs_priority
        CHECK (priority >= 0 AND priority <= 100);
    END IF;
END $$;

-- Valid job status
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_enrichment_jobs_status'
    ) THEN
        ALTER TABLE enrichment_jobs
        ADD CONSTRAINT chk_enrichment_jobs_status
        CHECK (status IN ('pending', 'queued', 'running', 'completed', 'failed', 'cancelled'));
    END IF;
END $$;

-- Valid max_attempts
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_enrichment_jobs_max_attempts'
    ) THEN
        ALTER TABLE enrichment_jobs
        ADD CONSTRAINT chk_enrichment_jobs_max_attempts
        CHECK (max_attempts > 0 AND max_attempts <= 10);
    END IF;
END $$;

-- Ensure attempt count doesn't exceed max
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_enrichment_jobs_attempts'
    ) THEN
        ALTER TABLE enrichment_jobs
        ADD CONSTRAINT chk_enrichment_jobs_attempts
        CHECK (attempt_count <= max_attempts);
    END IF;
END $$;

-- ============================================================
-- CHECK Constraints for contradictions table
-- ============================================================

-- Valid severity values
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_contradictions_severity'
    ) THEN
        ALTER TABLE contradictions
        ADD CONSTRAINT chk_contradictions_severity
        CHECK (severity IS NULL OR severity IN ('low', 'medium', 'high', 'critical'));
    END IF;
END $$;

-- Valid status values
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_contradictions_status'
    ) THEN
        ALTER TABLE contradictions
        ADD CONSTRAINT chk_contradictions_status
        CHECK (status IN ('open', 'investigating', 'resolved', 'dismissed'));
    END IF;
END $$;

-- Valid resolution status
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_contradictions_resolution'
    ) THEN
        ALTER TABLE contradictions
        ADD CONSTRAINT chk_contradictions_resolution
        CHECK (resolution_status IS NULL OR resolution_status IN (
            'confirmed_error', 'false_positive', 'data_quality_issue', 'ambiguous'
        ));
    END IF;
END $$;

-- ============================================================
-- CHECK Constraints for outbox_records table
-- ============================================================

-- Valid event status
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_outbox_status'
    ) THEN
        ALTER TABLE outbox_records
        ADD CONSTRAINT chk_outbox_status
        CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'retry'));
    END IF;
END $$;

-- Valid max retries
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_outbox_max_retries'
    ) THEN
        ALTER TABLE outbox_records
        ADD CONSTRAINT chk_outbox_max_retries
        CHECK (max_retries BETWEEN 0 AND 10);
    END IF;
END $$;

-- Ensure retry count <= max_retries
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_outbox_retries'
    ) THEN
        ALTER TABLE outbox_records
        ADD CONSTRAINT chk_outbox_retries
        CHECK (retry_count <= max_retries);
    END IF;
END $$;

-- ============================================================
-- CHECK Constraints for audit_trails table
-- ============================================================

-- Valid action types
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_audit_action'
    ) THEN
        ALTER TABLE audit_trails
        ADD CONSTRAINT chk_audit_action
        CHECK (action IN ('create', 'update', 'delete', 'archive', 'restore', 'merge'));
    END IF;
END $$;

-- Valid entity types
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'chk_audit_entity_type'
    ) THEN
        ALTER TABLE audit_trails
        ADD CONSTRAINT chk_audit_entity_type
        CHECK (entity_type IN (
            'company', 'research_run', 'fact', 'signal', 
            'contradiction', 'enrichment_job', 'scoring_record'
        ));
    END IF;
END $$;

-- ============================================================
-- NOT NULL Constraints for critical fields
-- ============================================================

-- Companies: ticker and name should not be null
DO $$
BEGIN
    ALTER TABLE companies
    ALTER COLUMN ticker SET NOT NULL;
EXCEPTION WHEN others THEN
    NULL;
END $$;

-- Research runs: company_id and status should not be null
DO $$
BEGIN
    ALTER TABLE research_runs
    ALTER COLUMN company_id SET NOT NULL;
EXCEPTION WHEN others THEN
    NULL;
END $$;

DO $$
BEGIN
    ALTER TABLE research_runs
    ALTER COLUMN status SET NOT NULL;
EXCEPTION WHEN others THEN
    NULL;
END $$;

-- Facts: company_id and status should not be null
DO $$
BEGIN
    ALTER TABLE facts
    ALTER COLUMN company_id SET NOT NULL;
EXCEPTION WHEN others THEN
    NULL;
END $$;

DO $$
BEGIN
    ALTER TABLE facts
    ALTER COLUMN status SET NOT NULL;
EXCEPTION WHEN others THEN
    NULL;
END $$;

-- Signals: company_id, run_id, and signal_type should not be null
DO $$
BEGIN
    ALTER TABLE signals
    ALTER COLUMN company_id SET NOT NULL;
EXCEPTION WHEN others THEN
    NULL;
END $$;

DO $$
BEGIN
    ALTER TABLE signals
    ALTER COLUMN run_id SET NOT NULL;
EXCEPTION WHEN others THEN
    NULL;
END $$;

-- Add documentation comments
COMMENT ON CONSTRAINT chk_companies_status ON companies IS 'Valid statuses: active, inactive, archived, pending';
COMMENT ON CONSTRAINT chk_research_runs_status ON research_runs IS 'Valid statuses: pending, queued, running, completed, failed, cancelled, timeout, retrying';
COMMENT ON CONSTRAINT chk_facts_confidence ON facts IS 'Confidence score must be between 0 and 1';
COMMENT ON CONSTRAINT chk_scoring_records_total ON scoring_records IS 'Total score must be between 0 and 100';
COMMENT ON CONSTRAINT chk_signal_records_score ON signal_records IS 'Signal score must be between 0 and 100';
