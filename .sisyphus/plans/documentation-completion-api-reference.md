# Documentation Completion: API Reference & Navigation

## TL;DR

> **Quick Summary**: Complete the documentation suite by documenting all 42 missing API endpoints, clarifying endpoint routing conflicts, and creating a developer navigation guide. Current API reference covers only 11 of 42 endpoints (26% coverage).
>
> **Deliverables**:
> - Complete `docs/api/reference.md` with all 42 endpoints documented
> - Clarify `/ready` endpoint routing conflict resolution
> - Create `docs/guides/getting-started.md` with clear reading order
> - Add endpoint cross-references in navigation guide
> - Verify all examples work with actual code
>
> **Estimated Effort**: Medium-Large (90-120 minutes)
> **Parallel Execution**: YES - 3 waves, max 4 tasks per wave
> **Critical Path**: Task 1 (inventory) → Task 2-4 (parallel documentation) → Task 5-6 (routing fix) → Task 7-8 (verification)

---

## Context

### What Was Discovered

Post-execution audit of documentation fixes revealed **3 critical issues**:

1. **API Reference Incomplete** (CRITICAL)
   - Documented endpoints: 11
   - Actual endpoints: 42
   - Gap: 31 missing endpoints (74% incomplete)
   - Affected routers: drill-down, async-jobs, enrichment, simulation, health, market

2. **Duplicate /ready Endpoint** (MODERATE)
   - Registered in both `health.py` and `enrichment.py`
   - Different implementations in each router
   - Unclear which one is actually used

3. **No Developer Navigation Guide** (MODERATE)
   - Developers don't know reading order
   - No "Getting Started" path
   - Missing cross-links between guides

### Impact Assessment

**Severity**: HIGH
- Developers can't discover 31 endpoints (74% of API is invisible)
- Routing confusion for health checks
- Onboarding friction for new developers

**Scope**: 
- 1 major file update (API reference)
- 1 new file creation (getting-started guide)
- 1 routing clarification doc
- ~200 lines of new documentation

---

## Work Objectives

### Core Objective
Document all 42 actual API endpoints with accurate, complete information. Create clear developer navigation to guide onboarding. Resolve endpoint routing ambiguities.

### Concrete Deliverables
- ✅ Updated `docs/api/reference.md` with all 42 endpoints
- ✅ Created `docs/guides/getting-started.md` with reading order
- ✅ Created `docs/architecture/health-endpoint-routing.md` explaining /ready conflict
- ✅ Updated `docs/DOCUMENTATION_INDEX.md` with new getting-started guide
- ✅ All examples verified against actual code
- ✅ All cross-references validated

### Definition of Done
- [ ] All 42 endpoints documented (path, method, parameters, response, examples)
- [ ] Getting Started guide created with clear reading order
- [ ] Health endpoint routing explained and disambiguated
- [ ] No links broken, all examples verified
- [ ] DOCUMENTATION_INDEX updated
- [ ] All markdown valid

### Must Have
- ✅ Complete endpoint inventory (all 42 documented)
- ✅ Getting Started guide (clear reading order)
- ✅ Routing clarification for /ready endpoints
- ✅ curl examples for 20+ endpoints
- ✅ All methods, paths, parameters documented

### Must NOT Have (Guardrails)
- ❌ Don't invent endpoints that don't exist
- ❌ Don't oversimplify endpoint behavior
- ❌ Don't contradict actual code implementation
- ❌ Don't break existing documentation
- ❌ Don't leave any endpoint undocumented
- ❌ Don't suggest changes to code structure

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (69 documentation files already exist)
- **Automated tests**: Tests-after (content verification via grep/comparison)
- **Verification approach**: Agent-executed verification by comparing docs against actual code

### QA Policy

Every task includes verification scenarios:
- **Endpoint documentation**: Read actual router code, verify documentation matches
- **Examples**: Verify curl commands use correct paths and methods
- **Cross-references**: Verify all links point to correct files
- **Completeness**: Verify no endpoints missing from inventory

Evidence saved to `.sisyphus/evidence/task-{N}-*.txt`

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — inventory & analysis):
└── Task 1: Complete endpoint inventory [critical, blocks Wave 2]

Wave 2 (After Wave 1 — documentation, MAX PARALLEL):
├── Task 2: Document core endpoints (companies, scoring, market) [unspecified-high]
├── Task 3: Document enrichment endpoints [unspecified-high]
├── Task 4: Document async job & drill-down endpoints [unspecified-high]
└── Task 5: Document health & export endpoints [unspecified-high]

Wave 3 (After Wave 1 — routing & navigation, PARALLEL):
├── Task 6: Create getting-started.md guide [unspecified-high]
└── Task 7: Document health endpoint routing [quick]

