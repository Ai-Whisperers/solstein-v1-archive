# EPIC-020: God Function Refactoring - Work Plan

> **Epic:** God Function Breakdown and Refactoring  
> **Points:** 194  
> **Status:** IN PROGRESS  
> **Created:** 2026-03-06  

---

## Overview

Systematically break down all 108 functions exceeding 50 lines into smaller, testable, maintainable units. Priority on the 24 god functions (>100 lines).

### Current State
- **24 God Functions** (>100 lines) 🔴 CRITICAL
- **84 Long Functions** (50-100 lines) 🟡 HIGH
- **Total:** 108 functions needing breakdown

### Goals
- [ ] Zero functions >100 lines remaining
- [ ] All functions <50 lines (ideal) or <100 lines (acceptable)
- [ ] Improved testability (each function does one thing)
- [ ] Reduced cognitive load for developers

### Success Metrics
- Code smell density reduced by 50%
- Test coverage increased to 80%+
- Average function length: <30 lines

---

## Worst Offenders (Top 14 God Functions)

| Rank | Function | Lines | Params | File | Priority |
|------|----------|-------|--------|------|----------|
| 1 | `run_market_intelligence` | 505 | 11 | `research/pipeline.py:27` | P0 |
| 2 | `_convert_to_domain_company` | 429 | 3 | `data/loaders.py:99` | P0 |
| 3 | `_catalog_for_market` | 429 | 1 | `research/discovery.py:39` | P0 |
| 4 | `_generate_competitive_analysis` | 225 | 4 | `exporters/markdown/generator.py:901` | P1 |
| 5 | `persist_research_run_records` | 198 | 10 | `infrastructure/research_dual_write.py:274` | P1 |
| 6 | `build_company_profile` | 188 | 1 | `research/gather.py:81` | P1 |
| 7 | `fill_nulls_from_sec_edgar` | 175 | 2 | `data/unified_loader.py:643` | P1 |
| 8 | `reconcile_research_run` | 170 | 3 | `infrastructure/reconcile_runs.py:84` | P1 |
| 9 | `_get_client` (enhanced_client) | 163 | 1 | `llm/enhanced_client.py:73` | P1 |
| 10 | `enrich_company` | 153 | 2 | `data/enrichment_service.py:231` | P1 |
| 11 | `_get_client` (health_checker) | 153 | 1 | `llm/health_checker.py:175` | P1 |
| 12 | `build_company_from_signals` | 151 | 3 | `research/gather.py:496` | P1 |
| 13 | `fill_nulls_from_companies_house` | 150 | 2 | `data/unified_loader.py:820` | P1 |
| 14 | `score` (growth_momentum) | 148 | 4 | `analytics/scorers/growth_momentum.py:24` | P1 |

---

## Task Breakdown

### Phase 1: Top 3 God Functions (P0) - 29 points

#### Task 1: Break Down run_market_intelligence (505 lines) - 13 pts
**File:** `src/solstein/research/pipeline.py:27`

**Current:**
```python
def run_market_intelligence(...):
    # 505 lines handling discovery, enrichment, validation, scoring, analysis, export
```

**Target:**
```python
class ResearchPipeline:
    def __init__(self, config: PipelineConfig):
        self.stages = [
            DiscoveryStage(),
            EnrichmentStage(),
            ValidationStage(),
            ScoringStage(),
            AnalysisStage(),
            ExportStage(),
        ]
    
    async def execute(self, context: PipelineContext) -> PipelineResult:
        for stage in self.stages:
            await stage.execute(context)
        return context.result
```

**Acceptance Criteria:**
- [ ] Extracted into 6+ stage classes
- [ ] Each stage <100 lines
- [ ] Full test coverage for each stage
- [ ] Integration tests for pipeline
- [ ] Documentation updated

**Parallelizable:** NO (foundational)
**Dependencies:** None

---

#### Task 2: Break Down _convert_to_domain_company (429 lines) - 8 pts
**File:** `src/solstein/data/loaders.py:99`

**Current:**
```python
def _convert_to_domain_company(raw_data, folder, config):
    # 429 lines of field mapping
```

**Target:**
```python
class CompanyConverter:
    def __init__(self):
        self.mappers = {
            'financials': FinancialFieldMapper(),
            'metadata': MetadataFieldMapper(),
            'scores': ScoreFieldMapper(),
            'timeline': TimelineFieldMapper(),
        }
    
    def convert(self, raw_data: dict, folder: str) -> Company:
        company = Company()
        for mapper in self.mappers.values():
            mapper.map(raw_data, company)
        return company
```

