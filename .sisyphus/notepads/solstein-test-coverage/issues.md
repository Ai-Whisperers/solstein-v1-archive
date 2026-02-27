# Issues & Blockers - Solstein Test Coverage

## BLOCKER: Task 1.1.1 - GitHubRefreshConnector Missing Dependency

**Status**: BLOCKED  
**Date**: 2026-02-26  
**Severity**: HIGH

### Issue
The file `src/solstein/infrastructure/connectors/github_refresh.py` (line 5) imports:
```python
from solstein.data.connectors.github_connector import GitHubConnector
```

However, the module `solstein.data.connectors.github_connector` **does not exist**.

### Evidence
- Checked `/home/ai-whisperers/solstein/src/solstein/data/connectors/`
- Only contains: `companies_house_connector.py`, `sec_edgar_connector.py`, `news_signal_detector.py`, `lookup_service.py`
- No `github_connector.py` file

### Impact
- Cannot import `GitHubRefreshConnector` for testing
- All 12 refresh connector tests (Tasks 1.1.1-1.1.12) may be blocked if they have similar issues
- Test file created: `tests/unit/test_github_refresh.py` (325 lines) but cannot run

### Root Cause
The `github_refresh.py` file references a connector that was either:
1. Never implemented
2. Deleted/refactored without updating imports
3. Moved to a different location

### Workaround Options
1. **Create the missing `GitHubConnector`** - Implement based on `GitHubAgent` pattern
2. **Refactor `github_refresh.py`** - Use `GitHubAgent` directly instead of non-existent connector
3. **Skip refresh connector tests** - Move to other test tasks (database, API, etc.)
4. **Mock the import** - Use `unittest.mock.patch` to mock the missing module

### Recommendation
**Option 1 or 2** - The codebase has a `GitHubAgent` class that provides GitHub API functionality. 
Either:
- Create `github_connector.py` as a wrapper around `GitHubAgent`
- Refactor `github_refresh.py` to use `GitHubAgent` directly

### Next Steps
1. Investigate if other refresh connectors have similar issues
2. Decide on implementation approach
3. Either fix source code or pivot to unblocked tasks

---

## DISCOVERY: Refresh Connector Implementation Patterns

**Status**: DOCUMENTED  
**Date**: 2026-02-26

### Key Findings

1. **YahooFinanceRefreshConnector** (191 LOC)
   - Uses `CompanyResearcher.research(ticker)` to fetch profile
   - Converts profile to 4 fact types: market_metrics, financial_metrics, growth_metrics, company_profile
   - Method: `_convert_profile_to_facts(ticker, profile) -> list[dict]`
   - Source type: "market_data" (NOT "financial_data")
   - Confidence: 0.88
   - Supports incremental refresh via hash comparison

2. **Test Pattern for Refresh Connectors**
   - Mock the researcher/connector dependency
   - Create mock profile/data object with all required attributes
   - Call `fetch_facts(company_ids)` and verify returned facts
   - Each connector returns different number of facts (YahooFinance = 4 per ticker)
   - All facts have: company_id, fact_type, value, confidence, extracted_at, source, metadata

3. **Import Dependencies Status**
   - ✅ CompanyResearcher (exists)
   - ✅ SECEdgarConnector (exists)
   - ✅ CompaniesHouseConnector (exists)
   - ✅ NewsSignalDetector (exists)
   - ❌ GitHubConnector (MISSING - only github_refresh.py uses it)

### Recommended Test Approach
- Create tests for each refresh connector following the pattern above
- Mock the underlying researcher/connector
- Verify fact structure and count
- Test error handling (API failures, empty results)
- Test metadata preservation

### Test File Template
```python
class TestXXXRefreshConnector:
    @pytest.fixture
    def connector(self, mock_db_manager):
        return XXXRefreshConnector(mock_db_manager)
    
    def test_initialization(self, connector):
        assert connector.source_name == "xxx"
        assert connector.confidence == X.XX
    
    @pytest.mark.asyncio
    async def test_fetch_facts_success(self, connector):
        # Mock the underlying researcher/connector
        # Call fetch_facts()
        # Verify facts structure and count
        pass
```

