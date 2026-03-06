# Epic: Testing Infrastructure Enhancement (EPIC-029)

## Overview
Build a world-class testing infrastructure with comprehensive test coverage, automated testing at multiple levels, and quality gates that prevent regressions. Transform testing from a bottleneck into a competitive advantage.

## Background
Current testing gaps:
- Test coverage unknown (likely low)
- Slow test execution
- Limited test types (mostly unit)
- No contract testing
- No visual regression testing
- Flaky tests not tracked
- No mutation testing

## Goals
- [ ] 80%+ code coverage
- [ ] All tests pass in <5 minutes
- [ ] Zero flaky tests
- [ ] Comprehensive test pyramid
- [ ] Automated regression detection
- [ ] Mutation score >70%

## Test Pyramid Target
```
       /\
      /  \      E2E Tests (10%)
     /----\     
    /      \    Integration Tests (30%)
   /--------\
  /          \  Unit Tests (60%)
 /------------\
```

---

## Stories

### Story 1: Test Coverage Improvement
**Points:** 13
**Priority:** P0

Achieve 80%+ code coverage.

**Current State Analysis:**
```bash
# Measure current coverage
pytest --cov=src/solstein --cov-report=html --cov-report=term-missing

# Expected output:
# Name                          Stmts   Miss  Cover   Missing
# -----------------------------------------------------------
# src/solstein/domain/models.py   200    100    50%   45-90, 120-150
# ...
```

**Coverage Strategy:**

**Priority 1 - Critical Paths (Week 1-2):**
- Domain models
- Scoring algorithms
- Data conversion
- API endpoints

**Priority 2 - Business Logic (Week 3-4):**
- Research pipeline stages
- Enrichment logic
- Export generation
- Validation rules

**Priority 3 - Infrastructure (Week 5-6):**
- Database repositories
- Cache layer
- External API clients
- Background tasks

**Testing Approach:**
```python
# Property-based testing with Hypothesis
from hypothesis import given, strategies as st

@given(st.floats(min_value=0, max_value=1000))
def test_score_classification(score_value):
    """Test that any valid score produces a valid classification."""
    result = classify_company(score_value)
    assert result in [CompanyClassification.PHOENIX, 
                     CompanyClassification.SALT, 
                     CompanyClassification.LEAD]

# Mutation testing
# Install: pip install mutmut
# Run: mutmut run
# Target: >70% mutation score
```

**Acceptance Criteria:**
- [ ] 80%+ line coverage
- [ ] 90%+ branch coverage for critical paths
- [ ] 0 uncovered critical functions
- [ ] Coverage report in CI

---

### Story 2: Mutation Testing Implementation
**Points:** 8
**Priority:** P0

Implement mutation testing to verify test quality.

**What is Mutation Testing?**
```
Original code:  def add(a, b): return a + b
Mutant:         def add(a, b): return a - b  # Mutant

Test:           assert add(2, 3) == 5

If test passes with mutant → WEAK TEST (mutant survived)
If test fails with mutant → STRONG TEST (mutant killed)
```

**Configuration:**
```ini
# setup.cfg
[mutmut]
paths_to_mutate=src/solstein
runner=pytest
tests_dir=tests

# Skip files
exclude=tests/*,venv/*,__pycache__/*
```

**CI Integration:**
```yaml
- name: Mutation Testing
  run: |
    mutmut run
    mutmut results
    
    # Fail if mutation score < 70%
    SCORE=$(mutmut results --json | jq '.mutation_score')
    if (( $(echo "$SCORE < 70" | bc -l) )); then
      echo "Mutation score $SCORE is below 70%"
      exit 1
    fi
```

**Target:**
- Mutation score: >70%
- Kill rate: >90% for critical code

---

### Story 3: Contract Testing
**Points:** 8
**Priority:** P0

Test API contracts with external services.

**Why Contract Testing?**
```
Your App -> External API (LinkedIn, Crunchbase)

Problem: External API changes break your app
Solution: Contract tests catch changes early
```

**Implementation with Pact:**
```python
# tests/contracts/test_linkedin_provider.py
import pytest
from pact import Consumer, Provider

@pytest.fixture
def pact():
    return Consumer('solstein').has_pact_with(Provider('linkedin'))

def test_get_company_profile(pact):
    expected = {
        "name": "Test Company",
        "industry": "Software",
        "employees": 100
    }
    
    (pact
     .given('company exists')
     .upon_receiving('a request for company profile')
     .with_request('GET', '/v2/organizations/test-company')
     .will_respond_with(200, body=expected))
    
    with pact:
        result = linkedin_client.get_company('test-company')
        assert result.name == "Test Company"
```

