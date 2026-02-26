import os
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("GITHUB_TOKEN", "test-github-token-12345")

from factories import make_company



from solstein.api.dependencies import get_current_user, get_repository
from solstein.api.main import app
from solstein.core.repositories import CompanyRepository


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
    repo = MagicMock(spec=CompanyRepository)
    repo.get_all.return_value = [mock_company]
    repo.get_by_id.return_value = mock_company
    return repo


@pytest.fixture
def client(mock_repo):
    """Provides an authenticated TestClient with dependency overrides."""
    app.dependency_overrides[get_current_user] = lambda: {
        "username": "testuser",
        "role": "admin",
    }
    app.dependency_overrides[get_repository] = lambda: mock_repo

    with TestClient(app) as test_client:
        yield test_client

    # Clear overrides after test
    app.dependency_overrides = {}


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
    
    # Create minimal test companies with required fields
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
            ai_maturity_score=7.5,
            geographic_presence=["Germany", "France", "UK", "Netherlands", "Belgium", "Austria", "Switzerland"],
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
            ai_maturity_score=6.0,
            geographic_presence=["US", "Canada"],
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
            ai_maturity_score=5.0,
            geographic_presence=["UK", "Ireland"],
        ),
    ]
    
    # Patch CompetitorDataLoader.load_companies to return test data
    def mock_load_companies(self, limit=None):
        return test_companies[:limit] if limit else test_companies
    
    monkeypatch.setattr(CompetitorDataLoader, "load_companies", mock_load_companies)
