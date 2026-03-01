# M3: Modern Data Layer

> Vector search, realtime updates, async exports, and data integrity.

| Field | Value |
|-------|-------|
| **Target Date** | 2026-04-15 |
| **Duration** | 2 weeks |
| **Epics** | 4 |
| **Stories** | 14 |
| **Status** | 🔴 Not Started |
| **Depends On** | [M2: Secure Identity](M2-Secure-Identity.md) |

---

## Goal

Modernize the data layer with pgvector for semantic search, Supabase Realtime for live updates, async exports for reliability, and ensure data completeness throughout the pipeline.

---

## Included Epics

| Epic | Title | Stories | Priority |
|------|-------|---------|----------|
| [EPIC-023](../EPICS/EPIC-023-pgvector-semantic-search/README.md) | pgvector Semantic Search | 3 | P2 |
| [EPIC-024](../EPICS/EPIC-024-supabase-realtime-job-status/README.md) | Supabase Realtime Job Status | 2 | P2 |
| [EPIC-030](../EPICS/EPIC-030-export-pipeline-modernization/README.md) | Export Pipeline Modernization | 5 | P2 |
| [EPIC-033](../EPICS/EPIC-033-data-completeness-export-integrity/README.md) | Data Completeness & Export Integrity | 4 | P1 |

---

## Story Breakdown

### EPIC-023: pgvector Semantic Search

| Story | Title | Size | Risk |
|-------|-------|------|------|
| STORY-080 | Add pgvector Extension and Embedding Schema | M | Medium |
| STORY-081 | Generate Company Embeddings During Research Pipeline | M | Medium |
| STORY-082 | Implement Semantic Similarity Search Endpoint | M | Low |

### EPIC-024: Supabase Realtime Job Status

| Story | Title | Size | Risk |
|-------|-------|------|------|
| STORY-083 | Define Research Job Status Table with Realtime | M | Low |
| STORY-084 | Replace Polling with Supabase Realtime Subscriptions | M | Medium |

### EPIC-030: Export Pipeline Modernization

| Story | Title | Size | Risk |
|-------|-------|------|------|
| STORY-111 | Move Exports to Async Celery Tasks | M | Medium |
| STORY-112 | Streaming Excel Export for Large Datasets | L | Medium |
| STORY-113 | Export Status Tracking and Download Links | M | Low |
| STORY-114 | Add PDF Export Format | M | Low |
| STORY-115 | Store Exports in Supabase Storage | M | Medium |

### EPIC-033: Data Completeness & Export Integrity

| Story | Title | Size | Risk |
|-------|-------|------|------|
| STORY-125 | Restore 20 Dropped Fields to Excel Export | M | Medium |
| STORY-126 | Add Export Schema Validation | M | Low |
| STORY-127 | Deduplicate profit_margin and employee Fields | S | Low |
| STORY-128 | Document Field Lineage from Ingestion to Export | S | Low |

---

## Dependencies

**Hard:**
- [M2: Secure Identity](M2-Secure-Identity.md) — Multi-tenancy must be in place
- EPIC-025 (Worker Reliability) — Must have persistent DLQ before async exports

**Soft:**
- EPIC-033 should complete before EPIC-030 (fix data before modernizing pipeline)

---

## Exit Criteria

- [ ] Semantic search functional with <500ms response
- [ ] Realtime job status updates working
- [ ] Export success rate >95%
- [ ] Zero data loss in migrations
- [ ] P95 query time <200ms
- [ ] All 20 dropped fields restored to exports

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Export success rate | ~60% | >95% |
| Export timeout rate | ~40% | 0% |
| Max export size | ~50 companies | 1000+ companies |
| Search type | Filter only | Semantic + filter |
| Job status updates | Polling | Realtime |

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| pgvector performance at scale | Medium | High | Benchmark with production data volume |
| Realtime connection limits | Medium | Medium | Implement connection pooling |
| Large exports still timeout | Medium | High | Chunked generation, progress tracking |
| Data migration errors | Medium | High | Test migrations on copy of prod data |

---

## Definition of Done

- [ ] All stories in Done status
- [ ] Load tests passing
- [ ] User acceptance testing complete
- [ ] Demo to stakeholders
- [ ] M4 planning ready

---

## Related

- [M2: Secure Identity](M2-Secure-Identity.md) — Previous milestone
- [M4: Intelligent Agents](M4-Intelligent-Agents.md) — Next milestone
