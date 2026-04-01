"""
STORY-046: Tests for adapter registry (adapters/registry.py).

Covers registration, lookup, property accessors, and edge cases
for the SourceRegistry dataclass.
"""

from unittest.mock import MagicMock

from solstein.adapters.registry import SourceRegistry


def _make_mock_source(name: str, source_type: str = "enrichment") -> MagicMock:
    """Create a mock adapter source with a source_name attribute."""
    mock = MagicMock()
    mock.source_name = name
    mock.source_type = source_type
    return mock


class TestSourceRegistryRegistration:
    """Tests for registering adapters into the registry."""

    def test_register_discovery_source(self):
        """Discovery source can be registered and retrieved."""
        registry = SourceRegistry()
        source = _make_mock_source("web_search", "discovery")
        registry.register_discovery(source)

        assert len(registry.discovery_sources) == 1
        assert registry.discovery_sources[0].source_name == "web_search"

    def test_register_enrichment_source(self):
        """Enrichment source can be registered and retrieved."""
        registry = SourceRegistry()
        source = _make_mock_source("yahoo_finance")
        registry.register_enrichment(source)

        assert len(registry.enrichment_sources) == 1
        assert registry.enrichment_sources[0].source_name == "yahoo_finance"

    def test_register_unified_source(self):
        """Unified source can be registered and retrieved."""
        registry = SourceRegistry()
        source = _make_mock_source("funding_unified")
        registry.register_unified(source)

        assert len(registry.unified_sources) == 1
        assert registry.unified_sources[0].source_name == "funding_unified"

    def test_register_multiple_discovery_sources(self):
        """Multiple discovery sources can be registered."""
        registry = SourceRegistry()
        for name in ["static_catalog", "competitor_json", "web_search"]:
            registry.register_discovery(_make_mock_source(name, "discovery"))

        assert len(registry.discovery_sources) == 3
        names = [s.source_name for s in registry.discovery_sources]
        assert names == ["static_catalog", "competitor_json", "web_search"]

    def test_register_multiple_enrichment_sources(self):
        """Multiple enrichment sources can be registered."""
        registry = SourceRegistry()
        for name in ["yahoo", "patents", "linkedin"]:
            registry.register_enrichment(_make_mock_source(name))

        assert len(registry.enrichment_sources) == 3

    def test_register_duplicate_name_allowed(self):
        """Registry allows duplicate adapter names (no dedup enforced)."""
        registry = SourceRegistry()
        source_a = _make_mock_source("same_name")
        source_b = _make_mock_source("same_name")
        registry.register_enrichment(source_a)
        registry.register_enrichment(source_b)

        assert len(registry.enrichment_sources) == 2


class TestSourceRegistryLookup:
    """Tests for retrieving registered adapters."""

    def test_empty_registry_returns_empty_lists(self):
        """A fresh registry has no sources in any category."""
        registry = SourceRegistry()
        assert registry.discovery_sources == []
        assert registry.enrichment_sources == []
        assert registry.unified_sources == []

    def test_all_enrichment_sources_combines_legacy_and_unified(self):
        """all_enrichment_sources combines enrichment + unified sources."""
        registry = SourceRegistry()
        legacy = _make_mock_source("yahoo")
        unified = _make_mock_source("funding_unified")
        registry.register_enrichment(legacy)
        registry.register_unified(unified)

        combined = registry.all_enrichment_sources
        assert len(combined) == 2
        names = [s.source_name for s in combined]
        assert "yahoo" in names
        assert "funding_unified" in names

    def test_all_enrichment_sources_empty_when_nothing_registered(self):
        """all_enrichment_sources returns empty list on fresh registry."""
        registry = SourceRegistry()
        assert registry.all_enrichment_sources == []

    def test_discovery_does_not_leak_into_enrichment(self):
        """Discovery sources are not visible in enrichment properties."""
        registry = SourceRegistry()
        registry.register_discovery(_make_mock_source("web_search", "discovery"))

        assert len(registry.discovery_sources) == 1
        assert len(registry.enrichment_sources) == 0
        assert len(registry.all_enrichment_sources) == 0

    def test_enrichment_does_not_leak_into_discovery(self):
        """Enrichment sources are not visible in discovery property."""
        registry = SourceRegistry()
        registry.register_enrichment(_make_mock_source("yahoo"))

        assert len(registry.enrichment_sources) == 1
        assert len(registry.discovery_sources) == 0

    def test_unified_appears_in_all_enrichment_but_not_plain_enrichment(self):
        """Unified sources appear in all_enrichment but not enrichment_sources."""
        registry = SourceRegistry()
        registry.register_unified(_make_mock_source("news_unified"))

        assert len(registry.enrichment_sources) == 0
        assert len(registry.unified_sources) == 1
        assert len(registry.all_enrichment_sources) == 1

    def test_properties_return_new_list_each_call(self):
        """Property accessors return fresh lists (no shared references)."""
        registry = SourceRegistry()
        registry.register_enrichment(_make_mock_source("yahoo"))

        list_a = registry.enrichment_sources
        list_b = registry.enrichment_sources
        assert list_a is not list_b
        assert list_a == list_b