**Acceptance Criteria:**
- [ ] 4-6 mapper classes created
- [ ] Each mapper <80 lines
- [ ] Unit tests for each mapper
- [ ] No regression in data conversion

**Parallelizable:** YES (independent of Task 1)
**Dependencies:** None

---

#### Task 3: Break Down _catalog_for_market (429 lines) - 8 pts
**File:** `src/solstein/research/discovery.py:39`

**Current:** Discovery logic monolith

**Target:**
```python
class DiscoveryEngine:
    def __init__(self):
        self.strategies = [
            KnownCompanyStrategy(),
            NewsSearchStrategy(),
            WebSearchStrategy(),
            CompetitorAnalysisStrategy(),
        ]
    
    async def discover(self, market: str) -> list[DiscoveryCandidate]:
        candidates = []
        for strategy in self.strategies:
            candidates.extend(await strategy.discover(market))
        return self.deduplicate(candidates)
```

**Acceptance Criteria:**
- [ ] Strategy pattern implemented
- [ ] Each strategy <100 lines
- [ ] Unit tests for each strategy
- [ ] Deduplication logic extracted

**Parallelizable:** YES (independent)
**Dependencies:** None

---

### Phase 2: Next 11 God Functions (P1) - 55 points

#### Task 4: Break Down _generate_competitive_analysis (225 lines) - 5 pts
**File:** `src/solstein/exporters/markdown/generator.py:901`

**Acceptance Criteria:**
- [ ] Extract into 3-5 smaller functions
- [ ] Create helper classes if needed
- [ ] Add unit tests
- [ ] Maintain backward compatibility

**Parallelizable:** YES
**Dependencies:** None

---

#### Task 5: Break Down persist_research_run_records (198 lines) - 5 pts
**File:** `src/solstein/infrastructure/research_dual_write.py:274`

**Acceptance Criteria:**
- [ ] Extract persistence logic into smaller methods
- [ ] Separate dual-write coordination from persistence
- [ ] Add unit tests
- [ ] Maintain backward compatibility

**Parallelizable:** YES
**Dependencies:** None

---

#### Task 6: Break Down build_company_profile (188 lines) - 5 pts
**File:** `src/solstein/research/gather.py:81`

**Acceptance Criteria:**
- [ ] Extract profile building steps into methods
- [ ] Create ProfileBuilder class
- [ ] Add unit tests
- [ ] Maintain backward compatibility

**Parallelizable:** YES
**Dependencies:** None

---

#### Task 7: Break Down fill_nulls_from_sec_edgar (175 lines) - 5 pts
**File:** `src/solstein/data/unified_loader.py:643`

**Acceptance Criteria:**
- [ ] Reduce nesting levels (currently 29)
- [ ] Extract field mapping logic
- [ ] Add unit tests
- [ ] Maintain backward compatibility

**Parallelizable:** YES
**Dependencies:** None

---

#### Task 8: Break Down reconcile_research_run (170 lines) - 5 pts
**File:** `src/solstein/infrastructure/reconcile_runs.py:84`

**Acceptance Criteria:**
- [ ] Extract reconciliation steps
- [ ] Create ReconciliationEngine class
- [ ] Add unit tests
- [ ] Maintain backward compatibility

**Parallelizable:** YES
**Dependencies:** None

---

#### Task 9: Break Down _get_client (enhanced_client) (163 lines) - 5 pts
**File:** `src/solstein/llm/enhanced_client.py:73`

**Acceptance Criteria:**
- [ ] Simplify client initialization
- [ ] Extract provider configuration
- [ ] Add unit tests
- [ ] Maintain backward compatibility

**Parallelizable:** YES
**Dependencies:** None

---

#### Task 10: Break Down enrich_company (153 lines) - 5 pts
**File:** `src/solstein/data/enrichment_service.py:231`

**Acceptance Criteria:**
- [ ] Extract enrichment steps
- [ ] Create EnrichmentOrchestrator methods
- [ ] Add unit tests
- [ ] Maintain backward compatibility

**Parallelizable:** YES
**Dependencies:** None

---

#### Task 11: Break Down _get_client (health_checker) (153 lines) - 5 pts
**File:** `src/solstein/llm/health_checker.py:175`

**Acceptance Criteria:**
- [ ] Deduplicate logic with enhanced_client version
- [ ] Extract health check logic
- [ ] Add unit tests
- [ ] Maintain backward compatibility

