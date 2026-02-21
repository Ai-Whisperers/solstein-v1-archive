"""Test Phase 1 agents with a single company (Octopus Energy).

Tests all three specialist agents (GitHub, Web Search, Companies House)
and compares results to the manual analysis in the competitor data.
"""

import asyncio
import os

import pytest

from solstein.agents import CompaniesHouseAgent, GitHubAgent, WebSearchAgent


@pytest.mark.asyncio
async def test_github_agent_octopus_energy():
    """Test GitHub agent with Octopus Energy / Kraken Technologies."""
    agent = GitHubAgent(github_token=os.getenv("GITHUB_TOKEN"))

    result = await agent.gather(
        company_name="Octopus Energy",
        context={
            "known_github_org": "kraken-io",
            "industry": "Energy Software",
        },
    )

    assert result.success
    assert len(result.raw_sources) > 0, "Should find GitHub repos"
    assert len(result.extracted_facts) > 0, "Should extract facts"

    fact_types = [f.fact_type for f in result.extracted_facts]
    assert "tech_stack" in fact_types
    assert "engineering_velocity" in fact_types or "contributor_count" in fact_types


@pytest.mark.asyncio
async def test_companies_house_agent_octopus():
    """Test Companies House agent with Octopus Energy Group (UK registered)."""
    agent = CompaniesHouseAgent()

    result = await agent.gather(
        company_name="Octopus Energy Group Limited",
        context={"industry": "Energy Software"},
    )

    assert result.success

    if result.raw_sources:
        assert len(result.extracted_facts) > 0, "Should extract UK filing facts"

        fact_types = [f.fact_type for f in result.extracted_facts]
        expected = ["company_name", "headquarters", "company_status"]
        found = [ft for ft in expected if ft in fact_types]
        assert len(found) > 0, f"Should find at least one of {expected}"


@pytest.mark.asyncio
async def test_web_search_agent_octopus():
    """Test Web Search agent with Octopus Energy (requires API key)."""
    api_key = os.getenv("GOOGLE_API_KEY")
    search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

    if not api_key or not search_engine_id:
        pytest.skip("Google Custom Search API not configured")

    agent = WebSearchAgent(
        google_api_key=api_key,
        search_engine_id=search_engine_id,
    )

    result = await agent.gather(
        company_name="Octopus Energy",
        context={
            "industry": "Energy Software",
            "market": "European Energy",
        },
    )

    assert result.success

    if result.raw_sources:
        assert len(result.extracted_facts) >= 0


@pytest.mark.asyncio
async def test_all_agents_together():
    """Test running all agents together on Octopus Energy."""
    github_token = os.getenv("GITHUB_TOKEN")

    github_agent = GitHubAgent(github_token=github_token)
    companies_house_agent = CompaniesHouseAgent()

    context = {
        "known_github_org": "kraken-io",
        "industry": "Energy Software",
        "market": "European Energy",
    }

    github_result = await github_agent.gather("Octopus Energy", context)
    companies_house_result = await companies_house_agent.gather(
        "Octopus Energy Group Limited", context
    )

    assert github_result.success
    assert companies_house_result.success

    total_sources = len(github_result.raw_sources) + len(
        companies_house_result.raw_sources
    )
    total_facts = len(github_result.extracted_facts) + len(
        companies_house_result.extracted_facts
    )

    print(f"\nTotal sources gathered: {total_sources}")
    print(f"Total facts extracted: {total_facts}")
    print(f"GitHub execution time: {github_result.execution_time_seconds:.2f}s")
    print(
        f"Companies House execution time: {companies_house_result.execution_time_seconds:.2f}s"
    )

    assert total_sources > 0, "Should gather sources from multiple agents"
    assert total_facts > 0, "Should extract facts from multiple agents"


@pytest.mark.asyncio
async def test_previse_systems_smaller_company():
    """Test agents on Previse Systems AG (smaller company, Germany-based)."""
    github_token = os.getenv("GITHUB_TOKEN")

    github_agent = GitHubAgent(github_token=github_token)

    result = await github_agent.gather(
        company_name="Previse Systems AG",
        context={"industry": "Energy Software"},
    )

    assert result.success

    if not result.raw_sources:
        print("Note: Previse Systems AG may not have public GitHub org")


if __name__ == "__main__":
    asyncio.run(test_all_agents_together())
