"""Gather sources workflow node.

EPIC-022: Extracted from CoordinatorAgent for modularity.
"""

import asyncio
from typing import Any

from ...domain.models import DataSourceType
from ..base_agent import AgentTaskResult
from .base import WorkflowNode


class GatherSourcesNode(WorkflowNode):
    """Gather data from specialist agents."""

    def __init__(
        self,
        github_agent: Any,
        web_search_agent: Any,
        companies_house_agent: Any,
        seed_markdown_agent: Any,
        website_agent: Any,
    ):
        super().__init__()
        self._github_agent = github_agent
        self._web_search_agent = web_search_agent
        self._companies_house_agent = companies_house_agent
        self._seed_markdown_agent = seed_markdown_agent
        self._website_agent = website_agent

    @property
    def name(self) -> str:
        return "gather_sources"

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Execute gather sources node.

        Args:
            state: Workflow state with company_name, context, enabled_sources

        Returns:
            Updated state with agent_results and errors
        """
        company_name = state["company_name"]
        context = state.get("context", {})
        enabled_sources = state.get("enabled_sources", [])

        agent_tasks = []

        if DataSourceType.GITHUB in enabled_sources:
            agent_tasks.append(self._github_agent.gather(company_name, context))
        if DataSourceType.NEWS in enabled_sources:
            agent_tasks.append(self._web_search_agent.gather(company_name, context))
        if DataSourceType.COMPANY_FILINGS in enabled_sources:
            agent_tasks.append(self._companies_house_agent.gather(company_name, context))
        if DataSourceType.PRESS_RELEASE in enabled_sources:
            agent_tasks.append(self._seed_markdown_agent.gather(company_name, context))
        if DataSourceType.WEBSITE in enabled_sources:
            agent_tasks.append(self._website_agent.gather(company_name, context))

        self.logger.info(f"Aura | Stage: Gathering | Spawning {len(agent_tasks)} specialist agents")

        results = await asyncio.gather(*agent_tasks, return_exceptions=True)

        valid_results = []
        errors = []

        for r in results:
            if isinstance(r, Exception):
                self.logger.warning(f"Aura | Agent error: {r}")
                errors.append(str(r))
            elif isinstance(r, AgentTaskResult):
                self.logger.info(f"Aura | {r.agent_name}: {len(r.raw_sources)} sources, {len(r.extracted_facts)} facts")
                valid_results.append(r)

        return {"agent_results": valid_results, "errors": errors}
