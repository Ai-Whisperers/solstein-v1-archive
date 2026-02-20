from fastapi.testclient import TestClient
from solstein.api.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data

def test_companies():
    response = client.get("/companies")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_market_analysis():
    response = client.get("/market/market/analysis?industry=Energy%20Software")
    # It might return 200 or 404 depending on data, but should be valid JSON
    assert response.status_code in [200, 404]

def test_search():
    response = client.get("/market/search?query=test")
    assert response.status_code == 200
    assert "results" in response.json()

def test_stats():
    response = client.get("/scoring/stats")
    assert response.status_code == 200
    assert "total_companies" in response.json()
