# 🚀 SOLSTEIN DATA INTEGRATION — WAVE 1 IMPLEMENTATION PLAN

**Project**: Solstein PE Intelligence Platform  
**Goal**: Transform from 8% → 40% data coverage by integrating free financial + news data sources  
**Duration**: Week 1-2 (10 business days)  
**Effort**: 40-50 hours (2-3 person team, parallel execution)  
**Status**: Ready for kickoff

---

## TL;DR

> **Quick Summary**: Build connectors for SEC EDGAR financial data, UK Companies House, and news signal detection. Integrate into existing scoring engine. All free data, zero cost.
>
> **Deliverables**:
> - SEC EDGAR financial data connector (revenue, margins, cash)
> - Companies House UK company financials connector
> - News signal detector (funding rounds, partnerships, key events)
> - Enhanced GitHub analysis (velocity, language trends)
> - 5 end-to-end integration tests
>
> **Estimated Effort**: 40-50 hours  
> **Parallel Execution**: YES - 3-4 independent task streams  
> **Critical Path**: Financial connectors → Scoring integration → Tests  

---

## Context

### Current State (Baseline)
- **Data Coverage**: 8% (only GitHub + basic company info)
- **Scoring Data**: Partially blind (financial, team, customer data missing)
- **Connectors Existing**: GitHub API, yfinance (stock quotes only)
- **Database Schema**: Companies table exists, facts infrastructure partially built

### Target State (Wave 1 Complete)
- **Data Coverage**: 40% (financial, news signals, enhanced GitHub)
- **Scoring Data**: Can calculate Growth Score, Financial Health from actual data
- **Connectors Built**: 4 new free data sources operational
- **Database Schema**: Facts table with confidence scoring

### Why This Matters
PE firms make decisions based on:
1. **Financial Health** (40% weight) ← We have 0% coverage today
2. **Team Quality** (20% weight) ← We have ~5% coverage today
3. **Growth Trajectory** (20% weight) ← We have 10% coverage today
4. **Competitive Position** (20% weight) ← We have 15% coverage today

**Result**: Scoring is blind. Company X (excellent GitHub) gets 8.0, but we don't see it burned $10M last quarter and has 3 months runway.

---

## Work Objectives

### Core Objective
Build a robust, production-grade data integration layer that fetches comprehensive company intelligence from free/freemium sources and fuses it into Solstein's scoring engine.

### Concrete Deliverables
- ✅ `sec_edgar_connector.py` — 10-K/10-Q → structured JSON (25 financial metrics)
- ✅ `companies_house_connector.py` — UK company financials API (10 metrics)
- ✅ `news_signal_detector.py` — NewsAPI → funding/partnership/key event signals
- ✅ `github_enhanced_agent.py` — Extended GitHub (velocity, language trends, dependencies)
- ✅ `FactModel` Postgres schema — Stores facts with confidence + sources
- ✅ Integration tests — End-to-end company → facts retrieval

### Definition of Done
- [ ] All connectors fetch data without errors
- [ ] 100% of extracted data stores in PostgreSQL with confidence scores
- [ ] Scoring engine ingests new data types
- [ ] No manual intervention required (fully automated pipeline)
- [ ] 80%+ test coverage for data layer
- [ ] Documentation for each connector (API calls, retry logic, rate limits)

### Must Have
- Zero external dependency on paid APIs (all free tier usage)
- Full error handling & retry logic (API rate limits, network failures)
- Data validation (no corrupted facts in database)
- Confidence scoring (distinguishing SEC data 0.95 from news rumors 0.60)
- Audit trail (every fact stores source URL + extraction timestamp)

### Must NOT Have (Guardrails)
- ❌ No LinkedIn scraping (legal risk) — use GitHub profiles + Crunchbase only
- ❌ No hardcoded credentials in code — use .env files
- ❌ No synchronous API calls for 1000+ companies (it will time out) — use async
- ❌ No incomplete error handling ("try: pass" forbidden)
- ❌ No data overwriting existing manual entries (merge, don't replace)

---

## Verification Strategy

### Test Decision
- **Infrastructure**: Pytest (existing)
- **Automated tests**: TDD workflow for each connector
- **Coverage Target**: 80% data layer coverage

### QA Policy
**Agent-Executed Verification Only** — No human manual testing allowed.

Each task includes executable QA scenarios:

1. **Unit Tests** (per connector)
   - Mock API responses
   - Test parsing logic
   - Verify confidence scoring
   - Check error handling

2. **Integration Tests**
   - Real API calls to sandbox/free tier
   - End-to-end: company_id → fetch all 4 connectors
   - Verify PostgreSQL schema + data types
   - Check scoring engine can ingest new facts

3. **Data Quality Tests**
   - Golden dataset: 5 known companies with expected outcomes
   - Revenue validation: +/- 2% vs. known values
   - No NULL critical fields
   - Timestamps within 24h of extraction

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — Foundation, 4 parallel streams):
├── Stream A: SEC EDGAR Connector (6-8 hours) [CRITICAL PATH]
├── Stream B: Companies House Connector (4-5 hours)
├── Stream C: News Signal Detector (6-8 hours) [CRITICAL PATH]
└── Stream D: GitHub Enhanced Analysis (5-6 hours)

