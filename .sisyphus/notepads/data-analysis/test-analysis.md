# Solstein Test Suite Analysis

**Date**: 2026-02-27  
**Test Count**: 1,297 tests collected (3 collection errors)

---

## 1. Database vs Mock Usage

### Tests Using Real Database (with `db_session` fixture)

| File | Tests | Pattern |
|------|-------|---------|
| `tests/unit/test_fact_repository.py` | 14 | Direct AsyncSession + Factory functions |
| `tests/unit/test_database_service.py` | 15 | Direct AsyncSession + Service methods |
| `tests/unit/test_enrichment_repositories.py` | 12 | Direct AsyncSession + Repository methods |
| `tests/integration/test_phase_11_12_integration.py` | 32 | Full database integration |

**Key Pattern**: Uses `db_session` fixture from `conftest.py`:
```python
@pytest.fixture
async def db_session(db_engine):
    async_session = sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        # Rollback ensures isolation
```

### Tests Using Mocks (54 files)

| Category | Files | Mock Pattern |
|----------|-------|--------------|
| Repository mocks | `test_repositories.py` | `MagicMock(spec=CompanyRepository)` |
| API client mocks | Multiple | `patch("solstein.core.supabase_client.get_supabase")` |
| Loader mocks | `test_loaders.py`, `test_json_repositories.py` | `patch("CompetitorDataLoader")` |
| External API mocks | `test_*_refresh.py` (16 files) | `@patch` for connectors |
| Worker mocks | `test_worker.py` | `@patch("solstein.worker.logger")` |

---

## 2. Test Data Creation: Factories vs Hardcoded

### Factory Functions (tests/factories.py)

| Factory | Usage Count | Purpose |
|---------|-------------|---------|
| `make_company()` | 10 files | Base Company with defaults |
| `make_phoenix_company()` | 5 files | High-growth Phoenix classification |
| `make_lead_company()` | 4 files | Declining Lead classification |
| `make_financial_metric()` | 3 files | FinancialMetric with defaults |
| `create_test_batch()` | 2 files | DB persistence - GatheringBatch |
| `create_test_fact()` | 2 files | DB persistence - Fact |
| `create_test_fact_source()` | 2 files | DB persistence - FactSource |

**Example Usage**:
```python
# From test_scoring.py
@pytest.fixture
def phoenix_company():
    return make_phoenix_company()

def test_growth_scorer_phoenix(phoenix_company):
    scorer = GrowthScorer()
    score = scorer.score(phoenix_company)
    assert score >= 7.0
```

### Hardcoded Test Data

**Common pattern** - Direct Company construction without factories:
```python
# From test_repositories.py
def sample_company():
    return Company(
        id="test-id",
        name="Test Corp",
        financials=FinancialMetric(revenue=150.5, ...),
        ...
    )
```

**Files with heavy hardcoded data** (should migrate to factories):
- `test_repositories.py` - Has `sample_company()` fixture
- `test_loaders.py` - Uses `@patch` with hardcoded JSON
- `test_unified_loader.py` - Multiple hardcoded Company objects
- All 16 `test_*_refresh.py` files

---

## 3. JSON Fixture Usage

**Status**: NO JSON fixture files in tests/ directory

The project previously used JSON fixtures but has migrated to:
1. Factory functions (`tests/factories.py`)
2. Python hardcoded data (in fixtures)
3. Database-backed test data (via factories)

**Legacy references** (comments only):
- `test_loaders.py` mentions "competitor_data.json" - now mocked via `conftest.py` fixture

---

## 4. Test Coverage by Module

### Test Distribution

| Directory | Tests | Purpose |
|-----------|-------|---------|
| `tests/unit/` | ~800 | Domain logic, scorers, models |
| `tests/integration/` | ~300 | API endpoints, connectors |
| `tests/data_quality/` | ~200 | Golden dataset regression |

### Top Test Files by Count

| File | Tests | Module |
|------|-------|--------|
| `test_enrichment_api.py` | 75 | Integration |
| `test_connector_enrichment_phase_5.py` | 38 | Integration |
| `test_facts_orm_models.py` | 36 | Unit/Database |
| `test_scoring.py` | 34 | Unit/Analytics |
| `test_unified_loader.py` | 33 | Unit/Data |
| `test_phase_11_12_integration.py` | 32 | Integration |
| `test_unified_adapters.py` | 31 | Integration |
| `test_golden_dataset_regression.py` | 31 | Data Quality |

---

## 5. Integration vs Unit Test Split

### Unit Tests (tests/unit/)
- **Characteristics**: Fast, isolated, use mocks
- **Fixtures**: Factory functions, simple mocks
- **Examples**:
  - `test_scoring.py` - Pure scoring logic
  - `test_models.py` - Pydantic validation
  - `test_classification.py` - Classification boundaries

