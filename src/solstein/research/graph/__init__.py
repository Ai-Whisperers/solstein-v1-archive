"""LangGraph-based research pipeline graph.

STORY-076: Defines the typed ResearchState and the explicit graph topology
for the market intelligence research pipeline.

Architecture:
    - ResearchState: typed state container for all inter-node data
    - topology.py: StateGraph definition (nodes, edges, fan-out/fan-in)
    - compile_research_graph(): entry point for graph compilation
"""

from .state import ResearchState
from .topology import compile_research_graph

__all__ = ["ResearchState", "compile_research_graph"]
