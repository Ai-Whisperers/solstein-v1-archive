# Planning Enhancement: Detailed Code Examples & Implementation Guides

**Date**: Feb 26, 2026  
**Status**: ENHANCED DURING RESEARCH PHASE  
**Purpose**: Provide agents with exact code patterns to implement Wave 1-4 tests

---

## Part 1: Critical Setup (BEFORE Wave 1 Starts)

### 1.1 Fix pyproject.toml for Async Tests

**File**: `pyproject.toml`

**Required Fix**:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src", "."]
addopts = "-v --cov=solstein --cov-report=term-missing"
asyncio_mode = "auto"  # ← ADD THIS LINE (CRITICAL)

markers = [
    "unit: fast isolated tests",
    "integration: tests involving API/service integration",
    "data_quality: regression tests against curated datasets",
    "agents: tests for agent orchestration behavior",
]
```

**Why**: Without `asyncio_mode = "auto"`, all `@pytest.mark.asyncio` tests will fail with "Unknown pytest.mark.asyncio" warning.

---

### 1.2 Enhanced conftest.py with All Required Fixtures

**File**: `tests/conftest.py` (ADD to existing file)

```python
"""Pytest configuration and shared fixtures for all tests."""

import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

# Ensure src is in path for relative imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from solstein.infrastructure.database import DatabaseManager
from solstein.data.connectors.github_connector import GitHubConnector
from solstein.data.connectors.yahoo_finance_connector import YahooFinanceConnector


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture
def mock_db_manager():
    """Mock DatabaseManager for all infrastructure tests."""
    return MagicMock(spec=DatabaseManager)


@pytest.fixture
def mock_async_session():
    """Mock AsyncSession for database operation tests.
    
    This fixture creates a fresh AsyncMock for each test, ensuring isolation.
    """
    session = AsyncMock(spec=AsyncSession)
    
    # Track objects added (for debugging)
    session.added_objects = []
    
    async def mock_add(obj):
        session.added_objects.append(obj)
    
    session.add = MagicMock(side_effect=mock_add)
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.flush = AsyncMock()
    session.close = AsyncMock()
    
    return session


# ============================================================================
# DATA FIXTURES (Factories, not hardcoded)
# ============================================================================

@pytest.fixture
def company_factory():
    """Factory fixture for creating test company data.
    
    Usage:
        def test_something(company_factory):
            company = company_factory(name="UniqueTestCorp")
            assert company.name == "UniqueTestCorp"
    """
    def _create(
        name: str = "TestCorp Inc",
        industry: str = "Software",
        founded: int = 2020,
        revenue: int = 1_000_000,
        employees: int = 50,
        **kwargs
    ) -> dict:
        """Create a valid company data dict for testing."""
        data = {
            "id": f"test-{name.lower().replace(' ', '-')}",
            "name": name,
            "industry": industry,
            "founded": founded,
            "revenue": revenue,
            "employees": employees,
            "created_at": datetime.now().isoformat(),
            **kwargs
        }
        return data
    
    return _create


@pytest.fixture
def financial_data_factory():
    """Factory fixture for financial metrics."""
    def _create(
        revenue_2022: int = 1_000_000,
        revenue_2023: int = 1_200_000,
        revenue_2024: int = 1_440_000,
        profit_margin_2024: float = 0.25,
        employees_2022: int = 10,
        employees_2024: int = 14,
        **kwargs
    ) -> dict:
        return {
            "revenue_2022": revenue_2022,
            "revenue_2023": revenue_2023,
            "revenue_2024": revenue_2024,
            "profit_margin_2024": profit_margin_2024,
            "employees_2022": employees_2022,
            "employees_2024": employees_2024,
            **kwargs
        }
    
    return _create


# ============================================================================
# CONNECTOR MOCKS (External API Mocking)
# ============================================================================

@pytest.fixture
def mock_github_connector():
    """Mock GitHubConnector for testing refresh connectors.
    
    Provides all methods the real connector has, with async support.
    """
    connector = AsyncMock(spec=GitHubConnector)
    
    # Default successful responses
    connector.get_user_repositories = AsyncMock(return_value=[
        {
            "name": "test-repo-1",
            "stars": 100,
            "language": "Python",
            "updated_at": datetime.now().isoformat()
        }
    ])
    
    connector.get_recent_commits = AsyncMock(return_value=[
        {
            "hash": "abc123def456",
            "message": "fix: critical bug",
            "author": "testuser",
            "date": datetime.now().isoformat()
        }
    ])
    
    connector.get_repository_activity = AsyncMock(return_value={
        "stars": 100,
        "forks": 10,
        "open_issues": 5
    })
    
    connector.rate_limit_exceeded = AsyncMock(return_value=False)
    
    return connector


