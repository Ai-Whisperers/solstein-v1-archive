"""LangGraph node: News aggregation and web-search collection.

STORY-078: Implements the news_search graph node using the real WebSearchAgent
(Google Custom Search API).

This node replaces the stub NewsAgent from additional_agents.py with a real
implementation. The WebSearchAgent queries Google Custom Search for news
articles, press releases, and market intelligence about each company.

Input interface (fields read from ResearchState):
    - company_identifiers: list of company IDs / names to research
    - config: optional runtime config

Output interface (fields written to ResearchState):
    - raw_news_facts: list of per-company news fact dicts
    - data_collection_errors: list of error strings (appended, not overwritten)
    - completed_nodes: appends "news_search"

Each fact dict schema:
    {
        company_id: str,
        headline: str,
        url: str,
        published_at: str | None,    # ISO-8601 date
        sentiment: str | None,       # "positive", "neutral", "negative"
        snippet: str | None,
        source_name: str | None,
    }
"""

from __future__ import annotations

import asyncio
from typing import Any

from loguru import logger

from ..state import ResearchState


def news_search_node(state: ResearchState, config: dict[str, Any] | None = None) -> dict[str, Any]:
    """News aggregation node — calls the real Google Custom Search API via WebSearchAgent.

    Reads: company_identifiers, config
    Writes: raw_news_facts, data_collection_errors, completed_nodes

    When the Google Custom Search API is not configured (missing api_key or
    search_engine_id), each company produces a coverage gap recorded in
    data_collection_errors. This is not a pipeline error — the graph continues.

    Args:
        state: Current ResearchState dict.
        config: LangGraph config dict.

    Returns:
        Partial state dict with raw_news_facts, data_collection_errors,
        and completed_nodes.
    """
    company_identifiers: list[str] = state.get("company_identifiers") or []
    raw_facts: list[dict[str, Any]] = []
    errors: list[str] = []

    if not company_identifiers:
        logger.warning("[news_search] No company_identifiers in state — skipping")
        return {
            "raw_news_facts": raw_facts,
            "data_collection_errors": errors,
            "completed_nodes": ["news_search"],
        }

    try:
        results = asyncio.run(_gather_all(company_identifiers))
        raw_facts, errors = results
    except RuntimeError as exc:
        logger.error("[news_search] Cannot run async agent in current context: %s", exc)
        errors.append(f"[news_search] event loop conflict: {exc}")

    return {
        "raw_news_facts": raw_facts,
        "data_collection_errors": errors,
        "completed_nodes": ["news_search"],
    }


async def _gather_all(
    company_identifiers: list[str],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Async helper: calls WebSearchAgent for each company.

    WebSearchAgent reads google_api_key from the environment; the Google
    Custom Search Engine ID must be passed separately. When either key is
    absent, the agent returns a graceful coverage gap rather than crashing.
    """
    from solstein.agents.web_search_agent import WebSearchAgent
    from solstein.config import get_settings

    settings = get_settings()
    # search_engine_id is not yet in Settings (see STORY-078 notes).
    # Pass google_api_key and leave search_engine_id to the caller to supply
    # via environment; the agent handles the unconfigured case gracefully.
    agent = WebSearchAgent(google_api_key=settings.google_api_key)

    raw_facts: list[dict[str, Any]] = []
    errors: list[str] = []

    for company_id in company_identifiers:
        try:
            result = await agent.gather(company_id, {})
            if result.success:
                facts = _extract_news_facts(company_id, result)
                raw_facts.extend(facts)
                logger.debug("[news_search] %s: collected %d news facts", company_id, len(facts))
            else:
                msg = f"[news_search] {company_id}: {result.error_message or 'unknown error'}"
                errors.append(msg)
                logger.warning(msg)
        except Exception as exc:
            msg = f"[news_search] {company_id}: exception — {exc}"
            errors.append(msg)
            logger.error(msg)

    return raw_facts, errors


def _extract_news_facts(company_id: str, result: Any) -> list[dict[str, Any]]:
    """Extract a list of standardised news fact dicts from an AgentTaskResult."""
    facts: list[dict[str, Any]] = []

    for fact in result.extracted_facts:
        ft = fact.fact_type
        val = fact.value
        if ft in {"news_headline", "press_mention", "search_result"}:
            entry: dict[str, Any] = {
                "company_id": company_id,
                "headline": str(val) if val else "",
                "url": "",
                "published_at": None,
                "sentiment": None,
                "snippet": None,
                "source_name": None,
            }
            # Enrich with metadata if available
            meta = getattr(fact, "metadata", {}) or {}
            if meta.get("url"):
                entry["url"] = str(meta["url"])
            if meta.get("published_at"):
                entry["published_at"] = str(meta["published_at"])
            if meta.get("sentiment"):
                entry["sentiment"] = str(meta["sentiment"])
            if meta.get("snippet"):
                entry["snippet"] = str(meta["snippet"])
            if meta.get("source"):
                entry["source_name"] = str(meta["source"])
            facts.append(entry)

    # If no structured facts, check raw_sources for search result metadata
    if not facts:
        for raw_source in result.raw_sources:
            meta = getattr(raw_source, "metadata", {}) or {}
            items = meta.get("items") or []
            for item in items[:10]:  # cap at 10 news items per company
                facts.append(
                    {
                        "company_id": company_id,
                        "headline": str(item.get("title", "")),
                        "url": str(item.get("link", "")),
                        "published_at": item.get("pagemap", {}).get("metatags", [{}])[0].get("article:published_time"),
                        "sentiment": None,
                        "snippet": str(item.get("snippet", "")),
                        "source_name": item.get("displayLink"),
                    }
                )

    return facts
