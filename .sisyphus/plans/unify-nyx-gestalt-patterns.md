# Solstein Pattern Unification Plan

> **Apply Nyx's data freshness infrastructure and Gestalt's adapter architecture consistently across the entire codebase**

## TL;DR

**Objective:** Eliminate architectural drift by unifying Nyx's refresh connector patterns with Gestalt's adapter protocols across all 13 data sources.

**Scope:** 
- 8 enrichment adapters need refresh capability
- 3 pipeline integration points need conflict resolution
- 13 data sources need confidence calibration
- 1 unified protocol to replace dual abstractions

**Effort:** ~40-50 hours across 4 waves
**Parallel Execution:** Yes (Waves 1-3 can parallelize)
**Critical Path:** Unified Protocol → Refresh Connectors → Conflict Resolution → Integration Tests

---

## Context

### What Nyx Built (Data Freshness Infrastructure)
- `BaseRefreshConnector` - Abstract base with incremental delta detection
- `ConflictResolutionEngine` - 4 strategies (confidence, timestamp, authority, manual)
- `ConfidenceAdjuster` - Bayesian-inspired calibration with time-weighting
- Celery tasks + API routes for scheduled refresh
- 4 concrete refresh connectors (SEC EDGAR, Companies House, News Signal, GitHub)

### What Gestalt Built (Adapter Architecture)
- `DiscoverySource`, `EnrichmentSource`, `FactAggregator` protocols
- `SourceRegistry` with factory pattern
- 8 `DataSourceType` enum values
- Static catalog and competitor JSON adapters
- Integration test patterns with real adapters

### The Problem
These two excellent but separate architectures need unification. Currently:
- 8 enrichment adapters have NO refresh capability
- 3 dead modules never got either pattern
- Confidence scoring is static, not calibrated
- Conflict resolution only exists in Nyx's connectors
- No unified interface for all data sources

---

## Work Objectives

### Core Objective
Create a unified data source architecture where every source supports discovery, enrichment, AND refresh with automatic conflict resolution and confidence calibration.

### Concrete Deliverables
1. Unified adapter protocol with refresh support
2. 8 new refresh connectors for enrichment adapters
3. 3 revived dead modules as unified adapters
4. Conflict resolution integrated in research pipeline
5. Confidence calibration for all 13 sources
6. Comprehensive integration tests

### Definition of Done
- [ ] All data sources implement unified protocol
- [ ] All sources support incremental refresh
- [ ] Conflict resolution runs on every aggregation
- [ ] Confidence scores are calibrated per source
- [ ] Integration tests pass for all adapters
- [ ] No "dead" modules remain
- [ ] Documentation updated

### Must Have
- Unified `DataSourceAdapter` protocol
- Refresh connectors for all enrichment sources
- Conflict resolution in pipeline
- Confidence calibration registry
- Celery tasks for scheduled refresh
- Integration tests

### Must NOT Have (Guardrails)
- Breaking changes to existing API signatures
- Changes to scoring algorithm behavior
- Removal of existing working functionality
- Hard dependencies on external APIs for tests

---

## Verification Strategy

### Test Decision
- **Infrastructure exists:** YES (pytest)
- **Automated tests:** YES (Tests after implementation)
- **Framework:** pytest with async support

### QA Policy
Every task MUST include:
- Unit test for new methods/functions
- Integration test for adapter behavior
- QA scenario verifying end-to-end flow

**Evidence saved to:** `.sisyphus/evidence/task-{N}-{scenario-slug}.ext`

### Verification Commands
```bash
# Run adapter tests
pytest tests/unit/adapters/ -v

# Run integration tests
pytest tests/integration/test_adapters.py -v

# Run refresh connector tests
pytest tests/unit/connectors/ -v

# Full test suite
pytest tests/ --cov=src/solstein
```

---

## Execution Strategy

### Wave 1: Foundation (Unified Protocol)
**Start Immediately - Blocks all other waves**
- Task 1: Extend adapter protocols with refresh support
- Task 2: Create unified SourceRegistry
- Task 3: Update existing adapters to implement unified protocol

### Wave 2: Refresh Connectors (Parallel)
**After Wave 1 - Can run in parallel**
- Tasks 4-11: Create refresh connectors for 8 enrichment adapters

### Wave 3: Integration (Parallel)
**After Wave 1 - Can run in parallel**
- Task 12: Integrate conflict resolution in research pipeline
- Task 13: Integrate confidence calibration
- Task 14: Create Celery tasks for all sources

