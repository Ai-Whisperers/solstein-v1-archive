-- Migration 013: Add Optimized Indexes for Performance
-- Adds composite and partial indexes for frequently queried patterns

-- ============================================================
-- Companies table indexes
-- ============================================================

-- Composite index for company lookups by status and ticker
CREATE INDEX IF NOT EXISTS idx_companies_status_ticker 
ON companies(status, ticker);

-- Index for sector queries
CREATE INDEX IF NOT EXISTS idx_companies_sector 
ON companies(sector) 
WHERE sector IS NOT NULL;

-- Partial index for active companies only (most common query)
CREATE INDEX IF NOT EXISTS idx_companies_active 
ON companies(ticker, name) 
WHERE status = 'active';

-- ============================================================
-- Research Runs table indexes
-- ============================================================

-- Composite index for runs by company and status
CREATE INDEX IF NOT EXISTS idx_research_runs_company_status 
ON research_runs(company_id, status);

-- Composite index for runs by status and created date
CREATE INDEX IF NOT EXISTS idx_research_runs_status_created 
ON research_runs(status, created_at DESC);

-- Partial index for non-terminal runs (for queue processing)
CREATE INDEX IF NOT EXISTS idx_research_runs_active 
ON research_runs(company_id, created_at DESC) 
WHERE status IN ('pending', 'queued', 'running', 'retrying');

-- Index for completed runs with temporal ID
CREATE INDEX IF NOT EXISTS idx_research_runs_completed_temporal 
ON research_runs(temporal_run_id) 
WHERE temporal_run_id IS NOT NULL;

-- ============================================================
-- Facts table indexes
-- ============================================================

-- Composite index for facts by company and status
CREATE INDEX IF NOT EXISTS idx_facts_company_status 
ON facts(company_id, status);

-- Composite index for facts by run and status
CREATE INDEX IF NOT EXISTS idx_facts_run_status 
ON facts(run_id, status);

-- Partial index for active facts only
CREATE INDEX IF NOT EXISTS idx_facts_active 
ON facts(company_id, created_at DESC) 
WHERE status = 'active';

-- Index for facts with high confidence
CREATE INDEX IF NOT EXISTS idx_facts_high_confidence 
ON facts(company_id, confidence DESC) 
WHERE status = 'active' AND confidence >= 0.8;

-- Index for fact key lookups
CREATE INDEX IF NOT EXISTS idx_facts_key 
ON facts(fact_key) 
WHERE fact_key IS NOT NULL;

-- ============================================================
-- Signals table indexes
-- ============================================================

-- Composite index for signals by company and type
CREATE INDEX IF NOT EXISTS idx_signals_company_type 
ON signals(company_id, signal_type);

-- Composite index for signals by status and date
CREATE INDEX IF NOT EXISTS idx_signals_status_date 
ON signals(status, detected_at DESC);

-- Partial index for active signals
CREATE INDEX IF NOT EXISTS idx_signals_active 
ON signals(company_id, signal_type, strength DESC) 
WHERE status = 'active';

-- Index for high-confidence signals
CREATE INDEX IF NOT EXISTS idx_signals_high_confidence 
ON signals(company_id, detected_at DESC) 
WHERE status = 'active' AND confidence >= 0.7;

-- ============================================================
-- Scoring Records table indexes
-- ============================================================

-- Composite index for scores by company and date
CREATE INDEX IF NOT EXISTS idx_scoring_records_company_date 
ON scoring_records(company_id, scored_at DESC);

-- Index for top scores
CREATE INDEX IF NOT EXISTS idx_scoring_records_top_scores 
ON scoring_records(total_score DESC, quartile) 
WHERE total_score >= 70;

-- Index for recent scores
CREATE INDEX IF NOT EXISTS idx_scoring_records_recent 
ON scoring_records(company_id, scored_at DESC) 
WHERE scored_at > now() - interval '30 days';

-- ============================================================
-- Signal Records table indexes
-- ============================================================

-- Composite index for signal records
CREATE INDEX IF NOT EXISTS idx_signal_records_company_score 
ON signal_records(company_id, score DESC);

-- Index for recent signals
CREATE INDEX IF NOT EXISTS idx_signal_records_recent 
ON signal_records(company_id, generated_at DESC) 
WHERE generated_at > now() - interval '7 days';

-- ============================================================
-- Enrichment Jobs table indexes
-- ============================================================

-- Composite index for job queue processing
CREATE INDEX IF NOT EXISTS idx_enrichment_jobs_queue 
ON enrichment_jobs(status, priority DESC, created_at ASC);

-- Partial index for pending jobs
CREATE INDEX IF NOT EXISTS idx_enrichment_jobs_pending 
ON enrichment_jobs(priority DESC, created_at ASC) 
WHERE status IN ('pending', 'queued');

