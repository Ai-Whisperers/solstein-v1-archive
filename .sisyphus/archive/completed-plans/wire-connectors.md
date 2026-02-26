# Wire Connectors Into Scoring Pipeline

## TL;DR

> **Quick Summary**: Integrate existing SEC EDGAR, Companies House, and News Signal connectors into the main data loading pipeline to eliminate 84% NULL data problem. Currently connectors exist but are never called.

> **Deliverables**:
> - SEC EDGAR data filling NULL financials for US companies
> - Companies House data enriching UK company records
> - News signals (funding, partnerships, key hires) attached to companies
> - Confidence scoring: API data = HIGH (0.95), Manual = LOWER
> - Data provenance tracking per field

> **Estimated Effort**: Short (4-6 hours)
> **Parallel Execution**: NO - sequential (each connector builds on previous)
> **Critical Path**: SEC EDGAR → Companies House → News Signals → Integration Tests

---

## Context

### The Problem
Connectors exist but aren't wired into the data pipeline:
- `SECEdgarConnector`: Fully implemented, extracts revenue/EBITDA/gross_margin/cash from 10-K/10-Q
- `CompaniesHouseConnector`: Fully implemented, UK company details + accounts
- `NewsSignalDetector`: Fully implemented, funding/partnership/key_hire signals
- `UnifiedCompanyLoader`: Only loads JSON/Markdown, **never calls connectors**

Result: 84% NULL revenue data because nobody invokes the connectors.

### What We Have
- Production-ready connectors (319, 134, 355 lines respectively)
- Confidence weighting logic (`populate_signal_confidences()`)
- Test infrastructure for connectors

### What We Need
- Wire connectors into `UnifiedCompanyLoader.load_unified_companies()`
- Fill NULL fields from APIs instead of leaving them empty
- Set confidence based on source: API = CONFIRMED (0.95), Manual = ESTIMATED (0.7)
- Track provenance: which field came from which source

---

## Work Objectives

### Core Objective
Eliminate NULL financial data by calling existing connectors when data is missing.

### Concrete Deliverables
- Modified `UnifiedCompanyLoader` that calls SEC EDGAR for US companies with NULL financials
- Modified `UnifiedCompanyLoader` that calls Companies House for UK companies
- Modified `UnifiedCompanyLoader` that attaches News signals to all companies
- Data source tracking: each field knows its origin (JSON, Markdown, SEC, CompaniesHouse, NewsAPI)
- Confidence scoring: API sources = 0.95, manual = existing confidence

### Definition of Done
- [ ] Run 10 companies through pipeline: NULL fields populated from APIs
- [ ] Verify SEC EDGAR data appears for US companies (AAPL, MSFT test)
- [ ] Verify Companies House data appears for UK companies
- [ ] Verify News signals attached (funding rounds, partnerships, key hires)
- [ ] Verify confidence: API-sourced data has 0.95 confidence
- [ ] Verify provenance: data_source_per_field shows correct sources

### Must Have
- Don't replace existing data, only fill NULLs
- Graceful failure: if connector fails, log error and continue with existing data
- Rate limiting: respect API limits (SEC: 10 requests/sec, NewsAPI: 100/day)
- No breaking changes to existing API endpoints

### Must NOT Have (Guardrails)
- Don't call connectors for companies that already have complete data
- Don't replace working data with API data if there's a conflict (existing > API)
- Don't add new API keys or credentials - use existing env vars
- Don't modify scoring math - only fill NULLs and set confidence

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES
- **Automated tests**: YES (tests-after for integration)
- **Framework**: pytest
- **No TDD needed**: This is integration work, not new feature

### QA Policy
Every task includes agent-executed QA scenarios. Evidence saved to `.sisyphus/evidence/`.

**API Testing**:
- Test SEC EDGAR with known tickers (AAPL, MSFT)
- Test Companies House with known UK companies
- Test NewsSignalDetector with known company names

---

## Execution Strategy

### Sequential Execution (Required)

