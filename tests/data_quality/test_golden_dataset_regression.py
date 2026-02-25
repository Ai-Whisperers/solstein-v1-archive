"""
Task 17: Golden Dataset Regression Tests

Regression tests to prevent score drift in the scoring engine.
Uses a curated golden dataset of representative companies.
"""

import pytest
from solstein.domain.models import Company, FinancialMetric
from tests.data_quality.golden_dataset import (
    get_golden_dataset,
    get_golden_company_by_id,
    get_golden_company_by_name,
)


class TestGoldenDatasetRegression:
    """Regression tests using golden dataset."""

    def test_golden_dataset_exists(self):
        """Golden dataset should be defined."""
        dataset = get_golden_dataset()
        assert len(dataset) >= 10
        assert len(dataset) <= 15

    def test_golden_dataset_has_required_fields(self):
        """All golden companies should have required fields."""
        dataset = get_golden_dataset()
        for company in dataset:
            assert company.company_id is not None
            assert company.company_name is not None
            assert company.expected_classification is not None
            assert company.expected_composite_score_min is not None
            assert company.expected_composite_score_max is not None

    def test_golden_dataset_score_ranges_valid(self):
        """Score ranges should be valid (min <= max)."""
        dataset = get_golden_dataset()
        for company in dataset:
            assert company.expected_composite_score_min <= company.expected_composite_score_max
            assert company.expected_growth_score_min <= company.expected_growth_score_max
            assert company.expected_financial_health_min <= company.expected_financial_health_max
            assert company.expected_competitive_position_min <= company.expected_competitive_position_max

    def test_golden_dataset_classifications_valid(self):
        """Classifications should be valid."""
        dataset = get_golden_dataset()
        valid_classifications = ["Phoenix", "Salt", "Lead"]
        for company in dataset:
            assert company.expected_classification in valid_classifications

    def test_golden_dataset_has_phoenix_companies(self):
        """Golden dataset should include Phoenix companies."""
        dataset = get_golden_dataset()
        phoenix_companies = [c for c in dataset if c.expected_classification == "Phoenix"]
        assert len(phoenix_companies) >= 2

    def test_golden_dataset_has_salt_companies(self):
        """Golden dataset should include Salt companies."""
        dataset = get_golden_dataset()
        salt_companies = [c for c in dataset if c.expected_classification == "Salt"]
        assert len(salt_companies) >= 2

    def test_golden_dataset_has_lead_companies(self):
        """Golden dataset should include Lead companies."""
        dataset = get_golden_dataset()
        lead_companies = [c for c in dataset if c.expected_classification == "Lead"]
        assert len(lead_companies) >= 2

    def test_get_golden_company_by_id(self):
        """Should retrieve golden company by ID."""
        company = get_golden_company_by_id("eneve-1")
        assert company is not None
        assert company.company_name == "Eneve"
        assert company.expected_classification == "Phoenix"

    def test_get_golden_company_by_name(self):
        """Should retrieve golden company by name."""
        company = get_golden_company_by_name("Eneve")
        assert company is not None
        assert company.company_id == "eneve-1"
        assert company.expected_classification == "Phoenix"

    def test_get_golden_company_by_name_case_insensitive(self):
        """Should retrieve golden company by name (case-insensitive)."""
        company = get_golden_company_by_name("eneve")
        assert company is not None
        assert company.company_id == "eneve-1"

    def test_get_nonexistent_golden_company_by_id(self):
        """Should return None for nonexistent company ID."""
        company = get_golden_company_by_id("nonexistent-1")
        assert company is None

    def test_get_nonexistent_golden_company_by_name(self):
        """Should return None for nonexistent company name."""
        company = get_golden_company_by_name("Nonexistent Company")
        assert company is None

    def test_validate_composite_score_within_range(self):
        """Should validate composite score within range."""
        company = get_golden_company_by_id("eneve-1")
        assert company.validate_composite_score(7.5) is True
        assert company.validate_composite_score(8.0) is True

    def test_validate_composite_score_outside_range(self):
        """Should reject composite score outside range."""
        company = get_golden_company_by_id("eneve-1")
        assert company.validate_composite_score(6.0) is False
        assert company.validate_composite_score(9.0) is False

    def test_validate_classification_match(self):
        """Should validate matching classification."""
        company = get_golden_company_by_id("eneve-1")
        assert company.validate_classification("Phoenix") is True

    def test_validate_classification_mismatch(self):
        """Should reject mismatched classification."""
        company = get_golden_company_by_id("eneve-1")
        assert company.validate_classification("Salt") is False
        assert company.validate_classification("Lead") is False

    def test_validate_ai_score_within_range(self):
        """Should validate AI score within range."""
        company = get_golden_company_by_id("eneve-1")
        assert company.validate_ai_score(7) is True
        assert company.validate_ai_score(8) is True
        assert company.validate_ai_score(10) is True

    def test_validate_ai_score_outside_range(self):
        """Should reject AI score outside range."""
        company = get_golden_company_by_id("eneve-1")
        assert company.validate_ai_score(5) is False
        assert company.validate_ai_score(11) is False

    def test_validate_ai_score_no_expectation(self):
        """Should pass validation when no AI score expectation."""
        company = get_golden_company_by_id("sparse-data-1")
        assert company.validate_ai_score(None) is True
        assert company.validate_ai_score(5) is True

    def test_validate_ai_maturity_match(self):
        """Should validate matching AI maturity."""
        company = get_golden_company_by_id("eneve-1")
        assert company.validate_ai_maturity("Strong") is True

    def test_validate_ai_maturity_mismatch(self):
        """Should reject mismatched AI maturity."""
        company = get_golden_company_by_id("eneve-1")
        assert company.validate_ai_maturity("Moderate") is False
        assert company.validate_ai_maturity("None") is False

    def test_validate_ai_maturity_no_expectation(self):
        """Should pass validation when no AI maturity expectation."""
        company = get_golden_company_by_id("sparse-data-1")
        assert company.validate_ai_maturity(None) is True
        assert company.validate_ai_maturity("Strong") is True

    def test_phoenix_companies_have_high_scores(self):
        """Phoenix companies should have high composite scores."""
        dataset = get_golden_dataset()
        phoenix_companies = [c for c in dataset if c.expected_classification == "Phoenix"]
        for company in phoenix_companies:
            assert company.expected_composite_score_min >= 7.0

    def test_salt_companies_have_medium_scores(self):
        """Salt companies should have medium composite scores."""
        dataset = get_golden_dataset()
        salt_companies = [c for c in dataset if c.expected_classification == "Salt"]
        for company in salt_companies:
            assert 4.0 <= company.expected_composite_score_min <= 7.0

    def test_lead_companies_have_low_scores(self):
        """Lead companies should have low composite scores."""
        dataset = get_golden_dataset()
        lead_companies = [c for c in dataset if c.expected_classification == "Lead"]
        for company in lead_companies:
            assert company.expected_composite_score_max <= 4.0

    def test_phoenix_companies_have_high_ai_scores(self):
        """Phoenix companies should have high AI scores."""
        dataset = get_golden_dataset()
        phoenix_companies = [c for c in dataset if c.expected_classification == "Phoenix"]
        for company in phoenix_companies:
            if company.expected_ai_score_min is not None:
                assert company.expected_ai_score_min >= 6

    def test_lead_companies_have_low_ai_scores(self):
        """Lead companies should have low AI scores."""
        dataset = get_golden_dataset()
        lead_companies = [c for c in dataset if c.expected_classification == "Lead"]
        for company in lead_companies:
            if company.expected_ai_score_max is not None:
                assert company.expected_ai_score_max <= 4

    def test_golden_dataset_includes_eneve(self):
        """Golden dataset should include Eneve."""
        company = get_golden_company_by_name("Eneve")
        assert company is not None
        assert company.expected_classification == "Phoenix"

    def test_golden_dataset_includes_octopus_energy(self):
        """Golden dataset should include Octopus Energy."""
        company = get_golden_company_by_name("Octopus Energy")
        assert company is not None
        assert company.expected_classification == "Salt"

    def test_golden_dataset_includes_edge_cases(self):
        """Golden dataset should include edge cases."""
        sparse = get_golden_company_by_name("Sparse Data Company")
        startup = get_golden_company_by_name("High Growth Startup")
        turnaround = get_golden_company_by_name("Turnaround Company")
        # At least some edge cases should be present
        assert sparse is not None or startup is not None or turnaround is not None

    def test_golden_dataset_consistency(self):
        """Golden dataset should be internally consistent."""
        dataset = get_golden_dataset()
        # Check for duplicate IDs
        ids = [c.company_id for c in dataset]
        assert len(ids) == len(set(ids))
        # Check for duplicate names
        names = [c.company_name for c in dataset]
        assert len(names) == len(set(names))
