ALTER TABLE public.research_contradictions
    ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'open',
    ADD COLUMN updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ADD COLUMN resolved_at TIMESTAMPTZ,
    ADD COLUMN ignored_at TIMESTAMPTZ;

ALTER TABLE public.research_contradictions
    ADD CONSTRAINT ck_contradiction_status
    CHECK (status IN ('open', 'resolved', 'ignored'));

UPDATE public.research_contradictions
SET updated_at = created_at
WHERE updated_at IS NULL;

CREATE TABLE public.research_contradiction_transitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contradiction_id UUID NOT NULL REFERENCES public.research_contradictions(id) ON DELETE CASCADE,
    from_status VARCHAR(50) NOT NULL,
    to_status VARCHAR(50) NOT NULL,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    changed_by VARCHAR(255),
    reason TEXT
);

CREATE INDEX ix_contradiction_transitions_contradiction
    ON public.research_contradiction_transitions (contradiction_id);

ALTER TABLE public.research_contradiction_transitions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow basic anon read" ON public.research_contradiction_transitions
    FOR SELECT TO anon USING (true);
