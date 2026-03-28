"""
STORY-046: Tests for instrumented adapter wrappers (adapters/instrumented.py).

Verifies that instrumentation wraps adapter calls and records metrics
without altering return values or swallowing exceptions.
"""

from unittest.mock import MagicMock

import pytest

from solstein.adapters.instrumented import (
    AdapterHealthRecord,
    InstrumentedDiscoverySource,
    InstrumentedEnrichmentSource,
)
from solstein.domain.models import DataSourceType, RawDataSource


def _make_enrichment_source(
    name: str = "test_enrichment",
    raw_content: dict | None = None,
    confidence: float = 0.85,
) -> MagicMock:
    """Create a mock enrichment source returning a RawDataSource."""
    mock = MagicMock()
    mock.source_name = name
    mock.source_type = DataSourceType.NEWS
    content = raw_content if raw_content is not None else {"key": "value"}
    mock.enrich.return_value = RawDataSource(
        source_name=name,
        source_type=DataSourceType.NEWS,
        raw_content=content,
        confidence=confidence,
    )
    return mock


def _make_discovery_source(
    name: str = "test_discovery",
    results: list | None = None,
) -> MagicMock:
    """Create a mock discovery source returning a list of candidates."""
    mock = MagicMock()
    mock.source_name = name
    mock.discover.return_value = results if results is not None else []
    return mock


class TestInstrumentedEnrichmentSource:
    """Tests for InstrumentedEnrichmentSource wrapper."""

    def test_enrich_returns_original_result(self):
        """Wrapper returns exactly what the inner adapter returns."""
        inner = _make_enrichment_source()
        wrapper = InstrumentedEnrichmentSource(inner)

        result = wrapper.enrich("comp-001", "Test Corp")

        assert isinstance(result, RawDataSource)
        assert result.confidence == 0.85
        assert result.raw_content == {"key": "value"}

    def test_enrich_records_success(self):
        """Successful call records a health record with status=success."""
        inner = _make_enrichment_source(name="yahoo")
        wrapper = InstrumentedEnrichmentSource(inner)

        wrapper.enrich("comp-001", "Test Corp")

        records = wrapper.health_records
        assert len(records) == 1
        assert records[0].adapter_name == "yahoo"
        assert records[0].adapter_type == "enrichment"
        assert records[0].status == "success"
        assert records[0].response_time_ms >= 0
        assert records[0].company_id == "comp-001"
        assert records[0].company_name == "Test Corp"
        assert records[0].error_message is None

    def test_enrich_records_error(self):
        """Failed call records a health record with status=error."""
        inner = _make_enrichment_source()
        inner.enrich.side_effect = ConnectionError("network down")
        wrapper = InstrumentedEnrichmentSource(inner)

        with pytest.raises(ConnectionError, match="network down"):
            wrapper.enrich("comp-001", "Test Corp")

        records = wrapper.health_records
        assert len(records) == 1
        assert records[0].status == "error"
        assert "network down" in records[0].error_message

    def test_enrich_preserves_exception(self):
        """Wrapper re-raises the original exception, not a wrapped one."""
        inner = _make_enrichment_source()
        inner.enrich.side_effect = ValueError("bad data")
        wrapper = InstrumentedEnrichmentSource(inner)

        with pytest.raises(ValueError, match="bad data"):
            wrapper.enrich("comp-001", "Test Corp")

    def test_multiple_calls_accumulate_records(self):
        """Each call appends a new record to health_records."""
        inner = _make_enrichment_source()
        wrapper = InstrumentedEnrichmentSource(inner)

        wrapper.enrich("comp-001", "Corp A")
        wrapper.enrich("comp-002", "Corp B")
        wrapper.enrich("comp-003", "Corp C")

        assert len(wrapper.health_records) == 3

    def test_source_name_property_delegates(self):
        """source_name is delegated to the inner adapter."""
        inner = _make_enrichment_source(name="patents")
        wrapper = InstrumentedEnrichmentSource(inner)

        assert wrapper.source_name == "patents"

    def test_source_type_property_delegates(self):
        """source_type is delegated to the inner adapter."""
        inner = _make_enrichment_source()
        wrapper = InstrumentedEnrichmentSource(inner)

        assert wrapper.source_type == DataSourceType.NEWS

    def test_health_records_returns_copy(self):
        """health_records returns a copy, not the internal list."""
        inner = _make_enrichment_source()
        wrapper = InstrumentedEnrichmentSource(inner)
        wrapper.enrich("comp-001", "Test Corp")

        records_a = wrapper.health_records
        records_b = wrapper.health_records
        assert records_a is not records_b

    def test_data_item_count_for_dict_content(self):
        """Data item count reflects dict key count."""
        inner = _make_enrichment_source(raw_content={"a": 1, "b": 2, "c": 3})
        wrapper = InstrumentedEnrichmentSource(inner)

        wrapper.enrich("comp-001", "Test Corp")

        assert wrapper.health_records[0].data_item_count == 3

    def test_data_item_count_for_list_content(self):
        """Data item count reflects list length when raw_content is a list.

        RawDataSource only accepts str|dict, so we use a MagicMock return
        value to exercise the instrumentation's list-counting branch.
        """
        inner = _make_enrichment_source()
        mock_result = MagicMock()
        mock_result.raw_content = [1, 2, 3, 4]
        mock_result.confidence = 0.9
        inner.enrich.return_value = mock_result
        wrapper = InstrumentedEnrichmentSource(inner)

        wrapper.enrich("comp-001", "Test Corp")

        assert wrapper.health_records[0].data_item_count == 4