Wave 2 (After Wave 1 — Integration, 2 streams):
├── Stream E: Fact Model + Database Schema (4-5 hours)
└── Stream F: Scoring Engine Integration (4-6 hours)

Wave 3 (After Wave 2 — Verification, 1 stream):
└── Stream G: Integration Tests + Golden Dataset (6-8 hours)

Critical Path: A/C → E → F → G
Parallel Speedup: ~60% faster than sequential (est. 50 hrs → 30 hrs)
```

### Dependency Matrix

```
Dependency Flow:
A (SEC) ──┐
B (CH)   ─┼─→ E (Fact Model) ──→ F (Scoring) ──→ G (Tests)
C (News) ─┤
D (GitHub)┘
```

**Key Points**:
- Streams A-D can run in parallel (no dependencies)
- E depends on A-D completing (needs to know all fact types)
- F depends on E (needs schema)
- G depends on F (needs working integration)

### Agent Dispatch Summary

| Stream | Task | Recommended Agent | Reasoning |
|--------|------|-------------------|-----------|
| A | SEC EDGAR connector | `quick` | Straightforward API + parsing |
| B | Companies House connector | `quick` | Similar to SEC, simpler API |
| C | News signal detector | `quick` | Pattern matching, clear requirements |
| D | GitHub enhanced | `quick` | Extension of existing code |
| E | Fact Model + Schema | `quick` | Data modeling (no complexity) |
| F | Scoring integration | `unspecified-high` | Logic integration (higher risk) |
| G | Integration tests | `unspecified-high` | QA + debugging (complex scenarios) |

---

## TODOs

### Stream A: SEC EDGAR Financial Connector (6-8 hours)

- [ ] **A1. Setup & Dependencies**

  **What to do**:
  - Install `edgartools` library: `pip install edgartools`
  - Install test mocks: `pip install pytest-httpx`
  - Create `src/solstein/data/connectors/sec_edgar_connector.py`
  - Create test file: `tests/unit/data/test_sec_edgar_connector.py`

  **Must NOT do**:
  - ❌ Don't use deprecated `sec-api` library (incompatible)
  - ❌ Don't hardcode API keys in code
  - ❌ Don't forget `.gitignore` for cache files

  **Recommended Agent Profile**:
  > **Category**: `quick`
  > - **Reason**: Straightforward library usage + parsing. edgartools handles SEC API complexity.
  > - **Skills**: None required (standard Python)

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1, Stream A (independent)
  - **Blocks**: E (Fact Model)
  - **Blocked By**: None

  **References** (CRITICAL):

  > **Why Each Reference Matters**:

  **Pattern References** (existing code):
  - `src/solstein/data/fetchers.py:28-80` — YahooFetcher pattern (error handling, retry logic)
  - `src/solstein/infrastructure/repositories.py` — How to store data in PostgreSQL

  **API/Type References**:
  - `edgartools` docs: https://github.com/dgunning/edgartools — Filing parsing API
  - SEC EDGAR: https://www.sec.gov/cgi-bin/browse-edgar — Company ticker lookup

  **Test References**:
  - `tests/unit/data/test_fetchers.py` — Mock API response pattern
  - `tests/integration/test_api.py` — Database storage verification

  **External References**:
  - edgartools GitHub: https://github.com/dgunning/edgartools
  - SEC EDGAR API reference: https://www.sec.gov/sec-api-documentation

  **Acceptance Criteria**:

  > **AGENT-EXECUTABLE VERIFICATION ONLY**

  - [ ] `pytest tests/unit/data/test_sec_edgar_connector.py` → PASS (8/8 tests)
  - [ ] `sec_edgar_connector.fetch_filing("AAPL", 2024, "10-K")` → returns dict with keys: revenue, gross_margin, ebitda, cash_position
  - [ ] Confidence score for all extracted metrics: 0.95 ± 0.02
  - [ ] Error handling test: `fetch_filing("INVALID", 2024, "10-K")` → raises `CompanyNotFoundError` (not silent fail)
  - [ ] Rate limit test: 10 sequential calls complete without throttling (60 req/min limit)

  **QA Scenarios (MANDATORY)**:

  ```
  Scenario: Happy path — Fetch Apple's 2024 10-K filing
    Tool: Bash (Python test)
    Preconditions: edgartools installed, internet connection
    Steps:
      1. from solstein.data.connectors import SECEdgarConnector
      2. connector = SECEdgarConnector()
      3. result = connector.fetch_filing("AAPL", 2024, "10-K")
      4. assert result["revenue_millions"] > 400000  # Apple Q24 revenue
      5. assert result["confidence"] == 0.95
    Expected Result: Dict returned with revenue ≈ 391,000M (±5%), confidence 0.95
    Failure Indicators: Exception raised, revenue < 100k, confidence < 0.90
    Evidence: .sisyphus/evidence/stream-a-happy-path.txt

  Scenario: Error path — Company not found
    Tool: Bash (Python test)
    Preconditions: Same as above
    Steps:
      1. connector = SECEdgarConnector()
      2. try:
           result = connector.fetch_filing("NOTREAL", 2024, "10-K")
         except CompanyNotFoundError as e:
           assert "NOTREAL" in str(e)
    Expected Result: CompanyNotFoundError raised with meaningful message
    Failure Indicators: Silent return None, generic Exception, empty dict
    Evidence: .sisyphus/evidence/stream-a-error-path.txt

  Scenario: Rate limit handling — 20 consecutive requests
    Tool: Bash (Python test)
    Preconditions: Same
    Steps:
      1. for i in range(20):
           result = connector.fetch_filing("AAPL", 2024, "10-K")
           time.sleep(0.2)  # 5 req/sec = within limits
      2. assert all results are valid
    Expected Result: All 20 calls succeed, no 429 errors, no crashes
    Failure Indicators: Any failed request, mixed empty results
    Evidence: .sisyphus/evidence/stream-a-rate-limit.txt
  ```

  **Evidence to Capture**:
  - [ ] pytest output: `stream-a-tests.log`
  - [ ] Sample API response: `stream-a-sample-filing.json`
  - [ ] Error handling test: `stream-a-error-scenarios.txt`

  **Commit**: YES (groups with E)
  - Message: `feat(data): add SEC EDGAR connector for 10-K/10-Q financial parsing`
  - Files: `src/solstein/data/connectors/sec_edgar_connector.py`, `tests/unit/data/test_sec_edgar_connector.py`
  - Pre-commit: `pytest tests/unit/data/test_sec_edgar_connector.py`

---

- [ ] **A2. Financial Metrics Extraction**

  **What to do**:
  - Implement `extract_financial_metrics(filing: Filing) → dict` method
  - Extract: revenue, growth rate, gross margin, net margin, ebitda, cash, debt, runways
  - Calculate derived metrics: burn rate (for private), runway months
  - Map to standardized field names

  **Must NOT do**:
  - ❌ Don't calculate metrics that aren't in filing (use only what SEC provides)
  - ❌ Don't assume currency (check for FX conversion needs)
  - ❌ Don't lose precision (store as float64, not string)

  **Time**: 3-4 hours

  **References**:
  - edgartools docs: https://github.com/dgunning/edgartools/wiki/Financial-Statements
  - SEC XBRL reference: https://www.sec.gov/cgi-bin/viewer?action=view&cik=…

  **Acceptance Criteria**:
  - [ ] Extract 25 financial metrics from 10-K (complete list in code comments)
  - [ ] All 25 metrics present for Apple 2024: revenue, margins, assets, liabilities, cash flow
  - [ ] Derived calculations: burn rate = (cash burn / 12), runway = cash / burn rate
  - [ ] Currency handling: Convert non-USD to USD if needed
  - [ ] Unit normalization: All revenue/cash in millions

  **QA Scenarios**:

  ```
  Scenario: Complete metric extraction
    Tool: Bash (Python)
    Steps:
      1. connector = SECEdgarConnector()
      2. metrics = connector.extract_financial_metrics("AAPL", 2024, "10-K")
      3. required_metrics = ["revenue", "gross_margin", "net_income", "cash_position", "total_debt"]
      4. for m in required_metrics: assert m in metrics and metrics[m] is not None
    Expected Result: All 25 metrics present, no None values for core metrics
    Evidence: .sisyphus/evidence/stream-a-metrics-extraction.json
  ```

---

- [ ] **A3. Error Handling & Retry Logic**

  **What to do**:
  - Implement retry logic for network failures (exponential backoff, 3 retries)
  - Handle SEC API rate limits (429 responses → back off 60 seconds)
  - Handle missing filings (404 → CompanyNotFoundError)
  - Log all failures with timestamps + context

  **Time**: 2-3 hours

  **Acceptance Criteria**:
  - [ ] Rate limit (429): Auto-retry after 60s, succeeds on 2nd attempt
  - [ ] Network timeout: Retries 3x with exponential backoff (1s, 2s, 4s)
  - [ ] Missing filing (404): Raises CompanyNotFoundError (not generic Exception)
  - [ ] All failures logged with: timestamp, company, attempt #, error details

  **QA Scenarios**:

  ```
  Scenario: Rate limit recovery
    Tool: Bash (Python test with mocking)
    Steps:
      1. Mock SEC API: 1st call returns 429, 2nd returns 200 OK
      2. connector.fetch_filing("TEST", 2024, "10-K")
      3. Assert: succeeded (no exception), retried once
    Expected Result: Succeeds on retry, delays observed
    Evidence: .sisyphus/evidence/stream-a-retry-logic.log
  ```

---

### Stream B: Companies House UK Connector (4-5 hours)

- [ ] **B1. Setup & Companies House API Integration**

  **What to do**:
  - Install `requests` (already available)
  - Create `src/solstein/data/connectors/companies_house_connector.py`
  - Implement REST API calls to UK Companies House API (free endpoint)
  - Handle auth (API key in .env, not code)

  **Must NOT do**:
  - ❌ Don't hardcode API key
  - ❌ Don't call API without retry logic
  - ❌ Don't forget UK company number lookup

  **Recommended Agent Profile**:
  > **Category**: `quick`
  > - **Reason**: Straightforward REST API, similar to SEC approach

  **Time**: 2 hours

  **References**:
  - Companies House API: https://beta.companieshouse.gov.uk/
  - API docs: https://developer.companieshouse.gov.uk/

  **Acceptance Criteria**:
  - [ ] `companies_house_connector.fetch_company("00445790")` → Returns dict with company info
  - [ ] Required fields: company_name, registered_office, annual_revenue, total_assets, officers
  - [ ] Error handling: Invalid company number → raises `CompanyNotFoundError`

  **QA Scenarios**:

  ```
  Scenario: Fetch UK company financials
    Tool: Bash (Python)
    Steps:
      1. connector = CompaniesHouseConnector(api_key=os.getenv("CH_API_KEY"))
      2. result = connector.fetch_company("00445790")  # Actual UK company
      3. assert result["revenue_millions"] is not None
      4. assert result["confidence"] == 0.93
    Expected Result: Valid company data returned
    Evidence: .sisyphus/evidence/stream-b-company-fetch.json
  ```

---

- [ ] **B2. Financial Data Extraction & Schema**

  **What to do**:
  - Parse Companies House XML/JSON response
  - Extract 10 core financial metrics (revenue, assets, liabilities, officers)
  - Store with confidence 0.93 (lower than SEC due to less standardization)

  **Time**: 2-3 hours

  **Acceptance Criteria**:
  - [ ] Extract 10 metrics from 5 test UK companies
  - [ ] All metrics present, none NULL
  - [ ] Confidence = 0.93 for all

---

### Stream C: News Signal Detector (6-8 hours)

- [ ] **C1. NewsAPI Setup & Funding Signal Detection**

  **What to do**:
  - Sign up for NewsAPI free tier (100 queries/day limit)
  - Create `src/solstein/data/connectors/news_signal_detector.py`
  - Implement pattern matching for funding rounds: "Series [A-Z]", "raised", "$", "million", "funding"
  - Store signals with timestamp + source URL

  **Must NOT do**:
  - ❌ Don't exceed 100 queries/day (track usage)
  - ❌ Don't store duplicate signals (deduplicate by (company_id, signal_type, date))
  - ❌ Don't lowercase company names in queries (precision matters)

  **Recommended Agent Profile**:
  > **Category**: `quick`
  > - **Reason**: Pattern matching, straightforward API

  **Time**: 3-4 hours

  **References**:
  - NewsAPI: https://newsapi.org/
  - Query syntax: https://newsapi.org/docs

  **Acceptance Criteria**:
  - [ ] `news_detector.detect_funding_signal("Kraken Technologies")` → Returns list of funding announcements
  - [ ] Pattern matching: Find "Series B", "$100 million", "announced funding" in news
  - [ ] Confidence: 0.75 for funding signals (news can be speculative)
  - [ ] Deduplication: Same signal not stored twice

  **QA Scenarios**:

  ```
  Scenario: Detect recent funding announcement
    Tool: Bash (Python)
    Steps:
      1. detector = NewsSignalDetector(api_key=os.getenv("NEWSAPI_KEY"))
      2. signals = detector.detect_funding_signal("Kraken Technologies")
      3. assert len(signals) > 0
      4. assert signals[0]["signal_type"] == "funding_round"
      5. assert signals[0]["confidence"] == 0.75
    Expected Result: At least one signal found, properly structured
    Evidence: .sisyphus/evidence/stream-c-funding-signals.json

  Scenario: Deduplicate identical signals
    Tool: Bash (Python)
    Steps:
      1. detector.detect_funding_signal("Kraken")
      2. detector.detect_funding_signal("Kraken Technologies")  # Same company, different query
      3. signals_db = fetch_signals_from_db(company_id)
      4. assert len(signals_db) == len(set(signals_db))  # No duplicates
    Expected Result: Duplicates removed, single record stored
    Evidence: .sisyphus/evidence/stream-c-dedup.log
  ```

---

- [ ] **C2. Partnership & Key Hire Detection**

  **What to do**:
  - Add pattern matching for partnerships: "partnership", "collaboration", "integrates with"
  - Add pattern matching for key hires: "appoints", "joins", "new CEO", "Chief", "executive"
  - Confidence: 0.70-0.75 (news can be inaccurate)

  **Time**: 2-3 hours

  **Acceptance Criteria**:
  - [ ] Pattern matches for partnerships (list 5+ keywords)
  - [ ] Pattern matches for key hires (list 5+ keywords)
  - [ ] Confidence scoring: news signals get 0.70-0.75

---

- [ ] **C3. Rate Limiting & Query Optimization**

  **What to do**:
  - Track API usage (log queries, remaining budget)
  - Implement exponential backoff for rate limits
  - Optimize queries to fit 100/day budget: batch companies, daily scan

  **Time**: 1-2 hours

  **Acceptance Criteria**:
  - [ ] Daily budget: 100 queries tracked, warning if approaching limit
  - [ ] Query optimization: Batch 10 companies per query (using OR logic)
  - [ ] Retry logic: 429 response → exponential backoff

---

### Stream D: GitHub Enhanced Analysis (5-6 hours)

- [ ] **D1. Extend GitHub Agent with Velocity & Trends**

  **What to do**:
  - Extend existing GitHub agent: `src/solstein/agents/github_agent.py`
  - Add: commit frequency trend (accelerating/decelerating)
  - Add: language distribution over time
  - Add: dependency health (requirement versions, outdated packages)

  **Must NOT do**:
  - ❌ Don't break existing GitHub functionality
  - ❌ Don't exceed GitHub API rate limits (60 req/hr unauthenticated)

  **Recommended Agent Profile**:
  > **Category**: `quick`
  > - **Reason**: Extend existing code, no new patterns

  **Time**: 3-4 hours

  **References**:
  - Existing: `src/solstein/agents/github_agent.py:1-50`
  - GitHub API: https://docs.github.com/en/rest

  **Acceptance Criteria**:
  - [ ] Commit frequency: Extract last 90 days, calculate commits/week trend
  - [ ] Language distribution: Parse repository languages, track changes
  - [ ] Dependency health: Parse requirements.txt/package.json, identify outdated versions
  - [ ] Signals: "Engineering velocity increasing 20% month-over-month"

  **QA Scenarios**:

  ```
  Scenario: Extract engineering velocity trend
    Tool: Bash (Python)
    Steps:
      1. github_agent.analyze_repository("solstein-repo-url")
      2. velocity = github_agent.get_commit_frequency_trend()
      3. assert velocity["direction"] in ["accelerating", "stable", "decelerating"]
      4. assert "confidence" in velocity
    Expected Result: Trend detected with confidence score
    Evidence: .sisyphus/evidence/stream-d-velocity.json
  ```

---

- [ ] **D2. Dependency Health Analysis**

  **What to do**:
  - Parse requirements.txt / package.json
  - Check for outdated dependencies (compare to latest versions on PyPI/npm)
  - Flag security vulnerabilities (check against known CVEs)
  - Confidence: 0.85 (automated, reliable)

  **Time**: 2-3 hours

  **Acceptance Criteria**:
  - [ ] Parse Python requirements.txt: identify 5+ dependencies
  - [ ] Parse JavaScript package.json: identify 5+ dependencies
  - [ ] Flag outdated: package version < latest by >3 minor versions
  - [ ] Security check: Cross-reference against CVE database (npm audit, pip audit)

  **QA Scenarios**:

  ```
  Scenario: Identify outdated dependencies
    Tool: Bash (Python)
    Steps:
      1. agent.analyze_dependencies(repo_url)
      2. outdated = agent.get_outdated_packages()
      3. assert len(outdated) >= 0  # May have none (good) or some
      4. for pkg in outdated:
           assert pkg["current_version"] < pkg["latest_version"]
    Expected Result: List of outdated packages with version info
    Evidence: .sisyphus/evidence/stream-d-dependencies.json
  ```

---

### Stream E: Fact Model & Database Schema (4-5 hours)

- [ ] **E1. PostgreSQL Schema: Facts Table**

  **What to do**:
  - Create/migrate Postgres schema for facts storage
  - Table: `facts` — immutable fact records
  - Table: `gathering_batches` — track which facts were gathered when
  - Table: `fact_sources` — audit trail (which API returned this fact)

  **Must NOT do**:
  - ❌ Don't modify existing tables (only add new ones)
  - ❌ Don't lose existing company data
  - ❌ Don't use SERIAL for IDs (use UUID for distributed systems)

  **Recommended Agent Profile**:
  > **Category**: `quick`
  > - **Reason**: Schema design (straightforward, no business logic)

  **Time**: 2-3 hours

  **SQL Schema**:

  ```sql
  CREATE TABLE gathering_batches (
    batch_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'in_progress',  -- in_progress, completed, failed
    FOREIGN KEY (company_id) REFERENCES companies(id)
  );

  CREATE TABLE facts (
    fact_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id VARCHAR(255) NOT NULL,
    batch_id UUID NOT NULL,
    fact_type VARCHAR(100) NOT NULL,  -- e.g., "annual_revenue", "series_b_funding"
    value NUMERIC,  -- For numeric facts
    value_str VARCHAR(500),  -- For text facts
    value_date DATE,  -- For date facts
    confidence NUMERIC(3, 2) DEFAULT 0.5,  -- 0.0 - 1.0
    extracted_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (fact_id),
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (batch_id) REFERENCES gathering_batches(batch_id),
    INDEX idx_company_fact (company_id, fact_type)
  );

  CREATE TABLE fact_sources (
    source_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fact_id UUID NOT NULL,
    source_type VARCHAR(100) NOT NULL,  -- "sec_edgar", "companies_house", "newsapi", "github"
    source_url VARCHAR(1000),
    extraction_timestamp TIMESTAMP DEFAULT NOW(),
    raw_content TEXT,  -- Store original API response for audit trail
    FOREIGN KEY (fact_id) REFERENCES facts(fact_id)
  );

  CREATE INDEX idx_fact_type ON facts(fact_type);
  CREATE INDEX idx_company_batch ON gathering_batches(company_id, created_at);
  ```

  **Acceptance Criteria**:
  - [ ] All tables created without errors
  - [ ] Foreign key constraints enforced
  - [ ] Indexes created on common queries
  - [ ] Can insert 1000 facts with diverse types
  - [ ] Query: `SELECT * FROM facts WHERE company_id = 'X'` returns all company facts

  **QA Scenarios**:

  ```
  Scenario: Create and query facts
    Tool: Bash (SQL/Python)
    Steps:
      1. psql < src/solstein/infrastructure/migrations/001_facts_schema.sql
      2. INSERT INTO gathering_batches (company_id) VALUES ('test-company')
      3. INSERT INTO facts (company_id, batch_id, fact_type, value, confidence)
         VALUES ('test-company', $1, 'annual_revenue', 1000000, 0.95)
      4. SELECT * FROM facts WHERE company_id = 'test-company'
      5. assert result.fact_type == 'annual_revenue'
    Expected Result: Fact stored and retrievable
    Evidence: .sisyphus/evidence/stream-e-schema-test.log
  ```

---

- [ ] **E2. Python ORM Models**

  **What to do**:
  - Create SQLAlchemy models for Fact, GatheringBatch, FactSource
  - Implement `FactRepository` for CRUD operations
  - Add validation (confidence 0.0-1.0, required fields)

  **Time**: 2-3 hours

  **Code Structure**:

  ```python
  # src/solstein/domain/facts.py
  from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey
  from sqlalchemy.orm import relationship
  from datetime import datetime

  class Fact(Base):
      __tablename__ = "facts"
      
      fact_id: str = Column(String, primary_key=True)
      company_id: str = Column(String, ForeignKey("companies.id"))
      fact_type: str = Column(String(100))
      value: float = Column(Numeric)
      confidence: float = Column(Numeric(3, 2))  # 0.0 - 1.0
      extracted_at: datetime = Column(DateTime, default=datetime.utcnow)
      
      sources: List["FactSource"] = relationship("FactSource")
      
      def validate(self):
          assert 0.0 <= self.confidence <= 1.0, "Confidence must be 0.0-1.0"
          assert self.fact_type is not None, "Fact type required"
  
  # src/solstein/infrastructure/repositories.py
  class FactRepository:
      def store(self, fact: Fact) -> str:
          """Store fact, return fact_id"""
          fact.validate()
          session.add(fact)
          session.commit()
          return fact.fact_id
      
      def get_company_facts(self, company_id: str) -> List[Fact]:
          """Fetch all facts for company"""
          return session.query(Fact).filter_by(company_id=company_id).all()
  ```

  **Acceptance Criteria**:
  - [ ] Create Fact object, validate confidence 0.0-1.0
  - [ ] Store in DB via repository
  - [ ] Retrieve all company facts
  - [ ] Query by fact_type

---

### Stream F: Scoring Engine Integration (4-6 hours)

- [ ] **F1. Integrate Financial Data into Growth Score**

  **What to do**:
  - Modify `src/solstein/analytics/scorers/growth_momentum.py`
  - Use SEC revenue data: current + YoY growth
  - Calculate growth signal: revenue growth % → score component
  - Blend with existing signals (GitHub commits, news)

  **Must NOT do**:
  - ❌ Don't break existing GitHub-based scoring
  - ❌ Don't overwrite user-provided data with API data (merge)

  **Recommended Agent Profile**:
  > **Category**: `unspecified-high`
  > - **Reason**: Logic integration (higher risk), needs careful testing

  **Time**: 2-3 hours

  **References**:
  - Existing scorer: `src/solstein/analytics/scorers/growth_momentum.py:1-50`

  **Acceptance Criteria**:
  - [ ] Growth Score now incorporates revenue growth data
  - [ ] Formula: Growth Score = 0.4 * GitHub_signals + 0.4 * Revenue_growth + 0.2 * News_signals
  - [ ] Example: Company with 30% YoY revenue growth gets +1.0 to Growth Score
  - [ ] Explainability: `company.growth_score_breakdown()` shows each component

  **QA Scenarios**:

  ```
  Scenario: Growth score with financial data
    Tool: Bash (Python)
    Steps:
      1. company = Company(id="test", name="Test Co")
      2. # Inject financial facts
      3. fact_repo.store(Fact(company_id="test", fact_type="annual_revenue", value=1000000, confidence=0.95))
      4. fact_repo.store(Fact(company_id="test", fact_type="revenue_growth_yoy", value=30, confidence=0.95))
      5. growth_score = scorer.score(company)
      6. assert 6.0 < growth_score < 8.0  # 30% growth should be strong
    Expected Result: Growth score reflects revenue growth
    Evidence: .sisyphus/evidence/stream-f-growth-score.json
  ```

---

- [ ] **F2. Integrate Financial Data into Financial Health Score**

  **What to do**:
  - Create new scorer: `src/solstein/analytics/scorers/financial_health.py`
  - Components: cash runway (0.3), profitability (0.2), revenue size (0.2), debt ratio (0.3)
  - Use SEC + news data
  - Confidence: inherit from source confidence

  **Time**: 2-3 hours

  **Acceptance Criteria**:
  - [ ] Financial Health Score combines 4+ metrics
  - [ ] Company with 24mo runway + profitable gets 7.0+
  - [ ] Company with 3mo runway gets < 3.0
  - [ ] Explainability: Show each component weight

  **QA Scenarios**:

  ```
  Scenario: Financial health scoring
    Tool: Bash (Python)
    Steps:
      1. company = Company(id="test")
      2. # Healthy company
      3. fact_repo.store(Fact(..., fact_type="cash_runway_months", value=24, confidence=0.95))
      4. fact_repo.store(Fact(..., fact_type="gross_margin", value=70, confidence=0.95))
      5. health_score = scorer.score(company)
      6. assert health_score > 6.0  # Healthy
      7. # Struggling company
      8. company2 = Company(id="test2")
      9. fact_repo.store(Fact(..., fact_type="cash_runway_months", value=3, confidence=0.95))
      10. health_score2 = scorer.score(company2)
      11. assert health_score2 < 3.0  # At risk
    Expected Result: Healthy > Struggling
    Evidence: .sisyphus/evidence/stream-f-financial-health.json
  ```

---

### Stream G: Integration Tests & Golden Dataset (6-8 hours)

- [ ] **G1. End-to-End Integration Test**

  **What to do**:
  - Create test: `tests/integration/test_data_gathering_e2e.py`
  - Flow: Company ID → fetch all 4 connectors → store facts → scoring engine
  - Verify: No errors, facts stored, scoring updated

  **Must NOT do**:
  - ❌ Don't call real APIs without mocking (tests must be fast)
  - ❌ Don't require API keys in test environment (mock responses)

  **Recommended Agent Profile**:
  > **Category**: `unspecified-high`
  > - **Reason**: QA & integration (complex scenarios)

  **Time**: 3-4 hours

  **References**:
  - Existing test pattern: `tests/integration/test_api.py`
  - Mock pattern: `tests/fixtures/mock_responses.py`

  **Acceptance Criteria**:
  - [ ] Test retrieves 5 test companies
  - [ ] All 4 connectors return data (mocked)
  - [ ] All facts stored in database with confidence scores
  - [ ] Scoring engine successfully ingests new facts
  - [ ] No errors, all assertions pass
  - [ ] Test completes in < 10 seconds (no real API calls)

  **QA Scenarios**:

  ```
  Scenario: Full data gathering pipeline
    Tool: Bash (Python test)
    Steps:
      1. Mock all APIs: SEC, CH, NewsAPI, GitHub
      2. company_id = "test-company"
      3. orchestrator = DataGatheringOrchestrator()
      4. result = orchestrator.gather_all_data(company_id)
      5. assert result["sec_data"]["revenue_millions"] > 0
      6. assert result["news_signals"] is not None
      7. assert result["github_stats"] is not None
      8. facts = fact_repo.get_company_facts(company_id)
      9. assert len(facts) > 50  # Should have 50+ facts
    Expected Result: All data sources integrated, facts stored
    Evidence: .sisyphus/evidence/stream-g-e2e-test.log
  ```

---

- [ ] **G2. Golden Dataset Regression Tests**

  **What to do**:
  - Create golden dataset: 5 known companies with expected scores
  - Example: Apple 2024 → expected Growth Score 7.5 ± 0.5
  - Test: Run connector → compare actual vs. expected
  - Regression protection: New changes can't break known cases

  **Time**: 2-3 hours

  **Golden Dataset Example**:

  ```json
  {
    "company_id": "AAPL",
    "company_name": "Apple Inc",
    "expected_metrics": {
      "annual_revenue_millions": {"value": 391000, "tolerance": "±2%"},
      "revenue_growth_yoy": {"value": 5, "tolerance": "±3%"},
      "gross_margin": {"value": 48, "tolerance": "±2%"}
    },
    "expected_scores": {
      "growth_score": {"value": 7.0, "tolerance": "±0.5"},
      "financial_health": {"value": 8.5, "tolerance": "±0.5"}
    }
  }
  ```

  **Acceptance Criteria**:
  - [ ] 5 golden companies tested
  - [ ] All metrics within tolerance
  - [ ] Growth Score predictions within ±0.5
  - [ ] Financial Health Score within ±0.5
  - [ ] Test fails if any regression detected

  **QA Scenarios**:

  ```
  Scenario: Regression test — Apple metrics
    Tool: Bash (Python)
    Steps:
      1. Load golden dataset: AAPL expected revenue $391B
      2. connector.fetch_filing("AAPL", 2024, "10-K")
      3. actual_revenue = result["revenue_millions"]
      4. expected_revenue = 391000
      5. error_pct = abs(actual_revenue - expected_revenue) / expected_revenue * 100
      6. assert error_pct < 2.0  # Within 2% tolerance
    Expected Result: Actual matches golden within tolerance
    Evidence: .sisyphus/evidence/stream-g-golden-apple.json
  ```

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Rejection → fix → re-run.

- [ ] **V1. Data Correctness Audit** — `oracle`
  
  **What to verify**: Read each connector code. For each data source (SEC, CH, News, GitHub):
  - Is the parsing logic correct? (Not missing fields, not corrupting data)
  - Are confidence scores justified? (Is SEC really 0.95? Is news 0.75?)
  - Are error cases handled? (No silent failures, proper exceptions)
  - Is the schema sound? (No data type mismatches, proper constraints)
  
  **Output**: `✅ All connectors safe to use` OR `❌ Issues: [list]`

---

- [ ] **V2. Performance & Scale Check** — `unspecified-high`
  
  **What to verify**: Can this actually run?
  - Fetch 100 companies from all 4 sources, measure time
  - Check for memory leaks (process memory doesn't grow unbounded)
  - Verify: Completes in < 15 minutes for 100 companies
  - Rate limit compliance: Uses < 100 NewsAPI queries/day
  
  **Output**: `Performance: 100 companies in 12 minutes ✅` OR `Issues: [slowness, memory]`

---

- [ ] **V3. Integration Success Verification** — `unspecified-high`
  
  **What to verify**: Run the full pipeline end-to-end
  - 10 test companies → all 4 connectors → facts database → scoring engine
  - Scoring engine produces Growth Score + Financial Health Score
  - Every fact has source URL + confidence
  - No crashes, no warnings, all logs clean
  
  **Output**: `End-to-end pipeline working ✅` OR `Issues: [integration failures]`

---

- [ ] **V4. Test Coverage & Quality** — `deep`
  
  **What to verify**: Are we actually testing this?
  - `pytest --cov=src/solstein/data` shows 80%+ coverage
  - All error paths tested (network failure, rate limit, invalid data)
  - All happy paths tested with real-like data
  - Golden dataset tests pass
  
  **Output**: `Coverage: 85% | All tests passing ✅` OR `Issues: [gaps, failures]`

---

## Commit Strategy

### Commit Points

**After Stream A (SEC Connector)**:
```bash
git add src/solstein/data/connectors/sec_edgar_connector.py tests/unit/data/test_sec_edgar_connector.py
git commit -m "feat(data): add SEC EDGAR financial data connector

