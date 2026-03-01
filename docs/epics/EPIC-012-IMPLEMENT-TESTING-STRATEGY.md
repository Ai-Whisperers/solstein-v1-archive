# EPIC-012: Implement Testing Strategy

## Status: 🔴 CRITICAL
## Priority: P0 - System Blocking
## Effort: 8 story points
## Sprint: Required for quality assurance

---

## Problem Statement

The system has **minimal test coverage**, making it impossible to verify fixes or prevent regressions.

### Current Broken State
```
Test Coverage: Unknown (likely < 20%)
Unit Tests: Minimal
Integration Tests: None
E2E Tests: None
Test Data: Synthetic only
```

### Impact
- **Cannot verify fixes** work correctly
- **Regressions go undetected**
- **No confidence** in system reliability
- **Cannot refactor safely**

---

## Success Criteria

- [ ] Unit test coverage > 80% for scoring logic
- [ ] Integration tests for data pipeline
- [ ] E2E tests for complete workflow
- [ ] Test data fixtures for all scenarios
- [ ] Automated test runs in CI/CD
- [ ] Regression test suite

---

## Technical Analysis

### Testing Gaps
1. **No unit tests** for scoring algorithms
2. **No integration tests** for data pipeline
3. **No E2E tests** for complete workflow
4. **No test fixtures** for different company types
5. **No performance tests**

### Affected Areas
- All scoring modules
- Data conversion pipeline
- Excel export
- Enrichment system

---

## Stories

### Story 12.1: Create Test Fixtures
**Priority:** P0 | **Effort:** 2 points

**Description:**
Create comprehensive test fixtures for different company scenarios.

**Acceptance Criteria:**
- [ ] Fixture: Small startup (€500K revenue, 10 employees)
- [ ] Fixture: Growth company (€5M revenue, 50 employees)
- [ ] Fixture: Enterprise (€100M revenue, 1000 employees)
- [ ] Fixture: Phoenix company (high growth, strong position)
- [ ] Fixture: Salt company (moderate growth)
- [ ] Fixture: Lead company (low growth)
- [ ] Fixture: Missing data (null fields)
- [ ] Fixture: Edge cases (zero revenue, negative growth)