**Consumer-Driven Contracts:**
```python
# tests/contracts/test_api_consumer.py
# For external consumers of our API

def test_get_company_contract(pact):
    """Contract with external API consumers."""
    (pact
     .given('company exists')
     .upon_receiving('get company by ID')
     .with_request('GET', '/api/v1/companies/123')
     .will_respond_with(200, body={
         'id': '123',
         'name': 'Test',
         'classification': 'Phoenix'
     }))
```

**Contract Broker:**
- Store contracts centrally
- Verify on CI
- Notify on breaking changes

---

### Story 4: Visual Regression Testing
**Points:** 5
**Priority:** P1

Test PDF/Excel exports for visual changes.

**PDF Comparison:**
```python
# tests/visual/test_pdf_export.py
import pytest
from pdf_diff import compare_pdfs

def test_company_report_pdf():
    """Test that PDF export hasn't changed visually."""
    # Generate new PDF
    new_pdf = generate_company_report(company_id="test")
    
    # Compare with baseline
    diff = compare_pdfs(
        baseline="tests/baselines/company_report.pdf",
        new=new_pdf
    )
    
    assert diff.similarity > 0.99, f"PDF changed: {diff.diff_pixels} pixels"
```

**Excel Comparison:**
```python
def test_excel_export_structure():
    """Test Excel export structure."""
    excel_file = generate_excel_export()
    
    # Verify sheets exist
    assert "Companies" in excel_file.sheets
    assert "Metrics" in excel_file.sheets
    
    # Verify column headers
    assert excel_file.sheets["Companies"].headers == [
        "ID", "Name", "Industry", "Revenue"
    ]
```

**Baseline Management:**
```bash
# Update baselines when intentional change
pytest tests/visual/ --update-baselines
```

---

### Story 5: Flaky Test Detection & Resolution
**Points:** 5
**Priority:** P1

Eliminate flaky tests.

**Flaky Test Detection:**
```python
# pytest-rerunfailures
pytest --reruns 3 --reruns-delay 1

# Detect flakes
pytest --count 10  # Run each test 10 times
```

**Common Flake Causes:**

**1. Time-based tests:**
```python
# BAD
def test_timestamp():
    result = create_record()
    assert result.created_at == datetime.now()  # Flaky!

# GOOD
from freezegun import freeze_time

@freeze_time("2026-03-06 12:00:00")
def test_timestamp():
    result = create_record()
    assert result.created_at == datetime(2026, 3, 6, 12, 0, 0)
```

**2. Async timing:**
```python
# BAD
async def test_async_operation():
    await operation()
    await asyncio.sleep(0.1)  # Flaky!
    assert result.ready

# GOOD
async def test_async_operation():
    await operation()
    # Wait with timeout
    for _ in range(50):
        if result.ready:
            break
        await asyncio.sleep(0.01)
    assert result.ready
```

**3. Database isolation:**
```python
# Ensure test isolation
@pytest.fixture(autouse=True)
def clean_db(db_session):
    yield
    db_session.rollback()
```

**Flaky Test Dashboard:**
- Track flakiness over time
- Alert when new flaky test detected
- Block PRs that introduce flakiness

---

### Story 6: Test Performance Optimization
**Points:** 5
**Priority:** P1

Make tests fast and parallel.

**Parallel Execution:**
```bash
# pytest-xdist
pytest -n auto  # Use all CPU cores
pytest -n 8     # Use 8 workers

# For integration tests (shared DB)
pytest -n 4 --dist=loadscope  # Group by module
```

**Test Time Tracking:**
```python
# pytest-slow
@pytest.mark.slow  # Tests >1s
@pytest.mark.fast  # Tests <100ms

# Run only fast during development
pytest -m fast

# Run slow only in CI
pytest -m slow
```

**Fixture Optimization:**
```python
# Session-scoped for expensive setup
@pytest.fixture(scope="session")
def test_db():
    """Create test database once."""
    db = create_test_database()
    yield db
    db.cleanup()

# Module-scoped for test data
@pytest.fixture(scope="module")
def sample_companies():
    """Create sample companies once per module."""
    return [
        Company(name="Company A"),
        Company(name="Company B"),
    ]
```

**Target:** All tests complete in <5 minutes

---

### Story 7: Test Data Factories
**Points:** 3
**Priority:** P1

Create comprehensive test data factories.

