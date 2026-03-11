# Epic: God Class Breakdown (EPIC-022) - UPDATED v2.0

## Overview
Refactor 19 god classes (>300 lines or >15 methods) into smaller, cohesive classes following Single Responsibility Principle.

**Status:** 🔄 Ready for Implementation  
**Dependencies:** EPIC-020 (COMPLETE), EPIC-021  
**Last Updated:** 2026-03-06

---

## Current State - UPDATED

### Before Any Work:
- ❌ 19 God Classes identified
- ❌ Worst: `UnifiedCompanyLoader` at 878 lines, 14 methods
- ❌ `ReportGenerator` at 848 lines, 31 methods

### After EPIC-020 (God Functions):
- 🔄 **RE-ASSESSMENT NEEDED:** Function extraction may have reduced class sizes
- ✅ **HELPER MODULES CREATED:** 10 modules that can become extracted classes
- ✅ **PATTERNS ESTABLISHED:** Extract Method, Strategy, Builder patterns

### Updated Class Inventory:

| Class | Lines | Methods | EPIC-020 Impact | New Status |
|-------|-------|---------|-----------------|------------|
| `UnifiedCompanyLoader` | 878 | 14 | Helpers extracted | 🔴 Still needs work |
| `ReportGenerator` | 848 | 31 | Sections extracted | 🟡 May be reduced |
| `CompetitorDataLoader` | 788 | 14 | Extractors created | 🟡 May be reduced |
| `GitHubAgent` | 755 | 12 | None | 🔴 Still needs work |
| `ProviderHealthChecker` | 595 | 14 | Strategies extracted | 🟡 Likely reduced |
| `AdditionalDataSources` | 605 | ? | None | 🔴 Still needs work |
| `EnhancedLLMClient` | 532 | ? | Strategies extracted | 🟡 Likely reduced |
| `SignalDefinitions` | 454 | ? | None | 🔴 Still needs work |
| `HealthMonitor` | 436 | ? | None | 🔴 Still needs work |
| `EnrichmentOrchestrator` | 413 | ? | Executors extracted | 🟡 Likely reduced |
| `ImprovedExcelExporter` | 408 | ? | None | 🔴 Still needs work |
| `Company` domain model | 407 | ? | Builders extracted | 🟡 May be reduced |
| `ClientReportGenerator` | 391 | ? | None | 🔴 Still needs work |
| `LLMReportEnhancer` | 388 | ? | None | 🔴 Still needs work |
| `IdentifierLookupService` | 379 | ? | None | 🔴 Still needs work |
| `NewsSignalDetector` | 333 | ? | None | 🔴 Still needs work |
| `MarkdownExtractor` | 332 | ? | None | 🔴 Still needs work |
| `CoordinatorAgent` | 320 | ? | None | 🔴 Still needs work |
| `CompanyReportGenerator` | 311 | ? | None | 🔴 Still needs work |

**Action Required:** Re-measure all classes after EPIC-020 before starting work.

---

## Goals
- [ ] Zero classes >300 lines remaining
- [ ] No class with >15 methods
- [ ] Clear responsibilities per class
- [ ] Improved testability
- [ ] Reduced cognitive load
- [ ] **NEW:** Use EPIC-020 helper modules as extracted classes
- [ ] **NEW:** Apply Strategy pattern consistently

---

## Stories - UPDATED

### Story 0: Re-assess Class Sizes ⭐ NEW - MUST DO FIRST
**Points:** 3  
**Priority:** P0  
**Status:** 🟡 READY

Re-measure all 19 classes after EPIC-020 function extraction:

**Tasks:**
- [ ] Run code analysis on all 19 classes
- [ ] Document new line counts
- [ ] Document new method counts
- [ ] Identify which classes are now under limits
- [ ] Update story priorities based on findings
- [ ] Mark stories as complete if classes now compliant

**Acceptance Criteria:**
- [ ] All 19 classes re-measured
- [ ] Updated inventory in this epic
- [ ] Stories updated/closed as appropriate
- [ ] Work effort recalculated

---

### Story 1: Break Down UnifiedCompanyLoader (878 lines)
**Points:** 8  
**Priority:** P0  
**Status:** 🔴 NOT STARTED (pending re-assessment)

Split the 878-line unified loader into focused loaders.

**Current:**
```python
class UnifiedCompanyLoader:
    # 878 lines handling multiple data sources
    def load_from_sec_edgar(self): ...
    def load_from_companies_house(self): ...
    def load_from_linkedin(self): ...
    def merge_data(self): ...
    def validate_data(self): ...
    # 9 more methods...
```

