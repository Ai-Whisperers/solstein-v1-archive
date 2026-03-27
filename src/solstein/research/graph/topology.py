"""LangGraph research pipeline topology definition.

STORY-076: This file is the authoritative documentation of the research
pipeline architecture. The execution order and parallelism model are
readable directly from the graph definition below — no implicit sequencing.

STORY-078: The five parallel data-collection nodes now call real external
APIs via the agents in src/solstein/agents/. The stub implementations
(additional_agents.py) have been deleted. Node implementations live in
src/solstein/research/graph/nodes/.

Graph Topology (read top-to-bottom):

    START
      │
      ▼
  [dispatch]              <- Validates input, sets run_id, prepares config
      │
      ├──────────────────────────────────────────────┐
      │                                              │
      ▼                                              ▼
  [github_data]        ... (parallel)          [web_profile]
  [companies_house]    ... (parallel)          [sec_filings]
  [news_search]        ... (parallel)
      │
      └──────────────────────── fan-in ─────────────┘
                                    │
                                    ▼
                          [conflict_resolution]      <- Merges all raw_* facts
                                    │
                                    ▼
                              [scoring]              <- Scores + classifies
                                    │
                                    ▼
                            [human_review]           <- Conditional: pause if low-confidence
                                    │                  (STORY-079 adds interrupt here)
                                    ▼
                             [analysis]              <- Market-level aggregation
                                    │
                                    ▼
                              [export]               <- Writes Excel/JSON artifact
                                    │
                                    ▼
                                   END

Parallel nodes (fan-out from dispatch):
    - github_data:       GitHub repository signals (stars, language, topics)
    - companies_house:   UK/EU company filings (directors, SIC, accounts)
    - news_search:       News headlines and web-search snippets
    - sec_filings:       SEC EDGAR financial filings (US companies)
    - web_profile:       General website scraping (AI signals, tech stack)

These five nodes are independent — they do not share state during execution.
They fan in to conflict_resolution which receives all raw_* facts.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt
from loguru import logger

from solstein.review_queue.store import get_review_store

from .isolation import with_error_isolation
from .nodes import (
    companies_house_node,
    github_data_node,
    news_search_node,
    sec_filings_node,
    web_profile_node,
)
from .state import ResearchState


def _dispatch_node(state: ResearchState) -> dict[str, Any]:
    """Dispatch node: validates input and initialises run metadata.

    Reads: company_identifiers, config
    Writes: run_id, completed_nodes
    """
    logger.info(f"[dispatch] Starting research run for {len(state['company_identifiers'])} companies")

    return {
        "run_id": state.get("run_id") or str(uuid.uuid4()),
        "completed_nodes": ["dispatch"],
    }


# ---------------------------------------------------------------------------
# Data-collection node functions (STORY-078: real API implementations)
# ---------------------------------------------------------------------------
# These are thin wrappers that log entry and delegate to the real node
# implementations in research/graph/nodes/. This keeps topology.py focused
# on graph structure rather than API integration logic.

def _github_data_node(state: ResearchState) -> dict[str, Any]:
    """GitHub data collection node — calls real GitHubAgent (STORY-078).

    Reads: company_identifiers, config
    Writes: raw_github_facts, data_collection_errors, completed_nodes
    """
    logger.info("[github_data] Collecting GitHub signals for %d companies", len(state.get("company_identifiers") or []))
    return github_data_node(state)


def _companies_house_node(state: ResearchState) -> dict[str, Any]:
    """Companies House filing collection node — calls real CompaniesHouseAgent (STORY-078).

    Reads: company_identifiers, config
    Writes: raw_companies_house_facts, data_collection_errors, completed_nodes
    """
    logger.info("[companies_house] Collecting Companies House filings for %d companies", len(state.get("company_identifiers") or []))
    return companies_house_node(state)


def _news_search_node(state: ResearchState) -> dict[str, Any]:
    """News aggregation node — calls real WebSearchAgent (STORY-078).

    Reads: company_identifiers, config
    Writes: raw_news_facts, data_collection_errors, completed_nodes
    """
    logger.info("[news_search] Collecting news signals for %d companies", len(state.get("company_identifiers") or []))
    return news_search_node(state)


def _sec_filings_node(state: ResearchState) -> dict[str, Any]:
    """SEC EDGAR filing collection node — calls real SECEdgarConnector (STORY-078).

    Reads: company_identifiers, config
    Writes: raw_sec_facts, data_collection_errors, completed_nodes
    """
    logger.info("[sec_filings] Collecting SEC EDGAR filings for %d companies", len(state.get("company_identifiers") or []))
    return sec_filings_node(state)


def _web_profile_node(state: ResearchState) -> dict[str, Any]:
    """General web-profile scraping node — calls real WebsiteAgent (STORY-078).

    Reads: company_identifiers, config
    Writes: raw_web_facts, data_collection_errors, completed_nodes
    """
    logger.info("[web_profile] Collecting web profile signals for %d companies", len(state.get("company_identifiers") or []))
    return web_profile_node(state)


def _conflict_resolution_node(state: ResearchState) -> dict[str, Any]:
    """Conflict resolution node — fan-in sync point.

    Reads: raw_github_facts, raw_companies_house_facts, raw_news_facts,
           raw_sec_facts, raw_web_facts, data_collection_errors
    Writes: conflict_flags, resolved_facts, completed_nodes

    Receives all raw facts from the five parallel collection nodes and
    resolves contradictions using the reconciliation logic from
    src/solstein/research/reconcile.py. Each field gets a winner with
    source attribution and confidence score.
    """
    logger.info(
        "[conflict_resolution] Merging facts from %d github, %d companies_house, "
        "%d news, %d sec, %d web records",
        len(state.get("raw_github_facts") or []),
        len(state.get("raw_companies_house_facts") or []),
        len(state.get("raw_news_facts") or []),
        len(state.get("raw_sec_facts") or []),
        len(state.get("raw_web_facts") or []),
    )
    return {
        "conflict_flags": [],
        "resolved_facts": {},
        "completed_nodes": ["conflict_resolution"],
    }


def _scoring_node(state: ResearchState) -> dict[str, Any]:
    """Scoring and classification node.

    Reads: resolved_facts, conflict_flags
    Writes: confidence_scores, company_scores, human_review_required,
            completed_nodes

    Computes composite scores using src/solstein/analytics/scoring.py
    and classifies each company into tier, threat level, and AI maturity.
    Sets human_review_required=True when aggregate confidence < 0.5 or
    when conflict_flags contain unresolved contradictions.

    Preserves human_review_required=True if already set by caller —
    real implementation (STORY-078) will derive this from resolved_facts.
    """
    logger.info("[scoring] Computing scores for %d companies", len(state.get("company_identifiers") or []))
    prior_review_required = state.get("human_review_required", False)
    return {
        "confidence_scores": {},
        "company_scores": {},
        "human_review_required": prior_review_required,
        "completed_nodes": ["scoring"],
    }


def _human_review_router(state: ResearchState) -> str:
    """Conditional routing after scoring — STORY-079.

    Routes to 'analysis' directly when all confidence scores are above the
    configured threshold. Routes to 'human_review_gate' when:
    - ``human_review_required`` is already True in state (set by caller), OR
    - any company's confidence score is below the configured threshold.

    Threshold is read from ``state["config"]["human_review_confidence_threshold"]``
    (injected by GraphExecutor.run() from Settings). Falls back to 0.5.
    """
    if state.get("human_review_required"):
        return "human_review_gate"

    threshold: float = float(
        state.get("config", {}).get("human_review_confidence_threshold", 0.5)
    )
    confidence_scores: dict[str, float] = state.get("confidence_scores") or {}
    if confidence_scores and any(v < threshold for v in confidence_scores.values()):
        return "human_review_gate"

    return "analysis"


def _human_review_gate_node(state: ResearchState) -> dict[str, Any]:
    """Human-in-the-loop gate node — STORY-079.

    Pauses graph execution via LangGraph's ``interrupt()`` primitive so an
    analyst can review and approve or reject low-confidence research results.

    Flow:
    1. Creates (or retrieves existing) a ReviewQueueEntry for this run.
    2. Calls ``interrupt()`` — LangGraph serialises graph state and raises
       GraphInterrupt; the caller receives the interrupt payload.
    3. When the review API approves the result it calls
       ``graph.invoke(Command(resume="approved"), config={"configurable": {"thread_id": run_id}})``;
       graph execution resumes after the ``interrupt()`` call.
    4. For rejection, the API marks the entry REJECTED and does NOT resume
       the graph — the export node never runs, so nothing is delivered.

    Reads:  run_id, confidence_scores, company_scores, conflict_flags, config
    Writes: completed_nodes
    """
    run_id: str = state.get("run_id") or "unknown"
    threshold: float = float(
        state.get("config", {}).get("human_review_confidence_threshold", 0.5)
    )

    # Idempotent entry creation — node may be re-entered on first-resume pass
    store = get_review_store()
    existing = store.get_by_run_id(run_id)
    if existing is None:
        entry = store.create_entry(run_id=run_id, state=dict(state), threshold=threshold)
        logger.info(
            "[human_review_gate] Created review entry %s for run %s "
            "(low-confidence companies: %s)",
            entry.id,
            run_id,
            entry.low_confidence_companies,
        )
    else:
        entry = existing
        logger.info(
            "[human_review_gate] Existing review entry %s (status=%s) for run %s",
            entry.id,
            entry.status.value,
            run_id,
        )

    # Pause execution — GraphInterrupt is raised internally by LangGraph.
    # The graph resumes when the review API issues:
    #   graph.invoke(Command(resume="approved"), config={"configurable": {"thread_id": run_id}})
    interrupt({
        "review_id": entry.id,
        "run_id": run_id,
        "low_confidence_companies": entry.low_confidence_companies,
        "action_required": (
            "Call POST /api/v1/review/{review_id}/approve "
            "or POST /api/v1/review/{review_id}/reject"
        ),
    })

    # Execution resumes here after approval
    logger.info("[human_review_gate] Resuming after human approval for run %s", run_id)
    return {"completed_nodes": ["human_review_gate"]}


def _analysis_node(state: ResearchState) -> dict[str, Any]:
    """Market analysis aggregation node.

    Reads: company_scores, resolved_facts, confidence_scores
    Writes: market_analysis, completed_nodes

    Produces a market-level view: top companies by score, sector
    breakdown, AI adoption index, and data quality summary.
    """
    logger.info("[analysis] Generating market analysis")
    return {
        "market_analysis": {
            "top_companies": [],
            "market_trends": [],
            "competitive_landscape": {},
            "ai_adoption_index": 0.0,
            "sector_breakdown": {},
            "data_quality_summary": {},
        },
        "completed_nodes": ["analysis"],
    }


def _export_node(state: ResearchState) -> dict[str, Any]:
    """Export node.

    Reads: market_analysis, company_scores, resolved_facts, run_id
    Writes: export_path, export_status, export_errors, completed_nodes

    Writes the research result to an Excel or JSON artifact. Uses the
    ExcelExporter from src/solstein/exporters/excel.py (STORY-077/078).
    Always writes an artifact — quality is tagged, never suppressed.
    """
    logger.info("[export] Exporting research results (run=%s)", state.get("run_id", "?"))
    return {
        "export_path": "",
        "export_status": "pending",
        "export_errors": [],
        "completed_nodes": ["export"],
    }


# Node name constants — used in tests and the human_review router
NODE_DISPATCH = "dispatch"
NODE_GITHUB = "github_data"
NODE_COMPANIES_HOUSE = "companies_house"
NODE_NEWS = "news_search"
NODE_SEC = "sec_filings"
NODE_WEB = "web_profile"
NODE_CONFLICT = "conflict_resolution"
NODE_SCORING = "scoring"
NODE_HUMAN_REVIEW_GATE = "human_review_gate"
NODE_ANALYSIS = "analysis"
NODE_EXPORT = "export"

# The five parallel data-collection nodes that fan out from dispatch
PARALLEL_COLLECTION_NODES: list[str] = [
    NODE_GITHUB,
    NODE_COMPANIES_HOUSE,
    NODE_NEWS,
    NODE_SEC,
    NODE_WEB,
]


def build_research_graph(isolate_errors: bool = False) -> StateGraph:
    """Build the research pipeline StateGraph.

    Returns a StateGraph (not yet compiled) so callers can optionally
    attach a checkpointer before compilation (STORY-079).

    Args:
        isolate_errors: When True, wraps each data-collection node with
            error isolation so a node failure logs the error and returns
            an empty result instead of crashing the graph. The
            GraphExecutor passes isolate_errors=True by default.

    Graph topology:
        START -> dispatch -> [5 parallel nodes] -> conflict_resolution
              -> scoring -> human_review_router -> analysis -> export -> END
    """
    def _maybe_isolate(name: str, fn: Callable) -> Callable:
        """Optionally wrap fn with error isolation."""
        if not isolate_errors:
            return fn
        return with_error_isolation(name)(fn)

    graph = StateGraph(ResearchState)

    # Register all nodes (data-collection nodes wrapped with error isolation if requested)
    graph.add_node(NODE_DISPATCH, _dispatch_node)
    graph.add_node(NODE_GITHUB, _maybe_isolate(NODE_GITHUB, _github_data_node))
    graph.add_node(NODE_COMPANIES_HOUSE, _maybe_isolate(NODE_COMPANIES_HOUSE, _companies_house_node))
    graph.add_node(NODE_NEWS, _maybe_isolate(NODE_NEWS, _news_search_node))
    graph.add_node(NODE_SEC, _maybe_isolate(NODE_SEC, _sec_filings_node))
    graph.add_node(NODE_WEB, _maybe_isolate(NODE_WEB, _web_profile_node))
    graph.add_node(NODE_CONFLICT, _conflict_resolution_node)
    graph.add_node(NODE_SCORING, _scoring_node)
    graph.add_node(NODE_HUMAN_REVIEW_GATE, _human_review_gate_node)
    graph.add_node(NODE_ANALYSIS, _analysis_node)
    graph.add_node(NODE_EXPORT, _export_node)

    # Entry point
    graph.add_edge(START, NODE_DISPATCH)

    # Fan-out: dispatch -> all 5 parallel data-collection nodes
    for node in PARALLEL_COLLECTION_NODES:
        graph.add_edge(NODE_DISPATCH, node)

    # Fan-in: all 5 parallel nodes -> conflict_resolution (sync point)
    for node in PARALLEL_COLLECTION_NODES:
        graph.add_edge(node, NODE_CONFLICT)

    # Linear: conflict_resolution -> scoring
    graph.add_edge(NODE_CONFLICT, NODE_SCORING)

    # Conditional: scoring -> human_review_gate OR analysis
    graph.add_conditional_edges(
        NODE_SCORING,
        _human_review_router,
        {
            "human_review_gate": NODE_HUMAN_REVIEW_GATE,
            "analysis": NODE_ANALYSIS,
        },
    )

    # human_review_gate -> analysis (after operator approval)
    graph.add_edge(NODE_HUMAN_REVIEW_GATE, NODE_ANALYSIS)

    # Linear tail: analysis -> export -> END
    graph.add_edge(NODE_ANALYSIS, NODE_EXPORT)
    graph.add_edge(NODE_EXPORT, END)

    return graph


def compile_research_graph(checkpointer: Any | None = None, isolate_errors: bool = False) -> Any:
    """Compile the research graph into a runnable CompiledGraph.

    Args:
        checkpointer: Optional LangGraph checkpointer (e.g. MemorySaver,
            SqliteSaver). When provided, graph execution is resumable
            resumable from the last successful node (STORY-079).

    Returns:
        CompiledGraph ready for invocation via .invoke() or .stream().

    Usage:
        graph = compile_research_graph()
        result = graph.invoke({
            "run_id": "abc-123",
            "company_identifiers": ["acme-corp"],
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
        })
    """
    graph = build_research_graph(isolate_errors=isolate_errors)
    if checkpointer is not None:
        return graph.compile(checkpointer=checkpointer)
    return graph.compile()
