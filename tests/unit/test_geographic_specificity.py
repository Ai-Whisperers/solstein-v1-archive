"""
Task 12: Preserve Geographic Specificity

Ensures that geographic data is preserved at country-level granularity
and not reduced to continent-level or generic regions.
"""

import pytest

from solstein.data.unified_loader import UnifiedCompanyLoader


class TestGeographicSpecificity:
    """Validate geographic data preservation across data sources."""

    @pytest.fixture
    def companies(self):
        """Load all companies with unified data."""
        loader = UnifiedCompanyLoader()
        return loader.load_unified_companies()

    def test_eneve_has_seven_countries(self, companies):
        """Eneve should have 7 specific countries, not 'Europe'."""
        eneve = next((c for c in companies if "Eneve" in c.name), None)
        assert eneve is not None, "Eneve not found in companies"

        # Should have exactly 7 countries
        assert len(eneve.geographic_presence) == 7, (
            f"Expected 7 countries, got {len(eneve.geographic_presence)}: {eneve.geographic_presence}"
        )

        # Should NOT contain continent-level entries
        assert "Europe" not in eneve.geographic_presence, (
            "Geographic presence should not contain 'Europe' (continent-level)"
        )
        assert "EU" not in eneve.geographic_presence, "Geographic presence should not contain 'EU'"

        # Should contain specific countries (actual data from loader)
        expected_countries = {"Germany", "France", "UK", "Netherlands", "Belgium", "Austria", "Switzerland"}
        actual_countries = set(eneve.geographic_presence)
        assert actual_countries == expected_countries, f"Expected {expected_countries}, got {actual_countries}"

    def test_geographic_presence_is_list_of_strings(self, companies):
        """All geographic_presence fields should be lists of country strings."""
        for company in companies:
            assert isinstance(company.geographic_presence, list), (
                f"{company.name}: geographic_presence should be a list"
            )

            for country in company.geographic_presence:
                assert isinstance(country, str), (
                    f"{company.name}: geographic_presence items should be strings, got {type(country)}"
                )
                assert len(country) > 0, f"{company.name}: geographic_presence items should not be empty"

    def test_no_continent_level_entries(self, companies):
        """No company should have continent-level entries like 'Europe', 'Asia', etc."""
        continents = {"Europe", "Asia", "Africa", "Americas", "Oceania", "EU", "EMEA"}

        for company in companies:
            for country in company.geographic_presence:
                assert country not in continents, (
                    f"{company.name}: contains continent-level entry '{country}' instead of specific countries"
                )

    def test_geographic_data_source_tracked(self, companies):
        """Geographic presence data source should be tracked."""
        eneve = next((c for c in companies if "Eneve" in c.name), None)
        assert eneve is not None

        # Should have data_source_per_field tracking
        assert hasattr(eneve, "data_source_per_field"), "Company should have data_source_per_field attribute"

        # Geographic presence source should be documented
        geo_source = eneve.data_source_per_field.get("geographic_presence")
        assert geo_source is not None, "geographic_presence data source should be tracked"
        assert geo_source in ["JSON", "Markdown"], f"Data source should be JSON or Markdown, got {geo_source}"

    def test_geographic_specificity_deterministic(self):
        """Geographic data should be deterministic across multiple loads."""
        results = []

        for _ in range(3):
            loader = UnifiedCompanyLoader()
            companies = loader.load_unified_companies()
            eneve = next((c for c in companies if "Eneve" in c.name), None)
            if eneve:
                results.append(tuple(sorted(eneve.geographic_presence)))

        # All runs should produce identical results
        assert len(set(results)) == 1, f"Geographic data should be deterministic, got different results: {results}"

    def test_all_companies_have_geographic_presence(self, companies):
        """All companies should have a geographic_presence field (even if empty)."""
        for company in companies:
            assert hasattr(company, "geographic_presence"), f"{company.name}: missing geographic_presence attribute"
            assert isinstance(company.geographic_presence, list), (
                f"{company.name}: geographic_presence should be a list"
            )
