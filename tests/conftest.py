import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

_ = os.environ.setdefault("GITHUB_TOKEN", "test-github-token-12345")

try:
    from tests.factories import make_company
except ModuleNotFoundError as exc:
    if exc.name == "factory":
        raise ModuleNotFoundError(
            "Missing test dependency 'factory-boy'. Install dev dependencies with `uv sync --dev` or "
            "`pip install -e .[dev]` before running tests."
        ) from exc
    raise


from solstein.api.dependencies import get_company_repository, get_current_tenant, get_current_user
from solstein.api.main import app
from solstein.config import get_settings
from solstein.domain.models import AIMaturity
from solstein.database_config import get_test_database_url, convert_to_async_url


@pytest.fixture
def mock_company():
    """Provides a deterministic company profile for testing (via factory)."""
    return make_company()


@pytest.fixture
def mock_repo(mock_company):
    """
    Provides a mocked CompanyRepository.

    Note: get_by_id returns the same company regardless of ID by default.
    Override in individual tests for 'not found' scenarios:
        mock_repo.get_by_id.return_value = None
    """
    repo = MagicMock()
    repo.get_all = AsyncMock(return_value=[mock_company])
    repo.get_all_filtered = AsyncMock(return_value=[mock_company])
    repo.get_by_id = AsyncMock(return_value=mock_company)
    repo.save = AsyncMock(return_value=mock_company)
    repo.delete = AsyncMock(return_value=True)
    repo.filter_by = AsyncMock(return_value=[mock_company])
    repo.search = AsyncMock(return_value=[mock_company])
    return repo


@pytest.fixture
def client(mock_repo):
    """Provides an authenticated TestClient with dependency overrides."""
    settings = get_settings()
    previous_require_api_key = settings.api.require_api_key
    settings.api.require_api_key = False

    app.dependency_overrides[get_current_user] = lambda: {
        "username": "testuser",
        "role": "admin",
    }
    app.dependency_overrides[get_current_tenant] = lambda: {
        "tenant_id": "test-tenant",
        "name": "Test Tenant",
    }
    app.dependency_overrides[get_company_repository] = lambda: mock_repo

    with TestClient(app) as test_client:
        test_client.headers.update({"Authorization": "Bearer " + "a" * 40})
        yield test_client

    # Clear overrides after test
    app.dependency_overrides = {}
    settings.api.require_api_key = previous_require_api_key


