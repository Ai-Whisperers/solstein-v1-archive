import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import json
from fastapi.testclient import TestClient

from solstein.api.main import app
from solstein.api.dependencies import get_repository, get_current_user
from solstein.domain.models import Company, FinancialMetric, CompanyTier, ThreatLevel, AIMaturity

# Override authentication
app.dependency_overrides[get_current_user] = lambda: {"username": "test_user"}

# Shared fixtures
@pytest.fixture
def mock_repo():
    repo = MagicMock()
    app.dependency_overrides[get_repository] = lambda: repo
    yield repo
    app.dependency_overrides.pop(get_repository, None)

@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)

def make_company(cid="c1", name="Test", ind="Tech"):
    fin = FinancialMetric(revenue=10.0, growth_rate=5.0)
    return Company(
        id=cid, name=name, industry=ind, financials=fin,
        tier=CompanyTier.TIER_3, threat_level=ThreatLevel.MEDIUM,
        ai_maturity=AIMaturity.NONE,
        geographic_presence=["US"],
        growth_score=5.0, competitive_position_score=4.0
    )

# --- Companies Router ---
def test_get_companies(client, mock_repo):
    mock_repo.get_all.return_value = [make_company()]
    resp = client.get("/companies?limit=10&tier=Tier 1&industry=Tech&min_revenue=1")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    
    # Exception
    mock_repo.get_all.side_effect = Exception("DB Error")
    resp = client.get("/companies")
    assert resp.status_code == 500

def test_get_company(client, mock_repo):
    mock_repo.get_by_id.return_value = make_company()
    resp = client.get("/companies/c1")
    assert resp.status_code == 200
    
    mock_repo.get_by_id.return_value = None
    resp = client.get("/companies/c1")
    assert resp.status_code == 404
    
    mock_repo.get_by_id.side_effect = Exception("DB Error")
    resp = client.get("/companies/c1")
    assert resp.status_code == 500

def test_create_company(client, mock_repo):
    payload = {
        "id": "cnew", "name": "New Co", "industry": "Tech",
        "financials": {"revenue": 5.0}
    }
    mock_repo.save.return_value = make_company("cnew", "New Co")
    resp = client.post("/companies", json=payload)
    assert resp.status_code == 201
    
    mock_repo.save.side_effect = Exception("Save Error")
    resp = client.post("/companies", json=payload)
    assert resp.status_code == 400

def test_delete_company(client, mock_repo):
    mock_repo.delete.return_value = True
    resp = client.delete("/companies/c1")
    assert resp.status_code == 204
    
    mock_repo.delete.return_value = False
    resp = client.delete("/companies/c1")
    assert resp.status_code == 404
    
    mock_repo.delete.side_effect = Exception("Delete Error")
    resp = client.delete("/companies/c1")
    assert resp.status_code == 500

# --- Market Router ---
def test_analyze_market(client, mock_repo):
    # Empty
    mock_repo.get_all.return_value = []
    resp = client.get("/market/analysis?industry=Tech&region=US")
    assert resp.status_code == 200
    assert resp.json()["market_name"] == "Tech"
    
    # With data
    mock_repo.get_all.return_value = [make_company("c1", "A"), make_company("c2", "B")]
    resp = client.get("/market/analysis?industry=Tech&region=US")
    assert resp.status_code == 200
    assert len(resp.json()["companies"]) == 2
    
    # Exception
    mock_repo.get_all.side_effect = Exception("Analysis Error")
    resp = client.get("/market/analysis")
    assert resp.status_code == 500

def test_competitive_overlap(client, mock_repo):
    target = make_company("c1", "Target")
    peer = make_company("c2", "Peer")
    
    mock_repo.get_by_id.return_value = target
    mock_repo.get_all.return_value = [target, peer]
    
    resp = client.get("/market/overlap/c1")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    
    # NotFound
    mock_repo.get_by_id.return_value = None
    resp = client.get("/market/overlap/c1")
    assert resp.status_code == 404
    
    # Exception
    mock_repo.get_by_id.side_effect = Exception("Err")
    resp = client.get("/market/overlap/c1")
    assert resp.status_code == 500