- Fetch 10-K/10-Q filings for US public companies
- Extract 25 financial metrics (revenue, margins, cash, debt)
- Implement retry logic for rate limits (429 handling)
- All metrics confidence-scored 0.95 (SEC is authoritative)
- Tested: 100% of extraction logic, error handling"
```

**After Stream B+C (CH + News)**:
```bash
git commit -m "feat(data): add Companies House and news signal connectors

- Companies House API connector for UK/EU companies
- News signal detector: funding rounds, partnerships, key hires
- All signals confidence-scored 0.70-0.75
- Rate limit compliance: 100 NewsAPI queries/day"
```

**After Stream D (GitHub)**:
```bash
git commit -m "feat(agents): enhance GitHub analysis with velocity & dependencies

- Add commit frequency trend (accelerating/decelerating)
- Add language distribution tracking
- Add dependency health checks (outdated, security CVEs)
- All metrics include confidence scores"
```

**After Stream E (Schema)**:
```bash
git commit -m "feat(db): add facts storage schema for multi-source data

- Create facts, gathering_batches, fact_sources tables
- Add SQLAlchemy ORM models
- Add FactRepository for CRUD operations
- Supports audit trail: every fact tracks source + confidence"
```

**After Stream F (Integration)**:
```bash
git commit -m "feat(scoring): integrate financial data into growth/health scores

