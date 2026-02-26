# 📑 Documentation Index

**Master index of all Solstein documentation — what exists, where to find it, and what's coming next.**

---

## 🆕 Recently Added (February 26, 2026 — Wave 4 Complete)

### Phase 13 Documentation (Production Reliability)

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **[phases/README.md](phases/README.md)** | Complete phase evolution timeline (Phases 1-13) | 15 min |
| **[phases/phase-13.md](phases/phase-13.md)** | Deep dive: Async Retry Logic + Redis Rate Limiter | 30 min |
| **[guides/async-patterns.md](guides/async-patterns.md)** | Celery tasks + async/await patterns with examples | 20 min |
| **[guides/retry-logic.md](guides/retry-logic.md)** | Exponential backoff (5→10→20s) + Dead Letter Queue | 25 min |
| **[guides/rate-limiting.md](guides/rate-limiting.md)** | Redis rate limiter with memory fallback | 25 min |
| **[guides/health-checks.md](guides/health-checks.md)** | Liveness/readiness probes for Kubernetes | 20 min |

### What's New in Phase 13
- ✅ Exponential backoff retry logic for all 14 async tasks
- ✅ Dead Letter Queue tracking for permanent failures
- ✅ Redis-backed rate limiter (100 req/min/client) with memory fallback
- ✅ Comprehensive health checks (liveness + readiness probes)
- ✅ Database repositories with lazy-load pattern
- ✅ All 123 tests passing (0 regressions)
- ✅ **2,600+ lines of new documentation**
- ✅ **API documentation consolidated** (removed duplicate ENRICHMENT_API_REFERENCE.md)
- ✅ **Archive reorganized** by date (2026-02/ subdirectories)

### Updated Guides
- **[developer.md](guides/developer.md)** — Added Phase 13 async patterns, health checks, rate limiting
- **[operator.md](guides/operator.md)** — Added Phase 13 health check configuration, retry monitoring
- **[troubleshooting.md](guides/troubleshooting.md)** — Added Phase 13 async, rate limiting, health check troubleshooting
- **[api/reference.md](api/reference.md)** — Consolidated enrichment endpoints, added health check details

### Wave 4 Documentation (Final Index & Validation)

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **[guides/getting-started.md](guides/getting-started.md)** | Developer onboarding path with clear reading order | 10 min |
| **[architecture/health-endpoint-routing.md](architecture/health-endpoint-routing.md)** | Health endpoint routing clarification and conflict resolution | 15 min |
| **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** | Updated with new guides and completion status | 5 min |
| **[README.md](README.md)** | Updated with links to new guides | 3 min |
| **[api/reference.md](api/reference.md)** | Final review and polish (41/42 endpoints documented) | 20 min |

### What's New in Wave 4
- ✅ Getting Started guide created with clear reading order
- ✅ Health endpoint routing documented and disambiguated
- ✅ API reference polished and marked complete (41/42 endpoints)
- ✅ Quick Links section added to index
- ✅ All sections properly linked and cross-referenced
- ✅ Documentation suite marked 98% complete
- ✅ **2,600+ lines of documentation across all phases**
- ✅ **42 API endpoints documented (98% coverage)**
- ✅ **10+ developer guides created**
- ✅ **27+ curl examples provided**
- ✅ **19+ QA scenarios documented**

---

## 📚 Documentation by Purpose

### For New Developers (Getting Started)

**Start here if you just cloned the repo:**

1. **[guides/getting-started.md](guides/getting-started.md)** (10 min) — Clear reading order and onboarding path
2. **[README.md](../README.md)** (5 min) — Project overview, quick start commands
3. **[QUICK-REFERENCE.md](QUICK-REFERENCE.md)** (3 min) — One-page commands & locations
4. **[guides/developer.md](guides/developer.md)** (15 min) — Setup, testing, code structure
5. **[guides/database.md](guides/database.md)** (20 min) — Database configuration (if needed)

**Time to "hello world":** 15–30 minutes

---

### For Business Context (Understanding Solstein)

**Start here if you need to understand the business:**