### Wave 4: Dead Module Revival (Sequential)
**After Wave 1 - Sequential, depends on protocol**
- Tasks 15-17: Revive 3 dead modules as unified adapters

### Wave 5: Testing & Verification (Parallel)
**After Waves 2-4**
- Tasks 18-20: Integration tests, documentation, final verification

### Critical Path
```
Task 1 → Task 2 → Task 3 → (Tasks 4-11, 12-14, 15-17 in parallel) → Tasks 18-20
```

---

## TODOs

### Wave 1: Foundation (Blocks everything)

- [ ] **1. Extend adapter protocols with refresh support**

  **What to do:**
  - Add `refresh()` method to `EnrichmentSource` protocol
  - Add `get_confidence()` method
  - Add `get_authority()` method
  - Add `supports_incremental() -> bool` method
  
  **Files to modify:**
  - `src/solstein/adapters/protocols.py`
  
  **Pattern to follow:**
  - See `BaseRefreshConnector` in `src/solstein/infrastructure/refresh.py`
  - See `EnrichmentSource` in `src/solstein/adapters/protocols.py`
  
  **Recommended Agent Profile:**
  - **Category:** `deep` - Protocol design requires careful abstraction
  - **Skills:** `development/architecture-patterns` for protocol design
  
  **Parallelization:**
  - **Can Run In Parallel:** NO (foundation task)
  - **Blocks:** Tasks 2-20
  
  **References:**
  - `src/solstein/infrastructure/refresh.py:BaseRefreshConnector` - Base class pattern
  - `src/solstein/adapters/protocols.py:EnrichmentSource` - Current protocol
  - `src/solstein/infrastructure/conflict_resolution.py:SourceAuthority` - Authority levels
  
  **Acceptance Criteria:**
  - [ ] Protocol has `refresh()`, `get_confidence()`, `get_authority()`, `supports_incremental()`
  - [ ] All methods have type hints
  - [ ] Protocol is runtime-checkable
  - [ ] pytest tests/protocols/test_protocols.py passes
  
  **QA Scenarios:**
  ```python
  Scenario: Protocol can be implemented by concrete adapter
    Tool: pytest
    Preconditions: New protocol defined
    Steps:
      1. Create mock adapter implementing protocol
      2. Run isinstance check
    Expected Result: isinstance(mock, UnifiedAdapterProtocol) == True
    Evidence: .sisyphus/evidence/task-1-protocol-check.png
  ```
  
  **Commit:** YES (standalone)
  - Message: `feat(adapters): extend protocols with refresh support`
  - Files: `src/solstein/adapters/protocols.py`, `tests/unit/adapters/test_protocols.py`
  - Pre-commit: `pytest tests/unit/adapters/test_protocols.py -v`

- [ ] **2. Create unified SourceRegistry**

  **What to do:**
  - Merge `SourceRegistry` with refresh connector registry
  - Support both adapter types during migration
  - Add method to get refresh connector for source
  - Add method to get adapter for source
  
  **Files to create/modify:**
  - Modify: `src/solstein/adapters/registry.py`
  - Create: `src/solstein/infrastructure/unified_registry.py`
  
  **Pattern to follow:**
  - See `SourceRegistry` in `src/solstein/adapters/registry.py`
  - See connector registration in Nyx's work
  
  **Recommended Agent Profile:**
  - **Category:** `deep` - Registry unification requires careful design
  - **Skills:** `development/architecture-patterns` for registry pattern
  
  **Parallelization:**
  - **Can Run In Parallel:** NO (depends on Task 1)
  - **Blocked By:** Task 1
  - **Blocks:** Tasks 3-20
  
  **Acceptance Criteria:**
  - [ ] Registry can register both adapters and refresh connectors
  - [ ] Can retrieve refresh connector by source name
  - [ ] Can retrieve adapter by source name
  - [ ] Backward compatibility with existing code
  
  **Commit:** YES (standalone)
  - Message: `feat(registry): create unified source registry`
  - Files: `src/solstein/infrastructure/unified_registry.py`
  - Pre-commit: `pytest tests/unit/test_unified_registry.py -v`

