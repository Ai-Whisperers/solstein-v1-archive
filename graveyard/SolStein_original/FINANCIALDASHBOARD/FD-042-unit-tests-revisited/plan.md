# FD-042: Unit Tests Revisited -- Market Analysis Pipeline

## Objective

Add pytest-based unit tests covering the market analysis pipeline (4 scripts, ~4,200 lines) to achieve 50%+ code coverage. Supersedes FD-009, which was scoped against the Phase 1 codebase (548 lines in report generator). Phase 3 expanded `generate_excel_report.py` to 2,605 lines and added 10+ sheet-generation functions, requiring a revised test strategy.

## Background

FD-009 was created during Phase 1 when the codebase was smaller. Phase 3 (FD-012 through FD-021) added AI Maturity, Investment Efficiency, M&A Vulnerability, Threat Timeline, Competitive Overlap, Confidence Dashboard, Scenario Projections, Portfolio Risk, and Dynamic Filters sheets. The test plan must now cover these additions.

**Current codebase size**:

| Module | Lines | Public Functions (est.) |
|--------|-------|------------------------|
| `competitor_utils.py` | 205 | ~13 |
| `extract_competitor_data.py` | 827 | ~10 |
| `generate_excel_report.py` | 2,605 | ~25 |
| `generate_markdown_dashboard.py` | 628 | ~8 |
| **Total** | **4,265** | **~56** |

## Requirements

1. Create `tests/` directory at `.cursor/scripts/analysis/market/tests/`
2. Add `conftest.py` with reusable fixtures: sample competitor dict (fully populated), Eneve competitor, multi-competitor list, empty/sparse competitor, sample markdown input blocks
3. Test `competitor_utils.py` -- all ~13 public functions with normal, edge-case, and None/missing-key inputs
4. Test `extract_competitor_data.py` -- core parsing functions with sample markdown strings
5. Test `generate_excel_report.py` -- prioritized by coverage impact:
   - Phase 1 computation logic (KPI calculations, sorting, sparkline generation)
   - Phase 3 sheet builders (AI maturity scoring, investment efficiency ratios, M&A classification, threat timeline, overlap matrix, confidence scoring, scenario projection, portfolio risk aggregation, slicer/pivot setup)
   - Workbook structure validation (sheet count, sheet names, header rows)
6. Test `generate_markdown_dashboard.py` -- table rendering, Mermaid chart generation
7. Add `pytest` and `pytest-cov` to `requirements.txt`
8. All tests pass with `pytest --tb=short`
9. Coverage report shows 50%+ overall

## Complexity Assessment

**Track**: Complex Implementation

**Rationale**: 4,200+ lines across 4 modules with ~56 public functions. Phase 3 sheet builders have complex data transformation logic (matrix generation, scoring algorithms, classification rules). Estimated 500-800 lines of test code.

**Criteria Met**:
- Root Cause: N/A (quality enhancement)
- Files Affected: 6+ new files (conftest.py, 4 test modules, requirements.txt update)
- Lines Changed: ~500-800 (new test code)
- Risk Level: Low (additive, no production code changes)
- Solution Pattern: Familiar (standard pytest patterns)

## Status

**Current**: Ready for Implementation

## Acceptance Criteria

- [ ] `tests/` directory exists at `.cursor/scripts/analysis/market/tests/`
- [ ] `conftest.py` provides reusable fixtures for competitor data structures
- [ ] `test_competitor_utils.py` covers all public functions with happy path + edge cases
- [ ] `test_extract_competitor_data.py` covers core parsers with sample markdown input
- [ ] `test_generate_excel_report.py` covers:
  - [ ] Phase 1 KPI logic and workbook structure
  - [ ] Phase 3 sheet builders (at least 5 of the new sheets)
  - [ ] Workbook output validation (sheet count, names, headers)
- [ ] `test_generate_markdown_dashboard.py` covers table and chart rendering
- [ ] `pytest` and `pytest-cov` in `requirements.txt`
- [ ] `pytest --tb=short` passes with 0 failures
- [ ] `pytest --cov=. --cov-report=term-missing` shows 50%+ overall coverage
- [ ] No production code modified (tests only)

## Implementation Strategy

### 1. Fixtures (`conftest.py`)

```python
@pytest.fixture
def sample_competitor():
    """Fully-populated competitor dict matching the JSON schema including Phase 3 fields."""

@pytest.fixture
def eneve_competitor():
    """Eneve-specific competitor with known values for positioning tests."""

@pytest.fixture
def competitors_list(sample_competitor, eneve_competitor):
    """List of 3+ competitors for multi-record and ranking tests."""

@pytest.fixture
def empty_competitor():
    """Minimal dict with empty/missing nested keys for edge-case testing."""

@pytest.fixture
def sample_markdown_block():
    """Sample financial-growth.md content for parser tests."""
```

### 2. Test Priority (highest coverage impact first)

1. **competitor_utils.py** (205 lines) -- 13 pure functions, 100% coverable, highest ROI
2. **extract_competitor_data.py** (827 lines) -- parsing functions with sample markdown
3. **generate_excel_report.py** (2,605 lines) -- focus on computation helpers and Phase 3 sheet builders; workbook output to `io.BytesIO` for structure validation
4. **generate_markdown_dashboard.py** (628 lines) -- string output validation

### 3. Phase 3 Sheet Testing Approach

For the large `generate_excel_report.py`, test each sheet builder function in isolation by mocking the workbook and verifying:
- Correct data transformation (input competitors -> output rows/cells)
- Scoring/classification logic produces expected values for known inputs
- Matrix dimensions match competitor count (e.g., 33x33 overlap matrix)
- Chart/conditional-formatting calls made with valid parameters

### 4. Testing Patterns

- **Pure function tests**: Direct input/output assertions
- **Markdown parsing tests**: Feed known markdown strings, assert extracted dict structure
- **Excel output tests**: Generate workbook to `io.BytesIO`, validate sheet names and header rows
- **Edge cases**: None values, missing keys, empty lists, single competitor, Eneve-only
- **Parameterized tests**: Use `@pytest.mark.parametrize` for scoring functions with multiple input/output pairs

## Testing Strategy

```bash
cd .cursor/scripts/analysis/market
pip install pytest pytest-cov
pytest --tb=short -v
pytest --cov=. --cov-report=term-missing
```

## Dependencies

- Phase 1 (FD-001 to FD-008) complete
- Phase 3 sheet implementations (FD-012 to FD-021) complete
- pytest >= 7.0
- pytest-cov >= 4.0

## Notes

- Supersedes FD-009 (moved to DONE). FD-009 was scoped for Phase 1 codebase only.
- The 50%+ coverage target applies to overall combined coverage across all 4 modules.
- `generate_excel_report.py` at 2,605 lines dominates the codebase; achieving 50% overall likely requires good coverage of this module specifically.
- Consider using `pytest-mock` if sheet builder functions have complex openpyxl dependencies that are hard to test directly.