```
Wave 1 (Start Immediately):
├── Task 1: Modify UnifiedCompanyLoader to accept connectors
├── Task 2: Wire SEC EDGAR connector - fill NULL financials
├── Task 3: Wire Companies House connector - enrich UK companies
├── Task 4: Wire News Signal Detector - attach signals
├── Task 5: Add data provenance tracking per field
├── Task 6: Integration test - full pipeline with 10 companies
└── Task 7: Verify NULL reduction (before vs after)
```

### Dependency Flow
- Task 1 must complete before Tasks 2-4
- Tasks 2-4 can run in parallel after Task 1
- Task 5 should complete with Tasks 2-4
- Task 6 depends on Tasks 2-5
- Task 7 depends on Task 6

---

- [ ] 1. **Modify UnifiedCompanyLoader to Accept Connectors**

  **What to do**:
  - Add connector instances as optional parameters to `UnifiedCompanyLoader.__init__()`
  - Default to None, create connectors if not provided
  - Add method `enrich_from_connectors(company: UnifiedCompany) -> UnifiedCompany`
  - Add method `fill_nulls_from_sec_edgar(company: UnifiedCompany) -> UnifiedCompany`
  - Add method `fill_nulls_from_companies_house(company: UnifiedCompany) -> UnifiedCompany`
  - Add method `attach_news_signals(company: UnifiedCompany) -> UnifiedCompany`

  **Must NOT do**:
  - Don't modify existing JSON/Markdown loading logic
  - Don't change the merge conflict resolution

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: This is straightforward modification of existing loader
  - **Skills**: None required

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Blocks**: Tasks 2, 3, 4 (they depend on these methods existing)

  **References**:
  - `src/solstein/data/unified_loader.py:30-45` - Current loader structure
  - `src/solstein/data/connectors/sec_edgar_connector.py:46-152` - SEC connector fetch_filing method
  - `src/solstein/data/connectors/companies_house_connector.py:60-65` - Companies House get_company_metrics

  **Acceptance Criteria**:
  - [ ] UnifiedCompanyLoader accepts optional connector parameters
  - [ ] Enrich method exists but doesn't call connectors yet
  - [ ] Tests pass: `pytest tests/unit/data/test_unified_loader.py -x`

  **QA Scenarios**:
  - Not needed for scaffolding - covered by existing tests

- [ ] 2. **Wire SEC EDGAR Connector - Fill NULL Financials**

  **What to do**:
  - Implement `fill_nulls_from_sec_edgar()` method
  - Check if company has ticker (required for SEC lookup)
  - Check if revenue/EBITDA/gross_margin/cash is NULL
  - If NULL and ticker exists, call `sec_connector.fetch_filing(ticker, year, "10-K")`
  - For most recent year with available data
  - Fill NULL fields with SEC data
  - Set confidence to 0.95 for SEC-sourced fields
  - Add "SEC" to data_source_per_field for filled fields
  - Handle failures gracefully: log warning, return company unchanged

  **Must NOT do**:
  - Don't replace existing non-NULL data
  - Don't call SEC for companies without tickers
  - Don't crash on API failures - log and continue

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Requires understanding of financial data formats and API error handling
  - **Skills**: None required

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Blocks**: Task 6 (integration test)
  - **Blocked By**: Task 1 (needs method to exist)

  **References**:
  - `src/solstein/data/connectors/sec_edgar_connector.py:61-119` - fetch_filing returns dict with revenue, ebitda, gross_margin, cash_position
  - `src/solstein/data/connectors/sec_edgar_connector.py:273-278` - Return format
  - `src/solstein/domain/models.py` - Company and FinancialMetric models

  **Acceptance Criteria**:
  - [ ] Test with AAPL ticker: revenue populated from SEC
  - [ ] Test with company that has existing revenue: stays unchanged
  - [ ] Test with company without ticker: skipped gracefully
  - [ ] Test with SEC API failure: company returned with NULL, no crash

  **QA Scenarios**:
  - Scenario: Company with NULL revenue and valid ticker (AAPL)
    - Tool: Python REPL (bash)
    - Preconditions: SEC_USER_AGENT set, AAPL has recent 10-K
    - Steps:
      1. Load company with NULL revenue from JSON
      2. Call fill_nulls_from_sec_edgar()
      3. Assert financials.revenue is not None
      4. Assert financials.revenue_confidence == 0.95
    - Expected Result: Revenue populated, confidence = 0.95
    - Evidence: .sisyphus/evidence/task-2-sec-edgar-fill.json

  - Scenario: Company already has revenue (should NOT overwrite)
    - Tool: Python REPL (bash)
    - Preconditions: Company with revenue = 1000000
    - Steps:
      1. Call fill_nulls_from_sec_edgar()
      2. Assert revenue still == 1000000
    - Expected Result: Revenue unchanged
    - Evidence: .sisyphus/evidence/task-2-no-overwrite.json

  - Scenario: SEC API fails (rate limit, timeout)
    - Tool: Python REPL (mock failure)
    - Preconditions: Mock SEC connector to raise RuntimeError
    - Steps:
      1. Call fill_nulls_from_sec_edgar()
      2. Check logs for warning
    - Expected Result: Company returned with NULL, warning logged
    - Evidence: .sisyphus/evidence/task-2-graceful-failure.json

