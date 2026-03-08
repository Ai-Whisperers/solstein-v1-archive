from solstein.adapters.registry import build_default_registry
from solstein.config import Settings


def _names(settings: Settings) -> set[str]:
    registry = build_default_registry(settings)
    return {source.__class__.__name__ for source in registry.enrichment_sources}


def test_registry_legacy_mode_avoids_unified_duplicate_adapters() -> None:
    names = _names(Settings(feature_new_unified_loader=False))

    assert "LinkedInEnrichment" in names
    assert "WebsiteEnrichment" in names
    assert "PatentEnrichment" in names
    assert "LinkedInUnifiedAdapter" not in names
    assert "WebsiteUnifiedAdapter" not in names
    assert "PatentsUnifiedAdapter" not in names


def test_registry_unified_mode_avoids_legacy_duplicate_adapters() -> None:
    names = _names(Settings(feature_new_unified_loader=True))

    assert "LinkedInUnifiedAdapter" in names
    assert "WebsiteUnifiedAdapter" in names
    assert "PatentsUnifiedAdapter" in names
    assert "LinkedInEnrichment" not in names
    assert "WebsiteEnrichment" not in names
    assert "PatentEnrichment" not in names
