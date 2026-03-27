# STORY-082: Implement Semantic Similarity Search API Endpoint

| Field | Value |
|-------|-------|
| Status | 🔴 Open |
| Priority | P2 |
| Severity | HIGH |
| Epic | [EPIC-023: pgvector Semantic Search](../README.md) |
| Created | 2026-02-28 |
| Dependencies | [STORY-080](STORY-080-pgvector-schema.md), [STORY-081](STORY-081-embed-during-research.md), [STORY-038](../../EPIC-010-api-layer-hardening/STORIES/STORY-038-add-typed-response-models.md) (typed response models) |

---

## The Audit Verdict

> No semantic search endpoint exists. The current search in `api/routers/companies.py` is entirely filter-based. There is no endpoint to query "companies similar to X" or to find companies in the database that resemble an external company description. This is a core missing product capability for a PE/VC intelligence platform.

## Problem Statement

Filter-based search finds companies that match exact criteria. Semantic search finds companies that are meaningfully similar to a reference — a qualitatively different and more valuable capability for PE/VC deal sourcing and competitive mapping. A fund evaluating an acquisition target needs to know what else in their research database resembles it. A portfolio manager needs to identify competitive overlap between holdings. These are semantic questions that filter-based search cannot answer.

## Impact

| Dimension | Effect |
|-----------|--------|
| **Product** | Deal sourcing is limited to engineers who know which filters to apply — non-technical users cannot express "find me something like this" |
| **Competitive** | Semantic similarity search is table stakes for modern intelligence platforms — its absence is a product gap |
| **Revenue** | The ability to discover hidden connections between companies is a premium feature PE/VC firms will pay for |

## Affected Files

| File | Change Type | Specific Concern |
|------|-------------|-----------------|
| `src/solstein/api/routers/companies.py` | Modify | Add semantic search endpoint |
| `src/solstein/api/schemas/` | Add | Semantic search request and response models |
| `src/solstein/application/services/` | Add | Semantic search service method |
| `src/solstein/infrastructure/company_repository.py` | Modify | Add vector similarity query method |

## Architectural Requirements

*What — never how. No code.*

- **REQ-1**: A `POST /api/v1/companies/search/semantic` endpoint must accept: a query text OR a reference `company_id`, and an optional `limit` parameter
- **REQ-2**: When given a text query, the endpoint must embed the query and return companies ranked by vector distance
- **REQ-3**: When given a reference `company_id`, the endpoint must use that company's stored embedding as the query vector
- **REQ-4**: Results must be scoped to the authenticated tenant's data (RLS from EPIC-019 must apply to vector queries)
- **REQ-5**: The response must include: company details, similarity score, and whether the company has a complete embedding
- **REQ-6**: Companies without embeddings must be excluded from semantic search results (not returned with null similarity)
- **REQ-7**: The endpoint must be paginated (consistent with [STORY-037](../../EPIC-010-api-layer-hardening/STORIES/STORY-037-add-pagination.md))

## Acceptance Criteria

- [ ] `POST /api/v1/companies/search/semantic` with a text query returns ranked results
- [ ] `POST /api/v1/companies/search/semantic` with a `company_id` returns similar companies
- [ ] Results are scoped to the authenticated tenant
- [ ] Results include similarity scores
- [ ] Companies without embeddings are excluded from results

## Definition of Done

**Tests Required:**
- [ ] Integration test: text query returns companies ordered by similarity
- [ ] Integration test: company_id reference returns similar companies ordered by similarity
- [ ] Tenant isolation test: Tenant A's query does not return Tenant B's companies
- [ ] Pagination test: results can be paged with consistent ordering
- [ ] Edge case test: query against database with no embeddings returns empty result set

**Documentation Required:**
- [ ] API endpoint documented in OpenAPI schema
- [ ] Similarity score interpretation guide (what does 0.85 mean vs 0.95)
- [ ] Request/response examples in API documentation

**Code Review Gate:**
- [ ] Tenant isolation verified — RLS applies to vector queries
- [ ] Response models follow typed response conventions from STORY-038
- [ ] Pagination follows conventions from STORY-037

## Notes

- The similarity score should be normalized to a 0–1 range regardless of the underlying distance metric (cosine, L2, inner product). Users should not need to understand vector mathematics to interpret results.
- Consider supporting a minimum similarity threshold parameter — "only return companies above 0.7 similarity" — to reduce noise in results.
- The text query path requires an embedding model call per request. This adds latency and cost. Consider caching frequently repeated queries.
- The company_id path is cheaper — it reuses the stored embedding. Prefer this path in the UI when the user selects a company and asks "show me similar."