### Integration Tests (tests/integration/)
- **Characteristics**: Slower, test component interactions
- **Patterns**: 
  - Some use `db_session` (real database)
  - Some use mocks for external APIs
- **Examples**:
  - `test_enrichment_api.py` - Full API flow
  - `test_connector_enrichment_real.py` - Real Company objects + mocked connectors
  - `test_phase_11_12_integration.py` - Real database + mocked loaders

### Data Quality Tests (tests/data_quality/)
- **Purpose**: Regression protection for scoring engine
- **Key**: Golden dataset with expected score ranges
- **Example**:
  - `test_golden_dataset_regression.py` - Validates score stability

---

## 6. Mocking Patterns (Should Be Replaced)

### Pattern 1: Repository Mocks (HIGH PRIORITY)

**Current** (`test_repositories.py`):
```python
@pytest.fixture
def mock_supabase():
    with patch("solstein.core.supabase_client.get_supabase") as mock_get:
        mock_client = MagicMock()
        mock_get.return_value = mock_client
        yield mock_client

def test_get_by_id_found(mock_supabase):
    repo = SupabaseRepository()
    mock_response = MagicMock()
    mock_response.data = [{"id": "foo", "name": "Bar"}]
    mock_supabase.table().select().eq().execute.return_value = mock_response
    company = repo.get_by_id("foo")
```

**Should Become**: Real database tests like `test_fact_repository.py`

---

### Pattern 2: Loader Mocks (MEDIUM PRIORITY)

**Current** (`test_loaders.py`):
```python
@patch("builtins.open", new_callable=mock_open, read_data=json.dumps({...}))
def test_loader_success(mock_file, mock_exists):
    mock_exists.return_value = True
    loader = CompetitorDataLoader(data_dir=Path("/mocked/path"))
    companies = loader.load_companies()
```

**Should Become**: Use existing `conftest.py` autouse fixture which already provides mock data

---

### Pattern 3: Refresh Test Mocks (MEDIUM PRIORITY)

**Files affected**: 16 `test_*_refresh.py` files

**Current**:
```python
@patch("solstein.data.connectors.SecEdgarConnector")
def test_sec_edgar_refresh(MockConnector):
    mock_instance = MockConnector.return_value
    mock_instance.fetch.return_value = {...}
    # Test refresh logic
```

**Should Become**: Use real connectors (with recorded responses) or move to integration tests

---

### Pattern 4: API Endpoint Mocks (LOW PRIORITY)

**Current** (`conftest.py`):
```python
@pytest.fixture
def mock_repo(mock_company):
    repo = MagicMock(spec=CompanyRepository)
    repo.get_all.return_value = [mock_company]
    repo.get_by_id.return_value = mock_company
    return repo

@pytest.fixture
def client(mock_repo):
    app.dependency_overrides[get_repository] = lambda: mock_repo
```

**Assessment**: Acceptable for API contract testing - these are fast and appropriate

---

## Recommendations for Test Improvements

### Priority 1: Migrate Repository Tests to Real Database

| Current | Target | Files |
|---------|--------|-------|
| `test_repositories.py` | Follow `test_fact_repository.py` pattern | 1 file |

**Effort**: Low - Same structure, swap mocks for `db_session`

---

### Priority 2: Standardize Hardcoded Data to Factories

| Files | Current Pattern | Should Use |
|-------|----------------|------------|
| `test_repositories.py` | `sample_company()` fixture | `make_company()` |
| 16 `test_*_refresh.py` files | Hardcoded dicts | `make_company()` |
| `test_loaders.py` | `@patch` with JSON | `make_company()` + existing fixture |

**Effort**: Medium - ~50 files to update

---

### Priority 3: Remove Redundant Mocks

The `conftest.py` already provides:
- Autouse `patch_competitor_data_loader` fixture (provides 3 test companies)
- `make_company()` factory

Many tests re-implement these unnecessarily.

---

### Priority 4: Fix Collection Errors

| File | Error |
|------|-------|
| `test_database_persistence.py` | Missing `pytest_asyncio` |
| `test_database_service.py` | Import error - `CompanyScoringRecord` |
| `test_enrichment_repositories.py` | Import error - `EnrichmentCache` |

**Effort**: Low - Fix imports/models

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total Tests | 1,297 |
| Tests with Real DB | ~75 (6%) |
| Tests with Mocks | ~1,100 (85%) |
| Tests with Factories | ~120 (9%) |
| JSON Fixture Files | 0 |
| Collection Errors | 3 |

---

## Action Items

1. **Immediate**: Fix 3 collection errors in imports
2. **Short-term**: Migrate `test_repositories.py` to real DB pattern
3. **Medium-term**: Update 16 refresh test files to use factories
4. **Long-term**: Create integration test layer for connector tests with recorded responses
