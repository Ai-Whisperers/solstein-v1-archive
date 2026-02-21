import pytest
from fastapi.testclient import TestClient
from fastapi import Request
from starlette.exceptions import HTTPException
from pydantic import BaseModel, ConfigDict
from solstein.api.main import app

# Add a test endpoint to raise exceptions
@app.get("/_test/error500")
async def raise_500():
    raise ValueError("A test error")

@app.get("/_test/error400")
async def raise_400():
    raise HTTPException(status_code=400, detail="A manual HTTP error")

class MockModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    req_field: int

@app.post("/_test/validation")
async def trigger_validation_error(model: MockModel):
    return {"ok": True}

client = TestClient(app)

def test_exception_handler_500():
    # Will hit LoggingMiddleware exception and global 500 handler
    with pytest.raises(ValueError):
        # By default TestClient raises server errors. We can suppress it.
        client.get("/_test/error500")
        
    client_no_raise = TestClient(app, raise_server_exceptions=False)
    resp = client_no_raise.get("/_test/error500")
    assert resp.status_code == 500
    assert "Internal Server Error" in resp.json()["error"]

def test_exception_handler_http():
    resp = client.get("/_test/error400")
    assert resp.status_code == 400
    assert "A manual HTTP error" in resp.json()["details"]
    assert resp.headers.get("X-Request-ID") is not None

def test_exception_handler_validation():
    # Send missing req_field
    resp = client.post("/_test/validation", json={})
    assert resp.status_code == 422
    assert "Unprocessable Entity" in resp.json()["error"]
    assert resp.headers.get("X-Request-ID") is not None
