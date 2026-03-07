# File Ownership Matrix: Parallel Agent Work

> **Purpose**: Define exclusive file ownership to prevent merge conflicts  
> **Last Updated**: 2026-03-06  
> **Applies To**: EPIC-020 through EPIC-030 + EPIC-XXX variants

---

## Legend

| Symbol | Meaning |
|--------|---------|
| 🔴 | EXCLUSIVE - One agent only, coordinate before changes |
| 🟡 | SHARED - Multiple agents, daily coordination required |
| 🟢 | FREE - No coordination needed |
| ⛔ | LOCKED - Do not modify (foundation/infrastructure) |

---

## STREAM A: Code Quality (@code-refactorer)

### Exclusive Ownership (🔴)

| File | Epic | Lines | Action |
|------|------|-------|--------|
| `exporters/markdown/generator.py` | EPIC-021 | 1,403 | Split into 8 modules |
| `data/unified_loader.py` | EPIC-021 | 1,066 | Split into loaders/ |
| `data/loaders.py` | EPIC-021 | 939 | Merge with unified_loader |
| `worker_tasks.py` | EPIC-021 | 903 | Split into worker/ |
| `infrastructure/database_models.py` | EPIC-021 | 836 | Split into models/ |
| `domain/models.py` | EPIC-021 | 818 | Split into domain/models/ |
| `api/routers/enrichment.py` | EPIC-021 | 802 | Extract service layer |
| `agents/github_agent.py` | EPIC-021 | 777 | Split into github/ |
| `data/additional_sources.py` | EPIC-021 | 769 | Split into sources/ |
| `llm/health_checker.py` | EPIC-021 | 704 | Split into health/ |
| `analytics/signals/models.py` | EPIC-022 | 514 | Extract signal types |
| `data/markets.py` | EPIC-021 | 511 | Split by market type |

### Function-Level Refactors (🔴 - EPIC-020)

| Function | File | Lines | New Location |
|----------|------|-------|--------------|
| `run_market_intelligence` | research/pipeline.py | 505 | research/pipeline/ |
| `_convert_to_domain_company` | data/converter.py | 429 | data/converters/ |
| `_catalog_for_market` | research/discovery.py | 429 | research/discovery/ |
| `_generate_competitive_analysis` | analytics/competitive.py | 225 | analytics/competitive/ |
| `persist_research_run_records` | research/persistence.py | 198 | research/persistence/ |

---

## STREAM B: Performance (@performance-optimizer)

### Exclusive Ownership (🔴)

| File | Epic | Lines | Action |
|------|------|-------|--------|
| `monitoring/performance.py` | EPIC-023 | NEW | Create profiler |
| `infrastructure/cache.py` | EPIC-023 | NEW | Multi-level cache |
| `infrastructure/database.py` | EPIC-025 | EXISTING | Optimize pool config |

### Shared Ownership (🟡 - Coordinate with Stream A)

| File | Epic | Coordination Point |
|------|------|-------------------|
| `infrastructure/repositories.py` | EPIC-025 | After EPIC-020/021 extractions |
| `research/pipeline.py` | EPIC-023 | After async conversion |
| `api/routers/*.py` | EPIC-023 | After service layer extraction |
| `data/fetchers/*.py` | EPIC-023 | After file splitting |

### Database Schema (🔴)

| Change | Epic | Impact |
|--------|------|--------|
| Add indexes | EPIC-025 | Migration only, no app changes |
| Query optimization | EPIC-025 | Read-only improvements |
| Connection pooling | EPIC-025 | Config only |
| N+1 elimination | EPIC-025 | Coordinate with Stream A repositories |

---

## STREAM C: Infrastructure/Security (@cloud-architect)

### Exclusive Ownership (🔴)

| File | Epic | Lines | Action |
|------|------|-------|--------|
| `security/secrets.py` | EPIC-027 | NEW | Vault integration |
| `security/rbac.py` | EPIC-027 | NEW | Role-based access |
| `infrastructure/tenant_middleware.py` | EPIC-030 | NEW | Tenant isolation |
| `tests/conftest.py` | EPIC-029 | EXISTING | Test fixtures |
| `tests/factories/` | EPIC-029 | NEW | Test data factories |
| `tests/property/` | EPIC-029 | NEW | Property-based tests |

### Shared Ownership (🟡 - Coordinate Daily)

| File | Epic | Coordination Point |
|------|------|-------------------|
| `infrastructure/database_models.py` | EPIC-030 | After EPIC-021 split, add tenant_id |
| `api/middleware/tenant.py` | EPIC-030 | Enhance existing |
| `api/dependencies.py` | EPIC-030 | Add tenant context |
| `.github/workflows/*.yml` | EPIC-XXX | CI improvements |

### Critical Coordination: Multi-Tenancy Schema

```python
# EPIC-030 MUST wait for EPIC-021 database split
# Then add tenant_id to all models

# Order:
# 1. EPIC-021 splits database_models.py into models/
# 2. EPIC-025 adds indexes to all tables
# 3. EPIC-030 adds tenant_id columns + RLS policies
```

---

## STREAM D: Documentation/DX (@documenter)

### Exclusive Ownership (🟢)

| File | Epic | Type |
|------|------|------|
| `docs/api/openapi.json` | EPIC-024 | Generated |
| `docs/api/CHANGELOG.md` | EPIC-024 | Markdown |
| `docs/developers/*.md` | EPIC-024 | Markdown |
| `docker-compose.dev.yml` | EPIC-028 | YAML |
| `Dockerfile.dev` | EPIC-028 | Dockerfile |
| `Makefile` | EPIC-028 | Makefile |
| `.github/workflows/` | EPIC-XXX | YAML configs |

### Read-Only Access (⛔)

