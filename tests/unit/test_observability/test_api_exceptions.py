"""Tests for secure error response handling."""

from unittest.mock import Mock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from solstein.api.exceptions import APIError, setup_exception_handlers
from solstein.exceptions import NotFoundError

# Create a test app
app = FastAPI()
setup_exception_handlers(app)

class DummyPayload(BaseModel):
    email: str
    age: int

@app.get("/api-error")
def trigger_api_error():
    raise APIError(code="TEST_ERROR", message="Test API error", status_code=400)

@app.get("/domain-error")
def trigger_domain_error():
    raise NotFoundError("Company", "COMP-123")

@app.post("/validation-error")
def trigger_validation_error(payload: DummyPayload):
    return {"status": "ok"}

@app.get("/generic-error")
def trigger_generic_error():
    raise ValueError("Secret error details")

client = TestClient(app, raise_server_exceptions=False)

class TestAPIError:
    """Test APIError custom exception."""

    def test_api_error_creation(self):
        """Test APIError creation."""
        exc = APIError("NOT_FOUND", "Resource not found", 404)
        assert exc.code == "NOT_FOUND"
        assert exc.message == "Resource not found"
        assert exc.status_code == 404

    def test_api_error_response(self):
        """Test APIError correctly mapped to JSONResponse."""
        response = client.get("/api-error")
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "TEST_ERROR"
        assert data["error"]["message"] == "Test API error"

class TestSolsteinErrorHandler:
    """Test SolsteinError exception handler."""

    def test_solstein_error_response(self):
        """Test SolsteinError properly serialized."""
        response = client.get("/domain-error")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "NOT_FOUND"

    def test_solstein_error_no_traceback_in_production(self):
        """Test SolsteinError never has traceback in prod."""
        with patch("solstein.api.exceptions.get_settings") as mock:
            mock.return_value = Mock(debug=False, environment="production")
            response = client.get("/domain-error")
            data = response.text
            assert "traceback" not in data.lower()
            assert "stack_trace" not in data.lower()

class TestValidationExceptionHandler:
    """Test Pydantic validation error handler."""

    def test_validation_error_formatting(self):
        """Test validation errors are formatted properly."""
        # Provide invalid payload
        response = client.post("/validation-error", json={"email": "not-an-email", "age": "abc"})
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "details" in data["error"]

class TestGlobalExceptionHandler:
    """Test global exception handler."""

    def test_internal_error_response(self):
        """Test internal error returns safe response in production."""
        with patch("solstein.api.exceptions.get_settings") as mock:
            mock.return_value = Mock(debug=False, environment="production")
            response = client.get("/generic-error")
            assert response.status_code == 500
            data = response.json()
            assert "error" in data
            assert data["error"]["code"] == "INTERNAL_ERROR"
            assert "unexpected error occurred" in data["error"]["message"].lower()
            assert "Secret" not in response.text
            assert "ValueError" not in response.text
