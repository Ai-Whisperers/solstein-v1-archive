# Solstein Public-Web Intelligence Implementation Roadmap

**Document:** Implementation Plan for EPIC-041 through EPIC-048  
**Based on:** GitHub Research Tools Survey (300+ repositories analyzed)  
**Date:** 2026-03-07  
**Status:** Draft for Review

---

## Executive Summary

This roadmap transforms the validated technology survey into an actionable implementation plan for Solstein's public-web intelligence expansion (EPIC-041 through EPIC-048). The plan prioritizes foundational capabilities first, builds incrementally, and delivers value at each milestone.

**Key Principles:**
1. **Foundation First:** Evidence graph (EPIC-042) before advanced features
2. **Compose, Don't Build:** Use battle-tested tools from survey
3. **Deliver Value Early:** First milestone shows tangible improvement
4. **Dependency-Aware:** Respect technical prerequisites

---

## Phase 1: Foundation (Weeks 1-8)

### Milestone 1.1: Evidence Infrastructure ✅ TARGET
**EPIC:** EPIC-042 - Evidence Graph and Claim Provenance  
**Duration:** 4 weeks  
**Story Points:** 55  
**Team:** 2 backend engineers

**Why First?**
- Without evidence-grade claims, more crawling creates unverifiable noise
- All downstream EPICs depend on this foundation
- Enables "explainability" as a core differentiator

**Technology Stack (from Survey):**
| Component | Tool | Rationale |
|-----------|------|-----------|
| Entity Resolution | **splink** | Probabilistic linkage with confidence scores |
| Graph Database | **Neo4j** | Relationships + Cypher query language |
| Vector Search | **Qdrant** | Rust-based, fast, metadata filtering |
| Claim Storage | PostgreSQL + JSONB | Structured + flexible claim schema |
| LLM Framework | **LlamaIndex** | Document agents, tool use, citations |

**Deliverables:**
- [ ] Claim data model with URL/snippet/timestamp/method
- [ ] Entity resolution pipeline (blocking → pairwise → clustering)
- [ ] Evidence lineage: claim → metric → signal → score
- [ ] Confidence decomposition (source + agreement + freshness)
- [ ] Contradiction detection and review queue
- [ ] API for provenance retrieval

**Success Metrics:**
- 10 critical company metrics evidence-linked end-to-end
- Contradictions reviewable at claim level
- Score explanations include citations

---

### Milestone 1.2: Deep Crawling Capability
**EPIC:** EPIC-041 - Deep Web Crawling and Document Ingestion  
**Duration:** 4 weeks (parallel with 1.1 after week 2)  
**Story Points:** 55  
**Team:** 2 backend engineers

**Why Second?**
- Crawling produces data; evidence infrastructure stores it
- Parallel start possible after evidence schema defined (week 2)
- Natural pairing: crawl → extract → claim

**Technology Stack (from Survey):**
| Component | Tool | Rationale |
|-----------|------|-----------|
| Crawl Engine | **Crawl4AI** | LLM-friendly output, Python-native |
| Browser Automation | **Playwright** | Cross-browser, auto-wait, reliable |
| Document Parsing | **Docling** | PDF/deck extraction for AI |
| Content Extraction | **Trafilatura** | Text discovery + boilerplate removal |
| Change Detection | **changedetection.io** | Visual diff + XPath selectors |
| Job Queue | **Celery + Redis** | Distributed, database-backed scheduling |

**Deliverables:**
- [ ] Robots-aware crawl policy engine
- [ ] Sitemap discovery and crawl frontier
- [ ] JS-rendered page support (Playwright)
- [ ] PDF/document ingestion pipeline
- [ ] Page-type classification (pricing, docs, careers, investor)
- [ ] Crawl snapshots with versioning

**Success Metrics:**
- 20 company websites crawled with >85% key-page coverage
- PDFs and documents extracted successfully
- Crawl metadata queryable

---

## Phase 2: Expansion (Weeks 9-16)

