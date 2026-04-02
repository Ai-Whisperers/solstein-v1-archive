# STORY-081: Generate and Store Company Embeddings During the Research Pipeline

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P2 |
| Severity | HIGH |
| Epic | [EPIC-023: pgvector Semantic Search](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-080](STORY-080-pgvector-schema.md), [STORY-073](../../EPIC-021-modern-llm-stack/STORIES/STORY-073-langfuse-integration.md) (Langfuse/Anthropic SDK for embedding calls) |

---

## The Audit Verdict

> No embedding generation exists anywhere in the research pipeline (`research/pipeline.py`, `research/aggregate.py`, `research/gather.py`). Company profiles are enriched and stored as relational data but never converted to vector representations. The intelligence accumulated during enrichment is not queryable by semantic similarity.

## Problem Statement

Embeddings must be generated at research pipeline completion, when the richest, most complete company profile is available. Generating them as a post-hoc batch process is more expensive and produces lower-quality embeddings than generating them at the moment of maximum data completeness. The pipeline already does the hard work of aggregating company intelligence — the last step of converting that intelligence to a vector representation is missing.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Product** | Enriched company data exists but cannot be searched semantically — the most valuable query pattern is unavailable |
| **Data Quality** | Embedding at pipeline completion captures the most complete profile; batch-after-the-fact produces stale or partial representations |
| **Cost** | Embedding at enrichment time adds marginal cost per job; a separate batch process doubles the infrastructure and operational burden |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/research/pipeline.py` | Modify | Add embedding generation as a final pipeline stage |
| `src/solstein/infrastructure/company_repository.py` | Modify | Add embedding upsert method |
| `src/solstein/llm/embeddings.py` | Add | Embedding generation utility using the Anthropic SDK or a dedicated embedding model |

## Architectural Requirements

*What — never how. No code.*

- **REQ-1**: Company profile embeddings must be generated at the end of the research pipeline, after all enrichment data has been aggregated
- **REQ-2**: The embedding must represent the full company profile — not just the company name. It must include: company description, sector, key financial signals, technology indicators, competitive positioning summary
- **REQ-3**: Embedding generation must be tracked in Langfuse (from STORY-073) — token usage and cost recorded per embedding call
- **REQ-4**: If the embedding model is unavailable, the research pipeline must complete successfully without an embedding — the embedding column remains null rather than failing the entire job
- **REQ-5**: Existing companies without embeddings must be batch-embeddable via a one-time migration script — not just future companies
- **REQ-6**: Embedding model and dimensions must be configurable — not hardcoded

## Acceptance Criteria

- [ ] After a research job completes, the company record has a non-null embedding
- [ ] Embedding generation failure does not fail the research job
- [ ] A batch script can generate embeddings for all companies without embeddings
- [ ] Embedding calls appear in Langfuse with token counts

## Definition of Done

**Tests Required:**
- [ ] Integration test: complete research job → company has embedding
- [ ] Resilience test: embedding model unavailable → research job succeeds, embedding is null
- [ ] Batch test: migration script generates embeddings for existing companies

**Documentation Required:**
- [ ] Embedding model selection rationale documented
- [ ] Profile-to-text serialization format documented (what fields are included in the embedding input)
- [ ] Batch migration script usage documented in runbook

**Code Review Gate:**
- [ ] Graceful degradation verified — embedding failure must never cascade to pipeline failure
- [ ] Langfuse integration verified — no untracked embedding calls
- [ ] Configuration reviewed — no hardcoded model names or dimensions

## Notes

- The profile-to-text serialization step is critical. A naive concatenation of fields produces poor embeddings. The text representation should read like a company brief — the kind of paragraph a human would write to describe the company to a colleague.
- Batch backfill for existing companies may be rate-limited by the embedding model provider. The migration script should support configurable batch sizes and rate limiting.
- Consider caching embeddings — if the company profile hasn't changed since the last embedding, regeneration is wasted cost.

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This story currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently list this story as active work, treat it as triage-required rather than immediately actionable.

### Next Agent Action

- Reconcile this story against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before starting.
- Do not begin implementation from this file alone unless the queue or a fresh planning decision reactivates it.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Preserve machine-checkable enforcement and avoid prose-only or speculative "AI slop" updates.

### Minimum Verification For Future Agents

- If this story is reactivated, update the queue or controlling planning artifact first.
- Then prove the work with the smallest relevant regression tests, gates, or generated artifacts for the touched boundary.
