# STORY-080: Add pgvector Extension and Company Embedding Schema

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P2 |
| Severity | HIGH |
| Epic | [EPIC-023: pgvector Semantic Search](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-063](../../EPIC-019-multi-tenancy-data-isolation/STORIES/STORY-063-tenant-model.md) (tenant model), [EPIC-019](../../EPIC-019-multi-tenancy-data-isolation/README.md) (RLS must apply to vector search) |

---

## The Audit Verdict

> No vector storage exists in the schema. `infrastructure/database_models.py` (768 lines) has no embedding column on the Company or FinancialData tables. The Supabase project does not have the pgvector extension enabled. Company intelligence data that would benefit from semantic search is stored as relational rows with no vector representation.

## Problem Statement

Without a vector column and the pgvector extension, semantic similarity search is impossible. This story establishes the schema foundation that STORY-081 and STORY-082 depend on. Every subsequent vector operation — embedding storage, nearest-neighbor queries, similarity ranking — requires the extension to be enabled and the column to exist.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Product** | No semantic search capability — users limited to exact-match and filter-based lookups |
| **Architecture** | Vector storage must be established before embeddings can be generated or searched |
| **Dependencies** | STORY-081 and STORY-082 are blocked until this schema exists |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| Supabase project configuration | Modify | Enable pgvector extension |
| `src/solstein/infrastructure/database_models.py` | Modify | Add embedding vector column to Company table |
| New Alembic migration file | Add | Migration to add vector column and pgvector index |

## Architectural Requirements

*What — never how. No code.*

- **REQ-1**: The pgvector extension must be enabled in the Supabase PostgreSQL instance
- **REQ-2**: The `Company` database table must have a `profile_embedding` column of type `vector(1536)` (or appropriate dimension for the chosen embedding model)
- **REQ-3**: An IVFFlat or HNSW index must be created on the embedding column for approximate nearest-neighbor search performance
- **REQ-4**: The embedding column must be nullable — companies without a completed research profile do not have embeddings yet
- **REQ-5**: The vector index must respect tenant_id — searches must not cross tenant boundaries (handled by RLS from EPIC-019, but the index must be designed to work with RLS efficiently)
- **REQ-6**: A database migration must add the column and index — no manual schema changes

## Acceptance Criteria

- [ ] `SELECT * FROM pg_extension WHERE extname = 'vector'` returns a row in Supabase
- [ ] `Company` table has a `profile_embedding` vector column
- [ ] A vector index exists on the embedding column
- [ ] Migration runs successfully on a clean database

## Definition of Done

**Tests Required:**
- [ ] Migration test: `alembic upgrade head` succeeds on a clean database
- [ ] Schema test: embedding column exists with correct type and nullability
- [ ] Index test: `EXPLAIN` on a vector similarity query shows index scan

**Documentation Required:**
- [ ] Embedding model choice and dimension rationale documented
- [ ] Migration rollback procedure documented

**Code Review Gate:**
- [ ] Migration reviewed for backward compatibility — existing data must not be affected
- [ ] Index type choice (IVFFlat vs HNSW) justified for expected data volume

## Notes

- Supabase includes pgvector natively — no infrastructure changes needed beyond enabling the extension via the Supabase dashboard or SQL.
- The vector dimension (1536) assumes OpenAI `text-embedding-3-small` or similar. If the team selects a different embedding model, the dimension must be adjusted before this migration runs.
- HNSW indexes are preferred for datasets under 1M rows. IVFFlat may be more appropriate at larger scale but requires periodic reindexing.