### Milestone 2.1: Open Data Source Integration
**EPIC:** EPIC-043 - Open-Data Source Expansion  
**Duration:** 4 weeks  
**Story Points:** 55  
**Team:** 2 backend engineers

**Prerequisites:** EPIC-042 (evidence schema), EPIC-041 (crawl pipeline)

**Technology Stack (from Survey):**
| Source Category | Tools |
|-----------------|-------|
| Academic/Papers | **LlamaIndex Readers** (100+ connectors) |
| Financial Data | **OpenBB** (multi-provider abstraction) |
| SEC EDGAR | **edgartools** (CIK mapping) |
| Company Registries | **chwrapper** (UK CH), custom adapters |
| News | **newsapi-python**, **Camel News** |
| Social Media | **Tweepy** (Twitter/X), **Agno** (multi-platform) |
| Geospatial | **geocoder** (50+ providers) |

**Deliverables:**
- [ ] 8+ new source families integrated
- [ ] Unified connector interface (OpenBB pattern)
- [ ] Rate limiting and caching per source
- [ ] Source quality scoring
- [ ] Coverage metrics by sector/geography

**Success Metrics:**
- Coverage uplift visible by sector
- New sources flow through evidence model
- Source ROI measurable

---

### Milestone 2.2: Entity Resolution & Market Universe
**EPIC:** EPIC-044 - Entity Resolution and Market Universe Builder  
**Duration:** 4 weeks (parallel with 2.1 after week 2)  
**Story Points:** 55  
**Team:** 2 backend engineers

**Prerequisites:** EPIC-042 (entity resolution foundation)

**Technology Stack (from Survey):**
| Component | Tool | Rationale |
|-----------|------|-----------|
| Fuzzy Matching | **sentence-transformers** | Semantic similarity |
| Blocking | Custom + **splink** | Efficient candidate generation |
| Clustering | **splink** | Probabilistic linkage |
| Graph Storage | **Neo4j** | Corporate relationships |
| Canonical IDs | UUID v5 (namespace) | Deterministic, reproducible |

**Deliverables:**
- [ ] Canonical entity identity model
- [ ] Parent/subsidiary relationship mapping
- [ ] Market universe builder (seed → expansion)
- [ ] Candidate ranking and review workflow
- [ ] Sector/geography templates

**Success Metrics:**
- Duplicate profiles detectable and mergeable
- Market universes generate ranked candidates
- False positive rate measurable

---

## Phase 3: Operations (Weeks 17-24)

### Milestone 3.1: Continuous Monitoring
**EPIC:** EPIC-045 - Continuous Monitoring and Change Intelligence  
**Duration:** 3 weeks  
**Story Points:** 34  
**Team:** 2 backend engineers

**Prerequisites:** EPIC-041 (crawling), EPIC-042 (evidence tracking)

**Technology Stack (from Survey):**
| Component | Tool | Rationale |
|-----------|------|-----------|
| Scheduling | **Celery beat** | Database-backed, reliable |
| Diffing | **changedetection.io** approach | Visual + structural diff |
| Stream Processing | **Bytewax** | Python-native, real-time |
| Alerting | **Apprise** | 80+ notification services |
| Dashboards | **Grafana** or **Metabase** | Observable metrics |

**Deliverables:**
- [ ] Refresh scheduling by source/entity priority
- [ ] Semantic and structural diffing
- [ ] Alerting and watchlists
- [ ] Freshness decay in confidence scores
- [ ] Change narratives (what changed + why it matters)

**Success Metrics:**
- Refresh jobs run automatically
- Material changes detected
- Alert precision >80%

---

### Milestone 3.2: Analyst Workflow
**EPIC:** EPIC-046 - Analyst Workflow and IC Memo Automation  
**Duration:** 3 weeks (parallel with 3.1)  
**Story Points:** 34  
**Team:** 1 backend + 1 full-stack engineer

**Prerequisites:** EPIC-042 (evidence), EPIC-045 (monitoring)

