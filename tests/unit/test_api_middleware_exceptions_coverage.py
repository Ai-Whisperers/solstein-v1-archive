import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict
from starlette.exceptions import HTTPException

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
    client_no_raise = TestClient(app, raise_server_exceptions=False)
    resp = client_no_raise.get("/_test/error500")
    assert resp.status_code == 500
    data = resp.json()
    assert data["error"]["code"] == "INTERNAL_ERROR"
    assert "request_id" in data


def test_exception_handler_http():
    client_no_raise = TestClient(app, raise_server_exceptions=False)
    resp = client_no_raise.get("/_test/error400")
    assert resp.status_code == 400
    data = resp.json()
    assert "A manual HTTP error" in data["error"]["message"]
    # Check for Request ID in body or header
    assert data.get("request_id") is not None or resp.headers.get("X-Request-ID") is not None


def test_exception_handler_validation():
    # Send missing req_field
    client_no_raise = TestClient(app, raise_server_exceptions=False)
    resp = client_no_raise.post("/_test/validation", json={})
    assert resp.status_code == 422
    data = resp.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data.get("request_id") is not None
