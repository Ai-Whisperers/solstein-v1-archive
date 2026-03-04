"""Input validation tests - Phase 2, Item 2.4

Tests for Pydantic validation schemas.
"""

import pytest
from pydantic import ValidationError

from solstein.api.schemas.validation import (
    CompanyCreateRequest,
    CompanyFilterRequest,
    MarketAnalysisRequest,
    PaginationParams,
    ScoreUpdateRequest,
    SearchRequest,
)


class TestSearchRequest:
    """Test SearchRequest validation."""

    def test_valid_search_request(self):
        """Should accept valid search request."""
        request = SearchRequest(field="name", value="Test Company", model_type="company")
        assert request.field == "name"
        assert request.value == "Test Company"
        assert request.model_type == "company"

    def test_invalid_field_rejected(self):
        """Should reject invalid field."""
        with pytest.raises(ValidationError) as exc_info:
            SearchRequest(field="invalid_field", value="test", model_type="company")

        assert "Invalid field" in str(exc_info.value)

    def test_invalid_model_type_rejected(self):
        """Should reject invalid model type."""
        with pytest.raises(ValidationError) as exc_info:
            SearchRequest(field="name", value="test", model_type="invalid_model")

        assert "Invalid model_type" in str(exc_info.value)

    def test_empty_field_rejected(self):
        """Should reject empty field."""
        with pytest.raises(ValidationError):
            SearchRequest(field="", value="test")

    def test_empty_value_rejected(self):
        """Should reject empty value."""
        with pytest.raises(ValidationError):
            SearchRequest(field="name", value="")

    def test_field_too_long_rejected(self):
        """Should reject field over 50 chars."""
        with pytest.raises(ValidationError):
            SearchRequest(field="a" * 51, value="test")

    def test_default_model_type(self):
        """Should default to company model type."""
        request = SearchRequest(field="name", value="test")
        assert request.model_type == "company"


class TestPaginationParams:
    """Test PaginationParams validation."""

    def test_default_pagination(self):
        """Should use default values."""
        params = PaginationParams()
        assert params.page == 1
        assert params.page_size == 20
        assert params.offset == 0

    def test_custom_pagination(self):
        """Should accept custom values."""
        params = PaginationParams(page=3, page_size=50)
        assert params.page == 3
        assert params.page_size == 50
        assert params.offset == 100  # (3-1) * 50

    def test_page_zero_rejected(self):
        """Should reject page 0."""
        with pytest.raises(ValidationError):
            PaginationParams(page=0)

    def test_negative_page_rejected(self):
        """Should reject negative page."""
        with pytest.raises(ValidationError):
            PaginationParams(page=-1)

    def test_page_size_too_large_rejected(self):
        """Should reject page size over 100."""
        with pytest.raises(ValidationError):
            PaginationParams(page_size=101)

    def test_page_size_zero_rejected(self):
        """Should reject page size 0."""
        with pytest.raises(ValidationError):
            PaginationParams(page_size=0)


class TestCompanyFilterRequest:
    """Test CompanyFilterRequest validation."""

    def test_valid_filter(self):
        """Should accept valid filter."""
        request = CompanyFilterRequest(industry="Technology", tier="A")
        assert request.industry == "Technology"
        assert request.tier == "A"

    def test_invalid_industry_rejected(self):
        """Should reject unknown industry."""
        with pytest.raises(ValidationError) as exc_info:
            CompanyFilterRequest(industry="UnknownIndustry")

        assert "Unknown industry" in str(exc_info.value)

    def test_invalid_tier_rejected(self):
        """Should reject invalid tier."""
        with pytest.raises(ValidationError):
            CompanyFilterRequest(tier="Z")

    def test_optional_fields(self):
        """Should allow all fields to be optional."""
        request = CompanyFilterRequest()
        assert request.industry is None
        assert request.headquarters is None

    def test_score_range_validation(self):
        """Should validate score ranges."""
        # Valid scores
        request = CompanyFilterRequest(min_score=0.5, max_score=0.9)
        assert request.min_score == 0.5
        assert request.max_score == 0.9

        # Invalid - too high
        with pytest.raises(ValidationError):
            CompanyFilterRequest(min_score=1.5)

        # Invalid - negative
        with pytest.raises(ValidationError):
            CompanyFilterRequest(max_score=-0.1)