-- Index for jobs by company
CREATE INDEX IF NOT EXISTS idx_enrichment_jobs_company 
ON enrichment_jobs(company_id, status);

-- ============================================================
-- Contradictions table indexes
-- ============================================================

-- Composite index for contradictions
CREATE INDEX IF NOT EXISTS idx_contradictions_company_status 
ON contradictions(company_id, status);

-- Partial index for open contradictions
CREATE INDEX IF NOT EXISTS idx_contradictions_open 
ON contradictions(company_id, severity, created_at DESC) 
WHERE status IN ('open', 'investigating');

-- Index for high severity contradictions
CREATE INDEX IF NOT EXISTS idx_contradictions_high_severity 
ON contradictions(company_id, created_at DESC) 
WHERE severity IN ('high', 'critical');

-- ============================================================
-- Outbox Records table indexes
-- ============================================================

-- Composite index for outbox processing
CREATE INDEX IF NOT EXISTS idx_outbox_status_retry 
ON outbox_records(status, retry_count, created_at ASC);

-- Partial index for pending outbox items
CREATE INDEX IF NOT EXISTS idx_outbox_pending 
ON outbox_records(created_at ASC) 
WHERE status IN ('pending', 'retry');

-- Index for failed items
CREATE INDEX IF NOT EXISTS idx_outbox_failed 
ON outbox_records(created_at DESC) 
WHERE status = 'failed';

-- ============================================================
-- Audit Trails table indexes
-- ============================================================

-- Composite index for audit queries
CREATE INDEX IF NOT EXISTS idx_audit_entity_action 
ON audit_trails(entity_type, entity_id, created_at DESC);

-- Index for company audit history
CREATE INDEX IF NOT EXISTS idx_audit_company 
ON audit_trails(company_id, created_at DESC) 
WHERE company_id IS NOT NULL;

-- Index for recent audits
CREATE INDEX IF NOT EXISTS idx_audit_recent 
ON audit_trails(created_at DESC) 
WHERE created_at > now() - interval '7 days';

-- ============================================================
-- Market Snapshots table indexes
-- ============================================================

-- Composite index for snapshots by company and date
CREATE INDEX IF NOT EXISTS idx_market_snapshots_company_date 
ON market_snapshots(company_id, recorded_at DESC);

-- Index for recent market data
CREATE INDEX IF NOT EXISTS idx_market_snapshots_recent 
ON market_snapshots(recorded_at DESC) 
WHERE recorded_at > now() - interval '1 day';

-- ============================================================
-- Enrichment tables indexes
-- ============================================================

-- Company Enrichment Queue
CREATE INDEX IF NOT EXISTS idx_enrichment_queue_company_status 
ON company_enrichment_queue(company_id, status);

CREATE INDEX IF NOT EXISTS idx_enrichment_queue_pending 
ON company_enrichment_queue(priority DESC, created_at ASC) 
WHERE status = 'pending';

-- Enrichment Results
CREATE INDEX IF NOT EXISTS idx_enrichment_results_company 
ON enrichment_results(company_id, enrichment_type, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_enrichment_results_success 
ON enrichment_results(company_id, enrichment_type) 
WHERE status = 'success';

-- Enrichment Cache
CREATE INDEX IF NOT EXISTS idx_enrichment_cache_lookup 
ON enrichment_cache(company_id, data_source, cache_key);

CREATE INDEX IF NOT EXISTS idx_enrichment_cache_ttl 
ON enrichment_cache(expires_at) 
WHERE expires_at > now();

-- Enrichment Audit
CREATE INDEX IF NOT EXISTS idx_enrichment_audit_company 
ON enrichment_audit(company_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_enrichment_audit_source 
ON enrichment_audit(data_source, status, created_at DESC);

-- ============================================================
-- Source Document Snapshots indexes
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_snapshots_run 
ON source_document_snapshots(run_id, document_type);

CREATE INDEX IF NOT EXISTS idx_snapshots_url 
ON source_document_snapshots(source_url) 
WHERE source_url IS NOT NULL;

-- ============================================================
-- Add comments for documentation
-- ============================================================

COMMENT ON INDEX idx_companies_active IS 'Partial index for active companies - optimizes most common lookup';
COMMENT ON INDEX idx_research_runs_active IS 'Partial index for non-terminal run statuses - optimizes queue processing';
COMMENT ON INDEX idx_facts_active IS 'Partial index for active facts only - optimizes fact queries';
COMMENT ON INDEX idx_signals_active IS 'Partial index for active signals - optimizes signal monitoring';
COMMENT ON INDEX idx_contradictions_open IS 'Partial index for open contradictions - optimizes issue tracking';
COMMENT ON INDEX idx_enrichment_jobs_pending IS 'Partial index for pending enrichment jobs - optimizes queue processing';
COMMENT ON INDEX idx_outbox_pending IS 'Partial index for pending outbox items - optimizes event processing';