**Technology Stack (from Survey):**
| Component | Tool | Rationale |
|-----------|------|-----------|
| Evidence Explorer | Custom UI + API | Drill-down from score to claim |
| Review Queues | Custom + **OSINT patterns** | Low-confidence item workflow |
| Dashboards | **Metabase** or **Streamlit** | Business intelligence |
| Memo Generation | **LlamaIndex** + templates | Citation-backed exports |
| Feedback Loop | Custom | Corrections → model improvement |

**Deliverables:**
- [ ] Evidence explorer (score → signal → claim → source)
- [ ] Review queues for contradictions
- [ ] Analyst feedback capture
- [ ] IC memo generation with citations
- [ ] Coverage and blind-spot indicators

**Success Metrics:**
- Analysts can review weak evidence
- Exports include citations
- Feedback captured with audit trail

---

## Phase 4: Global & Media (Weeks 25-33)

### Milestone 4.1: Multilingual & Global Research
**EPIC:** EPIC-047 - Multilingual and Global Research Coverage  
**Duration:** 3 weeks  
**Story Points:** 34  
**Team:** 1 backend engineer

**Prerequisites:** EPIC-041 (crawling), EPIC-043 (source expansion)

**Technology Stack (from Survey):**
| Component | Tool | Rationale |
|-----------|------|-----------|
| Language Detection | **langdetect** or **fasttext** | Fast, accurate |
| NER | **spaCy** + **transformers** | Multi-language support |
| Translation | **transformers** (NLLB) or API | Quality + speed balance |
| Regional Search | Custom strategies | Locale-aware queries |

**Deliverables:**
- [ ] Language detection pipeline
- [ ] Translation workflow with quality flags
- [ ] Region-aware search strategies
- [ ] Regional source adapters (pilot markets)
- [ ] Global coverage metrics

**Success Metrics:**
- Pilot languages supported
- Original + translated evidence accessible
- Regional discovery improved

---

### Milestone 4.2: Media & Transcript Intelligence
**EPIC:** EPIC-048 - Media and Transcript Intelligence  
**Duration:** 3 weeks  
**Story Points:** 34  
**Team:** 1 backend engineer

**Prerequisites:** EPIC-042 (evidence), EPIC-043 (source expansion)

**Technology Stack (from Survey):**
| Component | Tool | Rationale |
|-----------|------|-----------|
| Transcription | **faster-whisper** | Fast, accurate, local |
| Speaker Diarization | **pyannote.audio** | State-of-the-art |
| Media Discovery | Custom + APIs | Podcast/webinar search |
| Quote Attribution | Custom NLP | Speaker → claim mapping |

**Deliverables:**
- [ ] Media source discovery
- [ ] Transcript acquisition pipeline
- [ ] Speaker and quote attribution
- [ ] Narrative signal extraction
- [ ] Media-specific provenance

**Success Metrics:**
- Pilot transcript pipeline works
- Media claims traceable to source
- Company/market reports include media evidence

---

## Dependency Graph

```
EPIC-042 (Evidence) ─────────────────┬──────────────────────────────────┐
       │                             │                                  │
       ├──────────────┬──────────────┼──────────────┬───────────────────┤
       │              │              │              │                   │
EPIC-041 (Crawl) ─────┤              │              │                   │
       │              │              │              │                   │
       ├──────────────┼──────────────┤              │                   │
       │              │              │              │                   │
EPIC-043 (Open Data) ─┘              │              │                   │
       │                             │              │                   │
       ├─────────────────────────────┘              │                   │
       │                                            │                   │
EPIC-044 (Entity) ─────────────────────────────────┘                   │
       │                                                                │
       ├─────────────────────────────┬──────────────────────────────────┤
       │                             │                                  │
EPIC-045 (Monitoring) ──────────────┤                                  │
       │                             │                                  │
       ├─────────────────────────────┤                                  │
       │                             │                                  │
EPIC-046 (Workflow) ────────────────┘                                  │
       │                                                                │
       ├────────────────────────────────────────────────────────────────┤
       │                                                                │
EPIC-047 (Multilingual) ───────────────────────────────────────────────┤
       │                                                                │
EPIC-048 (Media) ──────────────────────────────────────────────────────┘
```

