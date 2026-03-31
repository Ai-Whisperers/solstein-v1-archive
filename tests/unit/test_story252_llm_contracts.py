"""Tests for STORY-252: Tighten Structured LLM Contracts.

Validates that:
- Empty or all-null extraction payloads fail validation
- Payloads with at least one meaningful field pass
- The is_minimal property correctly identifies identity-only payloads
- ResearchPlanResponse still enforces min_length=1 on queries
- EmptyExtractionError is raised (not generic ValidationError)
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from solstein.llm.schemas import (
    CompanyExtractionResponse,
    EmptyExtractionError,
    ResearchPlanResponse,
    SearchQueryItem,
)


class TestCompanyExtractionMinimumPayload:
    """STORY-252: Empty extraction payloads must be rejected."""

    def test_all_null_payload_rejected(self) -> None:
        """An all-null CompanyExtractionResponse must fail validation."""
        with pytest.raises(ValidationError, match="empty or non-informative"):
            CompanyExtractionResponse()

    def test_empty_dict_payload_rejected(self) -> None:
        """An empty dict must fail minimum-validity check."""
        with pytest.raises(ValidationError, match="empty or non-informative"):
            CompanyExtractionResponse.model_validate({})

    def test_only_revenue_currency_rejected(self) -> None:
        """revenue_currency alone is not a meaningful field."""
        with pytest.raises(ValidationError, match="empty or non-informative"):
            CompanyExtractionResponse(revenue_currency="USD")

    def test_company_name_alone_accepted(self) -> None:
        """company_name counts as meaningful (identity field)."""
        extraction = CompanyExtractionResponse(company_name="Acme Corp")
        assert extraction.company_name == "Acme Corp"

    def test_website_alone_accepted(self) -> None:
        extraction = CompanyExtractionResponse(website="https://acme.com")
        assert extraction.website == "https://acme.com"

    def test_revenue_alone_accepted(self) -> None:
        """A single substance field is enough."""
        extraction = CompanyExtractionResponse(revenue=42.0)
        assert extraction.revenue == 42.0

    def test_industry_alone_accepted(self) -> None:
        extraction = CompanyExtractionResponse(industry="Technology")
        assert extraction.industry == "Technology"

    def test_full_payload_accepted(self) -> None:
        extraction = CompanyExtractionResponse(
            company_name="Acme Corp",
            website="https://acme.com",
            industry="Technology",
            revenue=100.0,
            employees=500,
        )
        assert extraction.company_name == "Acme Corp"
        assert extraction.revenue == 100.0


class TestCompanyExtractionIsMinimal:
    """The is_minimal property identifies identity-only payloads."""

    def test_name_only_is_minimal(self) -> None:
        extraction = CompanyExtractionResponse(company_name="Acme")
        assert extraction.is_minimal is True

    def test_name_and_website_is_minimal(self) -> None:
        extraction = CompanyExtractionResponse(company_name="Acme", website="https://acme.com")
        assert extraction.is_minimal is True

    def test_name_and_revenue_is_not_minimal(self) -> None:
        extraction = CompanyExtractionResponse(company_name="Acme", revenue=42.0)
        assert extraction.is_minimal is False

    def test_industry_only_is_not_minimal(self) -> None:
        extraction = CompanyExtractionResponse(industry="Tech")
        assert extraction.is_minimal is False


class TestEmptyExtractionErrorType:
    """EmptyExtractionError is surfaced through ValidationError."""

    def test_error_is_value_error_subclass(self) -> None:
        assert issubclass(EmptyExtractionError, ValueError)

    def test_validation_error_wraps_empty_extraction(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            CompanyExtractionResponse()
        errors = exc_info.value.errors()
        assert any("empty or non-informative" in str(e) for e in errors)


class TestResearchPlanResponseStillStrict:
    """ResearchPlanResponse already enforces min_length=1 on queries."""

    def test_empty_queries_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ResearchPlanResponse(queries=[])

    def test_valid_plan_accepted(self) -> None:
        plan = ResearchPlanResponse(
            queries=[
                SearchQueryItem(query="test company", priority=1, intent="website"),
            ],
        )
        assert len(plan.queries) == 1

    def test_invalid_priority_rejected(self) -> None:
        with pytest.raises(ValidationError):
            SearchQueryItem(query="test", priority=0, intent="website")


class TestExtractionModelDump:
    """model_dump on valid extractions still works correctly."""

    def test_dump_includes_all_fields(self) -> None:
        extraction = CompanyExtractionResponse(
            company_name="Acme", revenue=42.0,
        )
        dumped = extraction.model_dump()
        assert "company_name" in dumped
        assert "revenue" in dumped
        assert dumped["company_name"] == "Acme"
        assert dumped["revenue"] == 42.0

    def test_dump_exclude_none(self) -> None:
        extraction = CompanyExtractionResponse(company_name="Acme")
        dumped = extraction.model_dump(exclude_none=True)
        assert "company_name" in dumped
        assert "revenue" not in dumped
