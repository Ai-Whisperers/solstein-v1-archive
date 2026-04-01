"""STORY-078 prerequisite tests: file deletion, ADR, and graph topology.

Verifies:
- additional_agents.py has been deleted (REQ-5)
- ADR-014 documents all 7 stub agent dispositions (REQ-2)
- The compiled research graph excludes all deprecated stub agents
"""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from solstein.research.graph.topology import PARALLEL_COLLECTION_NODES, build_research_graph

# ---------------------------------------------------------------------------
# REQ-5: additional_agents.py must not exist
# ---------------------------------------------------------------------------


class TestStubAgentDeletion:
    """Verify additional_agents.py has been removed (REQ-5)."""

    def test_additional_agents_file_deleted(self) -> None:
        """additional_agents.py must not exist anywhere in the agents package."""
        agents_dir = Path(__file__).parents[2] / "src" / "solstein" / "agents"
        stub_file = agents_dir / "additional_agents.py"
        assert not stub_file.exists(), (
            "additional_agents.py still exists — STORY-078 requires deleting it"
        )

    def test_additional_agents_not_importable(self) -> None:
        """Importing the stub module must raise ImportError."""
        with pytest.raises((ImportError, ModuleNotFoundError)):
            importlib.import_module("solstein.agents.additional_agents")


# ---------------------------------------------------------------------------
# REQ-2: ADR-014 documents all 7 stub agent dispositions
# ---------------------------------------------------------------------------


class TestADRDocumentation:
    """Verify ADR-014 exists and covers all 7 original stub agents."""

    ADR_PATH = Path(__file__).parents[2] / "docs" / "adr" / "ADR-014-stub-agent-disposition.md"

    def test_adr_file_exists(self) -> None:
        """ADR-014 file must exist at docs/adr/ADR-014-stub-agent-disposition.md."""
        assert self.ADR_PATH.exists(), f"ADR-014 not found at {self.ADR_PATH}"

    def test_adr_covers_all_seven_agents(self) -> None:
        """ADR must document the disposition of all 7 original stub agents."""
        content = self.ADR_PATH.read_text()
        required_agents = [
            "LinkedInAgent",
            "SECEdgarAgent",
            "PatentsAgent",
            "NewsAgent",
            "JobsAgent",
            "TechTrendsAgent",
            "WebsiteAgent",
        ]
        for agent in required_agents:
            assert agent in content, f"ADR-014 does not mention {agent}"

    def test_adr_contains_rationale_for_excluded_agents(self) -> None:
        """Excluded agents must have documented rationale, not just 'not implemented'."""
        content = self.ADR_PATH.read_text()
        excluded_agents = ["LinkedInAgent", "PatentsAgent", "JobsAgent", "TechTrendsAgent"]
        for agent in excluded_agents:
            assert "Excluded" in content or "EXCLUDED" in content, (
                f"ADR-014 must explain why {agent} is excluded"
            )

    def test_adr_identifies_implemented_nodes(self) -> None:
        """Implemented agents must be listed with their graph node names."""
        content = self.ADR_PATH.read_text()
        assert "sec_filings" in content
        assert "news_search" in content
        assert "web_profile" in content


# ---------------------------------------------------------------------------
# REQ-2: Compiled graph does not include excluded stub agents
# ---------------------------------------------------------------------------


class TestCompiledGraphExcludesStubs:
    """Verify the compiled research graph contains no excluded stub agents."""

    def test_compiled_graph_has_five_collection_nodes(self) -> None:
        """The graph must contain exactly the 5 implemented data-collection nodes."""
        expected = {"github_data", "companies_house", "news_search", "sec_filings", "web_profile"}
        actual = set(PARALLEL_COLLECTION_NODES)
        assert actual == expected, (
            f"Unexpected parallel nodes: {actual.symmetric_difference(expected)}"
        )

    def test_excluded_agents_not_in_graph_nodes(self) -> None:
        """linkedin_data, patents, jobs_data, tech_trends must not appear as graph nodes."""
        excluded = {"linkedin_data", "patents", "jobs_data", "tech_trends"}
        actual = set(PARALLEL_COLLECTION_NODES)
        overlap = excluded & actual
        assert not overlap, f"Excluded agents found in graph: {overlap}"

    def test_graph_compiles_successfully(self) -> None:
        """build_research_graph() must compile without error after STORY-078."""
        graph = build_research_graph(isolate_errors=True)
        compiled = graph.compile()
        assert compiled is not None