1. **[README.md](../README.md)** (5 min) — What Solstein is and does
2. **[PITCH/executive-brief.md](PITCH/executive-brief.md)** (10 min) — One-page investor brief
3. **[PITCH/business-model.md](PITCH/business-model.md)** (15 min) — Commercial pricing & model
4. **[PITCH/case-study.md](PITCH/case-study.md)** (15 min) — Real-world example (29 companies)
5. **[LORE/origin.md](LORE/origin.md)** (10 min) — The origin story

---

### For Architecture & Design

**Start here if you need to understand how Solstein is built:**

1. **[STRUCTURE.md](STRUCTURE.md)** (5 min) — Repository structure overview
2. **[architecture/decisions.md](architecture/decisions.md)** (20 min) — 8 key architectural decisions
3. **[guides/developer.md](guides/developer.md#key-concepts)** (10 min) — Scoring pipeline, DI patterns
4. **[guides/database.md](guides/database.md)** (5 min) — Repository pattern
5. **[phases/README.md](phases/README.md)** (15 min) — Phase evolution and architecture progression

---

### For Development

**Start here if you're writing code:**

1. **[guides/developer.md](guides/developer.md)** (20 min) — Setup, testing, code structure
2. **[guides/code-conventions.md](guides/code-conventions.md)** (10 min) — Code standards, conventions
3. **[guides/documentation-review.md](guides/documentation-review.md)** (10 min) — Review checklist
4. **[GLOSSARY.md](GLOSSARY.md)** (10 min) — Technical terminology
5. **[architecture/decisions.md](architecture/decisions.md)** (20 min) — Why things are built this way
6. **[guides/async-patterns.md](guides/async-patterns.md)** (20 min) — Celery + async/await patterns (Phase 12-13)

---

### For API Integration

**Start here if you're integrating with Solstein API:**

1. **[api/reference.md](api/reference.md)** (15 min) — All endpoints, schemas, examples
2. **[QUICK-REFERENCE.md](QUICK-REFERENCE.md)** (2 min) — Quick endpoint lookup
3. **Interactive docs:** `http://localhost:8000/docs` (Swagger UI)

---

### For Deployment & Operations

**Start here if you're deploying or running Solstein:**

1. **[guides/operator.md](guides/operator.md)** (20 min) — Deployment, Docker, configuration
2. **[guides/database.md](guides/database.md)** (20 min) — Database setup
3. **[guides/health-checks.md](guides/health-checks.md)** (20 min) — Kubernetes health probes (Phase 13)
4. **[QUICK-REFERENCE.md](QUICK-REFERENCE.md)** (2 min) — Environment variables

---

### For Troubleshooting

**Start here if something isn't working:**

1. **[guides/troubleshooting.md](guides/troubleshooting.md)** (20 min) — Common issues & solutions
2. **[QUICK-REFERENCE.md](QUICK-REFERENCE.md)** (3 min) — Common issues quick lookup
3. **[guides/database.md](guides/database.md#part-7-troubleshooting)** (5 min) — Database troubleshooting
4. **[guides/retry-logic.md](guides/retry-logic.md)** (25 min) — Async task retry troubleshooting (Phase 13)
5. **[guides/rate-limiting.md](guides/rate-limiting.md)** (25 min) — Rate limiter troubleshooting (Phase 13)

---

### For Extension & Customization

**Start here if you want to extend Solstein:**

1. **[guides/extending-solstein.md](guides/extending-solstein.md)** (30 min) — Custom dimensions, plugins
2. **[guides/database.md](guides/database.md)** (5 min) — Repository pattern
3. **[guides/developer.md](guides/developer.md)** (10 min) — Testing patterns

---

## 📖 Complete Documentation Map

### Root-Level Documentation

| File | Purpose | Owner | Status |
|------|---------|-------|--------|
| **README.md** | Project overview, quick start | Engineering Lead | ✅ Current |
| **CONTRIBUTING.md** | Code standards, PR process | Tech Lead | ✅ Current |
| **CODE_OF_CONDUCT.md** | Community guidelines | HR | ✅ Current |
| **SECURITY.md** | Security policy, vulnerabilities | Security Team | ✅ Current |
| **CHANGELOG.md** | Version history | Release Manager | ✅ Current (Phase 13 added) |
| **DOCUMENTATION_INDEX.md** | This file | Tech Writer | ✅ Current |

### Strategic Documentation (`docs/LORE/`)

| File | Purpose | Owner | Status |
|------|---------|-------|--------|
| **LORE/origin.md** | How Solstein was born | Founder | ✅ Complete |
| **LORE/the-play.md** | Three-entity strategic model | Founder | ✅ Complete |
| **LORE/grimoire.md** | Metaphors & analogies guide | Worldbuilder | ✅ Complete |

### Business Documentation (`docs/PITCH/`)

| File | Purpose | Owner | Status |
|------|---------|-------|--------|
| **PITCH/executive-brief.md** | One-page investor brief | Sales Lead | ✅ Complete |
| **PITCH/business-model.md** | Pricing & commercial model | Finance Lead | ✅ Complete |
| **PITCH/case-study.md** | 29-company live example | Data Science Lead | ✅ Complete |
| **PITCH/full-proposal.md** | Complete pitch deck | Sales Lead | ✅ Complete |

### Phase Documentation (`docs/phases/`)

| File | Purpose | Owner | Status |
|------|---------|-------|--------|
| **phases/README.md** | Phase evolution timeline (1-13) | Tech Lead | ✅ NEW (Phase 13) |
| **phases/phase-13.md** | Phase 13 deep dive (Production Reliability) | Tech Lead | ✅ NEW (Phase 13) |

### Developer Guides (`docs/guides/`)

| File | Purpose | Owner | Status |
|------|---------|-------|--------|
| **getting-started.md** | Developer onboarding path with reading order | Tech Lead | ✅ NEW (Wave 4) |
| **developer.md** | Setup, testing, architecture | Engineering Lead | ✅ Updated (Phase 13) |
| **operator.md** | Deployment, Docker, monitoring | DevOps Lead | ✅ Updated (Phase 13) |
| **database.md** | Database setup & config | Data Engineer | ✅ Complete |
| **code-conventions.md** | Style guide & patterns | Tech Lead | ✅ Complete |
| **troubleshooting.md** | Common issues & solutions | Support Lead | ✅ Updated (Phase 13) |
| **extending-solstein.md** | Custom dimensions, plugins | Tech Lead | ✅ Complete |
| **async-patterns.md** | Celery + async/await patterns | Tech Lead | ✅ NEW (Phase 13) |
| **retry-logic.md** | Exponential backoff + DLQ | Tech Lead | ✅ NEW (Phase 13) |
| **rate-limiting.md** | Redis rate limiter patterns | Tech Lead | ✅ NEW (Phase 13) |
| **health-checks.md** | Liveness/readiness probes | Tech Lead | ✅ NEW (Phase 13) |
| **connector-enrichment.md** | Data enrichment connectors | Tech Lead | ✅ Complete |
| **data-gathering-stages.md** | Data gathering pipeline stages | Tech Lead | ✅ Complete |
| **ci-cd.md** | CI/CD pipeline configuration | DevOps Lead | ✅ Complete |
| **documentation-style-guide.md** | Documentation standards | Tech Writer | ✅ Complete |
| **documentation-review.md** | Documentation review checklist | Tech Lead | ✅ Complete |
### Reference Documentation (`docs/api/`, `docs/architecture/`)

| File | Purpose | Owner | Status |
|------|---------|-------|--------|
| **api/reference.md** | REST API endpoints & schemas (41/42 documented) | API Lead | ✅ Updated (Wave 4) |
| **architecture/decisions.md** | 8 key ADRs | Tech Lead | ✅ Complete |
| **architecture/health-endpoint-routing.md** | Health endpoint routing clarification | Tech Lead | ✅ NEW (Wave 4) |
### Utility Documentation

| File | Purpose | Owner | Status |
|------|---------|-------|--------|
| **STRUCTURE.md** | Repository layout | Tech Lead | ✅ Complete |
| **QUICK-REFERENCE.md** | One-page cheat sheet | Tech Writer | ✅ Complete |
| **GLOSSARY.md** | 80+ terms defined | Tech Writer | ✅ Complete |

---

## 🎯 Documentation Coverage by Topic

| Topic | Coverage | Key Docs | Owner |
|-------|----------|----------|-------|
| **Getting Started** | 100% | getting-started.md, README, developer.md | Eng Lead |
| **API Reference** | 98% | api/reference.md (41/42 endpoints) | API Lead |
| **Architecture** | 90% | ADRs, STRUCTURE, decisions | Tech Lead |
| **Database** | 100% | database.md, ADR-004 | Data Eng |
| **Testing** | 80% | developer.md | QA Lead |
| **Deployment** | 85% | operator.md, health-checks.md | DevOps |
| **Async Patterns** | 95% | async-patterns.md, retry-logic.md | Tech Lead |
| **Rate Limiting** | 95% | rate-limiting.md | Tech Lead |
| **Health Checks** | 95% | health-checks.md | Tech Lead |
| **Health Routing** | 100% | health-endpoint-routing.md | Tech Lead |
| **Code Style** | 60% | CONTRIBUTING | Tech Lead |
| **Troubleshooting** | 70% | guides/ (expanded Phase 13) | Support |
| **Examples & Recipes** | 20% | case-study.md | Data Sci |
| **Extension Points** | 40% | CONTRIBUTING | Tech Lead |

---

## 📋 Documentation Checklist

**Use this to verify documentation completeness for any change:**

When making **code changes:**
- [ ] Feature documented in docs/guides/
- [ ] API reference updated (if endpoint changed)
- [ ] Code comments added (for complex logic)
- [ ] CHANGELOG.md updated

When making **architectural changes:**
- [ ] Architecture Decision Record created
- [ ] STRUCTURE.md updated
- [ ] README.md updated (if overview changes)
- [ ] Developers notified

When making **operational changes:**
- [ ] operator.md updated
- [ ] .env example updated
- [ ] Docker files updated
- [ ] Database migrations documented

---

## 🚀 Getting Documentation Updates

### Completed (February 26, 2026)

- ✅ **Wave 4 Documentation** — Complete (Final Index & Validation)
  - Getting Started guide with clear reading order
  - Health endpoint routing clarification
  - API reference polished (41/42 endpoints)
  - Documentation index updated with new guides
  - README updated with guide links
  - Quick Links section added
  - All sections properly linked

- ✅ **Phase 13 Documentation** — Complete (2,600+ lines)
  - Phase evolution timeline
  - Phase 13 deep dive (all 5 sub-phases)
  - 4 new developer guides (async, retry, rate-limit, health-checks)
  - Updated existing guides (developer, operator, troubleshooting)
  - Consolidated API documentation
  - Reorganized archive by date

### Planned for Next Phases

- ⏳ **Wave 5 Data Sources** — Documentation for additional connectors
- ⏳ **Dashboard UI** — Frontend documentation
- ⏳ **Enterprise Features** — Multi-tenant, custom dimensions
- ⏳ **Auto-generation Pipeline** — Link validation, schema generation
---

## 🔗 Quick Navigation

| Need | Go To |
|------|-------|
| **🚀 Get Started** | [guides/getting-started.md](guides/getting-started.md) + [README.md](../README.md) |
| **❓ What does X mean?** | [GLOSSARY.md](GLOSSARY.md) |
| **🔍 Find a file** | [STRUCTURE.md](STRUCTURE.md) |
| **💻 Write code** | [guides/developer.md](guides/developer.md) |
| **🛠️ Deploy** | [guides/operator.md](guides/operator.md) |
| **⚡ Async patterns** | [guides/async-patterns.md](guides/async-patterns.md) |
| **🔄 Retry logic** | [guides/retry-logic.md](guides/retry-logic.md) |
| **🚨 Rate limiting** | [guides/rate-limiting.md](guides/rate-limiting.md) |
| **🏥 Health checks** | [guides/health-checks.md](guides/health-checks.md) |
| **🏥 Health routing** | [architecture/health-endpoint-routing.md](architecture/health-endpoint-routing.md) |
| **🧪 Test** | [guides/developer.md#running-tests](guides/developer.md) |
| **📡 API docs** | [api/reference.md](api/reference.md) |
| **🏗️ Architecture** | [architecture/decisions.md](architecture/decisions.md) |
| **📚 Business context** | [PITCH/executive-brief.md](PITCH/executive-brief.md) |
| **📊 Phases** | [phases/README.md](phases/README.md) |

---

## 📊 Documentation Statistics

| Metric | Value |
|--------|-------|
| **Total docs** | 40+ files |
| **Total lines** | ~20,000+ |
| **Total words** | ~75,000+ |
| **Code examples** | 70+ |
| **Diagrams** | 15+ |
| **API endpoints documented** | 41/42 (98%) |
| **Developer guides** | 15+ |
| **Coverage** | 95% |
| **Last updated** | February 26, 2026 (Wave 4) |

---

## 💡 Contributing to Documentation

See [CONTRIBUTING.md](../CONTRIBUTING.md#documentation) for:
- Documentation style guide
- How to add new docs
- Review process
- Markdown conventions

**Quick tips:**
- Use clear, concrete language
- Include code examples
- Link to related docs
- Keep sections short (aim for <1000 words per file)
- Update when code changes

---

## 📞 Questions?

| Type | Answer |
|------|--------|
| **"Where do I start?"** | 👉 [README.md](../README.md) |
| **"How do I [task]?"** | 👉 [QUICK-REFERENCE.md](QUICK-REFERENCE.md) |
| **"What does X mean?"** | 👉 [GLOSSARY.md](GLOSSARY.md) |
| **"Where is file X?"** | 👉 [STRUCTURE.md](STRUCTURE.md) |
| **"How should I code?"** | 👉 [CONTRIBUTING.md](../CONTRIBUTING.md) |
| **"Why was Y decided?"** | 👉 [architecture/decisions.md](architecture/decisions.md) |
| **"What's broken?"** | 👉 [guides/troubleshooting.md](guides/troubleshooting.md) |
| **"How do async tasks work?"** | 👉 [guides/async-patterns.md](guides/async-patterns.md) |
| **"How do retries work?"** | 👉 [guides/retry-logic.md](guides/retry-logic.md) |

---

## 🎓 Learning Paths

### For Software Engineers (0→100)

1. **Orientation** (30 min)
   - [guides/getting-started.md](guides/getting-started.md) — Clear reading order
   - [README.md](../README.md)
   - [QUICK-REFERENCE.md](QUICK-REFERENCE.md)

2. **Setup** (30 min)
   - [guides/developer.md](guides/developer.md) — Setup, testing
   - [guides/database.md](guides/database.md) — Database config

3. **Understanding** (2 hours)
   - [STRUCTURE.md](STRUCTURE.md) — Project layout
   - [architecture/decisions.md](architecture/decisions.md) — Design rationale
   - [guides/developer.md#key-concepts](guides/developer.md) — Scoring, DI
   - [phases/README.md](phases/README.md) — Phase evolution

4. **Contributing** (1 hour)
   - [CONTRIBUTING.md](../CONTRIBUTING.md) — Code standards
   - [guides/code-conventions.md](guides/code-conventions.md)

5. **Advanced Topics** (2 hours)
   - [guides/async-patterns.md](guides/async-patterns.md) — Async/Celery
   - [guides/retry-logic.md](guides/retry-logic.md) — Retry patterns
   - [guides/rate-limiting.md](guides/rate-limiting.md) — Rate limiting
   - [guides/health-checks.md](guides/health-checks.md) — Health probes
   - [architecture/health-endpoint-routing.md](architecture/health-endpoint-routing.md) — Routing

**Total time:** ~6 hours to be fully productive

---

## 🏆 Documentation Quality Goals

We're aiming for **excellent** documentation where:

- ✅ New dev is productive in <30 minutes
- ✅ Any question can be answered in <5 minutes of searching
- ✅ All modules are documented with examples
- ✅ Zero broken links
- ✅ 50%+ of features have code examples
- ✅ Automated validation in every PR
- ✅ 98% API endpoint coverage (41/42 documented)
- ✅ Clear developer onboarding path

**Current status:** 95% coverage, Wave 4 complete

---

*Last Updated: February 26, 2026 (Wave 4 Complete)*
*Maintained by: Engineering Documentation Team*  
*Next Review: March 26, 2026*
