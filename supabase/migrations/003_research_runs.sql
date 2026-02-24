CREATE TABLE public.research_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id VARCHAR(255) NOT NULL UNIQUE,
    market VARCHAR(255) NOT NULL,
    seed_company VARCHAR(500) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'completed',
    strict_provenance BOOLEAN NOT NULL DEFAULT TRUE,
    min_readiness_score NUMERIC,
    max_contradictions INTEGER,
    min_total_sources INTEGER,
    summary JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE public.research_stages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES public.research_runs(id) ON DELETE CASCADE,
    stage_name VARCHAR(100) NOT NULL,
    stage_order INTEGER NOT NULL,
    status VARCHAR(50),
    metrics JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_research_stage_run_name UNIQUE (run_id, stage_name)
);

CREATE INDEX ix_research_stage_run_order ON public.research_stages (run_id, stage_order);

CREATE TABLE public.research_artifacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES public.research_runs(id) ON DELETE CASCADE,
    artifact_name VARCHAR(255) NOT NULL,
    artifact_path VARCHAR(1000),
    payload JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_research_artifact_run_name UNIQUE (run_id, artifact_name)
);

CREATE TABLE public.source_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES public.research_runs(id) ON DELETE CASCADE,
    company_id VARCHAR(255) NOT NULL,
    source_url VARCHAR(2000) NOT NULL,
    source_domain VARCHAR(255),
    source_type VARCHAR(100),
    observed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_source_document_run_company_url UNIQUE (run_id, company_id, source_url)
);

CREATE INDEX ix_source_documents_company_id ON public.source_documents (company_id);
CREATE INDEX ix_source_documents_source_domain ON public.source_documents (source_domain);

CREATE TABLE public.metric_observations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES public.research_runs(id) ON DELETE CASCADE,
    company_id VARCHAR(255) NOT NULL,
    metric_key VARCHAR(100) NOT NULL,
    metric_value NUMERIC,
    metric_value_raw JSONB,
    source_url VARCHAR(2000),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_metric_observation_run_company_metric_source_value UNIQUE (
        run_id,
        company_id,
        metric_key,
        source_url,
        metric_value
    )
);

CREATE INDEX ix_metric_observation_company_metric ON public.metric_observations (company_id, metric_key);

CREATE TABLE public.evidence_readiness (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES public.research_runs(id) ON DELETE CASCADE,
    company_id VARCHAR(255) NOT NULL,
    company_name VARCHAR(500) NOT NULL,
    readiness_score NUMERIC NOT NULL,
    readiness_level VARCHAR(100) NOT NULL,
    source_count INTEGER NOT NULL DEFAULT 0,
    source_domain_count INTEGER NOT NULL DEFAULT 0,
    metric_source_coverage NUMERIC NOT NULL DEFAULT 0,
    metric_explainability NUMERIC NOT NULL DEFAULT 0,
    unsupported_metrics INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_evidence_readiness_run_company UNIQUE (run_id, company_id)
);

CREATE INDEX ix_evidence_readiness_level ON public.evidence_readiness (readiness_level);

CREATE TABLE public.research_contradictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES public.research_runs(id) ON DELETE CASCADE,
    company_id VARCHAR(255) NOT NULL,
    metric_key VARCHAR(100) NOT NULL,
    contradiction_type VARCHAR(100) NOT NULL,
    details JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_contradiction_run_company_metric_type UNIQUE (
        run_id,
        company_id,
        metric_key,
        contradiction_type
    )
);

ALTER TABLE public.research_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.research_stages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.research_artifacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.source_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.metric_observations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.evidence_readiness ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.research_contradictions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow basic anon read" ON public.research_runs FOR SELECT TO anon USING (true);
CREATE POLICY "Allow basic anon read" ON public.research_stages FOR SELECT TO anon USING (true);
CREATE POLICY "Allow basic anon read" ON public.research_artifacts FOR SELECT TO anon USING (true);
CREATE POLICY "Allow basic anon read" ON public.source_documents FOR SELECT TO anon USING (true);
CREATE POLICY "Allow basic anon read" ON public.metric_observations FOR SELECT TO anon USING (true);
CREATE POLICY "Allow basic anon read" ON public.evidence_readiness FOR SELECT TO anon USING (true);
CREATE POLICY "Allow basic anon read" ON public.research_contradictions FOR SELECT TO anon USING (true);