**Critical Path:**
1. EPIC-042 (Evidence) → EPIC-041 (Crawl) → EPIC-043 (Open Data) → EPIC-044 (Entity)
2. EPIC-042 → EPIC-045 (Monitoring) → EPIC-046 (Workflow)
3. EPIC-043 → EPIC-047 (Multilingual) / EPIC-048 (Media)

---

## Quick Wins (Deliver in First 4 Weeks)

### Week 1-2: Evidence Schema + Basic Crawl
- Define claim data model
- Set up Neo4j + Qdrant
- Basic Crawl4AI integration
- Crawl 5 pilot company websites

### Week 3-4: Entity Resolution + Evidence Linking
- Implement splink pipeline
- Link 10 critical metrics to evidence
- Basic contradiction detection
- Score explanations with citations

**Result:** Tangible evidence-grade capability demonstrated

---

## Resource Requirements

| Phase | Duration | Backend | Full-Stack | Total |
|-------|----------|---------|------------|-------|
| Phase 1 (Foundation) | 8 weeks | 4 | 0 | 4 engineers |
| Phase 2 (Expansion) | 8 weeks | 4 | 0 | 4 engineers |
| Phase 3 (Operations) | 8 weeks | 3 | 1 | 4 engineers |
| Phase 4 (Global/Media) | 9 weeks | 2 | 0 | 2 engineers |
| **Total** | **33 weeks** | **—** | **—** | **4-6 engineers** |

**Note:** Phases overlap; peak team size is 4-6 engineers, not 13.

---

## Technology Stack Summary

| Layer | Primary | Alternatives |
|-------|---------|--------------|
| **Crawling** | Crawl4AI + Playwright | Firecrawl, Scrapy |
| **Document Parsing** | Docling | Trafilatura, custom |
| **Vector DB** | Qdrant | Weaviate, ChromaDB |
| **Graph DB** | Neo4j | Dgraph, ArangoDB |
| **Entity Resolution** | splink | dedupe.io, zingg |
| **Scheduling** | Celery + Redis | APScheduler, RQ |
| **Stream Processing** | Bytewax | Pathway, Faust |
| **LLM Framework** | LlamaIndex | LangChain, Haystack |
| **Dashboards** | Metabase | Grafana, Streamlit |
| **Change Detection** | changedetection.io | Custom + urlwatch |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Crawling blocked | Respect robots, rate limits, use residential proxies |
| Entity resolution quality | Confidence thresholds + human review |
| Translation errors | Preserve original text + quality flags |
| Scope creep | Strict milestone boundaries, MVP first |
| Integration complexity | Use standard interfaces (MCP, LangChain) |

---

## Success Metrics by Phase

### Phase 1 (Weeks 1-8)
- [ ] 10 metrics evidence-linked
- [ ] 20 companies crawled
- [ ] Contradictions reviewable

### Phase 2 (Weeks 9-16)
- [ ] 8+ source families integrated
- [ ] Market universes generate candidates
- [ ] Coverage metrics visible

### Phase 3 (Weeks 17-24)
- [ ] Refresh jobs automated
- [ ] Alert precision >80%
- [ ] Analyst workflow functional

### Phase 4 (Weeks 25-33)
- [ ] Pilot languages supported
- [ ] Media pipeline working
- [ ] Global coverage metrics

---

## First Action Items (This Week)

1. **Stakeholder Review:** Present this roadmap for approval
2. **Team Assignment:** Confirm 2 backend engineers for Phase 1
3. **Infrastructure Setup:** Provision Neo4j + Qdrant instances
4. **Pilot Selection:** Choose 5 companies for initial crawl
5. **EPIC Updates:** Add technology choices to EPIC-041 and EPIC-042

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-07 | Initial roadmap based on survey findings |

---

*Roadmap created by Sisyphus Agent*  
*Based on: GitHub Research Tools Survey (300+ repositories)*  
*EPICs covered: 041-048*