**Parallelizable:** YES
**Dependencies:** None (but consider merging with Task 9)

---

#### Task 12: Break Down build_company_from_signals (151 lines) - 5 pts
**File:** `src/solstein/research/gather.py:496`

**Acceptance Criteria:**
- [ ] Extract signal processing logic
- [ ] Create SignalProcessor class
- [ ] Add unit tests
- [ ] Maintain backward compatibility

**Parallelizable:** YES
**Dependencies:** None

---

#### Task 13: Break Down fill_nulls_from_companies_house (150 lines) - 5 pts
**File:** `src/solstein/data/unified_loader.py:820`

**Acceptance Criteria:**
- [ ] Reduce nesting levels (currently 25)
- [ ] Extract field mapping logic
- [ ] Add unit tests
- [ ] Maintain backward compatibility

**Parallelizable:** YES
**Dependencies:** None

---

#### Task 14: Break Down score (growth_momentum) (148 lines) - 5 pts
**File:** `src/solstein/analytics/scorers/growth_momentum.py:24`

**Acceptance Criteria:**
- [ ] Extract scoring sub-calculations
- [ ] Create GrowthScorer class with methods
- [ ] Add unit tests
- [ ] Maintain backward compatibility

**Parallelizable:** YES
**Dependencies:** None

---

### Phase 3: 50-100 Line Functions (Priority Batch 1) - 30 points

Top 10 functions by lines:

| Function | Lines | File |
|----------|-------|------|
| `_parse_valuation` | 99 | `data/loaders.py:601` |
| `_aggregate_numeric_fact` | 96 | `research/aggregate.py:397` |
| `persist_research_run` | 96 | `infrastructure/research_dual_write.py:475` |
| `evaluate` | 92 | `data/report_release_gate.py:53` |
| `fetch_filing` | 92 | `data/connectors/sec_edgar_connector.py:75` |
| `display_confidence_report` | 90 | `analytics/classification.py:264` |
| `attach_news_signals` | 89 | `data/unified_loader.py:972` |
| `generate_financial_growth` | 89 | `exporters/markdown/generator.py:402` |
| `enrich_companies_batch_async` | 82 | `worker_tasks.py:820` |
| `_discover_legacy` | 82 | `research/discovery.py:571` |

Each task: 3 points

**Parallelizable:** YES (all independent)
**Dependencies:** None

---

### Phase 4: Remaining Long Functions (50-100 lines) - 80 points

Remaining 74 functions in batches of 10.

Each batch: 10-20 points

**Parallelizable:** YES
**Dependencies:** Previous phases complete

---

## Technical Approach

### Refactoring Patterns

1. **Extract Method:** Break large functions into smaller, focused methods
2. **Replace Method with Method Object:** Convert complex functions to classes
3. **Strategy Pattern:** Use polymorphism for variant behaviors

### Testing Strategy

- Maintain existing behavior (golden tests)
- Add unit tests for extracted functions
- Add integration tests at boundary
- Performance regression testing

---

## Risks and Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking changes | Comprehensive test suite, feature flags |
| Time overrun | Prioritize by impact, incremental delivery |
| Merge conflicts | Small PRs, clear ownership |
| Performance regression | Benchmark before/after |

---

## Definition of Done

- [ ] All 24 god functions broken down
- [ ] All 84 long functions broken down
- [ ] No functions >100 lines remain
- [ ] Test coverage >80% for refactored code
- [ ] Performance benchmarks maintained
- [ ] Documentation updated

---

## Estimated Effort

| Phase | Points | Duration (1 dev) |
|-------|--------|------------------|
| Phase 1 (Stories 1-3) | 29 | 3 weeks |
| Phase 2 (Stories 4-14) | 55 | 6 weeks |
| Phase 3 (Stories 15-24) | 30 | 3 weeks |
| Phase 4 (Stories 25-64) | 80 | 8 weeks |
| **Total** | **194** | **20 weeks** |

---

## Dependencies

- EPIC-019 (Automated detection) - For monitoring
- EPIC-012 (Testing) - For test coverage

---

## Notepad Structure

```
.sisyphus/notepads/epic-020-god-function-refactoring/
├── learnings.md      # Conventions, patterns discovered
├── decisions.md      # Architectural decisions
├── issues.md         # Problems encountered
└── problems.md       # Unresolved blockers
```

---

*Created: 2026-03-06*  
*Based on: COMPLETE_CODE_SMELLS_FULL_ANALYSIS.md*