def test_search_companies(client, mock_repo):
    mock_repo.get_all.return_value = [make_company("c1", "Apple", "Tech"), make_company("c2", "Tesla", "Auto")]
    
    resp = client.get("/market/search?query=appl&field=name")
    assert resp.status_code == 200
    assert len(resp.json()["results"]) == 1
    
    resp = client.get("/market/search?query=auto&field=industry")
    assert resp.status_code == 200
    assert len(resp.json()["results"]) == 1

    mock_repo.get_all.return_value = [make_company("c3", "Desc Test", "Tech")]
    mock_repo.get_all.return_value[0].description = "some awesome product"
    resp = client.get("/market/search?query=awesome&field=description")
    assert resp.status_code == 200
    assert len(resp.json()["results"]) == 1
    
    mock_repo.get_all.side_effect = Exception("Err")
    resp = client.get("/market/search?query=appl&field=name")
    assert resp.status_code == 500

# --- Scoring Router ---
def test_score_company(client, mock_repo):
    mock_repo.get_by_id.return_value = make_company()
    resp = client.post("/scoring/company/c1/score")
    assert resp.status_code == 200
    
    mock_repo.get_by_id.return_value = None
    resp = client.post("/scoring/company/c1/score")
    assert resp.status_code == 404
    
    mock_repo.get_by_id.side_effect = Exception("Err")
    resp = client.post("/scoring/company/c1/score")
    assert resp.status_code == 500

@patch("solstein.api.routers.scoring.TemporalClient.connect")
def test_batch_score_temporal_success(mock_connect, client):
    mock_temp = AsyncMock()
    mock_temp.start_workflow.return_value.id = "wf_123"
    mock_connect.return_value = mock_temp
    
    resp = client.get("/scoring/batch?industry=Tech")
    assert resp.status_code == 200
    assert resp.json()["status"] == "running"

@patch("solstein.api.routers.scoring.TemporalClient.connect", side_effect=Exception("No Temporal"))
@patch("solstein.analytics.activities.fetch_market_company_ids", new_callable=AsyncMock)
@patch("solstein.analytics.activities.calculate_company_score", new_callable=AsyncMock)
def test_batch_score_temporal_fallback(mock_calc, mock_fetch, mock_connect, client, mock_repo):
    mock_fetch.return_value = ["c1"]
    mock_calc.return_value = {"company_id": "c1"}
    
    resp = client.get("/scoring/batch")
    assert resp.status_code == 200
    assert resp.json()["processed_count"] == 1
    
    mock_fetch.side_effect = Exception("Fatal Error")
    resp = client.get("/scoring/batch")
    assert resp.status_code == 500

def test_scoring_stats(client, mock_repo):
    mock_repo.get_all.return_value = [make_company()]
    resp = client.get("/scoring/stats")
    assert resp.status_code == 200
    assert resp.json()["total_companies"] == 1
    
    mock_repo.get_all.side_effect = Exception("Err")
    resp = client.get("/scoring/stats")
    assert resp.status_code == 500

# --- Export Router ---
def test_export_excel(client, mock_repo):
    resp = client.get("/export/excel?industry=Tech")
    assert resp.status_code == 200
    assert resp.json()["status"] == "processing"
    
    resp_no_ind = client.get("/export/excel")
    assert resp_no_ind.status_code == 200
    
    with patch("solstein.api.routers.export.BackgroundTasks") as mock_bg:
        mock_bg.return_value.add_task.side_effect = Exception("Export Err")
        # Wait, BackgroundTasks is an injected dependency, not easy to patch this way.
        # Patching datetime is easier
        with patch("solstein.api.routers.export.datetime") as mock_dt:
            mock_dt.now.side_effect = Exception("Export Err")
            resp = client.get("/export/excel")
            assert resp.status_code == 500

def test_export_json_success(client, mock_repo):
    mock_repo.get_all.return_value = [make_company("c1", "A", "Tech")]
    resp = client.get("/export/json?industry=Tech")
    assert resp.status_code == 200
    assert resp.json()["total_companies"] == 1

