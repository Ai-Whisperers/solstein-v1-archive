# Epic: God Class Breakdown (EPIC-022)

## Overview
Refactor 19 god classes (>300 lines or >15 methods) into smaller, cohesive classes following Single Responsibility Principle.

## Current State
- 19 God Classes identified
- Worst: `UnifiedCompanyLoader` at 878 lines, 14 methods
- `ReportGenerator` at 848 lines, 31 methods

## Goals
- [ ] Zero classes >300 lines remaining
- [ ] No class with >15 methods
- [ ] Clear responsibilities per class
- [ ] Improved testability
- [ ] Reduced cognitive load

## Worst Offenders
1. `UnifiedCompanyLoader` - 878 lines, 14 methods
2. `ReportGenerator` - 848 lines, 31 methods
3. `CompetitorDataLoader` - 788 lines, 14 methods
4. `GitHubAgent` - 755 lines, 12 methods
5. `ProviderHealthChecker` - 595 lines, 14 methods

---

## Stories

### Story 1: Break Down UnifiedCompanyLoader (878 lines)
**Points:** 8
**Priority:** P0

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
            'sec_edgar': SecEdgarLoader(),
            'companies_house': CompaniesHouseLoader(),
            'linkedin': LinkedInLoader(),
        }
        self.merger = DataMerger()
        self.validator = DataValidator()
    
    def load(self, company_id: str) -> Company:
        data = {}
        for source, loader in self.loaders.items():
            data[source] = loader.load(company_id)
        merged = self.merger.merge(data)
        return self.validator.validate(merged)
```

**Acceptance Criteria:**
- [ ] 4-6 loader classes extracted
- [ ] `DataMerger` class created
- [ ] `DataValidator` class created
- [ ] Each class <200 lines
- [ ] Full test coverage

### Story 2: Break Down ReportGenerator (848 lines)
**Points:** 8
**Priority:** P0

Split the 848-line, 31-method report generator.

**Target Structure:**
```python
class ReportGenerator:
    """Orchestrates report generation."""
    def __init__(self):
        self.sections = {
            'executive': ExecutiveSummaryGenerator(),
            'financial': FinancialSectionGenerator(),
            'competitive': CompetitiveAnalysisGenerator(),
            'market': MarketOverviewGenerator(),
        }
        self.formatter = MarkdownFormatter()
        self.template = ReportTemplate()
```

### Story 3-7: Break Down Next 5 God Classes (500-800 lines)
**Points:** 5 each
**Priority:** P1

Classes to refactor:
3. `CompetitorDataLoader` (788 lines) - Extract field mappers
4. `GitHubAgent` (755 lines) - Extract analyzers
5. `ProviderHealthChecker` (595 lines) - Extract provider checks
6. `AdditionalDataSources` (605 lines) - Split by source type
7. `EnhancedLLMClient` (532 lines) - Extract client strategies

### Story 8-14: Break Down Medium God Classes (300-500 lines)
**Points:** 3 each
**Priority:** P2

Classes:
8. `SignalDefinitions` (454 lines) - Split by signal type
9. `HealthMonitor` (436 lines) - Extract monitors
10. `EnrichmentOrchestrator` (413 lines) - Extract strategies
11. `ImprovedExcelExporter` (408 lines) - Extract formatters
12. `Company` domain model (407 lines) - Extract value objects
13. `ClientReportGenerator` (391 lines) - Extract sections
14. `LLMReportEnhancer` (388 lines) - Extract enhancers

### Story 15-19: Break Down Smaller God Classes (300-380 lines)
**Points:** 2 each
**Priority:** P3

Remaining classes:
15. `IdentifierLookupService` (379 lines)
16. `NewsSignalDetector` (333 lines)
17. `MarkdownExtractor` (332 lines)
18. `CoordinatorAgent` (320 lines)
19. `CompanyReportGenerator` (311 lines)

---

## Refactoring Patterns

### Extract Class
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

### Replace Conditional with Polymorphism
```python
# Before
class ReportGenerator:
    def generate_section(self, section_type):
        if section_type == 'financial':
            ...
        elif section_type == 'competitive':
            ...

# After
class SectionGenerator(ABC):
    @abstractmethod
    def generate(self): ...

class FinancialSectionGenerator(SectionGenerator): ...
class CompetitiveSectionGenerator(SectionGenerator): ...
```

---

## Testing Strategy
- Preserve behavior with golden tests
- Unit tests for extracted classes
- Integration tests for orchestration
- Performance benchmarks

---

## Definition of Done
- [ ] All 19 god classes broken down
- [ ] No classes >300 lines remain
- [ ] No classes with >15 methods
- [ ] Clear responsibilities documented
- [ ] Test coverage >80%

## Estimated Effort
- **Stories 1-2:** 16 points (2 weeks)
- **Stories 3-7:** 25 points (3 weeks)
- **Stories 8-14:** 21 points (3 weeks)
- **Stories 15-19:** 10 points (1 week)
- **Total:** 72 points (9 weeks)

## Dependencies
- EPIC-019 (Automated detection)
- EPIC-020 (God functions) - Coordinate
- EPIC-021 (File splitting) - May overlap

---

*Created: 2026-03-06*  
*Based on: COMPLETE_CODE_SMELLS_FULL_ANALYSIS.md*