- [ ] **3. Update existing adapters to implement unified protocol**

  **What to do:**
  - Update `StaticCatalogSource` with refresh methods
  - Update `CompetitorJsonSource` with refresh methods
  - Ensure all existing adapters pass isinstance checks
  
  **Files to modify:**
  - `src/solstein/adapters/discovery/static_catalog.py`
  - `src/solstein/adapters/discovery/competitor_json.py`
  
  **Recommended Agent Profile:**
  - **Category:** `quick` - Adapter updates are mechanical
  - **Skills:** None needed
  
  **Parallelization:**
  - **Can Run In Parallel:** NO (depends on Task 2)
  - **Blocked By:** Task 2
  - **Blocks:** Wave 2, 3, 4
  
  **Acceptance Criteria:**
  - [ ] All existing discovery adapters implement unified protocol
  - [ ] isinstance checks pass for all adapters
  - [ ] Existing tests still pass
  
  **Commit:** YES (groups with Task 2)
  - Message: `refactor(adapters): update existing adapters for unified protocol`
  - Files: `src/solstein/adapters/discovery/*.py`

---

### Wave 2: Refresh Connectors (Parallel)

- [ ] **4. Create Yahoo Finance refresh connector**

  **What to do:**
  - Create `YahooFinanceRefreshConnector` extending `BaseRefreshConnector`
  - Implement `fetch_facts()` using existing Yahoo Finance adapter
  - Implement `_filter_delta()` for market data
  - Implement `_fact_exists()` for conflict detection
  
  **Files to create:**
  - `src/solstein/infrastructure/connectors/yahoo_finance_refresh.py`
  
  **Pattern to follow:**
  - See `sec_edgar_refresh.py` for structure
  - See `yahoo_finance.py` adapter for data fetching
  
  **Recommended Agent Profile:**
  - **Category:** `unspecified-high` - Connector implementation
  - **Skills:** None needed
  
  **Parallelization:**
  - **Can Run In Parallel:** YES (Task 5-11)
  - **Blocked By:** Wave 1
  - **Blocks:** None
  
  **Acceptance Criteria:**
  - [ ] Connector fetches market data from Yahoo Finance
  - [ ] Delta detection filters unchanged data
  - [ ] Facts stored with correct source attribution
  
  **QA Scenarios:**
  ```python
  Scenario: Refresh connector fetches and stores market data
    Tool: pytest + mock
    Preconditions: Mock Yahoo Finance API response
    Steps:
      1. Create connector with mock db_manager
      2. Call fetch_facts(['AAPL'])
      3. Verify facts returned
    Expected Result: Returns list of fact dicts with market data
    Evidence: .sisyphus/evidence/task-4-yahoo-connector.log
  ```
  
  **Commit:** YES (groups with Task 5)

- [ ] **5. Create Patents refresh connector**

  **Files to create:**
  - `src/solstein/infrastructure/connectors/patents_refresh.py`
  
  **Pattern to follow:** Same as Task 4
  
  **Parallelization:** YES (with Tasks 4, 6-11)

- [ ] **6. Create News refresh connector**

  **Files to create:**
  - `src/solstein/infrastructure/connectors/news_refresh.py`
  
  **Note:** Use existing `news_signal_detector.py` patterns
  
  **Parallelization:** YES

- [ ] **7. Create Website refresh connector**

  **Files to create:**
  - `src/solstein/infrastructure/connectors/website_refresh.py`
  
  **Parallelization:** YES

- [ ] **8. Create LinkedIn refresh connector**

  **Files to create:**
  - `src/solstein/infrastructure/connectors/linkedin_refresh.py`
  
  **Parallelization:** YES

- [ ] **9. Create Funding refresh connector**

  **Files to create:**
  - `src/solstein/infrastructure/connectors/funding_refresh.py`
  
  **Parallelization:** YES

- [ ] **10. Create Global Market refresh connector**

  **Files to create:**
  - `src/solstein/infrastructure/connectors/global_market_refresh.py`
  
  **Parallelization:** YES

- [ ] **11. Create Web Search refresh connector**

  **Files to create:**
  - `src/solstein/infrastructure/connectors/web_search_refresh.py`
  
  **Note:** Revives dead `web_search_client.py` module
  
  **Parallelization:** YES

---

### Wave 3: Integration (Parallel)

