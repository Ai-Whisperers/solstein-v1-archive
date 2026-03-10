from __future__ import annotations

import pytest

from solstein.config import get_settings
from solstein.data.connectors.contracts import ConnectorRequest, ConnectorResponse
from solstein.data.connectors.lookup_service import IdentifierLookupService
from solstein.data.connectors.news_signal_detector import NewsSignalDetector


def test_connector_response_builders() -> None:
    req = ConnectorRequest(connector="lookup", operation="resolve", inputs={"company": "Acme"})

    success = ConnectorResponse.success(req, payload={"ticker": "ACME"}, metadata={"source": "mock"})
    degraded = ConnectorResponse.degraded(req, payload={}, error="No identifiers")
    failure = ConnectorResponse.failure(req, error="timeout")

    assert success.status == "success"
    assert success.payload == {"ticker": "ACME"}
    assert degraded.status == "degraded"
    assert degraded.error == "No identifiers"
    assert failure.status == "failure"
    assert failure.payload is None


@pytest.mark.asyncio
async def test_lookup_service_enveloped_success(monkeypatch: pytest.MonkeyPatch) -> None:
    service = IdentifierLookupService()

    async def _stub(*args, **kwargs):
        return {"ticker": "ACME", "ticker_confidence": 0.9}

    monkeypatch.setattr(service, "resolve_identifiers", _stub)

    response = await service.resolve_identifiers_enveloped("Acme")

    assert response.status == "success"
    assert response.payload is not None
    assert response.payload["ticker"] == "ACME"


@pytest.mark.asyncio
async def test_lookup_service_enveloped_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    service = IdentifierLookupService()

    async def _boom(*args, **kwargs):
        raise RuntimeError("lookup down")

    monkeypatch.setattr(service, "resolve_identifiers", _boom)

    response = await service.resolve_identifiers_enveloped("Acme")

    assert response.status == "degraded"
    assert response.error is not None


@pytest.mark.asyncio
async def test_news_signal_detector_enveloped_degraded(monkeypatch: pytest.MonkeyPatch) -> None:
    detector = NewsSignalDetector(api_key="test-key")

    async def _stub(*args, **kwargs):
        return []

    monkeypatch.setattr(detector, "detect_signals", _stub)

    response = await detector.detect_signals_enveloped("Acme")

    assert response.status == "degraded"
    assert response.payload == []


@pytest.mark.asyncio
async def test_news_signal_detector_enveloped_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    detector = NewsSignalDetector(api_key="test-key")

    async def _boom(*args, **kwargs):
        raise RuntimeError("news api down")

    monkeypatch.setattr(detector, "detect_signals", _boom)

    response = await detector.detect_signals_enveloped("Acme")

    assert response.status == "degraded"
    assert response.error is not None


def test_connector_runtime_uses_config_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONNECTOR_MAX_ATTEMPTS", "2")
    monkeypatch.setenv("CONNECTOR_RETRY_BASE_DELAY", "0.1")
    monkeypatch.setenv("CONNECTOR_RETRY_MAX_DELAY", "0.3")
    monkeypatch.setenv("CONNECTOR_CIRCUIT_FAILURE_THRESHOLD", "3")
    monkeypatch.setenv("CONNECTOR_CIRCUIT_COOLDOWN_SECONDS", "15")

    get_settings.cache_clear()

    lookup = IdentifierLookupService()
    detector = NewsSignalDetector(api_key="test-key")

    assert lookup._runtime.retry_policy.max_attempts == 2
    assert lookup._runtime.retry_policy.base_delay_seconds == 0.1
    assert lookup._runtime.retry_policy.max_delay_seconds == 0.3
    assert lookup._runtime.circuit_breaker.failure_threshold == 3
    assert lookup._runtime.circuit_breaker.cooldown_seconds == 15.0

    assert detector._runtime.retry_policy.max_attempts == 2
    assert detector._runtime.circuit_breaker.failure_threshold == 3

    get_settings.cache_clear()
