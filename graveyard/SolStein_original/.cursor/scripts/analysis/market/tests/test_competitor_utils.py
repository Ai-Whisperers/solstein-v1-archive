"""Tests for competitor_utils.py -- all 13 public functions + CLASSIFICATION_ORDER."""

import pytest

from competitor_utils import (
    CLASSIFICATION_ORDER,
    get_classification,
    get_cloud_revenue_pct,
    get_composite,
    get_countries_count,
    get_deployment_model,
    get_ebitda_margin,
    get_international_revenue_pct,
    get_lead_investors,
    get_revenue_per_employee,
    get_score,
    get_war_chest_signals,
    is_eneve,
)


# ---------------------------------------------------------------------------
# CLASSIFICATION_ORDER constant
# ---------------------------------------------------------------------------

class TestClassificationOrder:
    def test_contains_four_entries(self):
        assert len(CLASSIFICATION_ORDER) == 4

    def test_order(self):
        assert CLASSIFICATION_ORDER == ["Rocket", "Riser", "Steady", "Dinosaur"]


# ---------------------------------------------------------------------------
# get_score
# ---------------------------------------------------------------------------

class TestGetScore:
    def test_returns_score_for_existing_dimension(self, sample_competitor):
        assert get_score(sample_competitor, "Revenue Growth") == 7.5

    def test_returns_none_for_missing_dimension(self, sample_competitor):
        assert get_score(sample_competitor, "Nonexistent") is None

    def test_returns_none_when_scorecard_missing(self, empty_competitor):
        assert get_score(empty_competitor, "Revenue Growth") is None

    def test_returns_none_for_empty_dict(self):
        assert get_score({}, "Revenue Growth") is None

    def test_returns_none_when_dimensions_empty(self):
        comp = {"scorecard": {"dimensions": {}}}
        assert get_score(comp, "Revenue Growth") is None


# ---------------------------------------------------------------------------
# get_composite
# ---------------------------------------------------------------------------

class TestGetComposite:
    def test_returns_composite_score(self, sample_competitor):
        assert get_composite(sample_competitor) == 6.3

    def test_returns_none_when_empty(self, empty_competitor):
        assert get_composite(empty_competitor) is None

    def test_returns_none_for_bare_dict(self):
        assert get_composite({}) is None


# ---------------------------------------------------------------------------
# get_classification
# ---------------------------------------------------------------------------

class TestGetClassification:
    def test_returns_classification(self, sample_competitor):
        assert get_classification(sample_competitor) == "Riser"

    def test_returns_none_when_empty(self, empty_competitor):
        assert get_classification(empty_competitor) is None

    def test_returns_none_for_bare_dict(self):
        assert get_classification({}) is None


# ---------------------------------------------------------------------------
# is_eneve
# ---------------------------------------------------------------------------

class TestIsEneve:
    def test_eneve_folder_detected(self, eneve_competitor):
        assert is_eneve(eneve_competitor) is True

    def test_non_eneve_folder(self, sample_competitor):
        assert is_eneve(sample_competitor) is False

    def test_empty_folder(self):
        assert is_eneve({"folder": ""}) is False

    def test_missing_folder_key(self):
        assert is_eneve({}) is False

    def test_case_insensitive(self):
        assert is_eneve({"folder": "ENEVE-Corp"}) is True
        assert is_eneve({"folder": "Eneve"}) is True


# ---------------------------------------------------------------------------
# get_ebitda_margin
# ---------------------------------------------------------------------------

class TestGetEbitdaMargin:
    def test_returns_margin(self, sample_competitor):
        assert get_ebitda_margin(sample_competitor) == 12.0

    def test_returns_none_when_empty(self, empty_competitor):
        assert get_ebitda_margin(empty_competitor) is None

    def test_returns_none_for_bare_dict(self):
        assert get_ebitda_margin({}) is None


# ---------------------------------------------------------------------------
# get_revenue_per_employee
# ---------------------------------------------------------------------------

class TestGetRevenuePerEmployee:
    def test_returns_value(self, sample_competitor):
        assert get_revenue_per_employee(sample_competitor) == 118.0

    def test_returns_none_when_empty(self, empty_competitor):
        assert get_revenue_per_employee(empty_competitor) is None

    def test_returns_none_for_bare_dict(self):
        assert get_revenue_per_employee({}) is None


# ---------------------------------------------------------------------------
# get_lead_investors
# ---------------------------------------------------------------------------

class TestGetLeadInvestors:
    def test_returns_list(self, sample_competitor):
        result = get_lead_investors(sample_competitor)
        assert isinstance(result, list)
        assert "Tiger Global" in result

    def test_returns_empty_list_when_missing(self, empty_competitor):
        assert get_lead_investors(empty_competitor) == []

    def test_returns_empty_list_for_bare_dict(self):
        assert get_lead_investors({}) == []


# ---------------------------------------------------------------------------
# get_war_chest_signals
# ---------------------------------------------------------------------------

class TestGetWarChestSignals:
    def test_returns_text(self, sample_competitor):
        result = get_war_chest_signals(sample_competitor)
        assert result is not None
        assert "hiring" in result.lower()

    def test_returns_none_when_missing(self, empty_competitor):
        assert get_war_chest_signals(empty_competitor) is None

    def test_returns_none_for_bare_dict(self):
        assert get_war_chest_signals({}) is None


# ---------------------------------------------------------------------------
# get_international_revenue_pct
# ---------------------------------------------------------------------------

class TestGetInternationalRevenuePct:
    def test_returns_percentage(self, sample_competitor):
        assert get_international_revenue_pct(sample_competitor) == 40.0

    def test_returns_none_when_empty(self, empty_competitor):
        assert get_international_revenue_pct(empty_competitor) is None

    def test_returns_none_for_bare_dict(self):
        assert get_international_revenue_pct({}) is None


# ---------------------------------------------------------------------------
# get_countries_count
# ---------------------------------------------------------------------------

class TestGetCountriesCount:
    def test_returns_count(self, sample_competitor):
        assert get_countries_count(sample_competitor) == 8

    def test_returns_none_when_empty(self, empty_competitor):
        assert get_countries_count(empty_competitor) is None

    def test_returns_none_for_bare_dict(self):
        assert get_countries_count({}) is None


# ---------------------------------------------------------------------------
# get_deployment_model
# ---------------------------------------------------------------------------

class TestGetDeploymentModel:
    def test_returns_model(self, sample_competitor):
        assert get_deployment_model(sample_competitor) == "SaaS"

    def test_returns_hybrid_for_eneve(self, eneve_competitor):
        assert get_deployment_model(eneve_competitor) == "Hybrid"

    def test_returns_none_when_empty(self, empty_competitor):
        assert get_deployment_model(empty_competitor) is None

    def test_returns_none_for_bare_dict(self):
        assert get_deployment_model({}) is None


# ---------------------------------------------------------------------------
# get_cloud_revenue_pct
# ---------------------------------------------------------------------------

class TestGetCloudRevenuePct:
    def test_returns_percentage(self, sample_competitor):
        assert get_cloud_revenue_pct(sample_competitor) == 80.0

    def test_returns_none_when_empty(self, empty_competitor):
        assert get_cloud_revenue_pct(empty_competitor) is None

    def test_returns_none_for_bare_dict(self):
        assert get_cloud_revenue_pct({}) is None
