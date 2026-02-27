-- Migration 011: Add Foreign Key Constraints
-- Adds referential integrity constraints to ensure data consistency
-- All constraints use ON DELETE CASCADE for dependent data

-- ============================================================
-- Foreign Key: research_runs.company_id -> companies.id
-- ============================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_research_runs_company'
    ) THEN
        ALTER TABLE research_runs
        ADD CONSTRAINT fk_research_runs_company
        FOREIGN KEY (company_id) REFERENCES companies(id)
        ON DELETE CASCADE;
    END IF;
END $$;

-- ============================================================
-- Foreign Key: facts.company_id -> companies.id
-- ============================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_facts_company'
    ) THEN
        ALTER TABLE facts
        ADD CONSTRAINT fk_facts_company
        FOREIGN KEY (company_id) REFERENCES companies(id)
        ON DELETE CASCADE;
    END IF;
END $$;

-- ============================================================
-- Foreign Key: facts.run_id -> research_runs.id
-- ============================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_facts_run'
    ) THEN
        ALTER TABLE facts
        ADD CONSTRAINT fk_facts_run
        FOREIGN KEY (run_id) REFERENCES research_runs(id)
        ON DELETE CASCADE;
    END IF;
END $$;

-- ============================================================
-- Foreign Key: signals.company_id -> companies.id
-- ============================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_signals_company'
    ) THEN
        ALTER TABLE signals
        ADD CONSTRAINT fk_signals_company
        FOREIGN KEY (company_id) REFERENCES companies(id)
        ON DELETE CASCADE;
    END IF;
END $$;

-- ============================================================
-- Foreign Key: signals.run_id -> research_runs.id
-- ============================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_signals_run'
    ) THEN
        ALTER TABLE signals
        ADD CONSTRAINT fk_signals_run
        FOREIGN KEY (run_id) REFERENCES research_runs(id)
        ON DELETE CASCADE;
    END IF;
END $$;

-- ============================================================
-- Foreign Key: source_document_snapshots.run_id -> research_runs.id
-- ============================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_snapshots_run'
    ) THEN
        ALTER TABLE source_document_snapshots
        ADD CONSTRAINT fk_snapshots_run
        FOREIGN KEY (run_id) REFERENCES research_runs(id)
        ON DELETE CASCADE;
    END IF;
END $$;

-- ============================================================
-- Foreign Key: outbox_records.run_id -> research_runs.id
-- ============================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_outbox_run'
    ) THEN
        ALTER TABLE outbox_records
        ADD CONSTRAINT fk_outbox_run
        FOREIGN KEY (run_id) REFERENCES research_runs(id)
        ON DELETE CASCADE;
    END IF;
END $$;

-- ============================================================
-- Foreign Key: contradictions.company_id -> companies.id
-- ============================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_contradictions_company'
    ) THEN
        ALTER TABLE contradictions
        ADD CONSTRAINT fk_contradictions_company
        FOREIGN KEY (company_id) REFERENCES companies(id)
        ON DELETE CASCADE;
    END IF;
END $$;

-- ============================================================
-- Foreign Key: contradictions.run_id -> research_runs.id
-- ============================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_contradictions_run'
    ) THEN
        ALTER TABLE contradictions
        ADD CONSTRAINT fk_contradictions_run
        FOREIGN KEY (run_id) REFERENCES research_runs(id)
        ON DELETE CASCADE;
    END IF;
END $$;

-- ============================================================
-- Foreign Key: scoring_records.company_id -> companies.id
-- ============================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_scoring_records_company'
    ) THEN
        ALTER TABLE scoring_records
        ADD CONSTRAINT fk_scoring_records_company
        FOREIGN KEY (company_id) REFERENCES companies(id)
        ON DELETE CASCADE;
    END IF;
END $$;

-- ============================================================
-- Foreign Key: signal_records.company_id -> companies.id
-- ============================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_signal_records_company'
    ) THEN
        ALTER TABLE signal_records
        ADD CONSTRAINT fk_signal_records_company
        FOREIGN KEY (company_id) REFERENCES companies(id)
        ON DELETE CASCADE;
    END IF;
END $$;

-- ============================================================
-- Foreign Key: enrichment_jobs.company_id -> companies.id
-- ============================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_enrichment_jobs_company'
    ) THEN
        ALTER TABLE enrichment_jobs
        ADD CONSTRAINT fk_enrichment_jobs_company
        FOREIGN KEY (company_id) REFERENCES companies(id)
        ON DELETE CASCADE;
    END IF;
END $$;

-- ============================================================
-- Foreign Key: audit_trails.company_id -> companies.id
-- ============================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_audit_trails_company'
    ) THEN
        ALTER TABLE audit_trails
        ADD CONSTRAINT fk_audit_trails_company
        FOREIGN KEY (company_id) REFERENCES companies(id)
        ON DELETE CASCADE;
    END IF;
END $$;

-- ============================================================
-- Foreign Key: audit_trails.run_id -> research_runs.id
-- ============================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_audit_trails_run'
    ) THEN
        ALTER TABLE audit_trails
        ADD CONSTRAINT fk_audit_trails_run
        FOREIGN KEY (run_id) REFERENCES research_runs(id)
        ON DELETE CASCADE;
    END IF;
END $$;

-- ============================================================
-- Foreign Key: market_snapshots.company_id -> companies.id (SET NULL)
-- Market snapshots can exist independently as historical records
-- ============================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_market_snapshots_company'
    ) THEN
        ALTER TABLE market_snapshots
        ADD CONSTRAINT fk_market_snapshots_company
        FOREIGN KEY (company_id) REFERENCES companies(id)
        ON DELETE SET NULL;
    END IF;
END $$;

-- ============================================================
-- Foreign Key: company_enrichment_queue.company_id -> companies.id
-- ============================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_enrichment_queue_company'
    ) THEN
        ALTER TABLE company_enrichment_queue
        ADD CONSTRAINT fk_enrichment_queue_company
        FOREIGN KEY (company_id) REFERENCES companies(id)
        ON DELETE CASCADE;
    END IF;
END $$;

-- ============================================================
-- Foreign Key: enrichment_results.company_id -> companies.id
-- ============================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_enrichment_results_company'
    ) THEN
        ALTER TABLE enrichment_results
        ADD CONSTRAINT fk_enrichment_results_company
        FOREIGN KEY (company_id) REFERENCES companies(id)
        ON DELETE CASCADE;
    END IF;
END $$;

-- ============================================================
-- Foreign Key: enrichment_cache.company_id -> companies.id
-- ============================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_enrichment_cache_company'
    ) THEN
        ALTER TABLE enrichment_cache
        ADD CONSTRAINT fk_enrichment_cache_company
        FOREIGN KEY (company_id) REFERENCES companies(id)
        ON DELETE CASCADE;
    END IF;
END $$;

-- ============================================================
-- Foreign Key: enrichment_audit.company_id -> companies.id
-- ============================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_enrichment_audit_company'
    ) THEN
        ALTER TABLE enrichment_audit
        ADD CONSTRAINT fk_enrichment_audit_company
        FOREIGN KEY (company_id) REFERENCES companies(id)
        ON DELETE CASCADE;
    END IF;
END $$;

-- Add comment documenting the foreign key relationships
COMMENT ON TABLE research_runs IS 'Research execution runs linked to companies via fk_research_runs_company';
COMMENT ON TABLE facts IS 'Extracted facts linked to companies and research runs';
COMMENT ON TABLE signals IS 'Detected signals linked to companies and research runs';
COMMENT ON TABLE contradictions IS 'Fact contradictions linked to companies and research runs';