**Implementation:**
```python
# tests/fixtures/companies.py
import pytest
from solstein.domain.models import Company, FinancialMetric, CompanyTier

@pytest.fixture
def small_startup() -> Company:
    """Small startup fixture."""
    return Company(
        id="small-startup",
        name="Small Startup Inc",
        industry="Energy Software",
        tier=CompanyTier.TIER_4,
        financials=FinancialMetric(
            revenue=0.5,  # €500K
            revenue_confidence=ConfidenceLevel.ESTIMATED,
            growth_rate=50.0,  # 50% growth
            growth_confidence=ConfidenceLevel.ESTIMATED,
            employees=10,
            employees_confidence=ConfidenceLevel.ESTIMATED,
            funding_raised=1.0,  # €1M
            funding_confidence=ConfidenceLevel.CONFIRMED,
        )
    )

@pytest.fixture
def growth_company() -> Company:
    """Growth stage company fixture."""
    return Company(
        id="growth-co",
        name="Growth Company",
        industry="Energy Software",
        tier=CompanyTier.TIER_3,
        financials=FinancialMetric(
            revenue=5.0,  # €5M
            revenue_confidence=ConfidenceLevel.CONFIRMED,
            growth_rate=35.0,  # 35% growth
            growth_confidence=ConfidenceLevel.CONFIRMED,
            employees=50,
            employees_confidence=ConfidenceLevel.CONFIRMED,
            funding_raised=10.0,  # €10M
            funding_confidence=ConfidenceLevel.CONFIRMED,
        )
    )

@pytest.fixture
def enterprise_company() -> Company:
    """Enterprise company fixture."""
    return Company(
        id="enterprise-co",
        name="Enterprise Solutions",
        industry="Energy Software",
        tier=CompanyTier.TIER_1,
        financials=FinancialMetric(
            revenue=100.0,  # €100M
            revenue_confidence=ConfidenceLevel.CONFIRMED,
            growth_rate=15.0,  # 15% growth
            growth_confidence=ConfidenceLevel.CONFIRMED,
            employees=1000,
            employees_confidence=ConfidenceLevel.CONFIRMED,
            funding_raised=0.0,  # Self-funded
            funding_confidence=ConfidenceLevel.CONFIRMED,
        )
    )

@pytest.fixture
def phoenix_company() -> Company:
    """Phoenix classification fixture."""
    return Company(
        id="phoenix-co",
        name="Phoenix Energy",
        industry="Energy Software",
        tier=CompanyTier.TIER_1,
        ai_maturity=AIMaturity.VERY_STRONG,
        saas_maturity=9,
        financials=FinancialMetric(
            revenue=50.0,
            revenue_confidence=ConfidenceLevel.CONFIRMED,
            growth_rate=80.0,  # 80% growth
            growth_confidence=ConfidenceLevel.CONFIRMED,
            employees=200,
            employees_confidence=ConfidenceLevel.CONFIRMED,
            funding_raised=100.0,
            funding_confidence=ConfidenceLevel.CONFIRMED,
        )
    )

@pytest.fixture
def lead_company() -> Company:
    """Lead classification fixture."""
    return Company(
        id="lead-co",
        name="Legacy Systems",
        industry="Energy Software",
        tier=CompanyTier.TIER_4,
        ai_maturity=AIMaturity.NONE,
        saas_maturity=1,
        financials=FinancialMetric(
            revenue=2.0,
            revenue_confidence=ConfidenceLevel.CONFIRMED,
            growth_rate=-10.0,  # Negative growth
            growth_confidence=ConfidenceLevel.CONFIRMED,
            employees=100,
            employees_confidence=ConfidenceLevel.CONFIRMED,
            funding_raised=0.5,
            funding_confidence=ConfidenceLevel.CONFIRMED,
        )
    )

@pytest.fixture
def missing_data_company() -> Company:
    """Company with missing data fixture."""
    return Company(
        id="missing-data-co",
        name="Unknown Corp",
        industry="Energy Software",
        tier=CompanyTier.TIER_3,
        financials=FinancialMetric(
            revenue=None,
            revenue_confidence=ConfidenceLevel.UNKNOWN,
            growth_rate=None,
            growth_confidence=ConfidenceLevel.UNKNOWN,
            employees=None,
            employees_confidence=ConfidenceLevel.UNKNOWN,
        )
    )
```

---

### Story 12.2: Write Unit Tests for Scoring
**Priority:** P0 | **Effort:** 3 points

**Description:**
Write comprehensive unit tests for all scoring components.

**Acceptance Criteria:**
- [ ] Test growth momentum scorer
- [ ] Test financial health scorer
- [ ] Test competitive position scorer
- [ ] Test composite score calculation
- [ ] Test classification function
- [ ] Test confidence weighting
- [ ] Achieve > 80% coverage for scoring module