- Growth Score now 40% revenue-based (was 100% GitHub-based)
- New Financial Health Score: 30 cash runway, 20% profit, 30% debt ratio
- Full explainability: each score component shows contributing data
- Backward compatible: existing GitHub-based scoring still works"
```

**After Stream G (Tests)**:
```bash
git commit -m "test: add end-to-end integration tests and golden dataset

- E2E test: company → all connectors → facts → scores
- Golden dataset regression: 5 known companies validate metrics
- All tests pass, 85%+ coverage on data layer
- No real API calls (all mocked)"
```

---

## Success Criteria

### Week 1 Completion Criteria
- ✅ All 4 connectors (SEC, CH, News, GitHub) fetching data without errors
- ✅ All facts stored in PostgreSQL with confidence scores
- ✅ No manual intervention needed (fully automated)
- ✅ 80%+ test coverage for data layer

### Week 2 Completion Criteria
- ✅ Scoring engine ingests new financial data types
- ✅ Growth Score now reflects revenue growth (not just GitHub)
- ✅ Financial Health Score implemented (0-10 scale)
- ✅ Full end-to-end pipeline tested with golden dataset
- ✅ 5 test companies produce reasonable scores

### Overall Success (Both Weeks)
- ✅ Data coverage: 8% → 40% (financial + growth signals + news)
- ✅ Scoring now uses 5+ different data sources
- ✅ PE analyst can ask "Why did company X score 7.2?" and see full breakdown
- ✅ System processes 50+ companies in < 2 days (vs. 3 days manual)
- ✅ Zero paid APIs required (all free tier)
- ✅ Production-ready: error handling, logging, monitoring

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| SEC API rate limiting (100 req/min) | Connector blocks | Implement queue + exponential backoff, batch requests |
| NewsAPI 100 queries/day exhausted | Signal detection stops | Batch companies in single query, skip on exhaustion |
| GitHub API 60 req/hr limit | Repository analysis slow | Cache results, reuse from batch runs |
| Conflicting data (SEC says $1B revenue, news says $900M) | Accuracy doubt | Confidence scoring: trust SEC 0.95, news 0.75 |
| Database migration complexity | Data corruption | Test on staging first, reversible migrations only |
| Score calculation errors | Invalid scoring | Golden dataset regression prevents breakage |

---

## Next Steps (After Completion)

✅ **Week 3-4**: Multi-agent orchestration (Wave 2)  
✅ **Week 5-6**: Enrichment pipeline & conflict resolution (Wave 3)  
✅ **Week 7+**: Paid API integrations (if validated)

---

**Status**: Ready for implementation kickoff  
**Last Updated**: February 24, 2026  
**Prepared By**: Prometheus (Planning AI) + Research Team
