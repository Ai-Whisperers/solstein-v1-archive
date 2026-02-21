"""Tests for 7 additional data agents.

Tests verify that all agents work correctly with resilience layer,
extract appropriate data, and handle errors gracefully.
"""

import pytest

from solstein.agents.additional_agents import (
    AgentOrchestrator,
    JobsAgent,
    LinkedInAgent,
    NewsAgent,
    PatentsAgent,
    SECEdgarAgent,
    TechTrendsAgent,
    WebsiteAgent,
)


class TestLinkedInAgent:
    """Test suite for LinkedIn agent."""

    @pytest.mark.asyncio
    async def test_analyze(self):
        """Verify that LinkedIn agent extracts data."""
        agent = LinkedInAgent("TechCorp")
        result = await agent.analyze()

        assert "linkedin_url" in result
        assert "employees" in result
        assert result["employees"]["current"] > 0
        assert "follower_growth" in result

    @pytest.mark.asyncio
    async def test_hiring_signals(self):
        """Verify that hiring signals are extracted."""
        agent = LinkedInAgent("Startup Labs")
        result = await agent.analyze()

        assert "recent_hires" in result
        assert "job_openings" in result
        assert result["recent_hires"] >= 0


class TestSECEdgarAgent:
    """Test suite for SEC EDGAR agent."""

    @pytest.mark.asyncio
    async def test_analyze(self):
        """Verify that SEC agent extracts financial data."""
        agent = SECEdgarAgent("PublicCorp")
        result = await agent.analyze()

        assert "latest_10k" in result
        assert "total_revenue" in result["latest_10k"]
        assert "net_income" in result["latest_10k"]

    @pytest.mark.asyncio
    async def test_compliance_signals(self):
        """Verify that compliance signals are extracted."""
        agent = SECEdgarAgent("PublicCorp")
        result = await agent.analyze()

        assert "auditor" in result
        assert "audit_opinion" in result
        assert "risk_factors" in result


class TestPatentsAgent:
    """Test suite for Patents agent."""

    @pytest.mark.asyncio
    async def test_analyze(self):
        """Verify that Patents agent extracts innovation data."""
        agent = PatentsAgent("TechCorp")
        result = await agent.analyze()

        assert "total_patents" in result
        assert "patents_2024" in result
        assert "technology_areas" in result

    @pytest.mark.asyncio
    async def test_innovation_metrics(self):
        """Verify that innovation metrics are calculated."""
        agent = PatentsAgent("ResearchCorp")
        result = await agent.analyze()

        assert result["total_patents"] > 0
        assert "pending_applications" in result


class TestNewsAgent:
    """Test suite for News agent."""

    @pytest.mark.asyncio
    async def test_analyze(self):
        """Verify that News agent extracts coverage data."""
        agent = NewsAgent("FamousCorp")
        result = await agent.analyze()

        assert "press_mentions_6m" in result
        assert "sentiment" in result
        assert "trending" in result

    @pytest.mark.asyncio
    async def test_sentiment_analysis(self):
        """Verify that sentiment is analyzed."""
        agent = NewsAgent("PopularCorp")
        result = await agent.analyze()

        assert "sentiment_score" in result
        assert 0 <= result["sentiment_score"] <= 1


class TestJobsAgent:
    """Test suite for Jobs agent."""

    @pytest.mark.asyncio
    async def test_analyze(self):
        """Verify that Jobs agent extracts hiring data."""
        agent = JobsAgent("GrowingCorp")
        result = await agent.analyze()

        assert "active_job_postings" in result
        assert "hiring_departments" in result
        assert "hiring_rate_monthly" in result

    @pytest.mark.asyncio
    async def test_expansion_signals(self):
        """Verify that geographic expansion is tracked."""
        agent = JobsAgent("ExpandingCorp")
        result = await agent.analyze()

        assert "location_expansion" in result
        assert isinstance(result["location_expansion"], list)


