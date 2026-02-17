# FD-009: Unit Tests for Market Analysis Pipeline

## Objective

Add pytest-based unit tests covering the three market analysis scripts and shared utility module to achieve 50%+ code coverage -- a prerequisite for Advanced quality level.

## Requirements

1. Create `tests/` directory alongside the scripts at `.cursor/scripts/analysis/market/tests/`
2. Add `conftest.py` with reusable fixtures: sample competitor dict, multi-competitor list, Eneve competitor, empty data structures
3. Test `competitor_utils.py` -- all 13 public functions with normal, edge-case, and None/missing-key inputs
4. Test `extract_competitor_data.py` -- core parsing functions (`parse_scorecard`, `parse_revenue_timeline`, `parse_employee_timeline`, `parse_funding_history`, `parse_saas_metrics`, `parse_geographic_data`, `parse_profitability_data`)
5. Test `generate_excel_report.py` -- key computation logic (KPI calculations, sorting, filtering, sparkline generation); verify workbook structure (sheet count, sheet names, header rows)
6. Test `generate_markdown_dashboard.py` -- table rendering, Mermaid chart generation, section output
7. Add `pytest` and `pytest-cov` to `requirements.txt`
8. All tests pass with `pytest --tb=short`
9. Coverage report shows 50%+ overall

## Complexity Assessment

**Track**: Complex Implementation

**Rationale**: Involves creating a test suite across 4 modules with fixtures, mocks, and edge cases. Estimated 300-500 lines of test code across multiple files. Requires understanding the internal functions of each script to design meaningful tests.

**Criteria Met**:
- Root Cause: N/A (quality enhancement, not a defect)
- Files Affected: 5+ new files (conftest.py, 4 test modules)
- Lines Changed: ~300-500 (new test code)
- Risk Level: Low (additive, no production code changes)
- Solution Pattern: Familiar (standard pytest patterns)

**Decision Principle Applied**: When in doubt, prefer Complex track

## Status

**Current**: Ready for Implementation

## Acceptance Criteria

- [ ] `tests/` directory exists at `.cursor/scripts/analysis/market/tests/`
- [ ] `conftest.py` provides reusable fixtures for competitor data structures
- [ ] `test_competitor_utils.py` covers all 13 public functions:
  - `get_score`, `get_composite`, `get_classification`, `is_eneve`
  - `get_ebitda_margin`, `get_revenue_per_employee`
  - `get_lead_investors`, `get_war_chest_signals`
  - `get_international_revenue_pct`, `get_countries_count`
  - `get_deployment_model`, `get_cloud_revenue_pct`
  - `CLASSIFICATION_ORDER` constant
- [ ] `test_extract_competitor_data.py` covers core parsers with sample markdown input
- [ ] `test_generate_excel_report.py` covers KPI logic and workbook structure
- [ ] `test_generate_markdown_dashboard.py` covers table/chart rendering
- [ ] `pytest` and `pytest-cov` added to `requirements.txt`
- [ ] `pytest --tb=short` passes with 0 failures
- [ ] `pytest --cov=. --cov-report=term-missing` shows 50%+ overall coverage
- [ ] No production code modified (tests only)

## Implementation Strategy

### 1. Fixtures (`conftest.py`)

```python
@pytest.fixture
def sample_competitor():
    """A fully-populated competitor dict matching the JSON schema."""

@pytest.fixture
def eneve_competitor():
    """Eneve-specific competitor with known values."""

@pytest.fixture
def competitors_list(sample_competitor, eneve_competitor):
    """List of competitors for multi-record tests."""

@pytest.fixture
def empty_competitor():
    """Minimal dict with empty/missing nested keys for edge-case testing."""
```

### 2. Test Priority (highest coverage impact first)

1. **competitor_utils.py** -- 13 pure functions, easiest to test, 100% coverable
2. **extract_competitor_data.py** -- parsing functions with sample markdown strings
3. **generate_excel_report.py** -- computation helpers; workbook output validation
4. **generate_markdown_dashboard.py** -- string output validation

### 3. Testing Patterns

- **Pure function tests**: Direct input/output assertions
- **Markdown parsing tests**: Feed known markdown strings, assert extracted dict structure
- **Excel output tests**: Generate workbook to `io.BytesIO`, validate sheet names and header rows
- **Edge cases**: None values, missing keys, empty lists, single competitor, Eneve-only

## Testing Strategy

```bash
cd .cursor/scripts/analysis/market
pip install pytest pytest-cov
pytest --tb=short -v
pytest --cov=. --cov-report=term-missing
```

## Dependencies

- FD-001 through FD-008 complete (all production code finalized)
- pytest >= 7.0
- pytest-cov >= 4.0