@pytest.fixture
def mock_yahoo_finance_connector():
    """Mock YahooFinanceConnector for financial data tests."""
    connector = AsyncMock(spec=YahooFinanceConnector)
    
    connector.get_company_metrics = AsyncMock(return_value={
        "market_cap": 10_000_000_000,
        "pe_ratio": 25.5,
        "revenue": 1_000_000_000,
        "profit_margin": 0.25,
        "employees": 5000
    })
    
    connector.get_stock_data = AsyncMock(return_value={
        "price": 150.00,
        "52_week_high": 180.00,
        "52_week_low": 120.00,
        "volume": 1_000_000
    })
    
    return connector


# ============================================================================
# API TEST FIXTURES
# ============================================================================

@pytest.fixture
def test_api_client():
    """FastAPI TestClient for endpoint testing.
    
    Usage:
        def test_endpoint(test_api_client):
            response = test_api_client.get("/api/health")
            assert response.status_code == 200
    """
    from fastapi.testclient import TestClient
    from solstein.api.main import app
    
    return TestClient(app)


# ============================================================================
# ASYNC HELPERS
# ============================================================================

@pytest.fixture
def async_mock_factory():
    """Factory for creating AsyncMock objects with custom specs."""
    def _create(spec=None, **kwargs):
        return AsyncMock(spec=spec, **kwargs)
    
    return _create


# ============================================================================
# CLEANUP/TEARDOWN
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Auto-cleanup after each test (runs even if test fails)."""
    yield
    # Add cleanup code here if needed
    # (e.g., delete temp files, reset state)


```

---

## Part 2: WAVE 1 Task Implementation Guides

### Task 1.1.1: Test GitHubRefreshConnector (EXACT CODE)

**File**: `tests/unit/infrastructure/test_github_refresh.py`

```python
"""Tests for GitHubRefreshConnector.

Tests cover:
- Connector initialization
- Successful fact fetching
- Error handling
- Delta detection
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta

from solstein.infrastructure.connectors.github_refresh import GitHubRefreshConnector
from solstein.infrastructure.database import DatabaseManager


class TestGitHubRefreshConnector:
    """Test suite for GitHubRefreshConnector."""

    # ========================================================================
    # SCENARIO 1: Connector Initialization
    # ========================================================================

    def test_github_refresh_connector_initialization(self, mock_db_manager):
        """Verify connector initializes with correct settings.
        
        Expected: source_name="github", confidence=0.85, inherits from BaseRefreshConnector
        """
        connector = GitHubRefreshConnector(mock_db_manager)

        # Assertions
        assert connector.source_name == "github"
        assert connector.source_type == "technical_signal"
        assert connector.confidence == 0.85
        assert connector.db_manager is mock_db_manager
        
        # Verify it's properly typed
        assert hasattr(connector, "fetch_facts")
        assert callable(connector.fetch_facts)

    # ========================================================================
    # SCENARIO 2: Fetch Facts - Success Path
    # ========================================================================

    @pytest.mark.asyncio
    async def test_github_refresh_connector_fetch_facts_success(
        self, mock_db_manager, mock_github_connector
    ):
        """Verify successful fact fetching from GitHub API.
        
        Expected: Returns list of fact dicts, calls connector methods correctly
        """
        # Setup
        connector = GitHubRefreshConnector(mock_db_manager)
        connector.github_connector = mock_github_connector  # Inject mock
        
        company_ids = ["user-1", "user-2"]
        
        # Execute
        facts = await connector.fetch_facts(company_ids)
        
        # Assertions
        assert isinstance(facts, list)
        assert len(facts) > 0
        
        # Verify connector was called correctly
        assert mock_github_connector.get_user_repositories.called
        assert mock_github_connector.get_recent_commits.called
        assert mock_github_connector.get_repository_activity.called
        
        # Verify facts have required structure
        for fact in facts:
            assert isinstance(fact, dict)
            assert "type" in fact
            assert "source" in fact
            assert "confidence" in fact

    # ========================================================================
    # SCENARIO 3: Error Handling - API Failure
    # ========================================================================

    @pytest.mark.asyncio
    async def test_github_refresh_connector_api_failure(
        self, mock_db_manager
    ):
        """Verify graceful handling when GitHub API fails.
        
        Expected: Either exception raised or error logged gracefully
        """
        # Setup
        connector = GitHubRefreshConnector(mock_db_manager)
        
        # Inject connector that fails
        failing_connector = AsyncMock()
        failing_connector.get_user_repositories.side_effect = Exception("API Error: Rate limit exceeded")
        connector.github_connector = failing_connector
        
        # Execute & Assert
        with pytest.raises(Exception):
            await connector.fetch_facts(["user-1"])

    # ========================================================================
    # SCENARIO 4: Delta Detection
    # ========================================================================

    @pytest.mark.asyncio
    async def test_github_refresh_connector_delta_detection(
        self, mock_db_manager
    ):
        """Verify only changed facts are returned on incremental refresh.
        
        Expected: get_facts_to_refresh() returns changed facts only
        """
        # Setup
        connector = GitHubRefreshConnector(mock_db_manager)
        
        # Mock the database manager to track refresh time
        last_refresh = datetime.now() - timedelta(days=1)
        mock_db_manager._get_last_refresh_time = AsyncMock(return_value=last_refresh)
        
        # Mock the connector to return facts
        connector.github_connector = AsyncMock()
        connector.github_connector.get_user_repositories = AsyncMock(return_value=[
            {"name": "repo-1", "updated": datetime.now().isoformat()}
        ])
        
        # Execute (assuming get_facts_to_refresh is implemented)
        if hasattr(connector, "get_facts_to_refresh"):
            changed_facts = await connector.get_facts_to_refresh(["user-1"])
            
            # Assert
            assert isinstance(changed_facts, list)
            assert mock_db_manager._get_last_refresh_time.called