class TestMarketAnalysisRequest:
    """Test MarketAnalysisRequest validation."""

    def test_valid_request(self):
        """Should accept valid request."""
        request = MarketAnalysisRequest(industry="Technology", region="Europe")
        assert request.industry == "Technology"
        assert request.region == "Europe"

    def test_missing_industry_rejected(self):
        """Should reject missing industry."""
        with pytest.raises(ValidationError):
            MarketAnalysisRequest(region="Europe")

    def test_invalid_industry_rejected(self):
        """Should reject unknown industry."""
        with pytest.raises(ValidationError) as exc_info:
            MarketAnalysisRequest(industry="InvalidIndustry")

        assert "Unknown industry" in str(exc_info.value)

    def test_optional_region(self):
        """Should allow optional region."""
        request = MarketAnalysisRequest(industry="Finance")
        assert request.region is None


class TestScoreUpdateRequest:
    """Test ScoreUpdateRequest validation."""

    def test_valid_scores(self):
        """Should accept valid scores."""
        request = ScoreUpdateRequest(ai_score=0.75, growth_score=0.85, risk_score=0.25)
        assert request.ai_score == 0.75
        assert request.growth_score == 0.85
        assert request.risk_score == 0.25

    def test_score_too_high_rejected(self):
        """Should reject score > 1.0."""
        with pytest.raises(ValidationError):
            ScoreUpdateRequest(ai_score=1.5, growth_score=0.5, risk_score=0.5)

    def test_negative_score_rejected(self):
        """Should reject negative score."""
        with pytest.raises(ValidationError):
            ScoreUpdateRequest(ai_score=-0.1, growth_score=0.5, risk_score=0.5)

    def test_score_rounding(self):
        """Should round scores to 4 decimal places."""
        request = ScoreUpdateRequest(ai_score=0.12345678, growth_score=0.5, risk_score=0.5)
        assert request.ai_score == 0.1235


class TestCompanyCreateRequest:
    """Test CompanyCreateRequest validation."""

    def test_valid_request(self):
        """Should accept valid request."""
        request = CompanyCreateRequest(
            name="Test Company",
            industry="Technology",
            headquarters="Berlin",
            revenue_eur_m=100.0,
            employees=500,
            website="https://example.com",
        )
        assert request.name == "Test Company"
        assert request.industry == "Technology"

    def test_missing_required_fields_rejected(self):
        """Should reject missing required fields."""
        with pytest.raises(ValidationError):
            CompanyCreateRequest(name="Test")  # Missing industry

    def test_invalid_industry_rejected(self):
        """Should reject unknown industry."""
        with pytest.raises(ValidationError):
            CompanyCreateRequest(name="Test", industry="Unknown")

    def test_name_too_short_rejected(self):
        """Should reject name under 2 characters."""
        with pytest.raises(ValidationError):
            CompanyCreateRequest(name="A", industry="Technology")

    def test_invalid_website_rejected(self):
        """Should reject invalid website URL."""
        with pytest.raises(ValidationError):
            CompanyCreateRequest(name="Test", industry="Technology", website="not-a-url")

    def test_negative_revenue_rejected(self):
        """Should reject negative revenue."""
        with pytest.raises(ValidationError):
            CompanyCreateRequest(name="Test", industry="Technology", revenue_eur_m=-100)

    def test_zero_employees_rejected(self):
        """Should reject zero employees."""
        with pytest.raises(ValidationError):
            CompanyCreateRequest(name="Test", industry="Technology", employees=0)
