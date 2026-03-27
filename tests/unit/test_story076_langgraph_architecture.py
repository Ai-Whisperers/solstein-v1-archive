"""Tests for STORY-076: LangGraph State and Research Graph Architecture.

Verifies:
- Graph compiles without errors
- Graph topology contains all expected nodes and edges
- Parallel data-collection nodes are correctly modeled (fan-out / fan-in)
- ResearchState fields exist and carry correct type annotations
- Graph is invocable and produces the expected completed_nodes sequence
"""

from __future__ import annotations

import pytest
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph

from solstein.research.graph import ResearchState, compile_research_graph
from solstein.research.graph.state import ResearchState as ResearchStateDirect
from solstein.research.graph.topology import (
    NODE_ANALYSIS,
    NODE_COMPANIES_HOUSE,
    NODE_CONFLICT,
    NODE_DISPATCH,
    NODE_EXPORT,
    NODE_GITHUB,
    NODE_HUMAN_REVIEW_GATE,
    NODE_NEWS,
    NODE_SCORING,
    NODE_SEC,
    NODE_WEB,
    PARALLEL_COLLECTION_NODES,
    build_research_graph,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_initial_state() -> dict:
    """Return a minimal valid initial ResearchState dict for test runs."""
    return {
        "run_id": "test-run-001",
        "company_identifiers": ["acme-corp", "beta-inc"],
        "config": {"max_retries": 2},
        "raw_github_facts": [],
        "raw_companies_house_facts": [],
        "raw_news_facts": [],
        "raw_sec_facts": [],
        "raw_web_facts": [],
        "data_collection_errors": [],
        "conflict_flags": [],
        "resolved_facts": {},
        "confidence_scores": {},
        "company_scores": {},
        "market_analysis": {},
        "export_path": "",
        "export_status": "pending",
        "export_errors": [],
        "completed_nodes": [],
        "pipeline_errors": [],
        "human_review_required": False,
    }


# ---------------------------------------------------------------------------
# Import tests
# ---------------------------------------------------------------------------


class TestImports:
    """Verify that the graph module exports compile cleanly."""

    def test_research_state_importable(self) -> None:
        """ResearchState must be importable from the graph package."""
        assert ResearchState is not None

    def test_compile_research_graph_importable(self) -> None:
        """compile_research_graph must be importable from the graph package."""
        assert callable(compile_research_graph)

    def test_build_research_graph_importable(self) -> None:
        """build_research_graph must be importable from topology module."""
        assert callable(build_research_graph)

    def test_node_constants_importable(self) -> None:
        """Node name constants must be importable."""
        assert NODE_DISPATCH == "dispatch"
        assert NODE_CONFLICT == "conflict_resolution"
        assert len(PARALLEL_COLLECTION_NODES) == 5
        assert NODE_GITHUB in PARALLEL_COLLECTION_NODES
        assert NODE_COMPANIES_HOUSE in PARALLEL_COLLECTION_NODES
        assert NODE_NEWS in PARALLEL_COLLECTION_NODES
        assert NODE_SEC in PARALLEL_COLLECTION_NODES
        assert NODE_WEB in PARALLEL_COLLECTION_NODES
        assert NODE_SCORING == "scoring"
        assert NODE_HUMAN_REVIEW_GATE == "human_review_gate"
        assert NODE_ANALYSIS == "analysis"
        assert NODE_EXPORT == "export"


# ---------------------------------------------------------------------------
# Graph compilation tests
# ---------------------------------------------------------------------------


class TestGraphCompilation:
    """Verify the graph compiles without errors (REQ-5)."""

    def test_graph_compiles_without_checkpointer(self) -> None:
        """Graph must compile without errors when no checkpointer is provided."""
        compiled = compile_research_graph()
        assert compiled is not None

    def test_graph_compiles_with_memory_saver(self) -> None:
        """Graph must compile with a MemorySaver checkpointer (STORY-079 path)."""
        compiled = compile_research_graph(checkpointer=MemorySaver())
        assert compiled is not None

    def test_build_graph_returns_state_graph(self) -> None:
        """build_research_graph() must return a StateGraph before compilation."""
        graph = build_research_graph()
        assert isinstance(graph, StateGraph)


# ---------------------------------------------------------------------------
# Topology tests
# ---------------------------------------------------------------------------


class TestGraphTopology:
    """Verify the graph topology contains all expected nodes and edges (REQ-2)."""

    @pytest.fixture()
    def compiled(self):
        return compile_research_graph()

    def test_all_expected_nodes_present(self, compiled) -> None:
        """Graph must contain all 11 named nodes."""
        node_names = set(compiled.nodes.keys())
        expected = {
            NODE_DISPATCH,
            NODE_GITHUB,
            NODE_COMPANIES_HOUSE,
            NODE_NEWS,
            NODE_SEC,
            NODE_WEB,
            NODE_CONFLICT,
            NODE_SCORING,
            NODE_HUMAN_REVIEW_GATE,
            NODE_ANALYSIS,
            NODE_EXPORT,
        }
        assert expected.issubset(node_names), f"Missing nodes: {expected - node_names}"

    def test_parallel_nodes_are_five(self) -> None:
        """PARALLEL_COLLECTION_NODES must have exactly 5 members (REQ-3)."""
        assert len(PARALLEL_COLLECTION_NODES) == 5

    def test_parallel_nodes_are_unique(self) -> None:
        """Each parallel node name must be unique."""
        assert len(set(PARALLEL_COLLECTION_NODES)) == len(PARALLEL_COLLECTION_NODES)


# ---------------------------------------------------------------------------
# Fan-out / fan-in tests
# ---------------------------------------------------------------------------


class TestParallelModel:
    """Verify parallel nodes are correctly modeled (REQ-3)."""

    def test_all_parallel_nodes_in_graph(self) -> None:
        """All 5 collection nodes must appear in the compiled graph."""
        compiled = compile_research_graph()
        node_names = set(compiled.nodes.keys())
        for node in PARALLEL_COLLECTION_NODES:
            assert node in node_names, f"Parallel node '{node}' missing from graph"

    def test_graph_invoke_all_collection_nodes_run(self) -> None:
        """Invoking the graph must produce completed_nodes containing all 5 parallel nodes."""
        compiled = compile_research_graph()
        result = compiled.invoke(_make_initial_state())

        completed = result.get("completed_nodes", [])
        for node in PARALLEL_COLLECTION_NODES:
            assert node in completed, f"Parallel node '{node}' did not run"

    def test_conflict_resolution_runs_after_collection(self) -> None:
        """conflict_resolution must appear in completed_nodes after all collection nodes."""
        compiled = compile_research_graph()
        result = compiled.invoke(_make_initial_state())

        completed = result.get("completed_nodes", [])
        assert NODE_CONFLICT in completed, "conflict_resolution node did not run"

        conflict_idx = completed.index(NODE_CONFLICT)
        for node in PARALLEL_COLLECTION_NODES:
            assert node in completed[:conflict_idx], (
                f"'{node}' must appear before conflict_resolution in completed_nodes"
            )


# ---------------------------------------------------------------------------
# Full pipeline execution tests
# ---------------------------------------------------------------------------


class TestGraphExecution:
    """Verify the graph executes end-to-end and produces expected output."""

    def test_graph_runs_to_completion(self) -> None:
        """Graph must execute to END without raising an exception."""
        compiled = compile_research_graph()
        result = compiled.invoke(_make_initial_state())
        assert result is not None

    def test_export_status_in_result(self) -> None:
        """Result state must contain export_status."""
        compiled = compile_research_graph()
        result = compiled.invoke(_make_initial_state())
        assert "export_status" in result

    def test_market_analysis_in_result(self) -> None:
        """Result state must contain market_analysis dict."""
        compiled = compile_research_graph()
        result = compiled.invoke(_make_initial_state())
        assert isinstance(result.get("market_analysis"), dict)

    def test_no_human_review_by_default(self) -> None:
        """human_review_gate must not appear in completed_nodes for default state."""
        compiled = compile_research_graph()
        result = compiled.invoke(_make_initial_state())
        # Default state has human_review_required=False -> gate node should not run
        assert NODE_HUMAN_REVIEW_GATE not in result.get("completed_nodes", [])

    def test_human_review_gate_runs_when_required(self) -> None:
        """human_review_gate must appear in completed_nodes when human_review_required=True."""
        compiled = compile_research_graph()
        state = _make_initial_state()
        state["human_review_required"] = True

        result = compiled.invoke(state)
        assert NODE_HUMAN_REVIEW_GATE in result.get("completed_nodes", [])

    def test_all_major_nodes_complete(self) -> None:
        """All pipeline stages must appear in completed_nodes on successful run."""
        compiled = compile_research_graph()
        result = compiled.invoke(_make_initial_state())
        completed = result.get("completed_nodes", [])

        for node in [NODE_DISPATCH, NODE_CONFLICT, NODE_SCORING, NODE_ANALYSIS, NODE_EXPORT]:
            assert node in completed, f"Node '{node}' did not complete"


# ---------------------------------------------------------------------------
# ResearchState field tests
# ---------------------------------------------------------------------------


class TestResearchStateFields:
    """Verify ResearchState has all fields needed by downstream stories."""

    def test_research_state_has_parallel_fact_fields(self) -> None:
        """ResearchState must have one raw_*_facts field per parallel node."""
        annotations = ResearchStateDirect.__annotations__
        required = [
            "raw_github_facts",
            "raw_companies_house_facts",
            "raw_news_facts",
            "raw_sec_facts",
            "raw_web_facts",
        ]
        for field in required:
            assert field in annotations, f"ResearchState missing field: {field}"

    def test_research_state_has_run_metadata_fields(self) -> None:
        """ResearchState must have run_id, company_identifiers, config."""
        annotations = ResearchStateDirect.__annotations__
        for field in ["run_id", "company_identifiers", "config"]:
            assert field in annotations, f"ResearchState missing field: {field}"

    def test_research_state_has_output_fields(self) -> None:
        """ResearchState must have all fields needed by export node."""
        annotations = ResearchStateDirect.__annotations__
        for field in ["export_path", "export_status", "export_errors", "market_analysis"]:
            assert field in annotations, f"ResearchState missing field: {field}"

    def test_research_state_has_pipeline_control_fields(self) -> None:
        """ResearchState must have human_review_required and completed_nodes."""
        annotations = ResearchStateDirect.__annotations__
        for field in ["human_review_required", "completed_nodes", "pipeline_errors"]:
            assert field in annotations, f"ResearchState missing field: {field}"