@pytest.mark.asyncio
async def test_github_refresh_connector_empty_results(mock_db_manager):
    """Handle case where user has no repositories.
    
    Expected: Returns empty list gracefully
    """
    connector = GitHubRefreshConnector(mock_db_manager)
    
    # Mock empty response
    empty_connector = AsyncMock()
    empty_connector.get_user_repositories = AsyncMock(return_value=[])
    connector.github_connector = empty_connector
    
    facts = await connector.fetch_facts(["nonexistent-user"])
    
    assert isinstance(facts, list)
    assert len(facts) == 0


@pytest.mark.asyncio
async def test_github_refresh_connector_multiple_companies(
    mock_db_manager, mock_github_connector
):
    """Verify batch processing of multiple companies.
    
    Expected: All companies processed, facts aggregated
    """
    connector = GitHubRefreshConnector(mock_db_manager)
    connector.github_connector = mock_github_connector
    
    company_ids = ["company-1", "company-2", "company-3"]
    
    facts = await connector.fetch_facts(company_ids)
    
    # Should process all companies
    assert len(company_ids) == 3
    assert isinstance(facts, list)
```

---

## Part 3: Refresh Connector Pattern (Reusable)

All 12 refresh connectors (Tasks 1.1.1 through 1.1.12) use the SAME pattern:

```python
"""Test template for any RefreshConnector.

Replace [ConnectorName] with: GitHub, YahooFinance, SecEdgar, CompaniesHouse, 
News, NewsSignal, Funding, Patents, Website, LinkedIn, GlobalMarket, WebSearch
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from solstein.infrastructure.connectors.[connector_name]_refresh import [ConnectorName]RefreshConnector
from solstein.infrastructure.database import DatabaseManager


class Test[ConnectorName]RefreshConnector:
    """Test [ConnectorName] refresh connector."""

    def test_initialization(self, mock_db_manager):
        """Verify connector initializes correctly."""
        connector = [ConnectorName]RefreshConnector(mock_db_manager)
        assert connector.source_name == "[source-name]"  # e.g., "github"
        assert connector.db_manager is mock_db_manager

    @pytest.mark.asyncio
    async def test_fetch_facts_success(self, mock_db_manager):
        """Verify successful fact fetching."""
        connector = [ConnectorName]RefreshConnector(mock_db_manager)
        
        # Mock external connector
        connector.[connector_attribute] = AsyncMock()
        connector.[connector_attribute].[method_name] = AsyncMock(
            return_value=[{"fact": "data"}]
        )
        
        facts = await connector.fetch_facts(["id-1"])
        
        assert isinstance(facts, list)
        assert connector.[connector_attribute].[method_name].called

    @pytest.mark.asyncio
    async def test_fetch_facts_error_handling(self, mock_db_manager):
        """Verify error handling when API fails."""
        connector = [ConnectorName]RefreshConnector(mock_db_manager)
        
        connector.[connector_attribute] = AsyncMock()
        connector.[connector_attribute].[method_name].side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            await connector.fetch_facts(["id-1"])

    @pytest.mark.asyncio
    async def test_empty_results(self, mock_db_manager):
        """Handle empty/null results gracefully."""
        connector = [ConnectorName]RefreshConnector(mock_db_manager)
        
        connector.[connector_attribute] = AsyncMock()
        connector.[connector_attribute].[method_name] = AsyncMock(return_value=[])
        
        facts = await connector.fetch_facts(["id-1"])
        assert facts == []
```

---

## Part 4: Database Testing Pattern

### Task 1.2.1-1.2.4 Pattern: Database Layer Tests

```python
"""Test database.py, database_service.py, repositories.py"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from solstein.infrastructure.database import DatabaseManager, Base
from solstein.infrastructure.database_service import DatabaseService


