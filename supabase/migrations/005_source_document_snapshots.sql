ALTER TABLE public.source_documents
    ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'observed',
    ADD COLUMN fetched_at TIMESTAMPTZ,
    ADD COLUMN content_hash VARCHAR(128),
    ADD COLUMN extract_hash VARCHAR(128);

UPDATE public.source_documents
SET fetched_at = observed_at
WHERE fetched_at IS NULL;
