"""LangGraph graph executor with request deduplication and node error isolation.

.. warning:: FROZEN — STORY-255 (2026-03-31)

   This graph executor is **frozen**. See ``topology.py`` docstring and
   ``docs/architecture/decisions.md`` for rationale. Bug fixes and security
   patches only; no new features.

STORY-077: Provides the execution layer for the research pipeline graph.

Key responsibilities:
    1. Request deduplication — if two parallel nodes would fetch the same
       external resource (same company + same data source), only one HTTP
       call is made and the result is shared via RequestCache.
    2. Node error isolation — a failure in one data-collection node is logged
       and recorded in the state, but does not crash the graph. Independent
       nodes continue executing.
    3. Stable interface — run_graph_research() has the same signature shape as
       run_market_intelligence() so callers can switch execution paths without
       code changes beyond the import.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Any

from langgraph.types import Command
from loguru import logger

from solstein.config import Settings
from solstein.research.graph.checkpointer import build_checkpointer

from .isolation import with_error_isolation
from .state import ResearchState
from .topology import compile_research_graph

# Re-export with_error_isolation so callers can import it from executor
# (backward-compatible: tests import from solstein.research.graph.executor)
__all__ = ["GraphExecutor", "RequestCache", "run_graph_research", "with_error_isolation"]


# ---------------------------------------------------------------------------
# Request deduplication cache
# ---------------------------------------------------------------------------


class RequestCache:
    """Per-run cache for deduplicating external resource requests.

    When two parallel nodes would fetch the same external resource (same
    company_id + same source_type + same time_range), the second call hits
    the cache and returns the previously fetched result instead of making
    a second HTTP request.

    This is a simple in-memory dict keyed by (company_id, source_type).
    STORY-078 nodes should call RequestCache.get_or_fetch() instead of
    directly calling the external API.

    Usage in a LangGraph node (STORY-078):
        def _github_data_node(state, config):
            cache = config.get("configurable", {}).get("request_cache")
            for cid in state["company_identifiers"]:
                result = cache.get_or_fetch(
                    key=(cid, "github"),
                    fetcher=lambda: github_api.fetch(cid),
                )
    """

    def __init__(self) -> None:
        self._store: dict[tuple[str, str], Any] = {}
        self._hit_count: int = 0
        self._miss_count: int = 0

    def get_or_fetch(self, key: tuple[str, str], fetcher: Callable[[], Any]) -> Any:
        """Return cached result if available; otherwise call fetcher and cache result.

        Args:
            key: (company_id, source_type) tuple uniquely identifying the request.
            fetcher: Zero-argument callable that performs the external request.

        Returns:
            The result from cache (hit) or from fetcher (miss).
        """
        if key in self._store:
            self._hit_count += 1
            logger.debug(f"[RequestCache] HIT {key} (total hits: {self._hit_count})")
            return self._store[key]

        self._miss_count += 1
        result = fetcher()
        self._store[key] = result
        logger.debug(f"[RequestCache] MISS {key} (fetched, total misses: {self._miss_count})")
        return result

    @property
    def stats(self) -> dict[str, int]:
        """Return cache hit/miss statistics for observability."""
        return {
            "hits": self._hit_count,
            "misses": self._miss_count,
            "entries": len(self._store),
        }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _resolve_threshold(confidence_threshold: float | None) -> float:
    """Return effective confidence threshold, falling back to Settings default."""
    if confidence_threshold is not None:
        return confidence_threshold
    try:
        return Settings().human_review_confidence_threshold
    except Exception as exc:
        logger.warning("[GraphExecutor] Could not read Settings threshold (%s), using 0.5", exc)
        return 0.5


def _build_initial_state(
    company_identifiers: list[str],
    run_id: str,
    merged_config: dict[str, Any],
) -> ResearchState:
    """Return a fully-initialised ResearchState dict for a new graph run."""
    return {
        "run_id": run_id,
        "company_identifiers": company_identifiers,
        "config": merged_config,
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
# Graph executor
# ---------------------------------------------------------------------------


class GraphExecutor:
    """Executes the research pipeline graph with deduplication and error isolation.

    Creates a compiled graph once (expensive) and reuses it across runs.
    Each run gets its own RequestCache so there is no cross-run cache pollution.

    Usage:
        executor = GraphExecutor()
        result = executor.run(
            company_identifiers=["acme-corp", "beta-inc"],
            config={"max_retries": 2},
        )
    """

    def __init__(self, checkpointer: Any | None = None) -> None:
        """Initialize the executor and compile the research graph.

        Args:
            checkpointer: Optional LangGraph checkpointer (e.g. MemorySaver or
                SqliteSaver from ``build_checkpointer()``). When provided, graph
                execution is resumable from the last successful node after a crash
                (STORY-079). Enables human-in-the-loop interruption as well.
        """
        self._checkpointer = checkpointer
        self._compiled_graph = compile_research_graph(checkpointer=checkpointer, isolate_errors=True)
        logger.info("[GraphExecutor] Research graph compiled successfully")

    def run(
        self,
        company_identifiers: list[str],
        config: dict[str, Any] | None = None,
        run_id: str | None = None,
        confidence_threshold: float | None = None,
    ) -> dict[str, Any]:
        """Execute the research pipeline for the given companies.

        Creates a new RequestCache per run to isolate deduplication scope.
        The cache is passed via LangGraph's configurable config so nodes
        can access it via config["configurable"]["request_cache"].

        When a checkpointer is configured, the thread_id (= run_id) is passed
        in the LangGraph configurable so state is persisted after each node.
        A crashed run can be resumed by calling this method again with the same
        run_id — the graph will continue from the last successful checkpoint.

        Args:
            company_identifiers: List of company IDs to research.
            config: Optional runtime configuration (timeouts, max_retries).
            run_id: Optional run identifier. Auto-generated if not provided.
                    Must be stable across retries to enable checkpoint resume.
            confidence_threshold: Human-review confidence threshold (0.0–1.0).
                Overrides the value from Settings if provided.

        Returns:
            The final ResearchState dict after graph execution, OR the interrupt
            payload dict when the graph pauses awaiting analyst approval.
        """
        resolved_run_id = run_id or str(uuid.uuid4())
        request_cache = RequestCache()
        effective_threshold = _resolve_threshold(confidence_threshold)
        merged_config = {
            **(config or {}),
            "human_review_confidence_threshold": effective_threshold,
        }
        initial_state = _build_initial_state(company_identifiers, resolved_run_id, merged_config)
        lg_config: dict[str, Any] = {
            "configurable": {
                "request_cache": request_cache,
                "run_id": resolved_run_id,
                "thread_id": resolved_run_id,
            }
        }
        logger.info(
            "[GraphExecutor] Starting run run_id=%s companies=%d threshold=%.2f",
            resolved_run_id,
            len(company_identifiers),
            effective_threshold,
        )
        result = self._compiled_graph.invoke(initial_state, config=lg_config)
        cache_stats = request_cache.stats
        logger.info(
            "[GraphExecutor] Run complete run_id=%s cache_hits=%d cache_misses=%d errors=%d",
            resolved_run_id,
            cache_stats["hits"],
            cache_stats["misses"],
            len(result.get("data_collection_errors", [])) if isinstance(result, dict) else 0,
        )
        return result  # type: ignore[return-value]

    def resume_after_approval(self, run_id: str) -> dict[str, Any]:
        """Resume a graph that was paused at the human_review_gate interrupt.

        Called by the review API after an analyst approves a review entry.
        The graph continues execution from after the ``interrupt()`` call in
        ``_human_review_gate_node`` and proceeds to the analysis and export nodes.

        Args:
            run_id: The LangGraph thread_id (= research run identifier).

        Returns:
            The final ResearchState dict after graph completion.

        Raises:
            RuntimeError: If no checkpointer is configured — cannot resume
                          without a checkpoint store.
            ValueError:   If no checkpoint exists for the given run_id.
        """
        if self._checkpointer is None:
            raise RuntimeError(
                "[GraphExecutor] resume_after_approval requires a checkpointer. "
                "Create GraphExecutor with a MemorySaver or SqliteSaver."
            )
        lg_config: dict[str, Any] = {"configurable": {"thread_id": run_id}}
        logger.info("[GraphExecutor] Resuming run %s after human approval", run_id)
        result = self._compiled_graph.invoke(Command(resume="approved"), config=lg_config)
        logger.info("[GraphExecutor] Resumed run %s completed", run_id)
        return result  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Public entry point (stable interface for callers)
# ---------------------------------------------------------------------------

_DEFAULT_EXECUTOR: GraphExecutor | None = None


def _get_default_executor() -> GraphExecutor:
    """Return the singleton executor, creating it on first call.

    Initializes with a durable SqliteSaver checkpointer using the path from
    Settings.graph_checkpoint_db_path so that crashed graphs are automatically
    resumable. Falls back to no checkpointer if the sqlite package is missing.
    """
    global _DEFAULT_EXECUTOR
    if _DEFAULT_EXECUTOR is None:
        checkpointer: Any = None
        try:
            settings = Settings()
            checkpointer = build_checkpointer(settings.graph_checkpoint_db_path)
            logger.info(
                "[GraphExecutor] Singleton using SqliteSaver at %s",
                settings.graph_checkpoint_db_path,
            )
        except Exception as exc:
            logger.warning(
                "[GraphExecutor] Could not build SqliteSaver checkpointer (%s) — "
                "running without checkpoint resume support.",
                exc,
            )
        _DEFAULT_EXECUTOR = GraphExecutor(checkpointer=checkpointer)
    return _DEFAULT_EXECUTOR


def run_graph_research(
    company_identifiers: list[str],
    config: dict[str, Any] | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Execute the LangGraph research pipeline.

    This is the stable public interface for graph-based research.
    Callers switch from run_market_intelligence() to this function by
    changing the import — the signature is intentionally compatible.

    Args:
        company_identifiers: List of company IDs / names to research.
        config: Optional runtime configuration dict.
        run_id: Optional run identifier for tracing.

    Returns:
        Research result dict with keys: run_id, company_scores, market_analysis,
        export_path, export_status, data_collection_errors, completed_nodes.
    """
    executor = _get_default_executor()
    return executor.run(
        company_identifiers=company_identifiers,
        config=config,
        run_id=run_id,
    )