- [ ] **12. Integrate conflict resolution in research pipeline**

  **What to do:**
  - Add `ConflictResolutionEngine` to `aggregate_facts()`
  - Detect conflicts between sources during aggregation
  - Apply resolution before storing to DB
  - Log resolution decisions
  
  **Files to modify:**
  - `src/solstein/research/aggregate.py`
  - `src/solstein/research/pipeline.py`
  
  **Pattern to follow:**
  - See `conflict_resolution.py` for engine usage
  
  **Recommended Agent Profile:**
  - **Category:** `deep` - Pipeline integration requires care
  - **Skills:** None needed
  
  **Parallelization:**
  - **Can Run In Parallel:** YES (Tasks 13-14)
  - **Blocked By:** Wave 1
  - **Blocks:** None
  
  **Acceptance Criteria:**
  - [ ] Conflicts detected during aggregation
  - [ ] Resolution strategy applied automatically
  - [ ] Resolution decisions logged
  - [ ] No data loss during conflict resolution
  
  **Commit:** YES (standalone)

- [ ] **13. Integrate confidence calibration**

  **What to do:**
  - Register all adapters in `ConfidenceAdjuster`
  - Update scoring to use calibrated confidence
  - Add calibration tracking to pipeline
  
  **Files to modify:**
  - `src/solstein/infrastructure/confidence_adjustment.py` (extend)
  - `src/solstein/analytics/scoring.py`
  - `src/solstein/research/pipeline.py`
  
  **Pattern to follow:**
  - See `confidence_adjustment.py` for registration pattern
  
  **Recommended Agent Profile:**
  - **Category:** `deep` - Calibration integration
  
  **Parallelization:** YES

- [ ] **14. Create Celery tasks for all sources**

  **What to do:**
  - Add scheduled tasks for each refresh connector
  - Configure Celery Beat schedule
  - Add task failure handling
  
  **Files to modify:**
  - `src/solstein/worker_tasks.py`
  - `src/solstein/celery_config.py`
  
  **Pattern to follow:**
  - See existing Celery tasks in `worker_tasks.py`
  
  **Parallelization:** YES

---

### Wave 4: Dead Module Revival (Sequential)

- [ ] **15. Revive web_search_client as unified adapter**

  **What to do:**
  - Convert `web_search_client.py` to unified adapter
  - Implement discovery, enrichment, refresh
  - Add to registry
  
  **Files:**
  - Revive: `src/solstein/data/connectors/web_search_client.py`
  - Create: `src/solstein/adapters/enrichment/web_search.py`
  
  **Pattern to follow:**
  - Unified protocol from Wave 1
  - Refresh connector pattern from Wave 2
  
  **Parallelization:**
  - **Can Run In Parallel:** NO (sequential with Tasks 16-17)
  - **Blocked By:** Wave 1

- [ ] **16. Revive additional_sources as unified adapter**

  **What to do:**
  - Split `additional_sources.py` into focused adapters
  - Implement unified protocol
  - Add refresh connectors
  
  **Files:**
  - Revive: `src/solstein/data/additional_sources.py`
  - Create: Multiple focused adapter files
  
  **Parallelization:** NO (sequential)

- [ ] **17. Revive patent_client as unified adapter**

  **What to do:**
  - Convert `patent_client.py` to unified adapter
  - Integrate with existing patents adapter
  
  **Files:**
  - Revive: `src/solstein/data/patent_client.py`
  - Integrate with: `src/solstein/adapters/enrichment/patents.py`
  
  **Parallelization:** NO (sequential)

---

### Wave 5: Testing & Verification (Parallel)

- [ ] **18. Create integration tests for all adapters**

  **What to do:**
  - Test discovery for all adapters
  - Test enrichment for all adapters
  - Test refresh for all adapters
  - Test conflict resolution
  - Test confidence calibration
  
  **Files to create:**
  - `tests/integration/test_adapters.py`
  - `tests/integration/test_refresh_connectors.py`
  - `tests/integration/test_conflict_resolution.py`
  
  **Pattern to follow:**
  - See Gestalt's integration test patterns
  
  **Recommended Agent Profile:**
  - **Category:** `testing` - Comprehensive test suite
  - **Skills:** `testing/test-specialist`
  
  **Parallelization:** YES

- [ ] **19. Update DATA_SOURCE_WIRING_REFERENCE.md**

  **What to do:**
  - Document unified protocol
  - Update adapter mappings
  - Document refresh patterns
  - Add confidence calibration section
  
  **Files:**
  - `docs/architecture/DATA_SOURCE_WIRING_REFERENCE.md`
  
  **Parallelization:** YES

