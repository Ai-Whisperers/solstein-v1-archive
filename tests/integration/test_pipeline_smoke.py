"""Pipeline smoke test — Phase 2 verification gate.

Wires up CoordinatorAgent with mock sub-agents and verifies the full
workflow graph executes without raising. No real DB, no real API calls.

Confirms:
1. CoordinatorAgent can be constructed with injected dependencies
2. The LangGraph workflow nodes execute without crashing
3. The result is an AgentTaskResult, not an exception
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from solstein.agents.base_agent import AgentTaskResult
from solstein.agents.coordinator_agent import CoordinatorAgent
from solstein.domain.models import AggregatedFact, DataSourceType, RawDataSource


def _make_mock_agent(agent_name: str = "MockAgent") -> AsyncMock:
    """Create a mock data-gathering agent returning minimal valid results."""
    raw_source = RawDataSource(
        source_type=DataSourceType.NEWS,
        source_name="mock_source",
        raw_content="Mock content for testing",
        url="https://example.com/mock",
    )
    fact = AggregatedFact(
        fact_type="revenue",
        value=1_000_000.0,
        confidence=0.8,
        sources_used=["mock_source"],
    )
    result = AgentTaskResult(
        agent_name=agent_name,
        source_type=DataSourceType.NEWS,
        success=True,
        raw_sources=[raw_source],
        extracted_facts=[fact],
    )
    agent = AsyncMock()
    agent.gather = AsyncMock(return_value=result)
    return agent


@pytest.mark.asyncio
async def test_coordinator_constructs_without_error():
    """CoordinatorAgent can be instantiated with injected dependencies."""
    coordinator = CoordinatorAgent(
        github_agent=_make_mock_agent("GitHub"),
        web_search_agent=_make_mock_agent("WebSearch"),
        companies_house_agent=_make_mock_agent("CompaniesHouse"),
        seed_markdown_agent=_make_mock_agent("Markdown"),
        website_agent=_make_mock_agent("Website"),
        db_manager=MagicMock(),
    )
    assert coordinator is not None


@pytest.mark.asyncio
async def test_coordinator_analyze_company_returns_result():
    """Full workflow executes and returns AgentTaskResult — no real I/O."""
    db_manager = MagicMock()
    db_manager.save_research_run = AsyncMock(return_value=None)
    db_manager.get_session = MagicMock()

    coordinator = CoordinatorAgent(
        github_agent=_make_mock_agent("GitHub"),
        web_search_agent=_make_mock_agent("WebSearch"),
        companies_house_agent=_make_mock_agent("CompaniesHouse"),
        seed_markdown_agent=_make_mock_agent("Markdown"),
        website_agent=_make_mock_agent("Website"),
        db_manager=db_manager,
    )

    result = await coordinator.analyze_company("TestCo")

    assert isinstance(result, AgentTaskResult)
    assert result.agent_name == "Coordinator"
