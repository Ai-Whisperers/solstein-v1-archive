CREATE TABLE public.outbox_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_key VARCHAR(255) NOT NULL UNIQUE,
    event_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    payload JSONB NOT NULL,
    attempt_count INTEGER NOT NULL DEFAULT 0,
    available_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_error JSONB,
    CONSTRAINT ck_outbox_status CHECK (status IN ('pending', 'in_progress', 'succeeded', 'failed'))
);

CREATE INDEX ix_outbox_event_type ON public.outbox_records (event_type);
CREATE INDEX ix_outbox_status ON public.outbox_records (status);
CREATE INDEX ix_outbox_available_at ON public.outbox_records (available_at);
CREATE INDEX ix_outbox_status_available_at ON public.outbox_records (status, available_at);

ALTER TABLE public.outbox_records ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow basic anon read" ON public.outbox_records FOR SELECT TO anon USING (true);
