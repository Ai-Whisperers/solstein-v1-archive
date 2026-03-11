# Epic: God Function Breakdown and Refactoring (EPIC-020)

## Overview
Systematically break down all 108 functions exceeding 50 lines into smaller, testable, maintainable units. Priority on the 24 god functions (>100 lines).

## Current State
- 24 God Functions (>100 lines)
- 84 Long Functions (50-100 lines)
- Total: 108 functions needing breakdown

## Worst Offenders
1. `run_market_intelligence` - 505 lines, 11 params
2. `_convert_to_domain_company` - 429 lines, 3 params
3. `_catalog_for_market` - 429 lines, 1 param
4. `_generate_competitive_analysis` - 225 lines, 4 params
5. `persist_research_run_records` - 198 lines, 10 params

## Goals
- [ ] Zero functions >100 lines remaining
- [ ] All functions <50 lines (ideal) or <100 lines (acceptable)
- [ ] Improved testability (each function does one thing)
- [ ] Reduced cognitive load for developers

## Success Metrics
- Code smell density reduced by 50%
- Test coverage increased to 80%+
- Average function length: <30 lines

---

## Stories

### Story 1: Break Down run_market_intelligence (505 lines)
**Points:** 13
**Priority:** P0

Refactor the 505-line research pipeline function into stage classes.

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

### Story 2: Break Down _convert_to_domain_company (429 lines)
**Points:** 8
**Priority:** P0

Refactor the 429-line conversion function into field mapper classes.

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

### Story 3: Break Down _catalog_for_market (429 lines)
**Points:** 8
**Priority:** P0

Refactor discovery logic into strategy pattern.

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

### Story 4-14: Break Down Next 11 God Functions (100-225 lines)
**Points:** 5 each
**Priority:** P1

Functions to refactor:
4. `_generate_competitive_analysis` (225 lines)
5. `persist_research_run_records` (198 lines)
6. `build_company_profile` (188 lines)
7. `fill_nulls_from_sec_edgar` (175 lines)
8. `reconcile_research_run` (170 lines)
9. `_get_client` (enhanced_client) (163 lines)
10. `enrich_company` (153 lines)
11. `_get_client` (health_checker) (153 lines)
12. `build_company_from_signals` (151 lines)
13. `fill_nulls_from_companies_house` (150 lines)
14. `score` (growth_momentum) (148 lines)

**Pattern for each:**
- Extract into 3-5 smaller functions
- Create helper classes if needed
- Add unit tests
- Maintain backward compatibility

### Story 15-24: Break Down 50-100 Line Functions (Priority Batch 1)
**Points:** 3 each
**Priority:** P1

Top 10 functions by lines:
- `_parse_valuation` (99 lines)
- `_aggregate_numeric_fact` (96 lines)
- `persist_research_run` (96 lines)
- `evaluate` (report_release_gate) (92 lines)
- `fetch_filing` (92 lines)
- `display_confidence_report` (90 lines)
- `attach_news_signals` (89 lines)
- `generate_financial_growth` (89 lines)
- `enrich_companies_batch_async` (82 lines)
- `_discover_legacy` (82 lines)

### Story 25-64: Remaining Long Functions (50-100 lines)
**Points:** 2 each
**Priority:** P2

Remaining 74 functions in batches of 10.

---

## Technical Approach

### Refactoring Patterns

1. **Extract Method:**
```python
# Before
def big_function():
    # 100 lines of code
    
# After
def big_function():
    self.step_one()
    self.step_two()
    self.step_three()

def step_one(self): ...
def step_two(self): ...
def step_three(self): ...
```

2. **Replace Method with Method Object:**
```python
# Before
def complex_calculation(param1, param2, param3):
    # Uses many local variables
    
# After
class ComplexCalculation:
    def __init__(self, param1, param2, param3):
        self.param1 = param1
        self.param2 = param2
        self.param3 = param3
    
    def compute(self):
        # Now instance variables, not locals
```

3. **Strategy Pattern:**
```python
# Before
def process(data, type):
    if type == "A": ...
    elif type == "B": ...
    
# After
class ProcessorA: ...
class ProcessorB: ...

processor = self.get_processor(type)
processor.process(data)
```

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

## Estimated Effort
- **Stories 1-3:** 29 points (3 weeks)
- **Stories 4-14:** 55 points (6 weeks)
- **Stories 15-24:** 30 points (3 weeks)
- **Stories 25-64:** 80 points (8 weeks)
- **Total:** 194 points (20 weeks with 1 developer)

## Dependencies
- EPIC-019 (Automated detection) - For monitoring
- EPIC-012 (Testing) - For test coverage

---

*Created: 2026-03-06*  
*Based on: COMPLETE_CODE_SMELLS_FULL_ANALYSIS.md*
