"""Real LangGraph data-collection node implementations.

STORY-078: Replaces stub agents (additional_agents.py) with real LangGraph
node functions that call external APIs. Each node module contains a single
top-level function that can be passed directly to StateGraph.add_node().

Nodes implemented here:
    github_data     → github_node.github_data_node (GitHubAgent)
    companies_house → companies_house_node.companies_house_node (CompaniesHouseAgent)
    news_search     → news_node.news_search_node (WebSearchAgent)
    sec_filings     → sec_filings_node.sec_filings_node (SECEdgarConnector)
    web_profile     → web_profile_node.web_profile_node (WebsiteAgent)

Excluded agents (documented in docs/adr/ADR-014-stub-agent-disposition.md):
    linkedin_agent  → excluded: LinkedIn API requires paid partner access
    patents_agent   → excluded: no cost-effective public patents API
    jobs_agent      → excluded: Indeed/LinkedIn Jobs APIs require paid partner access
    tech_trends     → excluded: Wappalyzer/BuiltWith APIs are paid; tech stack
                       partially covered by web_profile_node via WebsiteAgent
"""

from .companies_house_node import companies_house_node
from .github_node import github_data_node
from .news_node import news_search_node
from .sec_filings_node import sec_filings_node
from .web_profile_node import web_profile_node

__all__ = [
    "github_data_node",
    "companies_house_node",
    "news_search_node",
    "sec_filings_node",
    "web_profile_node",
]