def test_export_json_not_found(client, mock_repo):
    mock_repo.get_all.return_value = [make_company("c1", "A", "Auto")]
    resp = client.get("/export/json?industry=Tech")
    assert resp.status_code == 404

def test_export_json_error(client, mock_repo):
    mock_repo.get_all.side_effect = Exception("JSON err")
    resp = client.get("/export/json")
    assert resp.status_code == 500


# --- Jobs Router ---
@patch("solstein.api.routers.jobs.TemporalClient.connect", new_callable=AsyncMock)
def test_get_job_status_success(mock_connect, client):
    import datetime
    mock_handle = MagicMock()
    mock_handle.describe = AsyncMock()
    mock_handle.describe.return_value.status = "COMPLETED"
    mock_handle.describe.return_value.start_time = None
    mock_handle.describe.return_value.close_time = datetime.datetime(2023, 1, 1)
    
    # We must patch result as an AsyncMock that returns some dict
    mock_handle.result = AsyncMock(return_value={"total_processed": 5})
    
    mock_temp = MagicMock()
    mock_temp.get_workflow_handle.return_value = mock_handle
    mock_connect.return_value = mock_temp
    
    resp = client.get("/jobs/wf_123")
    assert resp.status_code == 200
    assert resp.json()["status"] == "COMPLETED"

@patch("solstein.api.routers.jobs.TemporalClient.connect", new_callable=AsyncMock)
def test_get_job_status_result_error(mock_connect, client):
    import datetime
    mock_handle = MagicMock()
    mock_handle.describe = AsyncMock()
    mock_handle.describe.return_value.status = "COMPLETED"
    mock_handle.describe.return_value.start_time = None
    mock_handle.describe.return_value.close_time = datetime.datetime(2023, 1, 1)
    
    mock_handle.result = AsyncMock(side_effect=Exception("Failed Result"))
    
    mock_temp = MagicMock()
    mock_temp.get_workflow_handle.return_value = mock_handle
    mock_connect.return_value = mock_temp
    
    resp = client.get("/jobs/wf_123")
    assert resp.status_code == 200
    assert "Workflow failed" in resp.json()["error"]

@patch("solstein.api.routers.jobs.TemporalClient.connect", side_effect=Exception("Job Err"))
def test_get_job_status_error(mock_connect, client):
    resp = client.get("/jobs/wf_123")
    assert resp.status_code == 500


# --- Simulation Router ---
def test_run_simulation_success(client, mock_repo):
    payload = {
        "id": "s1", "name": "Scen1", "description": "desc",
        "conditions": [{"type": "interest_rate", "name": "rate up", "impact_factor": 1.05, "description": "up 5%", "affected_industries": ["Tech"]}]
    }
    # One invalid condition to test error ignoring
    invalid_payload = json.loads(json.dumps(payload))
    invalid_payload["conditions"].append({"type": "InvalidType", "name": "inv", "impact_factor": 1.0, "description": ""})
    
    mock_repo.get_all.return_value = [make_company()]

    # Since we use strict Pydantic Domains, passing bad Enums instantly 422s.
    resp_invalid = client.post("/simulation/run", json=invalid_payload)
    assert resp_invalid.status_code == 422

    # Verify a valid payload runs through 200 properly.
    resp_valid = client.post("/simulation/run", json=payload)
    assert resp_valid.status_code == 200
    assert len(resp_valid.json()) == 1

def test_run_simulation_empty(client, mock_repo):
    payload = {
        "id": "s1", "name": "Scen1", "description": "desc",
        "conditions": []
    }
    mock_repo.get_all.return_value = []
    resp = client.post("/simulation/run", json=payload)
    assert resp.status_code == 404

def test_run_simulation_error(client, mock_repo):
    payload = {
        "id": "s1", "name": "Scen1", "description": "desc",
        "conditions": []
    }
    mock_repo.get_all.side_effect = Exception("Sim Err")
    resp = client.post("/simulation/run", json=payload)
    assert resp.status_code == 500