**Factory Boy Implementation:**
```python
# tests/factories.py
import factory
from solstein.domain.models import Company, FinancialMetric

class CompanyFactory(factory.Factory):
    class Meta:
        model = Company
    
    id = factory.Sequence(lambda n: f"company-{n}")
    name = factory.Faker('company')
    industry = factory.Faker('bs')
    revenue = factory.Faker('random_number', digits=3)
    
    @factory.post_generation
    def with_financials(self, create, extracted, **kwargs):
        if create:
            FinancialMetricFactory(company=self)

class FinancialMetricFactory(factory.Factory):
    class Meta:
        model = FinancialMetric
    
    revenue = 100.0
    growth_rate = 25.0
    employees = 100
```

**Usage:**
```python
def test_company_scoring():
    # Create test data easily
    company = CompanyFactory(
        revenue=500,
        growth_rate=50
    )
    
    score = calculate_score(company)
    assert score > 7.0  # Should be Phoenix
```

**Faker Integration:**
```python
# Realistic but fake data
company = CompanyFactory(
    name="Acme Corporation",
    website="https://acme.example.com",
    founded_year=2015
)
```

---

### Story 8: Load and Stress Testing
**Points:** 8
**Priority:** P2

Test system under load.

**Load Testing with Locust:**
```python
# tests/load/locustfile.py
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def get_company(self):
        self.client.get("/api/v1/companies/123")
    
    @task(1)
    def create_research(self):
        self.client.post("/api/v1/research", json={
            "market": "energy",
            "company": "test"
        })
```

**Performance Benchmarks:**
```python
# tests/performance/test_api.py
import pytest
from pytest_benchmark.fixture import BenchmarkFixture

@pytest.mark.benchmark
class TestAPIPerformance:
    def test_get_company_latency(self, benchmark: BenchmarkFixture):
        """Benchmark company retrieval."""
        result = benchmark(client.get, "/api/v1/companies/123")
        assert result.elapsed.total_seconds() < 0.1
    
    def test_enrichment_throughput(self, benchmark: BenchmarkFixture):
        """Benchmark enrichment pipeline."""
        companies = [CompanyFactory() for _ in range(10)]
        benchmark(enrich_companies, companies)
```

**Chaos Testing:**
```python
# tests/chaos/test_resilience.py
@pytest.mark.chaos
def test_database_failure_resilience():
    """Test system behavior when DB fails."""
    with simulate_database_failure():
        response = client.get("/api/v1/companies/123")
        # Should return cached data or graceful error
        assert response.status_code in [200, 503]
```

---

## Test Infrastructure

### CI/CD Test Pipeline
```yaml
name: Test Suite
on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run unit tests
        run: pytest tests/unit -n auto --cov=src
      
  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
      redis:
        image: redis:7
    steps:
      - name: Run integration tests
        run: pytest tests/integration -v
  
  mutation-testing:
    runs-on: ubuntu-latest
    steps:
      - name: Run mutation tests
        run: |
          mutmut run
          mutmut results --ci
  
  contract-tests:
    runs-on: ubuntu-latest
    steps:
      - name: Verify contracts
        run: pytest tests/contracts --verify-pacts
```

### Test Organization
```
tests/
├── unit/                    # Fast, isolated tests
│   ├── domain/
│   ├── analytics/
│   └── api/
├── integration/             # Database, external APIs
│   ├── repositories/
│   ├── services/
│   └── api/
├── e2e/                     # Full workflows
│   └── test_research_pipeline.py
├── contracts/               # API contracts
│   ├── test_linkedin_provider.py
│   └── test_api_consumer.py
├── visual/                  # PDF/Excel comparison
│   └── test_exports.py
├── performance/             # Load tests
│   ├── test_latency.py
│   └── locustfile.py
├── chaos/                   # Resilience tests
│   └── test_resilience.py
├── factories.py             # Test data factories
├── conftest.py             # Shared fixtures
└── baselines/              # Visual test baselines
```

---

## Definition of Done
- [ ] 80%+ code coverage
- [ ] >70% mutation score
- [ ] All tests <5 min
- [ ] Zero flaky tests
- [ ] Contract tests passing
- [ ] Load tests defined

## Estimated Effort
- **Total Points:** 55
- **Duration:** 9-11 weeks
- **Team:** 1 QA engineer + 1 developer

## Dependencies
- EPIC-012 (Testing) - Builds on existing tests
- EPIC-019 (Code Quality) - Coverage enforcement

---

*Created: 2026-03-06*  
*Target Release: Q4 2026*
