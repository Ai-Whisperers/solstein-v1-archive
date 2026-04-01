"""Tests for STORY-072: Structured LLM Outputs with Instructor.

Acceptance criteria:
- Malformed LLM response raises validation error at call site (not downstream KeyError)
- All structured schemas are Pydantic models in designated module
- Instructor retry configured for schema violations
- Free-text outputs bypass Instructor
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel, ValidationError

from solstein.llm.schemas import (
    CompanyExtractionResponse,
    ResearchPlanResponse,
    SearchQueryItem,
)

# ---------------------------------------------------------------------------
# Schema validation tests
# ---------------------------------------------------------------------------


class TestSchemaDefinitions:
    """Verify schemas are Pydantic models in centralized location."""

    def test_research_plan_schema_is_pydantic(self):
        assert issubclass(ResearchPlanResponse, BaseModel)

    def test_company_extraction_schema_is_pydantic(self):
        assert issubclass(CompanyExtractionResponse, BaseModel)

    def test_search_query_item_is_pydantic(self):
        assert issubclass(SearchQueryItem, BaseModel)

    def test_research_plan_valid_data(self):
        plan = ResearchPlanResponse(
            queries=[
                SearchQueryItem(query="Acme Corp website", priority=1, intent="website"),
                SearchQueryItem(query="Acme Corp funding", priority=2, intent="funding"),
            ],
            estimated_sources=5,
        )
        assert len(plan.queries) == 2
        assert plan.estimated_sources == 5

    def test_research_plan_rejects_empty_queries(self):
        with pytest.raises(ValidationError):
            ResearchPlanResponse(queries=[], estimated_sources=5)

    def test_research_plan_rejects_invalid_priority(self):
        with pytest.raises(ValidationError):
            SearchQueryItem(query="test", priority=0, intent="website")

    def test_company_extraction_accepts_nulls(self):
        """All fields except none are optional - nulls are valid."""
        extraction = CompanyExtractionResponse()
        assert extraction.company_name is None
        assert extraction.revenue is None

    def test_company_extraction_full_data(self):
        extraction = CompanyExtractionResponse(
            company_name="Acme Corp",
            website="https://acme.com",
            description="A technology company",
            industry="Technology",
            headquarters="San Francisco, CA",
            founded_year=2015,
            employees=500,
            revenue=50.0,
            revenue_currency="USD",
            funding_raised=100.0,
            valuation=500.0,
            funding_rounds=["Seed", "Series A", "Series B"],
            key_executives=["Jane Doe", "John Smith"],
            products=["Widget", "Gadget"],
            is_public=False,
        )
        assert extraction.company_name == "Acme Corp"
        assert extraction.employees == 500


# ---------------------------------------------------------------------------
# Malformed response tests (AC: raises at call site, not downstream)
# ---------------------------------------------------------------------------


class TestMalformedResponseRaisesAtCallSite:
    """Malformed LLM responses must raise at the call site, not downstream."""

    def test_invalid_json_raises_validation_error(self):
        """If LLM returns invalid data, Pydantic catches it immediately."""
        with pytest.raises(ValidationError):
            ResearchPlanResponse.model_validate({"queries": "not a list"})

    def test_missing_required_field_raises(self):
        """Missing required fields raise at schema validation, not as KeyError."""
        with pytest.raises(ValidationError):
            ResearchPlanResponse.model_validate({})

    def test_wrong_type_raises_validation_error(self):
        with pytest.raises(ValidationError):
            SearchQueryItem.model_validate(
                {"query": "test", "priority": "not_an_int", "intent": "website"}
            )


# ---------------------------------------------------------------------------
# InstructorClient tests
# ---------------------------------------------------------------------------


class TestInstructorClient:
    """Test the Instructor-wrapped client."""

    @pytest.fixture
    def mock_settings(self):
        settings = MagicMock()
        settings.deepinfra_api_key = "test-key-12345678"
        settings.deepinfra_model = "meta-llama/Llama-3-70b-instruct"
        return settings

    @pytest.mark.asyncio
    async def test_extract_calls_instructor(self, mock_settings):
        """Instructor client delegates to patched SDK client."""
        from solstein.llm.instructor_client import InstructorClient

        client = InstructorClient()
        client.settings = mock_settings

        # Mock the patched client
        mock_patched = MagicMock()
        mock_response = CompanyExtractionResponse(
            company_name="Acme", industry="Tech"
        )
        mock_patched.chat.completions.create = AsyncMock(return_value=mock_response)
        client._patched_clients["deepinfra"] = mock_patched

        result = await client.extract(
            prompt="Extract company info",
            schema=CompanyExtractionResponse,
            provider="deepinfra",
        )
        assert result.company_name == "Acme"
        assert result.industry == "Tech"

    @pytest.mark.asyncio
    async def test_extract_anthropic_uses_messages_api(self, mock_settings):
        """Anthropic provider uses messages.create, not chat.completions."""
        from solstein.llm.instructor_client import InstructorClient

        mock_settings.anthropic_api_key = "test-key-anthropic"
        mock_settings.anthropic_model = "claude-sonnet-4-20250514"

        client = InstructorClient()
        client.settings = mock_settings

        mock_patched = MagicMock()
        mock_response = CompanyExtractionResponse(company_name="Anthropic")
        mock_patched.messages.create = AsyncMock(return_value=mock_response)
        client._patched_clients["anthropic"] = mock_patched

        result = await client.extract(
            prompt="Extract info",
            schema=CompanyExtractionResponse,
            provider="anthropic",
        )
        assert result.company_name == "Anthropic"
        mock_patched.messages.create.assert_awaited_once()


# ---------------------------------------------------------------------------
# Research agent integration tests
# ---------------------------------------------------------------------------


class TestResearchPlannerWithInstructor:
    """Test ResearchPlannerAgent with Instructor."""

    @pytest.mark.asyncio
    async def test_create_plan_uses_instructor(self):
        """Planner uses Instructor to get schema-validated plan."""
        from solstein.research.research_agents import ResearchPlannerAgent

        mock_instructor = MagicMock()
        mock_instructor.extract = AsyncMock(
            return_value=ResearchPlanResponse(
                queries=[
                    SearchQueryItem(query="Acme website", priority=1, intent="website"),
                    SearchQueryItem(query="Acme funding", priority=2, intent="funding"),
                ],
                estimated_sources=5,
            )
        )

        agent = ResearchPlannerAgent(instructor_client=mock_instructor)
        plan = await agent.create_plan("Acme Corp", industry="Technology")

        assert plan.company_name == "Acme Corp"
        assert len(plan.queries) == 2
        assert plan.estimated_sources == 5
        mock_instructor.extract.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_plan_fallback_on_failure(self):
        """Planner falls back to default queries when Instructor fails."""
        from solstein.research.research_agents import ResearchPlannerAgent

        mock_instructor = MagicMock()
        mock_instructor.extract = AsyncMock(side_effect=RuntimeError("LLM unavailable"))

        agent = ResearchPlannerAgent(instructor_client=mock_instructor)
        plan = await agent.create_plan("Acme Corp")

        assert plan.company_name == "Acme Corp"
        assert len(plan.queries) == 4  # fallback has 4 queries
        assert any("website" in q["intent"] for q in plan.queries)


class TestContentExtractorWithInstructor:
    """Test ContentExtractorAgent with Instructor."""

    @pytest.mark.asyncio
    async def test_llm_extract_uses_instructor(self):
        """Extractor uses Instructor for schema-validated extraction."""
        from solstein.research.research_agents import ContentExtractorAgent

        mock_instructor = MagicMock()
        mock_instructor.extract = AsyncMock(
            return_value=CompanyExtractionResponse(
                company_name="Acme Corp",
                website="https://acme.com",
                industry="Technology",
                employees=500,
            )
        )

        agent = ContentExtractorAgent(instructor_client=mock_instructor)
        data = await agent._llm_extract("Some page content", "Acme Corp", "https://acme.com")

        assert data["company_name"] == "Acme Corp"
        assert data["employees"] == 500
        mock_instructor.extract.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_llm_extract_returns_empty_on_failure(self):
        """Extractor returns empty dict on Instructor failure."""
        from solstein.research.research_agents import ContentExtractorAgent

        mock_instructor = MagicMock()
        mock_instructor.extract = AsyncMock(side_effect=ValidationError.from_exception_data(
            title="CompanyExtractionResponse",
            line_errors=[],
        ))

        agent = ContentExtractorAgent(instructor_client=mock_instructor)
        data = await agent._llm_extract("Bad content", "Unknown", "https://bad.com")

        assert data == {}


# ---------------------------------------------------------------------------
# Free-text bypass test (REQ-5)
# ---------------------------------------------------------------------------


class TestFreeTextBypassesInstructor:
    """Free-text outputs should use EnhancedLLMClient.generate(), not Instructor."""

    @pytest.mark.asyncio
    async def test_generate_returns_plain_string(self):
        """EnhancedLLMClient.generate() returns plain text, not schema-validated."""
        from solstein.llm.enhanced_client import EnhancedLLMClient

        mock_health = MagicMock()
        mock_health.check_all_providers = AsyncMock(return_value={})
        mock_health.get_health = MagicMock(return_value=None)
        mock_health.report_success = MagicMock()

        client = EnhancedLLMClient(health_checker=mock_health)

        mock_querier = MagicMock()
        mock_querier.query = AsyncMock(return_value="This is a narrative summary about Acme Corp.")
        client.cloud_querier = mock_querier

        with patch.object(client, "_get_client", return_value=MagicMock()):
            result = await client.generate("Summarize Acme Corp")

        assert isinstance(result, str)
        assert "narrative" in result.lower()


# ---------------------------------------------------------------------------
# No ad-hoc JSON parsing verification
# ---------------------------------------------------------------------------


class TestNoAdHocJsonParsing:
    """Verify research_agents.py no longer contains ad-hoc JSON parsing."""

    def test_no_json_loads_in_research_agents(self):
        """research_agents.py should not import or call json.loads."""
        import ast
        import inspect

        from solstein.research import research_agents

        source = inspect.getsource(research_agents)
        tree = ast.parse(source)

        # Check no json import
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "json", "research_agents.py should not import json"
            if isinstance(node, ast.ImportFrom):
                assert node.module != "json", "research_agents.py should not import from json"

    def test_no_extract_json_method(self):
        """Static _extract_json methods should be removed."""
        from solstein.research.research_agents import ContentExtractorAgent, ResearchPlannerAgent

        assert not hasattr(ResearchPlannerAgent, "_extract_json"), (
            "ResearchPlannerAgent._extract_json should be removed"
        )
        assert not hasattr(ContentExtractorAgent, "_extract_json_from_response"), (
            "ContentExtractorAgent._extract_json_from_response should be removed"
        )
