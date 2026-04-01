"""Typed state definition for the LangGraph research pipeline.

STORY-076: ResearchState is the single authoritative data container
passed between all nodes in the research graph. Every inter-node data
transfer goes through this state — no implicit side-channels.

Field ownership by stage:
    dispatch        → writes: run_id, company_identifiers, config, errors
    github_data     → writes: raw_github_facts
    companies_house → writes: raw_companies_house_facts
    news_search     → writes: raw_news_facts
    sec_filings     → writes: raw_sec_facts
    web_profile     → writes: raw_web_facts
    conflict_resolution → writes: conflict_flags, resolved_facts
    scoring         → writes: confidence_scores, company_score
    analysis        → writes: market_analysis
    export          → writes: export_path, export_status

Nodes read from any field they need; they must only write to their
owned fields to maintain clear data lineage.
"""

from __future__ import annotations

from typing import Annotated, Any

from typing_extensions import TypedDict


def _merge_list(a: list[Any], b: list[Any]) -> list[Any]:
    """Reducer for list fields: concatenate on fan-in."""
    return a + b


def _merge_errors(a: list[str], b: list[str]) -> list[str]:
    """Reducer for error lists: concatenate, preserving all errors."""
    return a + b


class ResearchState(TypedDict):
    """All data passed between LangGraph research pipeline nodes.

    This is the single source of truth for the research graph execution.
    STORY-077 (coordinator migration), STORY-078 (real agent nodes), and
    STORY-079 (checkpointing) all read and write through this state.

    Annotated fields use reducers for parallel fan-in merging:
    - list fields concatenate results from parallel data-collection nodes
    - dict fields merge (last-writer wins per key) from parallel nodes
    - error lists concatenate so all errors from all nodes are visible
    """

    # -------------------------------------------------------------------------
    # Dispatch node output — set once at job start, read-only thereafter
    # -------------------------------------------------------------------------

    run_id: str
    """Unique identifier for this research run (UUID4)."""

    company_identifiers: list[str]
    """List of company IDs / names to research in this run."""

    config: dict[str, Any]
    """Runtime configuration snapshot (scrape limits, timeouts, source flags)."""

    # -------------------------------------------------------------------------
    # Data collection nodes (parallel fan-out) — each writes its own namespace
    # -------------------------------------------------------------------------

    raw_github_facts: Annotated[list[dict[str, Any]], _merge_list]
    """Raw facts collected by the GitHub data-collection node.

    Each entry: {company_id, stars, forks, language, topics, last_commit_at, repo_url}
    Written by: github_data node.
    """

    raw_companies_house_facts: Annotated[list[dict[str, Any]], _merge_list]
    """Raw facts collected by the Companies House filing node.

    Each entry: {company_id, registered_name, company_number, filing_date,
                 directors, sic_codes, accounts_made_up_to}
    Written by: companies_house node.
    """

    raw_news_facts: Annotated[list[dict[str, Any]], _merge_list]
    """Raw facts collected by the news / web-search node.

    Each entry: {company_id, headline, url, published_at, sentiment, snippet}
    Written by: news_search node.
    """

    raw_sec_facts: Annotated[list[dict[str, Any]], _merge_list]
    """Raw facts collected by the SEC EDGAR filing node.

    Each entry: {company_id, form_type, period_of_report, revenue, net_income,
                 employees, filing_url}
    Written by: sec_filings node.
    """

    raw_web_facts: Annotated[list[dict[str, Any]], _merge_list]
    """Raw facts collected by the general web-profile scraping node.

    Each entry: {company_id, url, title, description, ai_signals, tech_stack}
    Written by: web_profile node.
    """

    data_collection_errors: Annotated[list[str], _merge_errors]
    """Structured error messages from data-collection nodes.

    Format: "[node_name] company_id: error description"
    All nodes append to this list — errors do not block fan-in.
    """

    # -------------------------------------------------------------------------
    # Conflict resolution node (fan-in sync point)
    # -------------------------------------------------------------------------

    conflict_flags: list[dict[str, Any]]
    """Contradiction flags raised during conflict resolution.

    Each entry: {company_id, field, value_a, source_a, value_b, source_b,
                 resolution, confidence_delta}
    Written by: conflict_resolution node after receiving all raw_* facts.
    """

    resolved_facts: dict[str, dict[str, Any]]
    """Per-company resolved facts after conflict resolution.

    Structure: {company_id: {field: {value, source_url, confidence, lineage}}}
    Written by: conflict_resolution node. Read by scoring node.
    """

    # -------------------------------------------------------------------------
    # Scoring node
    # -------------------------------------------------------------------------

    confidence_scores: dict[str, float]
    """Per-company confidence scores in [0.0, 1.0].

    Structure: {company_id: confidence_score}
    Written by: scoring node.
    """

    company_scores: dict[str, dict[str, Any]]
    """Per-company composite scores and classifications.

    Structure: {company_id: {composite_score, tier, threat_level,
                              ai_maturity, growth_score, funding_score}}
    Written by: scoring node.
    """

    # -------------------------------------------------------------------------
    # Analysis node
    # -------------------------------------------------------------------------

    market_analysis: dict[str, Any]
    """Aggregated market analysis across all researched companies.

    Keys: top_companies, market_trends, competitive_landscape,
          ai_adoption_index, sector_breakdown, data_quality_summary
    Written by: analysis node.
    """

    # -------------------------------------------------------------------------
    # Export node
    # -------------------------------------------------------------------------

    export_path: str
    """Absolute path to the generated export artifact (Excel/JSON).

    Empty string if export has not yet run or failed.
    Written by: export node.
    """

    export_status: str
    """Status of the export step: 'pending', 'success', 'failed'.

    Written by: export node.
    """

    export_errors: list[str]
    """Error messages from the export node, if any.

    Written by: export node.
    """

    # -------------------------------------------------------------------------
    # Pipeline-level metadata
    # -------------------------------------------------------------------------

    completed_nodes: Annotated[list[str], _merge_list]
    """Names of nodes that have successfully completed.

    Used for checkpointing and human-in-the-loop inspection.
    Each node appends its name on successful completion.
    """

    pipeline_errors: Annotated[list[str], _merge_errors]
    """Critical pipeline-level errors that may halt execution.

    Format: "[node_name] error description"
    Distinct from data_collection_errors — these affect pipeline control flow.
    """

    human_review_required: bool
    """Set to True by any node that detects low confidence or high conflict.

    When True, the pipeline pauses at the human_review interrupt point
    (STORY-079) before proceeding to export.
    """
