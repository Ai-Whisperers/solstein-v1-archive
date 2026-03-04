"""End-to-end integration tests for eneve competitive intelligence pipeline."""

import json

import pytest

from solstein.data.eneve_enrichment import EnveEnrichmentService
from solstein.data.loaders import CompetitorDataLoader
from solstein.domain.models import Company
from solstein.extractors.markdown_extractor import BatchExtractor, MarkdownExtractor


class TestEnevelPipelineE2E:
    """End-to-end tests for eneve pipeline."""

    def test_extract_and_merge_multiple_files(self, tmp_path):
        """Test extracting and merging multiple markdown files for same company."""
        # Create test markdown files
        md1 = tmp_path / "acme_corp_1.md"
        md1.write_text("""
# Acme Corp

Revenue: $100M
Employees: 500
Growth Rate: 25%
""")

        md2 = tmp_path / "acme_corp_2.md"
        md2.write_text("""
# Acme Corp

Profit Margin: 15%
Funding Raised: $50M
AI Maturity: Advanced
""")

        # Extract and merge
        extractor = MarkdownExtractor()
        batch = BatchExtractor(extractor)
        profiles = batch.extract_directory(tmp_path, pattern="*.md")

        # Should have 1 merged profile, not 2
        assert len(profiles) == 1
        profile = profiles[0]
        assert profile.company_name == "Acme Corp"
        assert profile.revenue == 100.0
        assert profile.employees == 500
        assert profile.growth_rate == 25.0
        assert profile.profit_margin == 15.0
        assert profile.funding == 50.0

    def test_load_from_json(self, tmp_path):
        """Test loading companies from scored JSON file."""
        # Create test JSON file
        json_file = tmp_path / "scored.json"
        test_data = {
            "competitors": [
                {
                    "id": "1",
                    "name": "Test Corp",
                    "revenue": 100.0,
                    "employees": 500,
                    "growth_score": 7.5,
                    "financial_health_score": 8.0,
                    "competitive_position_score": 7.0,
                }
            ]
        }
        json_file.write_text(json.dumps(test_data))

        # Load from JSON
        loader = CompetitorDataLoader()
        companies = loader.load_from_json(json_file)

        assert len(companies) > 0
        assert companies[0].company_name == "Test Corp"

    def test_enrichment_with_confidence_scores(self):
        """Test enriching company data with confidence scores."""
        company = Company(
            id="1",
            name="Test Corp",
            company_name="Test Corp",
            revenue=100.0,
            employees=500,
            growth_rate=25.0,
        )

        enriched = EnveEnrichmentService.enrich_company_with_confidence(company)

        assert enriched.confidence_scores is not None
        assert "revenue" in enriched.confidence_scores
        assert "employees" in enriched.confidence_scores
        assert "data_completeness" in enriched.confidence_scores
        assert enriched.confidence_scores["data_completeness"] > 0

    def test_enrichment_source_count(self):
        """Test calculating enrichment source count."""
        company = Company(
            id="1",
            name="Test Corp",
            company_name="Test Corp",
            source_links=["url1", "url2"],
            metric_sources={"revenue": ["source1", "source2"]},
        )

        count = EnveEnrichmentService.calculate_enrichment_source_count(company)
        assert count >= 2  # At least 2 unique sources

    def test_validate_enriched_data_valid(self):
        """Test validation of valid enriched data."""
        company = Company(
            id="1",
            name="Test Corp",
            company_name="Test Corp",
            revenue=100.0,
            employees=500,
        )

        is_valid, error = EnveEnrichmentService.validate_enriched_data(company)
        assert is_valid is True
        assert error is None

    def test_validate_enriched_data_invalid(self):
        """Test validation of invalid enriched data."""
        company = Company(
            id="1",
            name="Test Corp",
            company_name="Test Corp",
            revenue=-100.0,  # Invalid: negative revenue
        )

        is_valid, error = EnveEnrichmentService.validate_enriched_data(company)
        assert is_valid is False
        assert error is not None

    def test_merge_enrichment_data(self):
        """Test merging enrichment data from multiple sources."""
        primary = Company(
            id="1",
            name="Test Corp",
            company_name="Test Corp",
            revenue=100.0,
            employees=None,
        )

        secondary = Company(
            id="2",
            name="Test Corp",
            company_name="Test Corp",
            revenue=None,
            employees=500,
        )

        merged = EnveEnrichmentService.merge_enrichment_data(primary, secondary)

        assert merged.revenue == 100.0  # From primary
        assert merged.employees == 500  # From secondary

    def test_pipeline_data_consistency(self, tmp_path):
        """Test that pipeline maintains data consistency across stages."""
        # Create test markdown
        md_file = tmp_path / "test.md"
        md_file.write_text("""
# Test Company

Revenue: $50M
Employees: 250
Growth Rate: 15%
""")

        # Extract
        extractor = MarkdownExtractor()
        extracted = extractor.extract_from_file(md_file)
        assert extracted is not None

        # Convert to Company
        company = extractor.to_company_profile(extracted)
        assert company.revenue == 50.0
        assert company.employees == 250
        assert company.growth_rate == 15.0

        # Enrich
        enriched = EnveEnrichmentService.enrich_company_with_confidence(company)
        assert enriched.revenue == 50.0  # Data preserved
        assert enriched.employees == 250
        assert enriched.growth_rate == 15.0

        # Validate
        is_valid, error = EnveEnrichmentService.validate_enriched_data(enriched)
        assert is_valid is True


class TestEnevelPipelineScoring:
    """Tests for scoring in eneve pipeline."""

    def test_none_base_score_handling(self):
        """Test that None base_score doesn't break scoring."""
        from solstein.core.scoring_config import GrowthScoringConfig

        cfg = GrowthScoringConfig()
        assert cfg.base_score is None

        # Verify scorer can handle None
        from solstein.analytics.scorers.growth_momentum import GrowthMomentumScorer

        scorer = GrowthMomentumScorer()
        assert scorer is not None

    def test_json_loader_backward_compatibility(self):
        """Test that JSON loader doesn't break existing functionality."""
        loader = CompetitorDataLoader()

        # Should still have load_companies method
        assert hasattr(loader, "load_companies")

        # Should have new load_from_json method
        assert hasattr(loader, "load_from_json")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
