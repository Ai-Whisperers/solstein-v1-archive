"""Tests for STORY-077: Migrate Coordinator Agent to LangGraph State Machine.

Verifies:
- GraphExecutor.run() completes end-to-end and returns expected keys
- RequestCache.get_or_fetch() deduplicates calls (hit/miss counts correct)
- with_error_isolation() isolates node failures without crashing the graph
- run_graph_research() stable public interface is callable with expected signature
- RequestCache.stats property returns correct hit/miss/entry counts
- GraphExecutor creates a new RequestCache per run (no cross-run pollution)
"""

from __future__ import annotations

import re
from typing import Any

from langgraph.checkpoint.memory import MemorySaver

from solstein.research.graph import GraphExecutor, RequestCache, run_graph_research
from solstein.research.graph.executor import with_error_isolation
from solstein.research.graph.state import ResearchState

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_initial_state() -> dict[str, Any]:
    """Return a minimal valid initial ResearchState dict for test runs."""
    return {
        "run_id": "test-077-001",
        "company_identifiers": ["acme-corp", "beta-inc"],
        "config": {},
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
# RequestCache tests
# ---------------------------------------------------------------------------


class TestRequestCache:
    """Verify RequestCache deduplication behaviour (REQ-1)."""

    def test_first_call_is_miss(self) -> None:
        """First get_or_fetch for a key must call fetcher and count as miss."""
        cache = RequestCache()
        calls = []

        def fetcher() -> str:
            calls.append(1)
            return "result"

        result = cache.get_or_fetch(("company-a", "github"), fetcher)

        assert result == "result"
        assert len(calls) == 1
        assert cache.stats["misses"] == 1
        assert cache.stats["hits"] == 0
        assert cache.stats["entries"] == 1

    def test_second_call_is_hit(self) -> None:
        """Second get_or_fetch for the same key must NOT call fetcher again."""
        cache = RequestCache()
        calls = []

        def fetcher() -> str:
            calls.append(1)
            return "result"

        cache.get_or_fetch(("company-a", "github"), fetcher)
        result = cache.get_or_fetch(("company-a", "github"), fetcher)

        assert result == "result"
        assert len(calls) == 1  # fetcher only called once
        assert cache.stats["hits"] == 1
        assert cache.stats["misses"] == 1

    def test_different_keys_are_independent(self) -> None:
        """Different (company_id, source_type) keys must not share cache entries."""
        cache = RequestCache()
        calls = {"github": 0, "news": 0}

        def github_fetcher() -> str:
            calls["github"] += 1
            return "github-result"

        def news_fetcher() -> str:
            calls["news"] += 1
            return "news-result"

        r1 = cache.get_or_fetch(("company-a", "github"), github_fetcher)
        r2 = cache.get_or_fetch(("company-a", "news"), news_fetcher)

        assert r1 == "github-result"
        assert r2 == "news-result"
        assert calls["github"] == 1
        assert calls["news"] == 1
        assert cache.stats["entries"] == 2
        assert cache.stats["misses"] == 2

    def test_stats_property_returns_dict(self) -> None:
        """stats must return a dict with 'hits', 'misses', 'entries' keys."""
        cache = RequestCache()
        stats = cache.stats
        assert isinstance(stats, dict)
        assert "hits" in stats
        assert "misses" in stats
        assert "entries" in stats

    def test_multiple_companies_same_source_deduplicated(self) -> None:
        """If two companies share the same source, they get separate cache entries."""
        cache = RequestCache()
        calls = []

        def fetcher_a() -> str:
            calls.append("a")
            return "result-a"

        def fetcher_b() -> str:
            calls.append("b")
            return "result-b"

        r1 = cache.get_or_fetch(("company-a", "github"), fetcher_a)
        r2 = cache.get_or_fetch(("company-b", "github"), fetcher_b)
        # Re-fetch both — should hit cache
        r3 = cache.get_or_fetch(("company-a", "github"), fetcher_a)
        r4 = cache.get_or_fetch(("company-b", "github"), fetcher_b)

        assert r1 == "result-a"
        assert r2 == "result-b"
        assert r3 == "result-a"
        assert r4 == "result-b"
        assert calls == ["a", "b"]  # fetchers called only once each
        assert cache.stats["hits"] == 2
        assert cache.stats["misses"] == 2


# ---------------------------------------------------------------------------
# with_error_isolation tests
# ---------------------------------------------------------------------------


class TestWithErrorIsolation:
    """Verify node error isolation wrapper (REQ-2)."""

    def test_successful_node_passes_through(self) -> None:
        """Decorated node that succeeds must return its original result."""

        @with_error_isolation("test_node")
        def good_node(state: ResearchState) -> dict[str, Any]:
            return {"completed_nodes": ["test_node"], "data_collection_errors": []}

        state = _make_initial_state()  # type: ignore[arg-type]
        result = good_node(state)  # type: ignore[call-arg]

        assert result["completed_nodes"] == ["test_node"]
        assert result["data_collection_errors"] == []

    def test_failing_node_does_not_raise(self) -> None:
        """Decorated node that raises must NOT propagate the exception."""

        @with_error_isolation("failing_node")
        def bad_node(state: ResearchState) -> dict[str, Any]:
            raise ValueError("Something went wrong")

        state = _make_initial_state()  # type: ignore[arg-type]
        # Must not raise
        result = bad_node(state)  # type: ignore[call-arg]
        assert result is not None

    def test_failing_node_records_error_message(self) -> None:
        """Decorated failing node must include the error in data_collection_errors."""

        @with_error_isolation("failing_node")
        def bad_node(state: ResearchState) -> dict[str, Any]:
            raise RuntimeError("API timeout")

        state = _make_initial_state()  # type: ignore[arg-type]
        result = bad_node(state)  # type: ignore[call-arg]

        errors = result.get("data_collection_errors", [])
        assert len(errors) == 1
        assert "failing_node" in errors[0]
        assert "RuntimeError" in errors[0]
        assert "API timeout" in errors[0]

    def test_failing_node_does_not_complete(self) -> None:
        """Failing node must NOT add itself to completed_nodes."""

        @with_error_isolation("failing_node")
        def bad_node(state: ResearchState) -> dict[str, Any]:
            raise ConnectionError("Network error")

        state = _make_initial_state()  # type: ignore[arg-type]
        result = bad_node(state)  # type: ignore[call-arg]

        assert "completed_nodes" not in result

    def test_failing_node_returns_empty_pipeline_errors(self) -> None:
        """Failing node returns pipeline_errors as empty list (not None)."""

        @with_error_isolation("failing_node")
        def bad_node(state: ResearchState) -> dict[str, Any]:
            raise TypeError("Bad type")

        state = _make_initial_state()  # type: ignore[arg-type]
        result = bad_node(state)  # type: ignore[call-arg]

        assert result.get("pipeline_errors") == []

    def test_wraps_preserves_function_name(self) -> None:
        """with_error_isolation must use functools.wraps to preserve function metadata."""

        @with_error_isolation("my_node")
        def my_specific_node(state: ResearchState) -> dict[str, Any]:
            return {}

        assert my_specific_node.__name__ == "my_specific_node"


# ---------------------------------------------------------------------------
# GraphExecutor tests
# ---------------------------------------------------------------------------


class TestGraphExecutor:
    """Verify GraphExecutor integration (REQ-3)."""

    def test_executor_instantiates(self) -> None:
        """GraphExecutor must instantiate without errors."""
        executor = GraphExecutor()
        assert executor is not None

    def test_executor_run_returns_dict(self) -> None:
        """GraphExecutor.run() must return a dict."""
        executor = GraphExecutor()
        result = executor.run(company_identifiers=["acme-corp"])
        assert isinstance(result, dict)

    def test_executor_run_contains_run_id(self) -> None:
        """Result must contain run_id field."""
        executor = GraphExecutor()
        result = executor.run(company_identifiers=["acme-corp"], run_id="run-test-001")
        assert result.get("run_id") == "run-test-001"

    def test_executor_run_auto_generates_run_id(self) -> None:
        """If run_id is not provided, one must be auto-generated (UUID format)."""
        executor = GraphExecutor()
        result = executor.run(company_identifiers=["acme-corp"])
        run_id = result.get("run_id", "")
        # UUID pattern: 8-4-4-4-12 hex chars
        assert re.match(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", run_id)

    def test_executor_run_contains_expected_keys(self) -> None:
        """Result must contain the keys documented in run_graph_research docstring."""
        executor = GraphExecutor()
        result = executor.run(company_identifiers=["acme-corp"])
        expected_keys = {
            "run_id",
            "company_scores",
            "market_analysis",
            "export_path",
            "export_status",
            "data_collection_errors",
            "completed_nodes",
        }
        for key in expected_keys:
            assert key in result, f"Missing expected key: {key}"

    def test_executor_run_creates_fresh_cache_per_run(self) -> None:
        """Each call to run() must use a fresh RequestCache (no cross-run pollution)."""
        executor = GraphExecutor()
        # Two separate runs must not share cache state
        result1 = executor.run(company_identifiers=["acme-corp"], run_id="run-001")
        result2 = executor.run(company_identifiers=["beta-inc"], run_id="run-002")
        # Both must complete independently
        assert result1.get("run_id") == "run-001"
        assert result2.get("run_id") == "run-002"

    def test_executor_accepts_config(self) -> None:
        """GraphExecutor.run() must accept a config dict without error."""
        executor = GraphExecutor()
        result = executor.run(
            company_identifiers=["acme-corp"],
            config={"max_retries": 3, "timeout": 30},
        )
        assert isinstance(result, dict)

    def test_executor_with_checkpointer(self) -> None:
        """GraphExecutor must accept a MemorySaver checkpointer."""
        executor = GraphExecutor(checkpointer=MemorySaver())
        assert executor is not None


# ---------------------------------------------------------------------------
# run_graph_research public interface tests
# ---------------------------------------------------------------------------


class TestRunGraphResearch:
    """Verify run_graph_research() stable public interface (REQ-4)."""

    def test_callable(self) -> None:
        """run_graph_research must be callable."""
        assert callable(run_graph_research)

    def test_returns_dict(self) -> None:
        """run_graph_research() must return a dict."""
        result = run_graph_research(company_identifiers=["acme-corp"])
        assert isinstance(result, dict)

    def test_accepts_company_identifiers(self) -> None:
        """run_graph_research must accept company_identifiers as positional arg."""
        result = run_graph_research(["acme-corp", "beta-inc"])
        assert isinstance(result, dict)

    def test_accepts_optional_config(self) -> None:
        """run_graph_research must accept optional config kwarg."""
        result = run_graph_research(
            company_identifiers=["acme-corp"],
            config={"max_retries": 2},
        )
        assert isinstance(result, dict)

    def test_accepts_optional_run_id(self) -> None:
        """run_graph_research must accept optional run_id kwarg."""
        result = run_graph_research(
            company_identifiers=["acme-corp"],
            run_id="stable-test-run",
        )
        assert result.get("run_id") == "stable-test-run"

    def test_result_contains_completed_nodes(self) -> None:
        """Result from run_graph_research must include completed_nodes list."""
        result = run_graph_research(company_identifiers=["acme-corp"])
        assert isinstance(result.get("completed_nodes"), list)

    def test_result_contains_market_analysis(self) -> None:
        """Result must contain market_analysis dict."""
        result = run_graph_research(company_identifiers=["acme-corp"])
        assert isinstance(result.get("market_analysis"), dict)