**Target:**
```python
class UnifiedCompanyLoader:
    """Orchestrates multiple data source loaders."""
    def __init__(self):
        self.loaders = {
            'sec_edgar': SecEdgarLoader(),  # Uses EPIC-020 helpers
            'companies_house': CompaniesHouseLoader(),
            'linkedin': LinkedInLoader(),
        }
        self.merger = DataMerger()  # Uses reconciliation_helpers
        self.validator = DataValidator()
    
    def load(self, company_id: str) -> Company:
        data = {}
        for source, loader in self.loaders.items():
            data[source] = loader.load(company_id)
        merged = self.merger.merge(data)
        return self.validator.validate(merged)
```

**EPIC-020 Assets to Use:**
- `sec_edgar_helpers.py` → `SecEdgarLoader` class
- `enrichment_executors.py` → `CompaniesHouseLoader`, `LinkedInLoader`
- `reconciliation_helpers.py` → `DataMerger` class

**Acceptance Criteria:**
- [ ] 4-6 loader classes extracted
- [ ] `DataMerger` class created (uses EPIC-020 helpers)
- [ ] `DataValidator` class created
- [ ] Each class <200 lines
- [ ] Full test coverage
- [ ] No regression in functionality

---

### Story 2: Break Down ReportGenerator (848 lines)
**Points:** 8  
**Priority:** P0  
**Status:** 🔴 NOT STARTED (pending re-assessment)

Split the 848-line, 31-method report generator.

**Target Structure:**
```python
class ReportGenerator:
    """Orchestrates report generation."""
    def __init__(self):
        self.sections = {
            'executive': ExecutiveSummaryGenerator(),  # EPIC-020
            'financial': FinancialSectionGenerator(),  # EPIC-020
            'competitive': CompetitiveAnalysisGenerator(),  # EPIC-020
            'market': MarketOverviewGenerator(),
        }
        self.formatter = MarkdownFormatter()
        self.template = ReportTemplate()
```

**EPIC-020 Assets to Use:**
- `report_sections.py` → Section generator classes
- `market_catalogs.py` → Market overview data

**Acceptance Criteria:**
- [ ] 6-8 section generator classes extracted
- [ ] Each generator <150 lines
- [ ] Main generator <200 lines
- [ ] Uses EPIC-020 section generators
- [ ] All report types still work

---

### Story 3: Break Down CompetitorDataLoader (788 lines)
**Points:** 5  
**Priority:** P1  
**Status:** 🔴 NOT STARTED (pending re-assessment)

Extract field mappers and loading strategies.

**EPIC-020 Assets to Use:**
- `company_extractors.py` → Field mapper classes
- `company_builder.py` → Builder classes

**Target:**
```python
class CompetitorDataLoader:
    def __init__(self):
        self.mappers = {
            'financials': FinancialFieldMapper(),  # EPIC-020
            'metadata': MetadataFieldMapper(),
            'scores': ScoreFieldMapper(),
        }
        self.builder = CompanyBuilder()  # EPIC-020
```

**Acceptance Criteria:**
- [ ] 4-6 mapper classes extracted
- [ ] Builder pattern applied
- [ ] Each class <200 lines
- [ ] Uses EPIC-020 extractors

---

### Story 4: Break Down GitHubAgent (755 lines)
**Points:** 5  
**Priority:** P1  
**Status:** 🔴 NOT STARTED (pending re-assessment)

Extract analyzers and scanners.

**Target Structure:**
```python
class GitHubAgent:
    """Orchestrates GitHub analysis."""
    def __init__(self):
        self.analyzers = {
            'repository': RepositoryAnalyzer(),
            'security': SecurityScanner(),
            'activity': ActivityAnalyzer(),
        }
        self.client = GitHubAPIClient()
```

**Acceptance Criteria:**
- [ ] 3-4 analyzer classes extracted
- [ ] API client separated
- [ ] Each class <200 lines
- [ ] Strategy pattern for analyzers

---

### Story 5: Break Down ProviderHealthChecker (595 lines)
**Points:** 5 → **REDUCED to 3**  
**Priority:** P1  
**Status:** 🟡 PARTIALLY DONE (EPIC-020)

**EPIC-020 Progress:**
- ✅ Strategies extracted to `provider_strategies.py`

**Remaining Work:**
- Extract metrics collection
- Extract health check orchestration
- Create clean class structure

**Target:**
```python
class ProviderHealthChecker:
    """Orchestrates provider health checks."""
    def __init__(self):
        self.strategies = ProviderStrategyFactory()  # EPIC-020
        self.metrics = HealthMetricsCollector()
        self.monitor = HealthMonitor()
```

**Acceptance Criteria:**
- [ ] Uses EPIC-020 provider strategies
- [ ] Metrics collection extracted
- [ ] Main class <200 lines
- [ ] Each component <150 lines

---

