# EPIC-023: pgvector Semantic Company Search

| Field | Value |
|-------|-------|
| Priority | **P2** |
| Status | 🔴 Open |
| Stories | 3 |
| Created | 2026-02-28 |
| Depends On | [EPIC-019](../EPIC-019-multi-tenancy-data-isolation/README.md), [EPIC-021](../EPIC-021-modern-llm-stack/README.md) |

## Context

PE/VC firms do not look up companies by exact name. They ask questions: "Find companies similar to Stripe at Series A," "Which portfolio companies are operating in the same space as this acquisition target," "What companies in our database have a risk profile similar to this one."

The current Solstein search is filter-based. You can query by sector, revenue range, or employee count. You cannot query by semantic similarity. A firm with 500 companies in their research database has no way to ask "what else do we know about that looks like this."

The fix costs almost nothing. Supabase includes pgvector natively — the vector extension is available in every Supabase project. The research pipeline already generates rich company profiles (enriched data, scored attributes, LLM-generated summaries). Embedding these profiles during enrichment and storing them alongside the company record enables semantic search with zero new infrastructure.

## Scope

| Story | Title | Severity |
|-------|-------|----------|
| [STORY-080](STORIES/STORY-080-pgvector-schema.md) | Add pgvector Extension and Company Embedding Schema | HIGH |
| [STORY-081](STORIES/STORY-081-embed-during-research.md) | Generate and Store Company Embeddings During Research Pipeline | HIGH |
| [STORY-082](STORIES/STORY-082-semantic-search-endpoint.md) | Implement Semantic Similarity Search API Endpoint | HIGH |

## Definition of Done

- [ ] pgvector extension is enabled in the Supabase project
- [ ] Company embeddings are generated and stored during the research pipeline
- [ ] A semantic similarity search endpoint returns companies ranked by vector distance
- [ ] Semantic search results are tenant-scoped (RLS applies to vector search)

## Autonomous Continuation Notes

### Current Develop Status

- Consult `docs/audit/DEVELOP_BACKLOG_AUTONOMY_AUDIT_2026-03-30.md` first.
- This epic currently carries a historical open or in-progress backlog badge.
- If `planning/QUEUE.md` does not currently schedule this epic, treat it as triage-required backlog inventory instead of self-startable work.

### Develop-Relevant Evidence

- `tests/test_pgvector_schema.py` already provides real schema-validation coverage for pgvector-related model behavior.
- Future semantic-search work should preserve the same typed boundary discipline used elsewhere in `develop` rather than treating embeddings/search payloads as free-form blobs.

### Next Agent Action

- Reconcile this epic against current code reality, `planning/QUEUE.md`, and the develop autonomy audit before selecting a story.
- Do not start implementation from this README alone unless the queue or a fresh planning decision activates the epic.

### Required Working Style

- Follow `docs/reference/ENGINEERING_GUARDRAILS.md`, `docs/reference/PIPELINE_QUALITY_ENFORCEMENT_PLAN.md`, and `docs/reference/TYPESCRIPT_ISSUE_MAPPING_2026-03-26.md`.
- Prefer narrow, machine-checkable progress over broad narrative backlog churn.

### Minimum Verification For Future Agents

- If this epic is reactivated, update the queue or controlling planning artifact first.
- Then execute one story at a time with the relevant tests, gates, and generated references for the touched surface.
