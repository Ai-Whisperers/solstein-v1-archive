"""
Integration tests for Export and Jobs API endpoints.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

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