- [ ] 3. **Wire Companies House Connector - Enrich UK Companies**

  **What to do**:
  - Implement `fill_nulls_from_companies_house()` method
  - Check if company is UK-based (jurisdiction = "uk" or company_number exists)
  - Check if employees, sic_codes, or account dates are NULL
  - If NULL and UK company, call `companies_house_connector.get_company_metrics(company_number)`
  - Fill NULL fields with Companies House data
  - Set confidence to 0.93 for Companies House-sourced fields
  - Add "CompaniesHouse" to data_source_per_field
  - Handle failures gracefully

  **Must NOT do**:
  - Don't replace existing non-NULL data
  - Don't call for non-UK companies
  - Don't crash on API failures

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: UK company data structure differs from US
  - **Skills**: None required

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Blocks**: Task 6
  - **Blocked By**: Task 1

  **References**:
  - `src/solstein/data/connectors/companies_house_connector.py:60-65` - get_company_metrics returns dict
  - `src/solstein/data/connectors/companies_house_connector.py:102-134` - _extract_metrics shows fields

  **Acceptance Criteria**:
  - [ ] Test with UK company: employees/sic_codes populated
  - [ ] Test with US company: skipped gracefully
  - [ ] Test with missing API key: skipped gracefully

  **QA Scenarios**:
  - Scenario: UK company with NULL employees
    - Tool: Python REPL (bash)
    - Preconditions: COMPANIES_HOUSE_API_KEY set, valid UK company
    - Steps:
      1. Load UK company with NULL employees
      2. Call fill_nulls_from_companies_house()
      3. Assert financials.employees is not None
    - Expected Result: Employees populated, confidence = 0.93
    - Evidence: .sisyphus/evidence/task-3-uk-company.json

- [ ] 4. **Wire News Signal Detector - Attach Signals**

  **What to do**:
  - Implement `attach_news_signals()` method
  - Call news_connector for company name
  - Detect signals: funding_round, partnership, key_hire
  - Attach signals to company.news_signals list
  - Each signal should have confidence (0.70-0.75 based on type)
  - Add "NewsAPI" to data_source_per_field for signals
  - Handle failures gracefully

  **Must NOT do**:
  - Don't replace existing signals
  - Don't duplicate signals (check for existing)
  - Don't crash on API failures

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Signal detection and attachment logic
  - **Skills**: None required

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Blocks**: Task 6
  - **Blocked By**: Task 1

  **References**:
  - `src/solstein/data/connectors/news_signal_detector.py:243-271` - detect_funding_signal returns list
  - `src/solstein/data/connectors/news_signal_detector.py:225-239` - Signal format

  **Acceptance Criteria**:
  - [ ] Test with known company (e.g., a recent funding round): signals attached
  - [ ] Test with rate limit: skipped gracefully
  - [ ] Test with no news: empty list, no error

  **QA Scenarios**:
  - Scenario: Company with recent funding round
    - Tool: Python REPL (bash)
    - Preconditions: NEWSAPI_KEY set, company known to have recent news
    - Steps:
      1. Call attach_news_signals()
      2. Assert len(company.news_signals) > 0
    - Expected Result: At least one funding_round signal
    - Evidence: .sisyphus/evidence/task-4-news-signals.json

