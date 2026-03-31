"""Root conftest for the Solstein test suite.

STORY-254: All heavy imports (config, database, loaders) are deferred to
fixture time so that ``pytest --collect-only`` succeeds in a minimal
environment without DATABASE__URL or a running database.
"""

import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

_ = os.environ.setdefault("GITHUB_TOKEN", "test-github-token-12345")

# ---------------------------------------------------------------------------
# Lightweight imports only — everything below is safe at collection time.
# Heavy imports (config, database, loaders, API app) are deferred into the
# fixtures that actually need them.
# ---------------------------------------------------------------------------

try:
    from tests.factories import make_company
except ModuleNotFoundError as exc:
    if exc.name == "factory":
        raise ModuleNotFoundError(
            "Missing test dependency 'factory-boy'. Install dev dependencies with `uv sync --dev` or "
            "`pip install -e .[dev]` before running tests."
        ) from exc
    raise


def _load_api_test_dependencies():
    """Return API app and dependency objects for test fixtures.

    Lazy import: only triggers config/database access when a test actually
    needs the API client.
    """
    try:
        from solstein.api.dependencies import (  # noqa: lazy-import
            get_company_repository,
            get_current_tenant,
            get_current_user,
        )
        from solstein.api.main import app as _api_app  # noqa: lazy-import
    except ImportError as exc:
        raise ImportError(
            "API dependencies not available -- solstein.api.main failed to import. "
            "Check that AuthenticationMiddleware exists in solstein.api.middleware.security."
        ) from exc
    return _api_app, get_company_repository, get_current_tenant, get_current_user


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
    from fastapi.testclient import TestClient  # noqa: lazy-import

    from solstein.config import get_settings  # noqa: lazy-import

    app, get_company_repository, get_current_tenant, get_current_user = _load_api_test_dependencies()
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
    from fastapi.testclient import TestClient  # noqa: lazy-import

    app, _, _, _ = _load_api_test_dependencies()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_competitor_data(monkeypatch):
    """
    Opt-in fixture that patches CompetitorDataLoader with test data.

    STORY-044: Converted from autouse=True to explicit opt-in.
    Tests that need mock data loading must explicitly request this fixture.
    Tests that exercise real data loading should NOT use this fixture.

    Usage:
        def test_something(mock_competitor_data):
            # CompetitorDataLoader.load_companies() returns 3 test companies
            ...
    """
    from solstein.data.loaders import CompetitorDataLoader  # noqa: lazy-import
    from tests.test_data import make_test_companies  # noqa: lazy-import

    test_companies = make_test_companies()

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
    from sqlalchemy.ext.asyncio import create_async_engine  # noqa: lazy-import

    from solstein.database_config import convert_to_async_url, get_test_database_url  # noqa: lazy-import

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
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker  # noqa: lazy-import

    async_session = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
        # Session is automatically rolled back after test