class TestInstrumentedDiscoverySource:
    """Tests for InstrumentedDiscoverySource wrapper."""

    def test_discover_returns_original_results(self):
        """Wrapper returns exactly what the inner adapter returns."""
        candidates = [MagicMock(), MagicMock()]
        inner = _make_discovery_source(results=candidates)
        wrapper = InstrumentedDiscoverySource(inner)

        result = wrapper.discover("energy", "Solstein")

        assert result == candidates
        assert len(result) == 2

    def test_discover_records_success(self):
        """Successful call records a health record with correct count."""
        candidates = [MagicMock(), MagicMock(), MagicMock()]
        inner = _make_discovery_source(name="web_search", results=candidates)
        wrapper = InstrumentedDiscoverySource(inner)

        wrapper.discover("energy", "Solstein", max_results=10)

        records = wrapper.health_records
        assert len(records) == 1
        assert records[0].adapter_name == "web_search"
        assert records[0].adapter_type == "discovery"
        assert records[0].status == "success"
        assert records[0].data_item_count == 3

    def test_discover_records_error(self):
        """Failed call records error status and message."""
        inner = _make_discovery_source()
        inner.discover.side_effect = TimeoutError("request timed out")
        wrapper = InstrumentedDiscoverySource(inner)

        with pytest.raises(TimeoutError, match="request timed out"):
            wrapper.discover("energy", "Solstein")

        records = wrapper.health_records
        assert len(records) == 1
        assert records[0].status == "error"
        assert "timed out" in records[0].error_message

    def test_source_name_property_delegates(self):
        """source_name delegates to inner adapter."""
        inner = _make_discovery_source(name="static_catalog")
        wrapper = InstrumentedDiscoverySource(inner)

        assert wrapper.source_name == "static_catalog"

    def test_discover_with_extra_keywords(self):
        """Extra keywords are passed through to inner adapter."""
        inner = _make_discovery_source()
        wrapper = InstrumentedDiscoverySource(inner)

        wrapper.discover("energy", "Solstein", extra_keywords=["AI", "SaaS"])

        inner.discover.assert_called_once_with("energy", "Solstein", 50, ["AI", "SaaS"])


class TestAdapterHealthRecord:
    """Tests for the AdapterHealthRecord dataclass."""

    def test_default_values(self):
        """Health record has sensible defaults."""
        record = AdapterHealthRecord(
            adapter_name="test",
            adapter_type="enrichment",
            status="success",
            response_time_ms=42.5,
        )

        assert record.error_message is None
        assert record.data_item_count == 0
        assert record.confidence == 0.0
        assert record.company_id is None
        assert record.company_name is None
        assert record.timestamp is not None

    def test_error_record_fields(self):
        """Error record captures error message."""
        record = AdapterHealthRecord(
            adapter_name="failing_adapter",
            adapter_type="discovery",
            status="error",
            response_time_ms=1500.0,
            error_message="Connection refused",
        )

        assert record.status == "error"
        assert record.error_message == "Connection refused"