### Story 6: Break Down AdditionalDataSources (605 lines)
**Points:** 5  
**Priority:** P1  
**Status:** 🔴 NOT STARTED (pending re-assessment)

Split by source type.

**Target Structure:**
```python
class AdditionalDataSources:
    """Orchestrates additional data sources."""
    def __init__(self):
        self.sources = {
            'patents': PatentDataSource(),
            'trademarks': TrademarkDataSource(),
            'regulations': RegulationDataSource(),
            'events': EventDataSource(),
        }
```

**Acceptance Criteria:**
- [ ] 4-5 data source classes extracted
- [ ] Strategy pattern applied
- [ ] Each class <150 lines

---

### Story 7: Break Down EnhancedLLMClient (532 lines)
**Points:** 5 → **REDUCED to 3**  
**Priority:** P1  
**Status:** 🟡 PARTIALLY DONE (EPIC-020)

**EPIC-020 Progress:**
- ✅ Provider strategies extracted

**Remaining Work:**
- Extract client configuration
- Extract retry logic
- Extract response handling

**Acceptance Criteria:**
- [ ] Uses EPIC-020 provider strategies
- [ ] Configuration extracted
- [ ] Main client <200 lines

---

### Story 8-14: Break Down Medium God Classes (300-500 lines)
**Points:** 3 each → **MAY BE REDUCED**  
**Priority:** P2  
**Status:** 🔴 NOT STARTED (pending re-assessment)

Classes:
- `SignalDefinitions` (454 lines) - Split by signal type
- `HealthMonitor` (436 lines) - Extract monitors
- `EnrichmentOrchestrator` (413 lines) - **Uses EPIC-020 executors**
- `ImprovedExcelExporter` (408 lines) - Extract formatters
- `Company` domain model (407 lines) - **Uses EPIC-020 builders**
- `ClientReportGenerator` (391 lines) - Extract sections
- `LLMReportEnhancer` (388 lines) - Extract enhancers

**Acceptance Criteria (per class):**
- [ ] Re-measure first (may already be compliant)
- [ ] Extract 2-3 cohesive classes
- [ ] Each new class <200 lines
- [ ] Use EPIC-020 patterns where applicable

---

### Story 15-19: Break Down Smaller God Classes (300-380 lines)
**Points:** 2 each → **MAY BE COMPLETE**  
**Priority:** P3  
**Status:** 🔴 NOT STARTED (pending re-assessment)

Remaining classes:
- `IdentifierLookupService` (379 lines)
- `NewsSignalDetector` (333 lines)
- `MarkdownExtractor` (332 lines)
- `CoordinatorAgent` (320 lines)
- `CompanyReportGenerator` (311 lines)

**Acceptance Criteria (per class):**
- [ ] Re-measure first (may already be <300 lines)
- [ ] Extract if still >300 lines
- [ ] Each new class <200 lines

---

### Story 20: Create Class Extraction Patterns Guide ⭐ NEW
**Points:** 3  
**Priority:** P1  
**Status:** 🟡 READY

Document patterns for class extraction based on EPIC-020 and EPIC-022 work:

**Tasks:**
- [ ] Document Extract Class pattern
- [ ] Document Replace Conditional with Polymorphism
- [ ] Document Strategy pattern application
- [ ] Document Builder pattern application
- [ ] Create decision tree: when to extract class vs function
- [ ] Add examples from EPIC-020 and EPIC-022

**Acceptance Criteria:**
- [ ] Patterns documented in AGENTS.md
- [ ] Examples from real codebase
- [ ] Decision guidelines clear
- [ ] Code templates provided

---

### Story 21: Extract Reusable Components Library ⭐ NEW
**Points:** 5  
**Priority:** P2  
**Status:** 🟡 READY

Create reusable components from extracted classes:

**Components to Extract:**
- `DataLoader` - Base class for all data loaders
- `SectionGenerator` - Base class for report sections
- `Analyzer` - Base class for analysis components
- `Validator` - Base class for validation logic
- `Orchestrator` - Base class for orchestration

**Acceptance Criteria:**
- [ ] 5 base classes created
- [ ] Abstract methods defined
- [ ] Common utilities included
- [ ] Documentation complete
- [ ] Examples provided

---

### Story 22: Coordinate with EPIC-021 File Splitting ⭐ NEW
**Points:** 3  
**Priority:** P1  
**Status:** 🟡 READY

Ensure EPIC-022 class extraction aligns with EPIC-021 file splitting:

**Tasks:**
- [ ] Map class extractions to file splits
- [ ] Coordinate on module boundaries
- [ ] Avoid duplicate work
- [ ] Ensure consistent naming
- [ ] Share extracted components

**Acceptance Criteria:**
- [ ] Coordination document created
- [ ] Duplicate work identified and eliminated
- [ ] Module boundaries aligned
- [ ] Naming conventions consistent