Wave 4 (After all — verification & integration):
├── Task 8: Cross-reference verification [deep]
├── Task 9: Example verification [unspecified-high]
└── Task 10: Final index update & validation [quick]
```

### Dependency Matrix

- **1**: — → 2, 3, 4, 5, 6, 7 (inventory unblocks everything)
- **2**: 1 → 8, 10 (core endpoints documented)
- **3**: 1 → 8, 10 (enrichment documented)
- **4**: 1 → 8, 10 (async/drill-down documented)
- **5**: 1 → 8, 10 (health/export documented)
- **6**: 1 → 8, 10 (getting started guide)
- **7**: 1 → 8, 10 (routing explained)
- **8**: 2, 3, 4, 5, 6, 7 → 10 (cross-ref verification)
- **9**: 2, 3, 4, 5 → 10 (example verification)
- **10**: 8, 9 → COMPLETE (final validation)

### Agent Dispatch Summary

- **Wave 1**: Task 1 → `quick` (inventory creation)
- **Wave 2**: Tasks 2-5 → `unspecified-high` (substantial documentation writing)
- **Wave 3**: Task 6 → `unspecified-high` (guide writing), Task 7 → `quick` (routing doc)
- **Wave 4**: Task 8 → `deep` (comprehensive verification), Task 9 → `unspecified-high` (example testing), Task 10 → `quick` (final validation)

---

## TODOs

### Task 1: Complete Endpoint Inventory

**What to do**:
- Scan all 10 router files in `src/solstein/api/routers/`
- For each endpoint (@router.get, @router.post, @router.delete):
  - Extract path (with prefixes from main.py)
  - Extract method (GET/POST/DELETE)
  - Extract response model / schema
  - Note any path parameters or query parameters
  - Find example usage in code or tests
- Create complete inventory of all 42 endpoints
- Organize by functional group (companies, scoring, market, etc.)

**Must NOT do**:
- Don't invent endpoints
- Don't miss any router file
- Don't ignore prefixes from main.py registration

**Recommended Agent Profile**:
- **Category**: `quick`
  - Reason: Mechanical inventory task, straightforward code scanning
- **Skills**: None required

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 1 (start immediately)
- **Blocks**: Tasks 2-7 (all doc tasks depend on complete inventory)
- **Blocked By**: None

**References**:

**Code References** (routers to scan):
- `src/solstein/api/routers/companies.py` — Company endpoints
- `src/solstein/api/routers/scoring.py` — Scoring endpoints
- `src/solstein/api/routers/market.py` — Market analysis endpoints
- `src/solstein/api/routers/enrichment.py` — Enrichment & health endpoints
- `src/solstein/api/routers/health.py` — Health check endpoints (alternate impl)
- `src/solstein/api/routers/export.py` — Export endpoints
- `src/solstein/api/routers/jobs.py` — Job management endpoints
- `src/solstein/api/routers/async_jobs.py` — Async job endpoints
- `src/solstein/api/routers/drill_down.py` — Drill-down detail endpoints
- `src/solstein/api/routers/simulation.py` — Simulation endpoints

**Router Registration** (for prefixes):
- `src/solstein/api/main.py` — Lines with `app.include_router()`

**WHY Each Reference Matters**:
- Router files show actual endpoints implemented
- main.py shows how routes are mounted (with prefixes)
- Need both to get complete paths

**Acceptance Criteria**:

- [ ] All 10 router files scanned for endpoints
- [ ] Inventory includes: path, method, response_model, parameters, example
- [ ] Paths include prefixes from main.py (e.g., `/market/analysis` not `/analysis`)
- [ ] Total count: 42 endpoints identified
- [ ] Organized by functional group (companies, scoring, market, enrichment, etc.)
- [ ] Evidence file lists all 42 endpoints

**QA Scenarios**:

```
Scenario: All 42 endpoints identified and organized
  Tool: Bash (grep) + manual comparison
  Preconditions: All router files scanned
  Steps:
    1. Read inventory generated in task
    2. Grep for "@router\." in all 10 router files
    3. Count matches from grep
    4. Verify count matches inventory (should be 42)
    5. Check each endpoint has path, method, response model
  Expected Result: Inventory lists all 42 endpoints with complete information
  Failure Indicators: Missing endpoints, incomplete data, wrong count
  Evidence: .sisyphus/evidence/task-1-endpoint-inventory.txt
```

**Commit**: YES
- Message: `docs(api): create complete endpoint inventory from all 10 routers`
- Files: Inventory file (internal only)
- Pre-commit: `grep -r "@router\." src/solstein/api/routers/ | wc -l`

---

### Task 2: Document Core Endpoints (companies, scoring, market)

**What to do**:
- Use endpoint inventory from Task 1
- For each endpoint in companies, scoring, market routers:
  - Write section: `#### GET /path` or `#### POST /path`
  - Include: method, path, query parameters, response schema
  - Include: curl example (test with actual code)
  - Include: status codes and error responses
  - Include: authentication requirements (if any)
- Add to `docs/api/reference.md` in "Core Endpoints" section
- Verify examples are real, executable curl commands

**Must NOT do**:
- Don't skip endpoint examples
- Don't oversimplify parameter descriptions
- Don't invent error codes not in actual code

**Recommended Agent Profile**:
- **Category**: `unspecified-high`
  - Reason: Requires reading code, understanding endpoints, writing clear docs
- **Skills**: None required