| File | Reason |
|------|--------|
| `src/**/*.py` | Document only, don't modify |
| `tests/**/*.py` | Document test patterns |
| `pyproject.toml` | May update dev dependencies |

---

## Conflict Hotspots: Detailed Coordination

### Hotspot 1: Database Models

```
File: src/solstein/infrastructure/database_models.py (836 lines)

Timeline:
Week 1-2: EPIC-021 (Stream A) splits into models/
  ├─ models/company.py
  ├─ models/research.py
  ├─ models/enrichment.py
  └─ models/base.py

Week 5-6: EPIC-025 (Stream B) adds indexes
  └─ Alembic migrations only

Week 9-10: EPIC-030 (Stream C) adds tenant_id
  ├─ Add tenant_id to all models
  ├─ Create RLS policies
  └─ Update repositories

LOCK PERIODS:
- Week 1-2: Stream A has exclusive lock
- Week 3-4: OPEN for read-only
- Week 5-6: Stream B has migration lock
- Week 7-8: OPEN for read-only
- Week 9+: Stream C has exclusive lock
```

### Hotspot 2: Research Pipeline

```
File: src/solstein/research/pipeline.py

Timeline:
Week 3-4: EPIC-020 (Stream A) converts to async
  ├─ Extract stage classes
  └─ Convert to async/await

Week 7-8: EPIC-023 (Stream B) optimizes
  ├─ Add concurrency limits
  ├─ Optimize memory usage
  └─ Add streaming

COORDINATION REQUIRED:
- Stream B must review Stream A's async changes
- Performance benchmarks must pass before either merges
- Integration tests in tests/integration/test_pipeline.py
```

### Hotspot 3: API Routers

```
Files: src/solstein/api/routers/*.py

Order of Operations:
1. EPIC-021 (Stream A) extracts service layer
   ├─ routers/enrichment.py → services/enrichment_service.py
   └─ Routers become thin (150 lines each)

2. EPIC-023 (Stream B) optimizes response time
   ├─ Add caching decorators
   └─ Optimize database queries

3. EPIC-024 (Stream D) documents
   ├─ Add OpenAPI decorators
   └─ Generate openapi.json

4. EPIC-030 (Stream C) adds tenant validation
   └─ Add tenant middleware integration
```

---

## Daily Coordination Checklist

### Morning Standup Questions

1. **What files did you modify yesterday?**
   - List file paths
   - Type of change (refactor/optimize/add)

2. **What files will you touch today?**
   - Check against ownership matrix
   - Flag any 🔴 or 🟡 conflicts

3. **Are you blocked by another stream?**
   - Dependency waiting
   - Code review needed

### Conflict Prevention

```bash
# Before starting work each day:

# 1. Check integration branch status
git fetch origin epic/020-refactoring
git log --oneline origin/epic/020-refactoring -10

# 2. Check for upcoming changes to shared files
grep -r "database_models\|repositories\|pipeline" \
  docs/epics/EPIC-020*.md docs/epics/EPIC-021*.md \
  docs/epics/EPIC-022*.md docs/epics/EPIC-023*.md \
  docs/epics/EPIC-025*.md docs/epics/EPIC-030*.md

# 3. Notify other streams in Slack
@channel Working on X today - affects files Y and Z
```

---

## Emergency Protocol: Merge Conflict

### When Conflict Detected

```
1. STOP all work on conflicting files immediately
2. Notify in #dev-parallel-work:
   "CONFLICT: [file] between [Stream X] and [Stream Y]"
3. Both streams checkout integration branch
4. Reproduce conflict locally
5. Schedule 15-min conflict resolution call
6. Decide:
   a) Rebase one branch (preferred)
   b) Manual merge with both authors present
   c) Revert one change and redo
7. Document resolution for future reference
```

### Conflict Resolution Roles

| Role | Responsibility |
|------|---------------|
| **Older Branch Author** | Performs rebase, fixes conflicts |
| **Younger Branch Author** | Reviews rebase, tests integration |
| **Stream Lead** | Approves resolution strategy |
| **Integration Lead** | Merges to integration branch |

---

## File Change Notification Template

```markdown
## File Change Notification

**Stream**: A (Code Quality)
**Agent**: @code-refactorer
**Date**: 2026-03-06

### Files Modified
- `src/solstein/data/unified_loader.py` (splitting)
- `src/solstein/data/loaders/` (new directory)

### Impact
- 🟡 Affects EPIC-025 (Database) - loader uses repositories
- 🟢 No impact on EPIC-027, EPIC-030

### Coordination Needed
- Stream B: Review new loader structure before optimizing queries

### ETA
- PR ready for review: EOD
- Merge to integration: Tomorrow 10am
```

---

## Weekly Integration Schedule

| Day | Activity | Streams Involved |
|-----|----------|------------------|
| Monday | Planning & branch creation | All |
| Tuesday-Thursday | Development | Individual |
| Friday 10am | Integration branch merge | Stream leads |
| Friday 2pm | Integration testing | All |
| Friday 4pm | Demo & retrospective | All |

---

## Quick Reference: Who Owns What

### Need to refactor a god function?
→ **Stream A** (@code-refactorer)

### Need to optimize a database query?
→ **Stream B** (@performance-optimizer)  
→ But FIRST check if Stream A is refactoring that file

### Need to add a database column?
→ **Stream C** (@cloud-architect) for tenant_id  
→ **Stream B** (@performance-optimizer) for indexes  
→ Coordinate with both

### Need to document an API?
→ **Stream D** (@documenter)  
→ But API must be stable (after Stream A refactoring)

### Need to fix CI/CD?
→ **Stream D** (@documenter) for EPIC-XXX-CICD  
→ Affects all streams - announce in #dev-parallel-work

---

*This matrix should be updated weekly as files are refactored and ownership changes.*