- [ ] 5. **Add Data Provenance Tracking Per Field**

  **What to do**:
  - Ensure data_source_per_field is populated for ALL fields
  - After filling from connectors, update data_source_per_field
  - Add source tracking for: revenue, employees, financials, signals
  - Format: data_source_per_field = {"revenue": "SEC", "employees": "CompaniesHouse", ...}
  - Ensure merge_timestamp is updated when data is enriched

  **Must NOT do**:
  - Don't remove existing source tracking
  - Don't change the merge conflict logic

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple dict updates
  - **Skills**: None required

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Blocked By**: Tasks 2, 3, 4

  **References**:
  - `src/solstein/data/unified_loader.py:24-27` - data_source_per_field definition

  **Acceptance Criteria**:
  - [ ] SEC-filled revenue shows "SEC" as source
  - [ ] CompaniesHouse-filled employees shows source
  - [ ] Manual data shows "JSON" or "Markdown"

- [ ] 6. **Integration Test - Full Pipeline with 10 Companies**

  **What to do**:
  - Create integration test file: tests/integration/test_connector_enrichment.py
  - Test 10 companies through full pipeline
  - Verify NULL reduction: count NULL fields before vs after
  - Verify confidence: API data = 0.95, manual = 0.7
  - Verify provenance: correct sources tracked

  **Must NOT do**:
  - Don't modify existing tests
  - Don't test invalid tickers (use real SEC-registered companies)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Integration testing across multiple components
  - **Skills**: None required

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Blocked By**: Tasks 1, 2, 3, 4, 5

  **Acceptance Criteria**:
  - [ ] Test runs without errors
  - [ ] Shows measurable NULL reduction
  - [ ] All 10 companies have provenance data

  **QA Scenarios**:
  - Scenario: Full pipeline integration
    - Tool: pytest
    - Steps:
      1. Run test file
      2. Check output for NULL reduction percentage
    - Expected Result: NULLs reduced by >50%
    - Evidence: .sisyphus/evidence/task-6-integration.json

- [ ] 7. **Verify NULL Reduction (Before vs After)**

  **What to do**:
  - Run baseline: count NULL financials before connector integration
  - Run after: count NULL financials after integration
  - Calculate reduction percentage
  - Target: From 84% NULL to <30% NULL

  **Must NOT do**:
  - Don't manually edit data to make test pass

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Verification only
  - **Skills**: None required

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Blocked By**: Task 6

  **Acceptance Criteria**:
  - [ ] Before: 84% NULL (documented baseline)
  - [ ] After: <30% NULL
  - [ ] Reduction: >50%

---

## Final Verification Wave

- [ ] F1. **Data Completeness Check** - Verify NULL % reduced from 84% to <30%
- [ ] F2. **Source Attribution** - Spot check: revenue source = SEC, not manual
- [ ] F3. **Confidence Scoring** - Verify API data has 0.95 confidence
- [ ] F4. **Graceful Degradation** - Test with connector failures: system still works

---

## Commit Strategy

- **1**: `feat(connectors): wire SEC EDGAR into unified loader` - loader modifications
- **2**: `feat(connectors): wire Companies House into unified loader` - UK enrichment
- **3**: `feat(connectors): wire News signals into unified loader` - signal enrichment
- **4**: `test(connectors): integration test - 10 companies full pipeline` - integration test
- Pre-commit: `pytest tests/ -x -q`

---

## Success Criteria

### Verification Commands
```bash
# Before: Check NULL percentage
python -c "from src.solstein.data.unified_loader import unified_loader; companies = unified_loader.load_unified_companies(); nulls = sum(1 for c in companies if c.financials and c.financials.revenue is None); print(f'NULL revenue: {nulls}/{len(companies)} ({100*nulls/len(companies):.1f}%)')"

# After: Should be <30%
```

### Final Checklist
- [ ] All companies with NULL financials now have data from SEC/CompaniesHouse
- [ ] Confidence scoring: API data = 0.95, manual = 0.7
- [ ] Provenance tracking shows correct sources
- [ ] No breaking changes to existing tests
- [ ] Graceful handling when connectors fail