**Parallelization**:
- **Can Run In Parallel**: YES (with Tasks 3-5)
- **Parallel Group**: Wave 2
- **Blocks**: Task 8 (cross-reference verification)
- **Blocked By**: Task 1 (needs complete inventory)

**References**:

**Code References**:
- `src/solstein/api/routers/companies.py` — Company endpoints
- `src/solstein/api/routers/scoring.py` — Scoring endpoints
- `src/solstein/api/routers/market.py` — Market endpoints
- `src/solstein/api/main.py:35-40` — How these routers are registered

**Documentation References**:
- `docs/api/reference.md` — Where to add documentation

**WHY Each Reference Matters**:
- Router files show actual endpoint implementations
- main.py shows registration (to get prefixes correct)
- API reference shows where to add new documentation

**Acceptance Criteria**:

- [ ] All companies endpoints documented (GET /companies, GET /companies/{id}, POST /companies)
- [ ] All scoring endpoints documented (POST /scoring/company/{id}/score, GET /scoring/stats, GET /scoring/batch)
- [ ] All market endpoints documented (GET /market/analysis, GET /market/search, GET /market/overlap/{id})
- [ ] Each endpoint includes: path, method, parameters, response, example curl
- [ ] All examples are real curl commands that match actual endpoints
- [ ] No breaking of existing documentation structure

**QA Scenarios**:

```
Scenario: Company endpoints documented with real examples
  Tool: Read file + Bash (grep)
  Preconditions: Task 2 documentation added to API reference
  Steps:
    1. Read docs/api/reference.md company endpoints section
    2. Extract curl examples (e.g., `curl -X GET ...`)
    3. For each curl example, verify:
       - Path matches actual route in companies.py
       - Method (GET/POST) matches @router decorator
       - Query parameters (if any) match function signature
       - Response fields match response_model
  Expected Result: All curl examples are valid and match actual code
  Failure Indicators: Wrong paths, wrong methods, invented parameters
  Evidence: .sisyphus/evidence/task-2-company-endpoints.txt

Scenario: Market endpoints correctly list query parameters
  Tool: Code + doc comparison
  Preconditions: Market endpoints documented
  Steps:
    1. Read market.py endpoint definitions
    2. Check documentation lists all query parameters
    3. Verify parameter types match
    4. Verify optional vs required matches
  Expected Result: Documentation lists all parameters correctly
  Failure Indicators: Missing parameters, wrong types, wrong optional/required
  Evidence: .sisyphus/evidence/task-2-market-params.txt
```

**Commit**: YES
- Message: `docs(api): document core endpoints (companies, scoring, market)`
- Files: `docs/api/reference.md`
- Pre-commit: `grep -c "#### GET\|#### POST" docs/api/reference.md`

---

### Task 3: Document Enrichment Endpoints

**What to do**:
- Use endpoint inventory from Task 1
- Document all enrichment-specific endpoints:
  - POST /companies/{id}/enrich (single enrichment)
  - POST /companies/enrich/batch (batch enrichment)
  - GET /companies/{id}/enrichment/audit (audit trail)
  - GET /companies/{id}/enrichment/cache (cache info)
  - POST /enrichment/cache/clear (clear all)
  - POST /enrichment/cache/clear/{id} (clear specific)
  - GET /health (liveness from enrichment.py)
  - GET /ready (readiness from enrichment.py)
  - GET /metrics (performance metrics)
- For each: path, method, parameters, response, example curl
- Add to new "Enrichment Operations" section

**Must NOT do**:
- Don't duplicate health/ready from health.py documentation
- Don't confuse /ready from enrichment.py vs health.py
- Don't oversimplify cache operations

**Recommended Agent Profile**:
- **Category**: `unspecified-high`
  - Reason: Requires understanding enrichment flow, documenting carefully
- **Skills**: None required

**Parallelization**:
- **Can Run In Parallel**: YES (with Tasks 2, 4-5)
- **Parallel Group**: Wave 2
- **Blocks**: Task 8 (cross-reference verification)
- **Blocked By**: Task 1 (needs complete inventory)

**References**:

**Code References**:
- `src/solstein/api/routers/enrichment.py` — All enrichment endpoints
- `src/solstein/api/main.py:35` — Router registration (no prefix)

**Documentation References**:
- `docs/api/reference.md` — Where to add documentation
- `docs/guides/health-checks.md` — How health/ready are described (consistency)

**WHY Each Reference Matters**:
- enrichment.py shows all endpoints in this router
- main.py confirms no prefix (routes register as /path not /prefix/path)
- health-checks guide shows how these probes are used

**Acceptance Criteria**:

- [ ] All 9 enrichment endpoints documented
- [ ] POST endpoints show request body schema
- [ ] GET endpoints show query parameters
- [ ] Examples show actual curl commands
- [ ] No contradiction with health-checks.md descriptions
- [ ] Clearly notes which endpoints are health probes

**QA Scenarios**:

```
Scenario: Enrichment endpoints documented with request bodies
  Tool: Code + doc comparison
  Preconditions: Enrichment section documented
  Steps:
    1. Read enrichment.py POST endpoint definitions
    2. Check documentation shows request body fields
    3. Verify request body matches actual code (from schemas)
    4. Verify response body matches response_model
  Expected Result: Documentation shows complete request/response schemas
  Failure Indicators: Missing fields, wrong types, invented fields
  Evidence: .sisyphus/evidence/task-3-enrichment-schemas.txt

Scenario: Health probe endpoints consistent with health-checks.md
  Tool: Cross-file comparison
  Preconditions: Both health-checks.md and API reference have /health, /ready
  Steps:
    1. Read health-checks.md description of /health
    2. Read API reference documentation of /health
    3. Compare descriptions (should match)
    4. Verify both mention same components checked
  Expected Result: Consistent descriptions across both documents
  Failure Indicators: Contradictory descriptions, different components listed
  Evidence: .sisyphus/evidence/task-3-health-consistency.txt
```

**Commit**: YES
- Message: `docs(api): document enrichment endpoints (audit, cache, health, metrics)`
- Files: `docs/api/reference.md`
- Pre-commit: `grep -A2 "Enrichment Operations" docs/api/reference.md | head -5`

---

### Task 4: Document Async Job & Drill-Down Endpoints

**What to do**:
- Use endpoint inventory from Task 1
- Document async job endpoints:
  - POST /enrich/single — Single enrichment job
  - POST /enrich/batch — Batch enrichment job
  - GET /jobs/{job_id} — Job details
- Document drill-down endpoints:
  - GET /company/{id}/why/{signal} — Signal deep dive
  - GET /company/{id}/sources — Data sources for company
  - GET /company/{id}/source/{source_id} — Specific source details
- For each: path, method, parameters, response, example
- Add to new "Async Operations" and "Deep Dive Analysis" sections
- Include job status codes and polling strategy

**Must NOT do**:
- Don't confuse /enrich/single with /companies/{id}/enrich
- Don't oversimplify signal explanation
- Don't skip polling/status check examples

**Recommended Agent Profile**:
- **Category**: `unspecified-high`
  - Reason: Requires understanding async patterns and drill-down logic
- **Skills**: None required

**Parallelization**:
- **Can Run In Parallel**: YES (with Tasks 2-3, 5)
- **Parallel Group**: Wave 2
- **Blocks**: Task 8 (cross-reference verification)
- **Blocked By**: Task 1 (needs complete inventory)

**References**:

**Code References**:
- `src/solstein/api/routers/async_jobs.py` — Async job endpoints
- `src/solstein/api/routers/drill_down.py` — Drill-down endpoints
- `src/solstein/api/main.py:37, 41` — Router registrations

**Documentation References**:
- `docs/api/reference.md` — Where to add documentation

**WHY Each Reference Matters**:
- async_jobs.py shows POST endpoints for starting jobs
- drill_down.py shows GET endpoints for detailed analysis
- main.py confirms routes are registered without prefix

**Acceptance Criteria**:

- [ ] All 6 async/drill-down endpoints documented
- [ ] Async endpoints show job status codes (pending, running, completed, failed)
- [ ] Examples show polling strategy for job completion
- [ ] Drill-down endpoints explain signal/source meaning
- [ ] All examples are real curl commands
- [ ] Response schemas match actual code

**QA Scenarios**:

```
Scenario: Async job endpoints show correct status codes
  Tool: Code + doc comparison
  Preconditions: Async endpoints documented
  Steps:
    1. Read async_jobs.py response models
    2. Check documentation lists all status codes
    3. Verify each status code is documented
    4. Verify examples show polling pattern
  Expected Result: Documentation shows all status codes and polling example
  Failure Indicators: Missing status codes, no polling example
  Evidence: .sisyphus/evidence/task-4-async-status.txt

Scenario: Drill-down endpoints document signal names
  Tool: Code + doc comparison
  Preconditions: Drill-down endpoints documented
  Steps:
    1. Find valid signal names in drill_down.py or tests
    2. Check documentation provides example signals
    3. Verify curl example uses valid signal name
  Expected Result: Documentation shows real signal names
  Failure Indicators: Missing signals, made-up signal names
  Evidence: .sisyphus/evidence/task-4-drill-down-signals.txt
```

**Commit**: YES
- Message: `docs(api): document async job and drill-down endpoints`
- Files: `docs/api/reference.md`
- Pre-commit: `grep -c "Async Operations\|Deep Dive" docs/api/reference.md`

---

### Task 5: Document Health & Export Endpoints

**What to do**:
- Use endpoint inventory from Task 1
- Document health.py endpoints:
  - GET / (health check, base path)
  - GET /status (full health status)
  - GET /ready (readiness probe from health.py)
- Document export endpoints:
  - GET /export/excel — Export Excel dashboard
  - GET /export/json — Export JSON data
  - GET /export/search/llm — LLM-powered search
- Document simulation endpoint:
  - POST /simulation/run — Run market simulation
- For each: path, method, parameters, response, example
- Add to "Health & Monitoring" and "Export" sections

**Must NOT do**:
- Don't duplicate /ready documentation (it's in two places)
- Don't confuse export methods
- Don't skip simulation parameters