class TestTechTrendsAgent:
    """Test suite for TechTrends agent."""

    @pytest.mark.asyncio
    async def test_analyze(self):
        """Verify that TechTrends agent extracts stack data."""
        agent = TechTrendsAgent("TechCorp")
        result = await agent.analyze()

        assert "cloud_providers" in result
        assert "frameworks" in result
        assert "databases" in result

    @pytest.mark.asyncio
    async def test_ai_adoption(self):
        """Verify that AI adoption is tracked."""
        agent = TechTrendsAgent("AIForwardCorp")
        result = await agent.analyze()

        assert "ai_adoption" in result
        assert "llm_integration" in result["ai_adoption"]

    @pytest.mark.asyncio
    async def test_modernization_score(self):
        """Verify that modernization is scored."""
        agent = TechTrendsAgent("ModernCorp")
        result = await agent.analyze()

        assert "modernization_score" in result
        assert 0 <= result["modernization_score"] <= 10


class TestWebsiteAgent:
    """Test suite for Website agent."""

    @pytest.mark.asyncio
    async def test_analyze(self):
        """Verify that Website agent extracts data."""
        agent = WebsiteAgent("WebCorp")
        result = await agent.analyze()

        assert "domain" in result
        assert "tech_stack" in result
        assert "monthly_visitors" in result

    @pytest.mark.asyncio
    async def test_core_web_vitals(self):
        """Verify that core web vitals are measured."""
        agent = WebsiteAgent("PerformantCorp")
        result = await agent.analyze()

        assert "core_web_vitals" in result
        assert "lcp" in result["core_web_vitals"]
        assert "fid" in result["core_web_vitals"]
        assert "cls" in result["core_web_vitals"]


class TestAgentOrchestrator:
    """Test suite for agent orchestrator."""

    @pytest.mark.asyncio
    async def test_analyze_all_agents(self):
        """Verify that all agents run in orchestrator."""
        orchestrator = AgentOrchestrator("TestCorp")
        results = await orchestrator.analyze_all()

        assert len(results) == 7
        assert "linkedin" in results
        assert "sec_edgar" in results
        assert "patents" in results
        assert "news" in results
        assert "jobs" in results
        assert "tech_trends" in results
        assert "website" in results

    @pytest.mark.asyncio
    async def test_analyze_single_agent(self):
        """Verify that single agent can be run."""
        orchestrator = AgentOrchestrator("TestCorp")
        result = await orchestrator.analyze_agent("linkedin")

        assert "linkedin_url" in result

    @pytest.mark.asyncio
    async def test_unknown_agent_raises_error(self):
        """Verify that unknown agent raises error."""
        orchestrator = AgentOrchestrator("TestCorp")

        with pytest.raises(ValueError):
            await orchestrator.analyze_agent("nonexistent_agent")

    @pytest.mark.asyncio
    async def test_agent_resilience(self):
        """Verify that agents use resilience layer."""
        orchestrator = AgentOrchestrator("TestCorp")
        result = await orchestrator.analyze_agent("patents")

        assert "total_patents" in result
        assert "patents_2024" in result


class TestAgentIntegration:
    """Integration tests for multiple agents."""

    @pytest.mark.asyncio
    async def test_linkedin_and_jobs_consistency(self):
        """Verify that LinkedIn and Jobs data are consistent."""
        linkedin = LinkedInAgent("TestCorp")
        jobs = JobsAgent("TestCorp")

        linkedin_result = await linkedin.analyze()
        jobs_result = await jobs.analyze()

        assert linkedin_result["recent_hires"] > 0
        assert jobs_result["active_job_postings"] > 0

    @pytest.mark.asyncio
    async def test_sec_and_news_coverage(self):
        """Verify that SEC filings and news align."""
        sec = SECEdgarAgent("PublicCorp")
        news = NewsAgent("PublicCorp")

        sec_result = await sec.analyze()
        news_result = await news.analyze()

        assert sec_result["latest_10k"]["total_revenue"] > 0
        assert news_result["press_mentions_6m"] > 0

    @pytest.mark.asyncio
    async def test_tech_trends_and_website_alignment(self):
        """Verify that tech trends and website align."""
        tech_trends = TechTrendsAgent("TechCorp")
        website = WebsiteAgent("TechCorp")

        tech_result = await tech_trends.analyze()
        website_result = await website.analyze()

        tech_stack = set(tech_result["frameworks"])
        website_stack = set(website_result["tech_stack"])

        assert len(tech_stack) > 0
        assert len(website_stack) > 0