@pytest.fixture
def unauthenticated_client():
    """
    Provides a TestClient WITHOUT auth override.

    Note: the app uses auto_error=False, so unauthenticated requests
    receive an 'anonymous' user rather than a 401. This fixture exists
    to explicitly test this design behaviour.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def patch_competitor_data_loader(monkeypatch):
    """
    Auto-use fixture that patches CompetitorDataLoader globally.

    This ensures ALL tests that use UnifiedCompanyLoader will get mock data
    instead of trying to load from the missing data/input/competitor_data.json file.
    """
    from solstein.domain.models import Company
    from solstein.data.loaders import CompetitorDataLoader

    # Create comprehensive test companies with all required financial fields
    test_companies = [
        Company(
            id="eneve_001",
            name="Eneve",
            industry="Energy Software",
            country="Germany",
            founded_year=2015,
            employees=150,
            revenue=5000000.0,
            growth_rate=0.25,
            profit_margin=0.15,
            funding_raised=2000000.0,
            valuation=50000000.0,
            github_url="https://github.com/eneve",
            website="https://eneve.de",
            description="Energy software company",
            ai_maturity=AIMaturity.STRONG,
            ai_maturity_score=7.5,
            geographic_presence=["Germany", "France", "UK", "Netherlands", "Belgium", "Austria", "Switzerland"],
            revenue_timeline=[
                {"year": 2020, "eur_millions": 2.0, "yoy_growth_pct": 0},
                {"year": 2021, "eur_millions": 3.0, "yoy_growth_pct": 50},
                {"year": 2022, "eur_millions": 4.0, "yoy_growth_pct": 33},
                {"year": 2023, "eur_millions": 5.0, "yoy_growth_pct": 25},
            ],
            revenue_cagr_3yr=40.0,
            revenue_cagr_5yr=25.0,
            ebitda_margin=30.0,
            recurring_revenue_pct=85.0,
            revenue_per_employee_eur_k=333.0,
            classification="Phoenix",
        ),
        Company(
            id="test_002",
            name="Test Company 2",
            industry="Energy Software",
            country="US",
            founded_year=2016,
            employees=100,
            revenue=3000000.0,
            growth_rate=0.20,
            profit_margin=0.12,
            funding_raised=1500000.0,
            valuation=30000000.0,
            github_url="https://github.com/test2",
            website="https://test2.com",
            description="Test company",
            ai_maturity=AIMaturity.MODERATE,
            ai_maturity_score=6.0,
            geographic_presence=["US", "Canada"],
            revenue_timeline=[
                {"year": 2020, "eur_millions": 1.5, "yoy_growth_pct": 0},
                {"year": 2021, "eur_millions": 2.0, "yoy_growth_pct": 33},
                {"year": 2022, "eur_millions": 2.5, "yoy_growth_pct": 25},
                {"year": 2023, "eur_millions": 3.0, "yoy_growth_pct": 20},
            ],
            revenue_cagr_3yr=20.0,
            revenue_cagr_5yr=20.0,
            ebitda_margin=15.0,
            recurring_revenue_pct=75.0,
            revenue_per_employee_eur_k=300.0,
            classification="Salt",
        ),
        Company(
            id="test_003",
            name="Test Company 3",
            industry="Energy Software",
            country="UK",
            founded_year=2017,
            employees=80,
            revenue=2000000.0,
            growth_rate=0.15,
            profit_margin=0.10,
            funding_raised=1000000.0,
            valuation=20000000.0,
            github_url="https://github.com/test3",
            website="https://test3.com",
            description="Test company",
            ai_maturity=AIMaturity.LOW,
            ai_maturity_score=5.0,
            geographic_presence=["UK", "Ireland"],
            revenue_timeline=[
                {"year": 2020, "eur_millions": 1.0, "yoy_growth_pct": 0},
                {"year": 2021, "eur_millions": 1.2, "yoy_growth_pct": 20},
                {"year": 2022, "eur_millions": 1.5, "yoy_growth_pct": 25},
                {"year": 2023, "eur_millions": 2.0, "yoy_growth_pct": 33},
            ],
            revenue_cagr_3yr=15.0,
            revenue_cagr_5yr=20.0,
            ebitda_margin=12.0,
            recurring_revenue_pct=65.0,
            revenue_per_employee_eur_k=250.0,
            classification="Lead",
        ),
    ]

    # Patch CompetitorDataLoader.load_companies to return test data
    def mock_load_companies(self, limit=None):
        return test_companies[:limit] if limit else test_companies

    monkeypatch.setattr(CompetitorDataLoader, "load_companies", mock_load_companies)


# Note: pytest-asyncio handles event_loop automatically with mode=auto
# Removed custom event_loop fixture - pytest-asyncio mode=auto manages this


@pytest.fixture(scope="function")
async def db_engine():
    """Shared async engine with connection pooling.

    This fixture creates a single SQLAlchemy async engine for the entire
    test session. It uses connection pooling to efficiently manage database
    connections across all tests.

    Configuration:
    - pool_size=5: Maximum 5 connections in the pool
    - max_overflow=10: Allow up to 10 additional connections if needed
    - pool_recycle=3600: Recycle connections after 1 hour
    - pool_pre_ping=True: Test connections before using them
    """
    db_url = get_test_database_url()
    async_url = convert_to_async_url(db_url)

    engine = create_async_engine(
        async_url,
        echo=False,
        pool_size=5,
        max_overflow=10,
        pool_recycle=3600,
        pool_pre_ping=True,
    )

    yield engine

    # Cleanup: dispose of all connections
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    """Per-test database session.

    This fixture provides a fresh AsyncSession for each test. The session
    is automatically rolled back after the test completes, ensuring test
    isolation and preventing data leakage between tests.

    Usage in tests:
        async def test_something(db_session):
            # db_session is an AsyncSession
            result = await db_session.execute(...)
    """
    async_session = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
        # Session is automatically rolled back after test
