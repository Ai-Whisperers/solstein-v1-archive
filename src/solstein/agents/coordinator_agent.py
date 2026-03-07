"""Coordinator Agent for Solstein.

EPIC-022: Refactored to use modular workflow nodes.

Orchestrates multiple specialist agents using LangGraph workflow.
Each workflow node is implemented as a separate class for modularity.

Workflow:
1. gather_sources: Spawn specialist agents in parallel
2. process_raw: Create raw data records
3. logic_fusion: Aggregate facts
4. extract_signals: Extract business signals
"""

from typing import Any

from langgraph.graph import END, StateGraph
from loguru import logger

from ..domain.models import DataSourceType
from ..infrastructure.database import DatabaseManager
from .base_agent import AgentTaskResult, BaseDataGatheringAgent
from .workflow_nodes import (
    ExtractSignalsNode,
    GatherSourcesNode,
    LogicFusionNode,
    ProcessRawNode,
)


class CoordinatorAgent(BaseDataGatheringAgent):
    """Orchestrates specialist agents using modular workflow nodes.

    EPIC-022: Workflow nodes extracted into separate classes.
    Each node (gather_sources, process_raw, logic_fusion, extract_signals)
    is implemented as a separate class for modularity and testability.
    """

    def __init__(
        self,
        github_agent: BaseDataGatheringAgent,
        web_search_agent: BaseDataGatheringAgent,
        companies_house_agent: BaseDataGatheringAgent,
        seed_markdown_agent: BaseDataGatheringAgent,
        website_agent: BaseDataGatheringAgent,
        db_manager: DatabaseManager,
    ):
        """Initialize coordinator with specialist agents.

        Args:
            github_agent: GitHub data agent
            web_search_agent: Web search agent
            companies_house_agent: Companies House agent
            seed_markdown_agent: Markdown data agent
            website_agent: Website scraping agent
            db_manager: Database manager
        """
        super().__init__("Coordinator")

        # Store agent references
        self._github_agent = github_agent
        self._web_search_agent = web_search_agent
        self._companies_house_agent = companies_house_agent
        self._seed_markdown_agent = seed_markdown_agent
        self._website_agent = website_agent
        self._db = db_manager

        # Initialize workflow nodes
        self._gather_node = GatherSourcesNode(
            github_agent=github_agent,
            web_search_agent=web_search_agent,
            companies_house_agent=companies_house_agent,
            seed_markdown_agent=seed_markdown_agent,
            website_agent=website_agent,
        )
        self._process_node = ProcessRawNode()
        self._fusion_node = LogicFusionNode()
        self._signals_node = ExtractSignalsNode()

        # Build LangGraph workflow
        self._graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build LangGraph workflow using modular nodes.

        Returns:
            Compiled StateGraph
        """
        workflow = StateGraph(dict)

        # Add nodes (using modular node classes)
        workflow.add_node("gather_sources", self._gather_node.execute)
        workflow.add_node("process_raw", self._process_node.execute)
        workflow.add_node("logic_fusion", self._fusion_node.execute)
        workflow.add_node("extract_signals", self._signals_node.execute)

        # Define edges
        workflow.set_entry_point("gather_sources")
        workflow.add_edge("gather_sources", "process_raw")
        workflow.add_edge("process_raw", "logic_fusion")
        workflow.add_edge("logic_fusion", "extract_signals")
        workflow.add_edge("extract_signals", END)

        return workflow.compile()

    async def analyze_company(
        self,
        company_name: str,
        context: dict[str, Any] | None = None,
        enabled_sources: list[DataSourceType] | None = None,
    ) -> AgentTaskResult:
        """Analyze a company using specialist agents.

        Args:
            company_name: Company to analyze
            context: Optional context data
            enabled_sources: List of data sources to enable

        Returns:
            AgentTaskResult with analysis results
        """
        logger.info(f"Aura | Initiating analysis for {company_name}")

        # Initialize state
        initial_state = {
            "company_name": company_name,
            "context": context or {},
            "enabled_sources": enabled_sources or list(DataSourceType),
        }

        # Execute workflow
        final_state = await self._graph.ainvoke(initial_state)

        # Create result
        result = AgentTaskResult(
            agent_name="Coordinator",
            company_name=company_name,
            raw_sources=final_state.get("raw_data_records", []),
            extracted_facts=final_state.get("aggregated_facts", []),
            signals=final_state.get("extracted_signals", []),
            errors=final_state.get("errors", []),
        )

        logger.info(
            f"Aura | Analysis complete for {company_name}: "
            f"{len(result.raw_sources)} sources, "
            f"{len(result.extracted_facts)} facts, "
            f"{len(result.signals)} signals"
        )

        return result

    async def gather(self, company_name: str, context: dict[str, Any]) -> AgentTaskResult:
        """Gather data for a company (convenience method).

        Args:
            company_name: Company to gather data for
            context: Context data

        Returns:
            AgentTaskResult
        """
        return await self.analyze_company(company_name, context)
