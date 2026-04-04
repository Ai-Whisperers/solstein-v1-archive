# EPIC-050: Web Acquisition Pipeline (Map -> Crawl -> Schema Extract)

| Field | Value |
|-------|-------|
| **Status** | 🔴 Not Started |
| **Priority** | P1 – High |
| **Created** | 2026-03-10 |
| **Stories** | [STORY-190](STORIES/STORY-190.md), [STORY-191](STORIES/STORY-191.md), [STORY-192](STORIES/STORY-192.md), [STORY-193](STORIES/STORY-193.md) |
| **Dependencies** | EPIC-028 (External Service Consolidation), EPIC-035 (Async-First External Adapters) |

## Context

Current enrichment is too dependent on narrow sources and brittle single-step fetch patterns. We already have enrichment orchestration, conflict resolution, cache, and provenance primitives in place. The missing layer is a production-grade web acquisition pipeline that can discover relevant URLs, crawl at scale, and extract schema-validated structured data for downstream scoring.

This epic introduces a staged acquisition design:

1. **Map** a target domain to discover relevant pages.
2. **Crawl** selected pages asynchronously with retries and rate limiting.
3. **Extract** structured JSON with schema contracts.
4. **Persist** provenance-rich payloads to enrichment flow.

## Scope

| Category | Action |
|----------|--------|
| Discovery | Add domain URL mapping stage for company websites |
| Crawl | Add async crawl jobs with polling and backoff |
| Extraction | Enforce schema-based extraction contracts per signal type |
| Reliability | Add retry/circuit-breaker/degradation behavior |
| Integration | Feed output into enrichment orchestrator and conflict resolver |

## Stories

| Story | Title | Priority | Status |
|-------|-------|----------|--------|
| [STORY-190](STORIES/STORY-190.md) | Implement domain mapping stage for company URL discovery | P1 | 🔴 Not Started |
| [STORY-191](STORIES/STORY-191.md) | Implement async crawl executor with queue + polling | P1 | 🔴 Not Started |
| [STORY-192](STORIES/STORY-192.md) | Implement schema extraction contracts for product/team/tech fields | P1 | 🔴 Not Started |
| [STORY-193](STORIES/STORY-193.md) | Integrate crawl outputs into enrichment orchestrator with provenance | P1 | 🔴 Not Started |

## Target Integration Points

- `src/solstein/data/web_research_pipeline.py`
- `src/solstein/data/enrichment/orchestrator.py`
- `src/solstein/data/enrichment/models.py`
- `src/solstein/data/provenance.py`
- `src/solstein/data/source_policy.py`
- `src/solstein/data/enrichment_service.py`

## Architectural Requirements

- **REQ-1**: Acquisition must run as a staged pipeline (`map -> crawl -> extract`) with persisted intermediate state.
- **REQ-2**: Extraction output must validate against explicit schemas before entering scoring inputs.
- **REQ-3**: Source failures must degrade gracefully (warning + stale/partial marker), never silently return empty success.
- **REQ-4**: Every extracted field must carry source URL, timestamp, and confidence metadata.
- **REQ-5**: All network calls must honor per-domain rate limits and bounded retries.

## Success Criteria

- At least 90% of researched companies produce one or more valid mapped pages.
- Crawl success rate >= 85% across selected pages (excluding hard blocks).
- Schema validation pass rate >= 95% for accepted extracted payloads.
- 100% of extracted fields include provenance metadata.
- No silent-failure path: all acquisition failures emit structured logs and metrics.

## Risks

| Risk | Mitigation |
|------|------------|
| Website anti-bot measures reduce crawl yield | Add fallback connectors and per-domain strategy controls |
| Overly strict schemas drop useful data | Start with optional fields + warn mode, then tighten |
| Crawl cost/latency spikes | Add bounded page budgets and cache with freshness windows |
| Orchestrator coupling increases complexity | Keep acquisition outputs behind typed adapter interface |

## Notes

This epic is not "add another scraper." It defines the acquisition contract that upstream data must satisfy before Solstein trusts it. The main objective is predictable, inspectable ingestion quality.
