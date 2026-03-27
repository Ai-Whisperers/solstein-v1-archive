"""LangGraph-based research pipeline graph.

STORY-076: Defines the typed ResearchState and the explicit graph topology.
STORY-077: Adds GraphExecutor with request deduplication and node error isolation.

Architecture:
    - state.py: ResearchState TypedDict (all inter-node data)
    - topology.py: StateGraph definition (nodes, edges, fan-out/fan-in)
    - executor.py: GraphExecutor with deduplication + error isolation
    - compile_research_graph(): entry point for graph compilation
    - run_graph_research(): stable public interface for callers
"""

from .executor import GraphExecutor, RequestCache, run_graph_research
from .state import ResearchState
from .topology import compile_research_graph

__all__ = [
    "ResearchState",
    "compile_research_graph",
    "GraphExecutor",
    "RequestCache",
    "run_graph_research",
]
