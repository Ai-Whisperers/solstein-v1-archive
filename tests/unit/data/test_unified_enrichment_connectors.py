from __future__ import annotations

from datetime import datetime, timezone

from solstein.data.connectors.contracts import ConnectorResponse
from solstein.data.connectors.signal_detectors.base import Signal
from solstein.data.unified.company import UnifiedCompany
from solstein.data.unified.enrichment import attach_news_signals, fill_identifiers_from_lookup


class _DummyDetector:
    def __init__(self, response: ConnectorResponse[list[Signal]]):
        self._response = response

    async def detect_signals_enveloped(self, company_name: str) -> ConnectorResponse[list[Signal]]:
        _ = company_name
        return self._response


class _DummyLoader:
    def __init__(self, detector: _DummyDetector | None, lookup_service=None):
        self.news_signal_detector = detector
        self.lookup_service = lookup_service


class _DummyLookupService:
    def __init__(self, response: ConnectorResponse[dict[str, object]]):
        self._response = response

    async def resolve_identifiers_enveloped(
        self,
        company_name: str,
        headquarters: str | None = None,
    ) -> ConnectorResponse[dict[str, object]]:
        _ = company_name
        _ = headquarters
        return self._response


def _company() -> UnifiedCompany:
    return UnifiedCompany(id="cmp-news-1", name="Acme Corp")


def test_attach_news_signals_success_populates_metadata() -> None:
    signal = Signal(
        signal_type="funding",
        company_name="Acme Corp",
        description="Raised Series A",
        confidence=0.9,
        source="https://example.com/news",
        detected_at=datetime.now(timezone.utc),
        raw_data={},
    )
    response = ConnectorResponse(
        status="success",
        connector="news_signal_detector",
        operation="detect_signals",
        payload=[signal],
        metadata={"attempts": 1},
    )
    loader = _DummyLoader(_DummyDetector(response))
    company = _company()

    enriched = attach_news_signals(loader, company)

    assert enriched.metric_justifications["news_signal_status"] == "success"
    assert enriched.metric_justifications["news_signal_count"] == "1"
    assert enriched.metric_observations["news_signals"]
    assert "news_signals" in enriched.enrichment_sources
    assert not enriched.enrichment_errors


def test_attach_news_signals_degraded_adds_error() -> None:
    response = ConnectorResponse(
        status="degraded",
        connector="news_signal_detector",
        operation="detect_signals",
        payload=[],
        error="No signals detected",
        metadata={"attempts": 2},
    )
    loader = _DummyLoader(_DummyDetector(response))
    company = _company()

    enriched = attach_news_signals(loader, company)

    assert enriched.metric_justifications["news_signal_status"] == "degraded"
    assert enriched.metric_justifications["news_signal_count"] == "0"
    assert enriched.enrichment_errors


def test_attach_news_signals_no_detector_keeps_company() -> None:
    loader = _DummyLoader(None)
    company = _company()

    enriched = attach_news_signals(loader, company)

    assert enriched is company
    assert not enriched.enrichment_errors


def test_fill_identifiers_from_lookup_updates_missing_fields() -> None:
    payload: dict[str, object] = {
        "ticker": "ACME",
        "company_number": "01234567",
        "isin": "US1234567890",
        "geography_code": "US",
    }
    response = ConnectorResponse(
        status="success",
        connector="identifier_lookup_service",
        operation="resolve_identifiers",
        payload=payload,
        metadata={"attempts": 1},
    )
    loader = _DummyLoader(None, _DummyLookupService(response))
    company = _company()

    enriched = fill_identifiers_from_lookup(loader, company)

    assert enriched.ticker == "ACME"
    assert enriched.company_number == "01234567"
    assert enriched.metric_justifications["identifier_lookup_status"] == "success"
    assert "identifier_lookup" in enriched.enrichment_sources
    assert "identifier_lookup_service" in enriched.metric_sources["ticker"]


def test_fill_identifiers_from_lookup_degraded_records_error() -> None:
    response = ConnectorResponse(
        status="degraded",
        connector="identifier_lookup_service",
        operation="resolve_identifiers",
        payload={},
        error="No identifiers resolved",
        metadata={"attempts": 2},
    )
    loader = _DummyLoader(None, _DummyLookupService(response))
    company = _company()

    enriched = fill_identifiers_from_lookup(loader, company)

    assert enriched.metric_justifications["identifier_lookup_status"] == "degraded"
    assert enriched.enrichment_errors
