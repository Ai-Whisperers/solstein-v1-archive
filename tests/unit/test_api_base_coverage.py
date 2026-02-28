from unittest.mock import MagicMock, patch

import pytest
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.testclient import TestClient

from solstein.api.dependencies import get_current_user, get_company_repository
from solstein.api.main import app, lifespan
from solstein.data.repositories import JsonFileRepository

client = TestClient(app)


# --- Dependencies Tests ---
@patch("solstein.api.dependencies.get_settings")
def test_get_company_repository_fallback_json(mock_settings, caplog):
    m_set = MagicMock()
    m_set.supabase.url = "https://your-project.supabase.co"
    mock_settings.return_value = m_set

    repo = get_company_repository()
    assert isinstance(repo, JsonFileRepository)


@patch("solstein.api.dependencies.get_settings")
@patch("solstein.api.dependencies.SupabaseRepository")
def test_get_company_repository_supabase_success(mock_supa, mock_settings):
    m_set = MagicMock()
    m_set.supabase.url = "https://valid.supabase.co"
    mock_settings.return_value = m_set
    mock_supa.return_value = MagicMock()

    repo = get_company_repository()
    assert repo is mock_supa.return_value


@patch("solstein.api.dependencies.get_settings")
@patch("solstein.api.dependencies.SupabaseRepository", side_effect=Exception("DB Error"))
def test_get_company_repository_supabase_exception(mock_supa, mock_settings, caplog):
    m_set = MagicMock()
    m_set.supabase.url = "https://valid.supabase.co"
    mock_settings.return_value = m_set

    repo = get_company_repository()
    assert isinstance(repo, JsonFileRepository)


@pytest.mark.asyncio
async def test_get_current_user_anonymous():
    user = await get_current_user(None)
    assert user["username"] == "anonymous"


@pytest.mark.asyncio
async def test_get_current_user_authenticated():
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")
    user = await get_current_user(creds)
    assert user["username"] == "demo_user"


# --- Main App Tests ---
def test_main_health_endpoints():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] in ("healthy", "degraded", "unhealthy")

    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] in ("healthy", "degraded", "unhealthy")


def test_main_docs_endpoint():
    response = client.get("/docs")
    assert response.status_code == 200
    assert b"SolStein" in response.content


@pytest.mark.asyncio
async def test_startup_and_shutdown_events():
    # Will just execute them to get coverage since they just log and mk dir
    with patch("solstein.api.main.settings") as mock_set:
        mock_set.environment = "test"
        mock_set.data.data_dir = "/tmp"
        mock_set.data.ensure_dirs = MagicMock()
        mock_set.logging.file_path = MagicMock()
        mock_set.logging.file_path.parent.mkdir = MagicMock()

        async with lifespan(app):
            mock_set.data.ensure_dirs.assert_called_once()
            mock_set.logging.file_path.parent.mkdir.assert_called_once()
