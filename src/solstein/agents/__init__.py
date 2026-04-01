"""AI agents for data gathering and analysis.

This module contains the agent framework for automated data collection
from multiple sources with transparency and audit trail support.

Note: The LangGraph-based CoordinatorAgent was removed as it was never
wired into the production pipeline. The production pipeline uses
adapter-based enrichment via UnifiedCompanyLoader instead.
"""

from .base_agent import AgentTaskResult, BaseDataGatheringAgent
from .companies_house_agent import CompaniesHouseAgent
from .github_agent import GitHubAgent
from .web_search_agent import WebSearchAgent

__all__ = [
    "BaseDataGatheringAgent",
    "AgentTaskResult",
    "GitHubAgent",
    "WebSearchAgent",
    "CompaniesHouseAgent",
]
