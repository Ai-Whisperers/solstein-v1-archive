import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

os.environ.setdefault("GITHUB_TOKEN", "test-github-token-12345")

from solstein.api.main import app
from solstein.api.dependencies import get_current_user, get_repository
from solstein.core.repositories import CompanyRepository
from tests.factories import make_company


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