- [ ] **20. Final verification and cleanup**

  **What to do:**
  - Run full test suite
  - Verify no dead modules remain
  - Verify no import errors
  - Check test coverage
  - Update CHANGELOG
  
  **Commands:**
  ```bash
  pytest tests/ --cov=src/solstein --cov-report=term-missing
  python -c "from solstein.adapters import *; print('All imports OK')"
  ```
  
  **Parallelization:** YES

---

## Final Verification Wave

### F1. Architecture Compliance Audit - `oracle`

Read the entire codebase and verify:
- All data sources implement unified protocol
- No dead modules remain
- All adapters have refresh capability
- Conflict resolution integrated
- Confidence calibration registered

**Output:** Architecture compliance report

### F2. Test Coverage Review - `testing`

- Run pytest with coverage
- Verify >80% coverage for adapters
- Verify >90% coverage for refresh connectors
- Verify integration tests pass

**Output:** Coverage report

### F3. Documentation Review - `writing`

- Review all documentation
- Verify DATA_SOURCE_WIRING_REFERENCE is current
- Verify API documentation updated
- Verify CHANGELOG updated

**Output:** Documentation review report

### F4. Performance Check - `performance`

- Profile refresh connector performance
- Verify delta detection is efficient
- Verify conflict resolution doesn't slow pipeline
- Check memory usage

**Output:** Performance report

---

## Success Criteria

### Verification Commands
```bash
# All tests pass
pytest tests/ -x --tb=short

# Coverage threshold met
pytest tests/ --cov=src/solstein --cov-fail-under=80

# No import errors
python -c "from solstein import *; from solstein.adapters import *"

# All adapters registered
python -c "from solstein.adapters.registry import get_registry; print(len(get_registry().list_sources()), 'sources registered')"

# Refresh connectors available
python -c "from solstein.infrastructure.unified_registry import get_refresh_connectors; print(len(get_refresh_connectors()), 'refresh connectors available')"
```

### Final Checklist
- [ ] 13 data sources unified under single protocol
- [ ] 11 refresh connectors (4 existing + 7 new)
- [ ] Conflict resolution running on every aggregation
- [ ] Confidence calibration for all sources
- [ ] Integration tests for all adapters
- [ ] Documentation updated
- [ ] No dead modules remain
- [ ] Full test suite passes
- [ ] Coverage >80%

---

## Commit Strategy

### Phase Commits
1. `feat(adapters): extend protocols with refresh support`
2. `feat(registry): create unified source registry`
3. `refactor(adapters): update existing adapters for unified protocol`
4-11. `feat(connectors): add {source} refresh connector` (grouped by 2)
12. `feat(pipeline): integrate conflict resolution in research aggregation`
13. `feat(scoring): integrate confidence calibration`
14. `feat(tasks): add Celery tasks for all refresh connectors`
15-17. `feat(adapters): revive {module} as unified adapter`
18. `test(integration): add comprehensive adapter tests`
19. `docs: update DATA_SOURCE_WIRING_REFERENCE with unified architecture`
20. `chore: final cleanup and verification`

---

## Risk Mitigation

### Risk: Breaking existing functionality
**Mitigation:** Maintain backward compatibility during migration
- Keep old protocols functional during transition
- Use deprecation warnings
- Gradual migration, not big bang

### Risk: Test failures
**Mitigation:** Run tests after every task
- Pre-commit hooks for tests
- CI/CD pipeline validation
- Integration tests before merge

### Risk: Performance degradation
**Mitigation:** Profile before and after
- Delta detection must be efficient
- Conflict resolution must cache results
- Confidence calibration must be lazy

### Risk: Documentation drift
**Mitigation:** Update docs with every change
- Architecture docs updated in Task 19
- API docs auto-generated
- CHANGELOG updated per commit

---

## Notes

This plan represents a significant architectural improvement that unifies two excellent but separate contributions (Nyx's data freshness and Gestalt's adapter architecture). The unification eliminates dead code, provides consistent interfaces, and enables powerful features like automatic conflict resolution and confidence calibration across all data sources.

**Estimated Timeline:**
- Wave 1: 1-2 days
- Wave 2: 2-3 days (parallel)
- Wave 3: 1-2 days (parallel)
- Wave 4: 2-3 days (sequential)
- Wave 5: 1-2 days (parallel)
- **Total: 7-12 days**

**Parallel Speedup:** ~60% faster than sequential
**Max Concurrent: 8 (Wave 2)**
