from solstein.data.source_policy import SourceTier, default_source_policy_catalog


def test_default_source_policy_catalog_contains_core_sources() -> None:
    catalog = default_source_policy_catalog()

    assert "SEC_EDGAR" in catalog
    assert "COMPANIES_HOUSE" in catalog
    assert "NEWS_SIGNALS" in catalog


def test_default_source_policy_catalog_uses_free_tier_for_current_sources() -> None:
    catalog = default_source_policy_catalog()

    assert catalog["SEC_EDGAR"].tier == SourceTier.FREE
    assert catalog["COMPANIES_HOUSE"].tier == SourceTier.FREE
    assert catalog["NEWS_SIGNALS"].tier == SourceTier.FREE


def test_default_source_policy_catalog_required_identifiers_are_explicit() -> None:
    catalog = default_source_policy_catalog()

    assert catalog["SEC_EDGAR"].required_identifiers == {"ticker"}
    assert catalog["COMPANIES_HOUSE"].required_identifiers == {"company_number"}
