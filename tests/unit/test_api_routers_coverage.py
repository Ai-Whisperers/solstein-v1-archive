import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from solstein.api.dependencies import get_company_repository, get_current_user
from solstein.api.main import app
from solstein.domain.models import (
    AIMaturity,
    Company,
    CompanyTier,
    FinancialMetric,
    ThreatLevel,
)

# Override authentication
app.dependency_overrides[get_current_user] = lambda: {"username": "test_user"}


@pytest.fixture(autouse=True)
def bypass_rate_limit(monkeypatch):
    """Bypass rate limiting to prevent 429 errors across multiple tests."""
    monkeypatch.setattr(
        "solstein.api.middleware.rate_limit.RateLimitMiddleware._check_rate_limit",
        lambda self, key, rpm: (True, {}),
    )


# Shared fixtures
@pytest.fixture
def mock_repo():
    repo = MagicMock()
    # Use AsyncMock for methods that are awaited by routers
    repo.get_all = AsyncMock(return_value=[])
    repo.get_by_id = AsyncMock(return_value=None)
    repo.save = AsyncMock(return_value=None)
    repo.delete = AsyncMock(return_value=False)
    repo.search = AsyncMock(return_value=[])
    repo.get_all_filtered = AsyncMock(return_value=[])
    repo.filter_by = AsyncMock(return_value=[])
    app.dependency_overrides[get_company_repository] = lambda: repo
    yield repo
    app.dependency_overrides.pop(get_company_repository, None)


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


def make_company(cid="c1", name="Test", ind="Tech"):
    fin = FinancialMetric(revenue=10.0, growth_rate=5.0)
    return Company(
        id=cid,
        name=name,
        industry=ind,
        financials=fin,
        tier=CompanyTier.TIER_3,
        threat_level=ThreatLevel.MEDIUM,
        ai_maturity=AIMaturity.NONE,
        geographic_presence=["US"],
        growth_score=5.0,
        competitive_position_score=4.0,
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
        "id": "cnew",
        "name": "New Co",
        "industry": "Tech",
        "financials": {"revenue": 5.0},
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
    mock_repo.get_all_filtered.return_value = []
    resp = client.get("/market/analysis?industry=Tech&region=US")
    assert resp.status_code == 200
    assert resp.json()["market_name"] == "Tech"

    # With data
    mock_repo.get_all_filtered.return_value = [make_company("c1", "A"), make_company("c2", "B")]
    resp = client.get("/market/analysis?industry=Tech&region=US")
    assert resp.status_code == 200
    assert len(resp.json()["companies"]) == 2

    # Exception
    mock_repo.get_all_filtered.side_effect = Exception("Analysis Error")
    resp = client.get("/market/analysis")
    assert resp.status_code == 500


def test_competitive_overlap(client, mock_repo):
    target = make_company("c1", "Target")
    peer = make_company("c2", "Peer")

    mock_repo.get_by_id.return_value = target
    mock_repo.filter_by.return_value = [target, peer]

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
    apple = make_company("c1", "Apple", "Tech")
    tesla = make_company("c2", "Tesla", "Auto")
    desc_co = make_company("c3", "Desc Test", "Tech")

    # name search
    mock_repo.search.return_value = [apple]
    resp = client.get("/market/search?query=appl&field=name")
    assert resp.status_code == 200
    assert len(resp.json()["results"]) == 1

    # industry search
    mock_repo.search.return_value = [tesla]
    resp = client.get("/market/search?query=auto&field=industry")
    assert resp.status_code == 200
    assert len(resp.json()["results"]) == 1

    # description search
    mock_repo.search.return_value = [desc_co]
    resp = client.get("/market/search?query=awesome&field=description")
    assert resp.status_code == 200
    assert len(resp.json()["results"]) == 1

    # error
    mock_repo.search.side_effect = Exception("Err")
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


def test_batch_score_disabled(client):
    """Batch scoring is disabled (Temporal integration removed) - returns 501."""
    resp = client.get("/scoring/batch?industry=Tech")
    assert resp.status_code == 501

    resp = client.get("/scoring/batch")
    assert resp.status_code == 501


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
def test_get_job_status_disabled(client):
    """Job status is disabled (Temporal integration removed) - returns 501."""
    resp = client.get("/jobs/wf_123")
    assert resp.status_code == 501


# --- Simulation Router ---
def test_run_simulation_success(client, mock_repo):
    payload = {
        "id": "s1",
        "name": "Scen1",
        "description": "desc",
        "conditions": [
            {
                "type": "interest_rate",
                "name": "rate up",
                "impact_factor": 1.05,
                "description": "up 5%",
                "affected_industries": ["Tech"],
            }
        ],
    }
    # One invalid condition to test error ignoring
    invalid_payload = json.loads(json.dumps(payload))
    invalid_payload["conditions"].append(
        {"type": "InvalidType", "name": "inv", "impact_factor": 1.0, "description": ""}
    )

    mock_repo.get_all.return_value = [make_company()]

    # Since we use strict Pydantic Domains, passing bad Enums instantly 422s.
    resp_invalid = client.post("/simulation/run", json=invalid_payload)
    assert resp_invalid.status_code == 422

    # Verify a valid payload runs through 200 properly.
    resp_valid = client.post("/simulation/run", json=payload)
    assert resp_valid.status_code == 200
    assert len(resp_valid.json()) == 1


def test_run_simulation_empty(client, mock_repo):
    payload = {"id": "s1", "name": "Scen1", "description": "desc", "conditions": []}
    mock_repo.get_all.return_value = []
    resp = client.post("/simulation/run", json=payload)
    assert resp.status_code == 404


def test_run_simulation_error(client, mock_repo):
    payload = {"id": "s1", "name": "Scen1", "description": "desc", "conditions": []}
    mock_repo.get_all.side_effect = Exception("Sim Err")
    resp = client.post("/simulation/run", json=payload)
    assert resp.status_code == 500