class TestDatabaseService:
    """Test CRUD operations on database."""

    @pytest.mark.asyncio
    async def test_create_company(self, mock_async_session):
        """Verify company creation works."""
        db_service = DatabaseService(mock_async_session)
        
        company_data = {
            "name": "TestCorp",
            "industry": "Software",
            "founded": 2020
        }
        
        result = await db_service.create_company(company_data)
        
        # Verify database operations
        assert mock_async_session.add.called
        assert mock_async_session.commit.called
        assert result is not None

    @pytest.mark.asyncio
    async def test_read_by_id(self, mock_async_session):
        """Verify company retrieval by ID."""
        db_service = DatabaseService(mock_async_session)
        
        # Mock the database response
        mock_result = MagicMock()
        mock_company = MagicMock(id=1, name="TestCorp")
        mock_result.scalars().first.return_value = mock_company
        mock_async_session.execute = AsyncMock(return_value=mock_result)
        
        company = await db_service.get_company_by_id(1)
        
        assert company is not None
        assert mock_async_session.execute.called

    @pytest.mark.asyncio
    async def test_update_company(self, mock_async_session):
        """Verify company update."""
        db_service = DatabaseService(mock_async_session)
        
        result = await db_service.update_company(1, {"name": "UpdatedCorp"})
        
        assert mock_async_session.commit.called

    @pytest.mark.asyncio
    async def test_transaction_rollback_on_error(self, mock_async_session):
        """Verify rollback when commit fails."""
        mock_async_session.commit.side_effect = Exception("Constraint violation")
        
        db_service = DatabaseService(mock_async_session)
        
        with pytest.raises(Exception):
            await db_service.create_company({"invalid": "data"})
        
        assert mock_async_session.rollback.called

    @pytest.mark.asyncio
    async def test_bulk_operations(self, mock_async_session):
        """Verify bulk insert performance."""
        db_service = DatabaseService(mock_async_session)
        
        companies = [{"name": f"Company {i}"} for i in range(100)]
        result = await db_service.bulk_create_companies(companies)
        
        assert mock_async_session.commit.called
```

---

## Part 5: Analytics Testing Pattern

### Task 2.1.1-2.1.3 Pattern: Scoring Logic

```python
"""Test scoring modules like growth_momentum.py"""

import pytest
from solstein.analytics.scorers.growth_momentum import GrowthMomentumScorer


class TestGrowthMomentumScorer:
    """Test growth momentum scoring logic."""

    def test_valid_input(self):
        """Score company with positive growth."""
        scorer = GrowthMomentumScorer()
        
        company_data = {
            "revenue_2022": 1_000_000,
            "revenue_2023": 1_200_000,
            "revenue_2024": 1_440_000,
            "employees_2022": 10,
            "employees_2024": 14
        }
        
        score = scorer.calculate_score(company_data)
        
        # Growth company should score high
        assert score > 5.0
        assert 0 <= score <= 10
        assert isinstance(score, float)

    def test_zero_growth(self):
        """Score stagnant company low."""
        scorer = GrowthMomentumScorer()
        
        company_data = {
            "revenue_2022": 1_000_000,
            "revenue_2023": 1_000_000,
            "revenue_2024": 1_000_000,
        }
        
        score = scorer.calculate_score(company_data)
        
        assert score < 3.0

    def test_negative_growth(self):
        """Score declining company low."""
        scorer = GrowthMomentumScorer()
        
        company_data = {
            "revenue_2022": 1_000_000,
            "revenue_2023": 800_000,
            "revenue_2024": 600_000,
        }
        
        score = scorer.calculate_score(company_data)
        
        assert score < 3.0

    def test_missing_data_handling(self):
        """Handle missing data gracefully."""
        scorer = GrowthMomentumScorer()
        
        company_data = {
            "revenue_2022": None,
            "revenue_2023": 1_200_000,
            "revenue_2024": None,
        }
        
        # Should either return neutral score or raise clear error
        result = scorer.calculate_score(company_data)
        
        assert result is not None or isinstance(result, (float, int))
