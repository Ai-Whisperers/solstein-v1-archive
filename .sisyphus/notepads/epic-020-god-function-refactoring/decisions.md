# EPIC-020 Decisions

> Architectural decisions made during god function refactoring

---

## Decision Log

### DECISION-001: Pipeline Architecture for run_market_intelligence
**Date:** 2026-03-06  
**Status:** PROPOSED  

**Context:** The 505-line `run_market_intelligence` function handles discovery, enrichment, validation, scoring, analysis, and export in one monolithic block.

**Decision:** Extract into a `ResearchPipeline` class with 6 stage classes:
- DiscoveryStage
- EnrichmentStage
- ValidationStage
- ScoringStage
- AnalysisStage
- ExportStage

**Rationale:**
- Each stage has clear boundaries
- Enables parallel stage execution in future
- Easier to test each stage independently
- Follows pipeline pattern used in data engineering

**Consequences:**
- (+) Improved testability
- (+) Clear separation of concerns
- (-) More files to manage
- (-) Slight overhead from class structure

---

### DECISION-002: Field Mapper Pattern for _convert_to_domain_company
**Date:** 2026-03-06  
**Status:** PROPOSED  

**Context:** The 429-line conversion function maps raw JSON data to domain Company objects with 72 levels of nesting.

**Decision:** Create `CompanyConverter` with specialized mappers:
- FinancialFieldMapper
- MetadataFieldMapper
- ScoreFieldMapper
- TimelineFieldMapper

**Rationale:**
- Each mapper handles one concern
- Easier to add new field mappings
- Reduces nesting by extracting methods

**Consequences:**
- (+) Each mapper <80 lines
- (+) Easy to test each mapping independently
- (-) More classes to understand

---

### DECISION-003: Strategy Pattern for _catalog_for_market
**Date:** 2026-03-06  
**Status:** PROPOSED  

**Context:** The 429-line discovery function has multiple discovery strategies mixed together.

**Decision:** Use Strategy pattern with `DiscoveryEngine`:
- KnownCompanyStrategy
- NewsSearchStrategy
- WebSearchStrategy
- CompetitorAnalysisStrategy

**Rationale:**
- Each strategy is self-contained
- Easy to add new discovery methods
- Enables strategy selection based on market type

**Consequences:**
- (+) Pluggable discovery methods
- (+) Easier to test each strategy
- (-) Need to manage strategy selection logic

---

## Pending Decisions

### PENDING-001: Duplicated _get_client Logic
Both `enhanced_client.py` and `health_checker.py` have 153-line `_get_client` functions with similar logic.

**Options:**
1. Extract to shared utility class
2. Merge into single client module
3. Keep separate but extract common parts

**Status:** Needs analysis of differences first.

---

### PENDING-002: unified_loader.py God Class
`UnifiedCompanyLoader` is 878 lines with 14 methods - the largest god class.

**Options:**
1. Extract field filling methods to separate classes
2. Create loader strategy pattern
3. Split into multiple specialized loaders

**Status:** Analyze dependencies first.

---

*Last updated: 2026-03-06*
