"""Tests for STORY-252: Tighten Structured LLM Contracts.

Validates that:
- Empty or all-null extraction payloads fail validation
- Payloads with at least one meaningful field pass
- The is_minimal property correctly identifies identity-only payloads
- ResearchPlanResponse still enforces min_length=1 on queries
- EmptyExtractionError is raised (not generic ValidationError)
- Agent-level fallback distinguishes schema failure from generic errors
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel, ConfigDict, ValidationError

from solstein.llm.schemas import (
    CompanyExtractionResponse,
    EmptyExtractionError,
    ResearchPlanResponse,
    SearchQueryItem,
)
from solstein.research.fetch_policy import FetchResult
from solstein.research.research_agents import ContentExtractorAgent


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
            company_name="Acme",
            revenue=42.0,
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


# ===========================================================================
# Agent-level fallback: _llm_extract distinguishes schema failure
# ===========================================================================


class TestContentExtractorAgentEmptyPayloadFallback:
    """STORY-252: Agent-level fallback surfaces schema failure, not silent success.

    These tests verify that ContentExtractorAgent._llm_extract returns None
    when the LLM produces an empty/non-informative payload, and that
    extract() surfaces this as extraction_method='schema_failure:empty_payload'.
    """

    @pytest.fixture()
    def extractor(self) -> ContentExtractorAgent:
        """Create a ContentExtractorAgent with mocked dependencies."""
        mock_llm = MagicMock()
        mock_instructor = MagicMock()
        agent = ContentExtractorAgent(
            llm_client=mock_llm,
            instructor_client=mock_instructor,
        )
        return agent

    @pytest.mark.asyncio()
    async def test_llm_extract_returns_none_on_empty_payload(
        self,
        extractor: ContentExtractorAgent,
    ) -> None:
        """_llm_extract returns None when LLM yields empty payload."""
        # Make instructor.extract raise ValidationError from empty payload
        extractor.instructor.extract = AsyncMock(
            side_effect=_make_empty_payload_validation_error(),
        )
        result = await extractor._llm_extract("some text", "Acme Corp", "https://acme.com")
        assert result is None

    @pytest.mark.asyncio()
    async def test_llm_extract_returns_empty_dict_on_other_validation_error(
        self,
        extractor: ContentExtractorAgent,
    ) -> None:
        """_llm_extract returns {} on non-empty-payload ValidationError."""
        # A schema error that is NOT about empty payloads (e.g., wrong type)
        extractor.instructor.extract = AsyncMock(
            side_effect=_make_type_validation_error(),
        )
        result = await extractor._llm_extract("some text", "Acme Corp", "https://acme.com")
        assert result == {}

    @pytest.mark.asyncio()
    async def test_llm_extract_returns_empty_dict_on_generic_exception(
        self,
        extractor: ContentExtractorAgent,
    ) -> None:
        """_llm_extract returns {} on unexpected exceptions (e.g., network)."""
        extractor.instructor.extract = AsyncMock(
            side_effect=RuntimeError("LLM provider timeout"),
        )
        result = await extractor._llm_extract("some text", "Acme Corp", "https://acme.com")
        assert result == {}

    @pytest.mark.asyncio()
    async def test_llm_extract_returns_dict_on_success(
        self,
        extractor: ContentExtractorAgent,
    ) -> None:
        """_llm_extract returns a dict with data on success."""
        valid_extraction = CompanyExtractionResponse(
            company_name="Acme Corp",
            revenue=100.0,
        )
        extractor.instructor.extract = AsyncMock(return_value=valid_extraction)
        result = await extractor._llm_extract("some text", "Acme Corp", "https://acme.com")
        assert isinstance(result, dict)
        assert result["company_name"] == "Acme Corp"
        assert result["revenue"] == 100.0

    @pytest.mark.asyncio()
    async def test_extract_surfaces_schema_failure_on_empty_payload(
        self,
        extractor: ContentExtractorAgent,
    ) -> None:
        """extract() returns extraction_method='schema_failure:empty_payload'
        when LLM returns an empty payload.
        """
        # Mock _fetch_page to return a successful fetch
        mock_fetch_result = MagicMock(spec=FetchResult)
        mock_fetch_result.success = True
        mock_fetch_result.content = "<html><body>" + "x" * 200 + "</body></html>"
        mock_fetch_result.to_metadata.return_value = {"status": 200}
        extractor._fetch_page = AsyncMock(return_value=mock_fetch_result)

        # Mock _llm_extract to return None (empty payload)
        extractor._llm_extract = AsyncMock(return_value=None)

        result = await extractor.extract("https://acme.com", "Acme Corp")
        assert result.extraction_method == "schema_failure:empty_payload"
        assert result.confidence == 0.0

    @pytest.mark.asyncio()
    async def test_extract_surfaces_llm_parsing_on_success(
        self,
        extractor: ContentExtractorAgent,
    ) -> None:
        """extract() returns extraction_method='llm_parsing' on valid extraction."""
        mock_fetch_result = MagicMock(spec=FetchResult)
        mock_fetch_result.success = True
        mock_fetch_result.content = "<html><body>" + "x" * 200 + "</body></html>"
        mock_fetch_result.to_metadata.return_value = {"status": 200}
        extractor._fetch_page = AsyncMock(return_value=mock_fetch_result)

        # Mock _llm_extract to return valid data
        extractor._llm_extract = AsyncMock(
            return_value={
                "company_name": "Acme Corp",
                "revenue": 100.0,
            }
        )

        result = await extractor.extract("https://acme.com", "Acme Corp")
        assert result.extraction_method == "llm_parsing"
        assert result.confidence > 0.0


# ---------------------------------------------------------------------------
# Helpers for constructing realistic ValidationErrors
# ---------------------------------------------------------------------------


def _make_empty_payload_validation_error() -> ValidationError:
    """Create a ValidationError matching the empty-payload rejection pattern."""
    try:
        CompanyExtractionResponse()
    except ValidationError as e:
        return e
    raise AssertionError("Expected ValidationError from empty CompanyExtractionResponse")  # pragma: no cover


def _make_type_validation_error() -> ValidationError:
    """Create a ValidationError from a type mismatch (not empty-payload)."""

    class StrictModel(BaseModel):
        model_config = ConfigDict(strict=True)  # type: ignore[misc]
        value: int

    try:
        StrictModel(value="not_an_int")  # type: ignore[arg-type]
    except ValidationError as e:
        return e
    raise AssertionError("Expected ValidationError from type mismatch")  # pragma: no cover
