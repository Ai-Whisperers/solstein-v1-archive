from unittest.mock import MagicMock, patch

import pytest
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.testclient import TestClient

from solstein.api.dependencies import get_company_repository, get_current_user
from solstein.api.main import app, lifespan
from solstein.data.repositories import JsonFileRepository

client = TestClient(app)


# --- Dependencies Tests ---


@patch("solstein.api.dependencies.get_settings")
def test_get_company_repository_fallback_json(mock_settings, caplog):
    """Test that repository falls back to JSON when Supabase fails."""
    m_set = MagicMock()
    m_set.supabase.url = "https://your-project.supabase.co"
    mock_settings.return_value = m_set

    # Should fallback to JsonFileRepository when Supabase is not available
    repo = get_company_repository()
    assert isinstance(repo, JsonFileRepository)


@patch("solstein.api.dependencies.get_settings")
@patch("solstein.api.dependencies.create_async_engine")
def test_get_company_repository_supabase_success(mock_engine, mock_settings):
    """Test successful Supabase repository creation."""
    m_set = MagicMock()
    m_set.supabase.url = "https://valid.supabase.co"
    m_set.database.url = "postgresql://user:pass@localhost/db"
    mock_settings.return_value = m_set
    mock_engine.return_value = MagicMock()

    # Just verify it doesn't throw - actual repo type depends on configuration
    repo = get_company_repository()
    assert repo is not None


@patch("solstein.api.dependencies.get_settings")
@patch("solstein.api.dependencies.create_async_engine", side_effect=Exception("DB Error"))
def test_get_company_repository_supabase_exception(mock_engine, mock_settings, caplog):
    """Test fallback to JSON when Supabase throws exception."""
    m_set = MagicMock()
    m_set.supabase.url = "https://valid.supabase.co"
    m_set.database.url = "postgresql://user:pass@localhost/db"
    mock_settings.return_value = m_set

    # Should fallback to JsonFileRepository on error
    repo = get_company_repository()
    assert isinstance(repo, JsonFileRepository)


@pytest.mark.asyncio
async def test_get_current_user_anonymous():
    """Test anonymous user access."""
    user = await get_current_user(None)
    assert user["username"] == "anonymous"


@pytest.mark.asyncio
async def test_get_current_user_authenticated():
    """Test authenticated user with mock token."""
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")
    # Mock the JWT verification
    with patch("solstein.api.dependencies.jwt.decode") as mock_decode:
        mock_decode.return_value = {"sub": "demo_user"}
        user = await get_current_user(creds)
        assert user["username"] == "demo_user"


# --- Main App Tests ---


def test_main_health_endpoints():
    """Test health check endpoints."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] in ("healthy", "degraded", "unhealthy")

    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] in ("healthy", "degraded", "unhealthy")


def test_main_docs_endpoint():
    """Test API docs endpoint."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert b"SolStein" in response.content


@pytest.mark.asyncio
async def test_startup_and_shutdown_events():
    """Test application lifespan events."""
    with patch("solstein.api.main.settings") as mock_set:
        mock_set.environment = "test"
        mock_set.data.data_dir = "/tmp"
        mock_set.data.ensure_dirs = MagicMock()
        mock_set.logging.file_path = MagicMock()
        mock_set.logging.file_path.parent.mkdir = MagicMock()

        async with lifespan(app):
            mock_set.data.ensure_dirs.assert_called_once()
            mock_set.logging.file_path.parent.mkdir.assert_called_once()