**Recommended Agent Profile**:
- **Category**: `unspecified-high`
  - Reason: Requires careful documentation of multiple endpoint types
- **Skills**: None required

**Parallelization**:
- **Can Run In Parallel**: YES (with Tasks 2-4)
- **Parallel Group**: Wave 2
- **Blocks**: Task 8 (cross-reference verification)
- **Blocked By**: Task 1 (needs complete inventory)

**References**:

**Code References**:
- `src/solstein/api/routers/health.py` — Health endpoints
- `src/solstein/api/routers/export.py` — Export endpoints
- `src/solstein/api/routers/simulation.py` — Simulation endpoint
- `src/solstein/api/main.py:36, 38, 42` — Router registrations

**Documentation References**:
- `docs/api/reference.md` — Where to add documentation

**WHY Each Reference Matters**:
- health.py shows the "other" health endpoint implementation (not enrichment.py)
- export.py shows different export formats available
- simulation.py shows market simulation capabilities
- main.py shows registration with correct prefixes

**Acceptance Criteria**:

- [ ] All 7 health/export/simulation endpoints documented
- [ ] Health endpoints explain difference between status, ready, and root
- [ ] Export endpoints show available formats and use cases
- [ ] Simulation endpoint documents parameters and response
- [ ] Clear warning about /ready being defined in TWO routers
- [ ] All examples are real curl commands

**QA Scenarios**:

```
Scenario: Health endpoints disambiguate /ready implementation
  Tool: Code + doc comparison
  Preconditions: All health endpoints documented
  Steps:
    1. Read documentation of GET /ready
    2. Verify documentation notes TWO implementations (health.py, enrichment.py)
    3. Verify documentation explains which is actually used
    4. Verify curl examples work with actual routing
  Expected Result: Documentation clearly explains /ready routing
  Failure Indicators: No mention of dual implementation, confusing explanation
  Evidence: .sisyphus/evidence/task-5-ready-routing.txt

Scenario: Export endpoints show all formats
  Tool: Code + doc comparison
  Preconditions: Export endpoints documented
  Steps:
    1. Read export.py endpoints
    2. Check documentation lists all formats (excel, json, etc.)
    3. Verify examples show correct query parameters
    4. Verify response types match file formats
  Expected Result: Documentation shows all export formats
  Failure Indicators: Missing formats, wrong parameters
  Evidence: .sisyphus/evidence/task-5-export-formats.txt
```

**Commit**: YES
- Message: `docs(api): document health, export, and simulation endpoints`
- Files: `docs/api/reference.md`
- Pre-commit: `grep -c "Health & Monitoring\|Export\|Simulation" docs/api/reference.md`

---

### Task 6: Create Getting Started Guide

**What to do**:
- Create new file: `docs/guides/getting-started.md`
- Structure:
  1. **Welcome** — What Solstein is (1 paragraph)
  2. **Five-Minute Quickstart** — Run locally, hit /health
  3. **Recommended Reading Order** — Path for different audiences:
     - API users: Read this, then API reference
     - Developers: Read developer.md, then async-patterns.md
     - Operators: Read operator.md, then deployment guide
  4. **Key Concepts** — Score, classification, enrichment (links to other docs)
  5. **Next Steps** — Where to go from here (links to all guides)
  6. **Common Tasks** — Short links to how-tos:
     - How to score a company
     - How to enrich data
     - How to export results
     - How to deploy
- Cross-link to all guides
- Include TOC (table of contents)

**Must NOT do**:
- Don't repeat content from existing guides
- Don't create navigation that contradicts existing docs
- Don't omit any major guide or feature

**Recommended Agent Profile**:
- **Category**: `unspecified-high`
  - Reason: Requires understanding entire documentation structure, writing clear guidance
- **Skills**: None required

**Parallelization**:
- **Can Run In Parallel**: YES (with Task 7)
- **Parallel Group**: Wave 3
- **Blocks**: Task 8 (cross-reference verification)
- **Blocked By**: Task 1 (needs to understand all endpoints)

**References**:

**Documentation References** (all existing guides):
- `docs/guides/developer.md` — Developer setup
- `docs/guides/async-patterns.md` — Async/Celery patterns
- `docs/guides/operator.md` — Operations guide
- `docs/api/reference.md` — API reference (will be updated by Tasks 2-5)
- `docs/guides/health-checks.md` — Health probes
- `docs/guides/rate-limiting.md` — Rate limiting
- `docs/guides/retry-logic.md` — Retry patterns

**WHY Each Reference Matters**:
- Need to understand flow to create good reading order
- Need to know what each guide covers to guide readers correctly

**Acceptance Criteria**:

- [ ] File created: `docs/guides/getting-started.md`
- [ ] Includes welcome/intro section
- [ ] Includes quickstart (5 minutes)
- [ ] Includes recommended reading order for 3+ personas
- [ ] Includes key concepts with links
- [ ] Includes common tasks section
- [ ] All links point to correct files
- [ ] No markdown syntax errors

**QA Scenarios**:

```
Scenario: All internal links are valid
  Tool: Bash (grep + file verification)
  Preconditions: getting-started.md created
  Steps:
    1. Extract all markdown links from getting-started.md
    2. For each link [text](path):
       - Verify file at path exists
       - Verify anchor (#section) exists if specified
    3. Count broken links
  Expected Result: Zero broken links
  Failure Indicators: Any link to non-existent file or anchor
  Evidence: .sisyphus/evidence/task-6-link-validation.txt

Scenario: Reading order is logical and helps onboarding
  Tool: Manual review
  Preconditions: getting-started.md complete
  Steps:
    1. Follow "API user" reading path
    2. Verify: 1st doc → 2nd doc → API reference makes sense
    3. Follow "developer" path
    4. Verify: 1st doc → 2nd doc → async doc makes sense
  Expected Result: Each path is logical and complete
  Failure Indicators: Missing intermediate steps, confusing order
  Evidence: .sisyphus/evidence/task-6-reading-order.txt
```

**Commit**: YES
- Message: `docs(guides): add getting-started.md with recommended reading order`
- Files: `docs/guides/getting-started.md`
- Pre-commit: `test -f docs/guides/getting-started.md && echo "OK"`

---

### Task 7: Document Health Endpoint Routing

**What to do**:
- Create new file: `docs/architecture/health-endpoint-routing.md`
- Explain the problem: /ready and /health are defined in TWO routers
  - `health.py`: GET /, GET /status, GET /ready
  - `enrichment.py`: GET /health, GET /ready, GET /metrics
- Explain router registration in main.py:
  ```python
  app.include_router(enrichment.router)  # Registers /health, /ready, /metrics
  app.include_router(health.router)      # Registers /, /status, /ready (DUPLICATE!)
  ```
- Clarify which implementations are actually used
- Explain why this exists (historical reasons)
- Recommend which to use for new code
- Document all 3 health check types

**Must NOT do**:
- Don't suggest removing one implementation (that's code change, not doc)
- Don't oversimplify the routing problem
- Don't leave ambiguity about which is used

**Recommended Agent Profile**:
- **Category**: `quick`
  - Reason: Straightforward technical documentation
- **Skills**: None required

**Parallelization**:
- **Can Run In Parallel**: YES (with Task 6)
- **Parallel Group**: Wave 3
- **Blocks**: Task 8 (cross-reference verification)
- **Blocked By**: Task 1 (needs complete endpoint inventory)

**References**:

**Code References**:
- `src/solstein/api/routers/health.py` — Health router
- `src/solstein/api/routers/enrichment.py` — Enrichment router
- `src/solstein/api/main.py:35-42` — Router registration order

**Documentation References**:
- `docs/guides/health-checks.md` — How health probes are used

**WHY Each Reference Matters**:
- health.py and enrichment.py show the two implementations
- main.py shows registration order (determines which wins)
- health-checks.md shows how these are used operationally

**Acceptance Criteria**:

- [ ] File created: `docs/architecture/health-endpoint-routing.md`
- [ ] Explains the problem (duplicate endpoints)
- [ ] Shows router registration order from main.py
- [ ] Clarifies which implementation is actually used
- [ ] Documents all 3 endpoints clearly
- [ ] Recommends best practice for new code
- [ ] References health-checks.md for operational context

**QA Scenarios**:

```
Scenario: Routing explanation matches actual code
  Tool: Code + doc comparison
  Preconditions: routing doc created
  Steps:
    1. Read health-endpoint-routing.md explanation
    2. Read actual main.py router registration
    3. Verify explanation matches code order
    4. Verify which endpoint is said to "win"
  Expected Result: Explanation matches actual code
  Failure Indicators: Contradicts code, wrong registration order
  Evidence: .sisyphus/evidence/task-7-routing-accuracy.txt
```

**Commit**: YES
- Message: `docs(architecture): explain health endpoint routing conflict`
- Files: `docs/architecture/health-endpoint-routing.md`
- Pre-commit: `grep -c "@router" docs/architecture/health-endpoint-routing.md`

---

### Task 8: Cross-Reference Verification

