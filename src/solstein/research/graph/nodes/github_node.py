"""LangGraph node: GitHub data collection.

STORY-078: Implements the github_data graph node using the real GitHubAgent.

Input interface (fields read from ResearchState):
    - company_identifiers: list of company IDs / names to research
    - config: optional runtime config (keys: known_github_org)

Output interface (fields written to ResearchState):
    - raw_github_facts: list of per-company GitHub fact dicts
    - data_collection_errors: list of error strings (appended, not overwritten)
    - completed_nodes: appends "github_data"

Each fact dict schema:
    {
        company_id: str,
        stars: int,
        forks: int,
        language: str | None,
        topics: list[str],
        last_commit_at: str | None,   # ISO-8601
        repo_url: str,
        org: str,
        repo_count: int,
    }
"""

from __future__ import annotations

import asyncio
from typing import Any

from loguru import logger

from ..state import ResearchState

# Maps fact_type → (field_name, converter).
# Using a dict dispatch eliminates deep elif chains in _extract_github_fact.
_GITHUB_FACT_MAP: dict[str, tuple[str, Any]] = {
    "github_stars": ("stars", lambda v: int(v) if v is not None else 0),
    "github_forks": ("forks", lambda v: int(v) if v is not None else 0),
    "primary_language": ("language", lambda v: str(v) if v else None),
    "github_topics": ("topics", lambda v: v if isinstance(v, list) else []),
    "last_commit_date": ("last_commit_at", lambda v: str(v) if v else None),
    "github_url": ("repo_url", lambda v: str(v) if v else ""),
    "github_org": ("org", lambda v: str(v) if v else ""),
    "repo_count": ("repo_count", lambda v: int(v) if v is not None else 0),
}


def github_data_node(state: ResearchState, config: dict[str, Any] | None = None) -> dict[str, Any]:
    """GitHub data collection node — calls the real GitHub API via GitHubAgent.

    Reads: company_identifiers, config
    Writes: raw_github_facts, data_collection_errors, completed_nodes

    Uses asyncio.run() to bridge synchronous LangGraph execution with the
    async GitHubAgent. Requires no running event loop in the calling context.

    Args:
        state: Current ResearchState dict.
        config: LangGraph config dict (may contain request_cache under
                config["configurable"]["request_cache"]).

    Returns:
        Partial state dict with raw_github_facts, data_collection_errors,
        and completed_nodes.
    """
    company_identifiers: list[str] = state.get("company_identifiers") or []
    extra_config: dict[str, Any] = state.get("config") or {}

    raw_facts: list[dict[str, Any]] = []
    errors: list[str] = []

    if not company_identifiers:
        logger.warning("[github_data] No company_identifiers in state — skipping")
        return {
            "raw_github_facts": raw_facts,
            "data_collection_errors": errors,
            "completed_nodes": ["github_data"],
        }

    try:
        results = asyncio.run(_gather_all(company_identifiers, extra_config))
        raw_facts, errors = results
    except RuntimeError as exc:
        # Already inside a running event loop (e.g. Jupyter); fall back to sync stub
        logger.error("[github_data] Cannot run async agent in current context: %s", exc)
        errors.append(f"[github_data] event loop conflict: {exc}")

    return {
        "raw_github_facts": raw_facts,
        "data_collection_errors": errors,
        "completed_nodes": ["github_data"],
    }


async def _gather_all(
    company_identifiers: list[str],
    extra_config: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Async helper: calls GitHubAgent for each company."""
    from solstein.agents.github_agent import GitHubAgent

    agent = GitHubAgent()
    raw_facts: list[dict[str, Any]] = []
    errors: list[str] = []

    for company_id in company_identifiers:
        context = {"known_github_org": extra_config.get(f"github_org_{company_id}")}
        try:
            result = await agent.gather(company_id, context)
            if result.success:
                fact = _extract_github_fact(company_id, result)
                raw_facts.append(fact)
                logger.debug("[github_data] %s: collected %d facts", company_id, len(result.extracted_facts))
            else:
                msg = f"[github_data] {company_id}: {result.error_message or 'unknown error'}"
                errors.append(msg)
                logger.warning(msg)
        except Exception as exc:
            msg = f"[github_data] {company_id}: exception — {exc}"
            errors.append(msg)
            logger.error(msg)

    return raw_facts, errors


def _extract_github_fact(company_id: str, result: Any) -> dict[str, Any]:
    """Extract a standardised fact dict from an AgentTaskResult.

    Uses _GITHUB_FACT_MAP for O(1) dispatch to avoid deep elif nesting.
    """
    fields: dict[str, Any] = {
        "company_id": company_id,
        "stars": 0,
        "forks": 0,
        "language": None,
        "topics": [],
        "last_commit_at": None,
        "repo_url": "",
        "org": "",
        "repo_count": 0,
    }

    for fact in result.extracted_facts:
        entry = _GITHUB_FACT_MAP.get(fact.fact_type)
        if entry:
            field_name, converter = entry
            fields[field_name] = converter(fact.value)

    return fields