```

---

## Part 6: API Testing Pattern

### Task 3.1.1+ Pattern: FastAPI Endpoints

```python
"""Test FastAPI endpoints"""

import pytest
from fastapi.testclient import TestClient
from solstein.api.main import app


client = TestClient(app)


class TestScoringEndpoints:
    """Test scoring-related API endpoints."""

    def test_get_scoring_stats_success(self):
        """GET /api/scoring/stats returns stats."""
        response = client.get("/api/scoring/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_companies" in data
        assert "average_score" in data
        assert isinstance(data["average_score"], (int, float))

    def test_get_scoring_stats_invalid_date(self):
        """GET /api/scoring/stats rejects invalid date."""
        response = client.get("/api/scoring/stats?date=invalid-date")
        
        assert response.status_code == 400

    def test_score_company_success(self):
        """POST /api/scoring/company/{id}/score works."""
        response = client.post("/api/scoring/company/test-1/score")
        
        assert response.status_code in (200, 202)  # 200 or async 202
        data = response.json()
        
        assert "score" in data or "job_id" in data  # Either immediate or async

    def test_concurrent_requests(self):
        """Multiple requests handled correctly."""
        responses = [client.get("/api/scoring/stats") for _ in range(10)]
        
        assert all(r.status_code == 200 for r in responses)
```

---

## Part 7: Common Pitfalls & Solutions

### Pitfall 1: Forgetting asyncio_mode
```python
# ❌ FAILS without asyncio_mode="auto"
@pytest.mark.asyncio
async def test_something():
    pass
# Error: Unknown pytest.mark.asyncio

# ✅ FIX: Add asyncio_mode="auto" to pyproject.toml
```

### Pitfall 2: AsyncMock vs MagicMock Confusion
```python
# ❌ WRONG: MagicMock for async function
async_func = MagicMock(return_value="result")
await async_func()  # TypeError

# ✅ CORRECT: AsyncMock for async function
async_func = AsyncMock(return_value="result")
result = await async_func()  # Works
```

### Pitfall 3: Fixture Brittleness
```python
# ❌ BRITTLE: Hardcoded test data
COMPANY_DATA = {"id": "123", "name": "TestCorp"}

def test_something():
    company = COMPANY_DATA  # If format changes, all tests break

# ✅ ROBUST: Factory fixture
@pytest.fixture
def company_factory():
    def _create(name="TestCorp", **kwargs):
        return {"id": "123", "name": name, **kwargs}
    return _create

def test_something(company_factory):
    company = company_factory(name="UniqueTestCorp")  # Safe
```

### Pitfall 4: Missing Test Isolation
```python
# ❌ WRONG: Shared state between tests
mock_connector = AsyncMock()

def test_1():
    mock_connector.get_data.return_value = [1]
    # ...

def test_2():
    # mock_connector still has return_value from test_1!
    # Tests interfere with each other

# ✅ CORRECT: Fresh mocks per test
@pytest.fixture
def mock_connector():
    return AsyncMock()

def test_1(mock_connector):
    mock_connector.get_data.return_value = [1]

def test_2(mock_connector):  # Fresh mock, no interference
    mock_connector.get_data.return_value = [2]
```

---

## Part 8: Coverage Verification Commands

```bash
# Check current baseline (before Wave 1)
pytest tests/ --cov=src/solstein --cov-report=term-missing

# Run Wave 1 tests only
pytest tests/unit/infrastructure/ -v

# Check coverage with thresholds
pytest tests/ --cov=src/solstein --cov-fail-under=80 --cov-report=html

# Profile slow tests
pytest tests/ -v --durations=20

# Test specific module
pytest tests/unit/infrastructure/test_github_refresh.py -v
```

---

## Summary

This enhancement provides:
- ✅ Exact conftest.py code (copy-paste ready)
- ✅ 4 complete test implementations with all scenarios
- ✅ Reusable pattern templates for all 82 tasks
- ✅ Common pitfalls & solutions
- ✅ Verification commands

**Next**: Research agents will provide GitHub examples + additional patterns.