**What to do**:
- Review all 6 updated/created documentation files
- For each file:
  - Extract all markdown links: `[text](path)`
  - Verify file at path exists
  - Verify anchor (#section) exists if specified
  - Check for dead links
- Create evidence file listing all verified links
- Flag any broken links for correction

**Must NOT do**:
- Don't fix broken links (just report them)
- Don't change documentation content
- Don't assume links work without verification

**Recommended Agent Profile**:
- **Category**: `deep`
  - Reason: Comprehensive verification across multiple files
- **Skills**: None required

**Parallelization**:
- **Can Run In Parallel**: NO (needs all docs complete)
- **Parallel Group**: Wave 4
- **Blocks**: Task 10 (final validation)
- **Blocked By**: Tasks 2-7 (all documentation tasks)

**References**:

**Documentation References** (all files to verify):
- `docs/api/reference.md` — Updated
- `docs/guides/getting-started.md` — New
- `docs/architecture/health-endpoint-routing.md` — New
- `docs/guides/health-checks.md` — Updated
- `docs/guides/async-patterns.md` — Updated
- `docs/guides/developer.md` — Updated

**WHY Each Reference Matters**:
- Need to verify all cross-references are correct
- Broken links break navigation

**Acceptance Criteria**:

- [ ] All markdown links verified
- [ ] Zero broken links to non-existent files
- [ ] Zero broken anchors (#sections)
- [ ] Evidence file documents all verified links
- [ ] No false positives (links that look broken but aren't)

**QA Scenarios**:

```
Scenario: All internal links point to existing files
  Tool: Bash (grep + file test)
  Preconditions: All 6 docs completed
  Steps:
    1. Extract all [text](path) links from docs
    2. For each link, test: test -f path
    3. Report any failures
  Expected Result: All files exist
  Failure Indicators: test -f returns false for any link
  Evidence: .sisyphus/evidence/task-8-link-verification.txt
```

**Commit**: NO (verification only)
- Evidence: `.sisyphus/evidence/task-8-cross-ref-verification.txt`

---

### Task 9: Example Verification

**What to do**:
- Review all curl examples in updated API reference
- For each curl example:
  - Extract command
  - Verify endpoint path matches actual route
  - Verify method (GET/POST) matches route
  - Verify query parameters (if any) are documented in code
  - Test command format (check syntax)
- Create evidence file documenting verified examples
- Flag any incorrect examples

**Must NOT do**:
- Don't execute curl commands (just verify syntax)
- Don't modify examples
- Don't assume examples are correct

**Recommended Agent Profile**:
- **Category**: `unspecified-high`
  - Reason: Requires code understanding and example verification
- **Skills**: None required

**Parallelization**:
- **Can Run In Parallel**: NO (needs all API docs complete)
- **Parallel Group**: Wave 4
- **Blocks**: Task 10 (final validation)
- **Blocked By**: Tasks 2-5 (all API documentation tasks)

**References**:

**Code References**:
- All router files in `src/solstein/api/routers/` — For endpoint verification

**Documentation References**:
- `docs/api/reference.md` — Where examples are

**WHY Each Reference Matters**:
- Need to verify examples match actual endpoints
- Broken examples waste developer time

**Acceptance Criteria**:

- [ ] All curl examples verified (50+ examples)
- [ ] Each example has correct endpoint path
- [ ] Each example has correct HTTP method
- [ ] Query parameters match code
- [ ] Syntax is valid (no typos in command)
- [ ] Evidence documents all examples verified

**QA Scenarios**:

```
Scenario: Curl examples have correct endpoints and methods
  Tool: Bash (grep) + code comparison
  Preconditions: API reference complete
  Steps:
    1. Extract all curl commands from API reference
    2. For each command, check:
       - Is endpoint path in that router file? (grep for path in code)
       - Is method correct? (grep for @router.method)
       - Are query parameters documented? (grep function signature)
  Expected Result: All examples match actual code
  Failure Indicators: Endpoint not found, wrong method, undocumented params
  Evidence: .sisyphus/evidence/task-9-example-verification.txt
```

**Commit**: NO (verification only)
- Evidence: `.sisyphus/evidence/task-9-examples-verified.txt`

---

### Task 10: Final Index Update & Validation

**What to do**:
- Update `docs/DOCUMENTATION_INDEX.md`:
  - Add entry for `docs/guides/getting-started.md`
  - Add entry for `docs/architecture/health-endpoint-routing.md`
  - Mark which docs are "Required Reading" vs "Reference"
  - Update API reference entry to note: "Now includes all 42 endpoints"
- Run final verification:
  - Confirm all 69 doc files still exist
  - Confirm no files broken in updates
  - Confirm markdown syntax valid in new files
- Create final validation report

**Must NOT do**:
- Don't remove any documentation
- Don't break existing links
- Don't make content changes (only index updates)

**Recommended Agent Profile**:
- **Category**: `quick`
  - Reason: Final validation and index updates
- **Skills**: None required

**Parallelization**:
- **Can Run In Parallel**: NO (final task)
- **Parallel Group**: Wave 4
- **Blocks**: COMPLETION
- **Blocked By**: Tasks 8-9 (all verification)

**References**:

**Documentation References**:
- `docs/DOCUMENTATION_INDEX.md` — Index to update
- All 69 documentation files (verify existence)

**WHY Each Reference Matters**:
- Index is developers' entry point
- Need to ensure all files still accessible

**Acceptance Criteria**:

- [ ] DOCUMENTATION_INDEX.md updated with new guides
- [ ] "Required Reading" vs "Reference" sections clear
- [ ] API reference entry updated (all 42 endpoints now)
- [ ] All 69 documentation files verified to exist
- [ ] No markdown syntax errors in new files
- [ ] Final validation report generated

**QA Scenarios**:

```
Scenario: All 69 documentation files still accessible
  Tool: Bash (find + wc)
  Preconditions: All updates complete
  Steps:
    1. Find all *.md files in docs/
    2. Count total (should be 69)
    3. Verify none are missing/broken
    4. Spot-check 10 random files for readability
  Expected Result: All 69 files present and readable
  Failure Indicators: Count != 69, files unreadable
  Evidence: .sisyphus/evidence/task-10-doc-inventory.txt

Scenario: New markdown files have valid syntax
  Tool: Bash (markdown linter if available, or manual check)
  Preconditions: getting-started.md and health-endpoint-routing.md created
  Steps:
    1. Check markdown syntax in getting-started.md
    2. Check markdown syntax in health-endpoint-routing.md
    3. Verify no unclosed code blocks, bad headings, etc.
  Expected Result: All markdown valid
  Failure Indicators: Syntax errors detected
  Evidence: .sisyphus/evidence/task-10-markdown-syntax.txt
```

**Commit**: YES
- Message: `docs: complete API reference (all 42 endpoints) and add getting started guide`
- Files: `docs/DOCUMENTATION_INDEX.md`, `docs/api/reference.md`, `docs/guides/getting-started.md`, `docs/architecture/health-endpoint-routing.md`
- Pre-commit: `find docs -name "*.md" | wc -l`

---

## Final Verification Wave

> 2 parallel verification tasks run after ALL implementation tasks

- [ ] **F1. Documentation Completeness Audit** — `deep`
  Read every updated/created documentation file. For each endpoint in API reference, verify it's real (exists in code). For getting-started.md, verify all links work. For health-endpoint-routing.md, verify explanation matches code.
  Output: `Documentation complete | Endpoints [42/42] | Links [N valid/N total] | VERDICT: APPROVE/REJECT`

- [ ] **F2. Navigation & Usability Check** — `unspecified-high`
  Follow the three reading paths in getting-started.md (API user, developer, operator). Verify each path makes sense and has all needed information. Check that cross-references guide readers correctly. Verify no dead ends.
  Output: `Paths tested [3/3] | Dead ends [0] | Clarity [good/fair/poor] | VERDICT`

---

## Commit Strategy

**Structure**: 5 commits (one per major change category) + 1 final summary

1. **Commit 1** (Task 1)
   - `docs(api): create complete inventory of 42 endpoints`
   - 1 file (inventory only, internal)

2. **Commit 2** (Tasks 2-5)
   - `docs(api): document all 42 API endpoints comprehensively`
   - 1 file: `docs/api/reference.md`

3. **Commit 3** (Task 6)
   - `docs(guides): add getting-started.md with recommended reading order`
   - 1 file: `docs/guides/getting-started.md`

4. **Commit 4** (Task 7)
   - `docs(architecture): explain health endpoint routing conflict`
   - 1 file: `docs/architecture/health-endpoint-routing.md`

5. **Commit 5** (Task 10)
   - `docs: complete API reference update and navigation improvements`
   - 1 file: `docs/DOCUMENTATION_INDEX.md`

---

## Success Criteria

### Verification Commands
```bash
# Verify endpoint count
grep -c "#### GET\|#### POST\|#### DELETE" docs/api/reference.md
# Expected: 42+ endpoint sections

# Verify new guides exist
test -f docs/guides/getting-started.md && echo "getting-started: OK"
test -f docs/architecture/health-endpoint-routing.md && echo "routing: OK"

# Verify documentation index updated
grep "getting-started\|health-endpoint-routing" docs/DOCUMENTATION_INDEX.md | wc -l
# Expected: 2 references
```

### Final Checklist
- [ ] All 42 endpoints documented in API reference
- [ ] Getting started guide created with reading order
- [ ] Health endpoint routing explained
- [ ] All internal links verified
- [ ] All curl examples verified
- [ ] Documentation index updated
- [ ] All commits follow conventional commits format
- [ ] No files broken or removed
- [ ] No markdown syntax errors

---

## Notes for Executor

### What This Plan Does
1. Documents all 42 API endpoints (currently only 11 documented)
2. Creates developer onboarding guide with recommended reading order
3. Explains the health endpoint routing conflict
4. Verifies all examples and links are correct

### What This Plan Does NOT Do
- ❌ Change code (only documentation)
- ❌ Modify routing (just explains it)
- ❌ Consolidate duplicate implementations

### Critical Success Factor
**Task 1 must complete first** — the endpoint inventory is the foundation for all documentation tasks. All other tasks depend on knowing ALL 42 endpoints exist.

### Time Estimate
- Wave 1 (Task 1): 10 minutes (inventory)
- Wave 2 (Tasks 2-5): 60-75 minutes (parallel, ~30-40 wall clock minutes)
- Wave 3 (Tasks 6-7): 15-20 minutes (parallel)
- Wave 4 (Tasks 8-10): 15-20 minutes (sequential)
- **Total: 100-125 minutes (~70-80 minutes wall clock time)**

### If Anything Breaks
- Check that endpoint paths include correct prefixes from main.py
- Verify curl examples use exact endpoint paths (with prefixes)
- Ensure all links use correct relative paths (../guides/, etc.)
- Validate that health endpoint routing explanation matches code

---

**Status**: 🟡 READY FOR EXECUTION  
**Complexity**: Medium-Large  
**Parallelism**: High (Waves 2 & 3)  
**Risk**: Low (documentation only, no code changes)