---

## Refactoring Patterns - UPDATED

### 1. Extract Class (Primary Pattern)
```python
# Before
class BigClass:
    def method_a(self): ...  # Uses fields 1, 2, 3
    def method_b(self): ...  # Uses fields 1, 2, 3
    def method_c(self): ...  # Uses fields 4, 5, 6
    def method_d(self): ...  # Uses fields 4, 5, 6

# After
class ExtractedA:
    def __init__(self, field1, field2, field3):
        self.field1 = field1
        self.field2 = field2
        self.field3 = field3
    
    def method_a(self): ...
    def method_b(self): ...

class ExtractedB:
    def __init__(self, field4, field5, field6):
        self.field4 = field4
        self.field5 = field5
        self.field6 = field6
    
    def method_c(self): ...
    def method_d(self): ...

class BigClass:
    def __init__(self):
        self.a = ExtractedA(...)
        self.b = ExtractedB(...)
```

### 2. Replace Conditional with Polymorphism
```python
# Before
class ReportGenerator:
    def generate_section(self, section_type):
        if section_type == 'financial': ...
        elif section_type == 'competitive': ...

# After
class SectionGenerator(ABC):
    @abstractmethod
    def generate(self): ...

class FinancialSectionGenerator(SectionGenerator): ...
class CompetitiveSectionGenerator(SectionGenerator): ...
```

### 3. Strategy Pattern (from EPIC-020)
```python
class Strategy(ABC):
    @abstractmethod
    def execute(self): ...

class Context:
    def __init__(self, strategy: Strategy):
        self.strategy = strategy
    
    def execute(self):
        return self.strategy.execute()
```

### 4. Builder Pattern (from EPIC-020)
```python
class Builder(ABC):
    @abstractmethod
    def build_part_a(self): ...
    @abstractmethod
    def build_part_b(self): ...
    @abstractmethod
    def get_result(self): ...
```

---

## Testing Strategy
- Preserve behavior with golden tests
- Unit tests for extracted classes
- Integration tests for orchestration
- Performance benchmarks
- **NEW:** Test base classes independently
- **NEW:** Test Strategy pattern implementations

---

## Definition of Done
- [ ] Story 0 complete (re-assessment)
- [ ] All remaining god classes broken down
- [ ] No classes >300 lines remain
- [ ] No classes with >15 methods
- [ ] Clear responsibilities documented
- [ ] Test coverage >80%
- [ ] **NEW:** Base component library created
- [ ] **NEW:** Patterns documented in AGENTS.md
- [ ] **NEW:** Coordination with EPIC-021 complete

---

## Estimated Effort - UPDATED

### Phase 1: Assessment (Week 1)
- Story 0 (Re-assessment): 3 points
- **Subtotal:** 3 points (3 days)

### Phase 2: Major Classes (Weeks 2-5)
- Stories 1-2 (Major loaders/generators): 16 points
- Stories 3-4 (Loaders/GitHub): 10 points
- **Subtotal:** 26 points (4 weeks)

### Phase 3: Medium Classes (Weeks 6-9)
- Stories 5-7 (Partially done): 9 points (reduced from 15)
- Stories 8-14 (Medium classes): 21 points (may reduce)
- **Subtotal:** 30 points (4 weeks)

### Phase 4: Smaller Classes + Documentation (Weeks 10-12)
- Stories 15-19 (Smaller classes): 10 points (may reduce to 0)
- Story 20 (Patterns guide): 3 points
- Story 21 (Component library): 5 points
- Story 22 (Coordination): 3 points
- **Subtotal:** 21 points (3 weeks)

### **Total:** 80 points (12 weeks) - MAY REDUCE based on re-assessment

**Note:** If re-assessment shows many classes are now compliant, total effort could reduce to ~50 points (8 weeks).

---

## Dependencies
- 🔄 EPIC-019 (Automated detection) - For size monitoring
- ✅ EPIC-020 (God functions) - COMPLETE - Helper modules ready
- 🔄 EPIC-021 (File splitting) - Coordinate on module boundaries

---

## Impact Summary

### What EPIC-020 Provides:
1. **Helper Modules:** Ready to become extracted classes
2. **Patterns:** Strategy, Builder, Extract Method
3. **Examples:** 10 modules showing proper structure
4. **Reduced Work:** Some classes may already be compliant

### What EPIC-022 Must Do:
1. Re-assess all classes first
2. Convert helper modules to classes where appropriate
3. Apply Strategy pattern consistently
4. Create base component library
5. Coordinate with EPIC-021

---

*Updated: 2026-03-06*  
*Version: 2.0*  
*Based on: EPIC-020 Completion Analysis*
