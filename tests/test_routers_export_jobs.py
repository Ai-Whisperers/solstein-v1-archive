"""
Integration tests for Export and Jobs API endpoints.
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from datetime import datetime

from tests.factories import make_company


# ---------------------------------------------------------------------------
# GET /export/excel
# ---------------------------------------------------------------------------
@patch("solstein.api.routers.export.excel_exporter")
def test_export_to_excel(mock_exporter, client, mock_repo):
    """Test background excel export endpoint."""
    mock_company = make_company()
    mock_repo.get_all.return_value = [mock_company]

    response = client.get("/export/excel?industry=Technology")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Export started"
    assert "solstein_technology" in data["filename"]

    # In FastAPI, TestClient runs background tasks synchronously after returning response
    mock_exporter.create_dashboard.assert_called_once()
    mock_repo.get_all.assert_called_once()

# ---------------------------------------------------------------------------
# GET /export/json
# ---------------------------------------------------------------------------
def test_export_to_json(client, mock_repo):
    """Test JSON export endpoint."""
    mock_company = make_company()
    mock_company.industry = "Technology"
    mock_repo.get_all.return_value = [mock_company]

    response = client.get("/export/json?industry=Technology")
    assert response.status_code == 200
    data = response.json()
    assert data["total_companies"] == 1
    assert data["companies"][0]["name"] == mock_company.name

def test_export_to_json_not_found(client, mock_repo):
    """Test JSON export returns 404 when no companies found."""
    mock_repo.get_all.return_value = []

    response = client.get("/export/json?industry=Unknown")
    assert response.status_code == 404

# ---------------------------------------------------------------------------
# GET /jobs/{workflow_id}
# ---------------------------------------------------------------------------
@patch("solstein.api.routers.jobs.TemporalClient.connect", new_callable=AsyncMock)
def test_get_job_status_completed(mock_connect, client):
    """Test retrieving completed job status."""
    mock_client = MagicMock()
    mock_connect.return_value = mock_client
    
    mock_handle = MagicMock()
    mock_desc = MagicMock()
    mock_desc.status = "COMPLETED"
    mock_desc.start_time = None
    mock_desc.close_time = datetime(2026, 2, 20, 12, 0, 0)
    
    mock_client.get_workflow_handle.return_value = mock_handle
    mock_handle.describe = AsyncMock(return_value=mock_desc)
    mock_handle.result = AsyncMock(return_value={"success": True})

    response = client.get("/jobs/wf-123")
    assert response.status_code == 200
    data = response.json()
    assert data["workflow_id"] == "wf-123"
    assert data["status"] == "COMPLETED"
    assert data["result"] == {"success": True}

@patch("solstein.api.routers.jobs.TemporalClient.connect", new_callable=AsyncMock)
def test_get_job_status_running(mock_connect, client):
    """Test retrieving running job status."""
    mock_client = MagicMock()
    mock_connect.return_value = mock_client
    
    mock_handle = MagicMock()
    mock_desc = MagicMock()
    mock_desc.status = "RUNNING"
    mock_desc.start_time = datetime(2026, 2, 20, 12, 0, 0)
    mock_desc.close_time = None
    
    mock_client.get_workflow_handle.return_value = mock_handle
    mock_handle.describe = AsyncMock(return_value=mock_desc)

    response = client.get("/jobs/wf-456")
    assert response.status_code == 200
    data = response.json()
    assert data["workflow_id"] == "wf-456"
    assert data["status"] == "RUNNING"
    assert "result" not in data