**Implementation:**
```python
# tests/unit/test_scoring.py
import pytest
from solstein.analytics.scoring import GrowthScorer, classify_company
from solstein.domain.models import CompanyClassification

class TestGrowthScorer:
    """Test growth momentum scoring."""
    
    def test_high_growth_company(self, phoenix_company):
        """High growth company should get high score."""
        scorer = GrowthScorer()
        result = scorer.calculate(phoenix_company)
        
        assert result.growth_score > 8.0
        assert result.classification == CompanyClassification.PHOENIX
    
    def test_negative_growth_company(self, lead_company):
        """Negative growth company should get low score."""
        scorer = GrowthScorer()
        result = scorer.calculate(lead_company)
        
        assert result.growth_score < 5.0
        assert result.classification == CompanyClassification.LEAD
    
    def test_missing_growth_data(self, missing_data_company):
        """Missing growth data should handle gracefully."""
        scorer = GrowthScorer()
        result = scorer.calculate(missing_data_company)
        
        assert result.growth_score is not None
        assert result.growth_score >= 0.0

class TestFinancialHealthScorer:
    """Test financial health scoring."""
    
    def test_large_company_bonus(self, enterprise_company):
        """Large company should get revenue scale bonus."""
        scorer = FinancialHealthScorer()
        score = scorer.calculate(enterprise_company)
        
        assert score > 6.0  # Should get bonuses for size
    
    def test_small_company_penalty(self, small_startup):
        """Small company should get revenue scale penalty."""
        scorer = FinancialHealthScorer()
        score = scorer.calculate(small_startup)
        
        assert score < 6.0  # Should get penalty for small size
    
    def test_efficiency_calculation(self, growth_company):
        """Revenue per employee should be calculated correctly."""
        scorer = FinancialHealthScorer()
        
        # €5M revenue / 50 employees = €100K per employee
        expected_rev_per_emp = 5_000_000 / 50
        
        result = scorer.calculate_with_breakdown(growth_company)
        efficiency_component = next(
            (c for c in result.components if c.name == "Operating Efficiency"),
            None
        )
        
        assert efficiency_component is not None

class TestClassification:
    """Test company classification."""
    
    def test_phoenix_threshold(self):
        """Score >= 7.0 should be Phoenix."""
        assert classify_company(7.0) == CompanyClassification.PHOENIX
        assert classify_company(8.5) == CompanyClassification.PHOENIX
    
    def test_salt_threshold(self):
        """Score 4.0-6.99 should be Salt."""
        assert classify_company(4.0) == CompanyClassification.SALT
        assert classify_company(5.5) == CompanyClassification.SALT
        assert classify_company(6.99) == CompanyClassification.SALT
    
    def test_lead_threshold(self):
        """Score < 4.0 should be Lead."""
        assert classify_company(3.9) == CompanyClassification.LEAD
        assert classify_company(2.0) == CompanyClassification.LEAD
        assert classify_company(0.0) == CompanyClassification.LEAD
```

---

### Story 12.3: Write Integration Tests
**Priority:** P0 | **Effort:** 2 points

**Description:**
Write integration tests for the data pipeline.

**Acceptance Criteria:**
- [ ] Test JSON to Company conversion
- [ ] Test scoring pipeline end-to-end
- [ ] Test Excel export generation
- [ ] Test enrichment integration
- [ ] Test error handling

**Implementation:**
```python
# tests/integration/test_pipeline.py
import pytest
import json
from pathlib import Path

class TestDataPipeline:
    """Test complete data pipeline."""
    
    def test_json_to_scored_output(self, tmp_path):
        """Test complete pipeline from JSON to scored output."""
        # Arrange
        input_data = {
            "competitors": [
                {
                    "company_name": "Test Co",
                    "revenue": {"timeline": [{"year": 2023, "eur_millions": 5.0, "yoy_growth_pct": 35}]},
                    "employees": 50,
                }
            ]
        }
        input_file = tmp_path / "input.json"
        with open(input_file, 'w') as f:
            json.dump(input_data, f)
        
        # Act
        from scripts.run_eneve_199 import process_companies
        result = process_companies(input_file)
        
        # Assert
        assert len(result) == 1
        assert result[0].name == "Test Co"
        assert result[0].composite_score > 0
        assert result[0].classification is not None
    
    def test_excel_export_generation(self, tmp_path):
        """Test Excel export generation."""
        # Arrange
        companies = [growth_company(), enterprise_company()]
        output_file = tmp_path / "test.xlsx"
        
        # Act
        from solstein.exporters.excel import ExcelExporter
        ExcelExporter().create_dashboard(companies, output_file)
        
        # Assert
        assert output_file.exists()
        import openpyxl
        wb = openpyxl.load_workbook(output_file)
        assert len(wb.sheetnames) >= 5
```

---

### Story 12.4: Set Up CI/CD Testing
**Priority:** P1 | **Effort:** 1 point

**Description:**
Set up automated test runs in CI/CD pipeline.

**Acceptance Criteria:**
- [ ] GitHub Actions workflow for tests
- [ ] Run on every PR
- [ ] Run on every push to main
- [ ] Generate coverage reports
- [ ] Block merge if tests fail

**Implementation:**
```yaml
# .github/workflows/tests.yml
name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run tests
      run: pytest --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

---

## Dependencies

- Story 12.1 must be done first
- Story 12.2 and 12.3 can be done in parallel
- Story 12.4 should be done last

## Definition of Done

- [ ] Test fixtures created
- [ ] Unit tests > 80% coverage
- [ ] Integration tests passing
- [ ] CI/CD running tests automatically
- [ ] Coverage reports generated
