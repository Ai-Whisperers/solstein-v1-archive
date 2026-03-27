"""LangGraph node: General web-profile scraping.

STORY-078: Implements the web_profile graph node using the real WebsiteAgent.

This node replaces the stub WebsiteAgent from additional_agents.py with a real
implementation. The WebsiteAgent performs SSRF-protected HTTP GET requests
to each company's website URL and extracts title, meta-description, AI signals,
and detected technology stack.

Input interface (fields read from ResearchState):
    - company_identifiers: list of company IDs / names to research
    - config: optional runtime config (keys: websites — dict[company_id, url])

Output interface (fields written to ResearchState):
    - raw_web_facts: list of per-company web fact dicts
    - data_collection_errors: list of error strings (appended, not overwritten)
    - completed_nodes: appends "web_profile"

Each fact dict schema:
    {
        company_id: str,
        url: str,
        title: str | None,
        description: str | None,
        ai_signals: list[str],
        tech_stack: list[str],
    }
"""

from __future__ import annotations

import asyncio
from typing import Any

from loguru import logger

from ..state import ResearchState


def web_profile_node(state: ResearchState, config: dict[str, Any] | None = None) -> dict[str, Any]:
    """General web-profile scraping node — calls the real WebsiteAgent.

    Reads: company_identifiers, config
    Writes: raw_web_facts, data_collection_errors, completed_nodes

    For each company, looks up the website URL in config["websites"] or
    state["config"]["websites"]. When no URL is known, the company is
    skipped with a coverage gap. When the URL is present, the WebsiteAgent
    performs a real HTTP GET request and extracts title, description, and
    AI/tech signals.

    Args:
        state: Current ResearchState dict.
        config: LangGraph config dict. May contain config["configurable"]["websites"]
                as a dict mapping company_id to website URL.

    Returns:
        Partial state dict with raw_web_facts, data_collection_errors,
        and completed_nodes.
    """
    company_identifiers: list[str] = state.get("company_identifiers") or []
    extra_config: dict[str, Any] = state.get("config") or {}
    lg_config = config or {}
    configurable: dict[str, Any] = lg_config.get("configurable") or {}

    # Caller may supply known website URLs via config
    known_websites: dict[str, str] = configurable.get("websites") or extra_config.get("websites") or {}

    raw_facts: list[dict[str, Any]] = []
    errors: list[str] = []

    if not company_identifiers:
        logger.warning("[web_profile] No company_identifiers in state — skipping")
        return {
            "raw_web_facts": raw_facts,
            "data_collection_errors": errors,
            "completed_nodes": ["web_profile"],
        }

    try:
        results = asyncio.run(_gather_all(company_identifiers, known_websites))
        raw_facts, errors = results
    except RuntimeError as exc:
        logger.error("[web_profile] Cannot run async agent in current context: %s", exc)
        errors.append(f"[web_profile] event loop conflict: {exc}")

    return {
        "raw_web_facts": raw_facts,
        "data_collection_errors": errors,
        "completed_nodes": ["web_profile"],
    }


async def _gather_all(
    company_identifiers: list[str],
    known_websites: dict[str, str],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Async helper: calls WebsiteAgent for each company that has a known URL."""
    from solstein.agents.website_agent import WebsiteAgent

    agent = WebsiteAgent()
    raw_facts: list[dict[str, Any]] = []
    errors: list[str] = []

    for company_id in company_identifiers:
        url = known_websites.get(company_id)
        if not url:
            msg = f"[web_profile] {company_id}: no website URL in config — skipping"
            errors.append(msg)
            logger.info(msg)
            continue

        context = {"website": url}
        try:
            result = await agent.gather(company_id, context)
            if result.success:
                fact = _extract_web_fact(company_id, url, result)
                raw_facts.append(fact)
                logger.debug("[web_profile] %s: scraped %s", company_id, url)
            else:
                msg = f"[web_profile] {company_id}: {result.error_message or 'unknown error'}"
                errors.append(msg)
                logger.warning(msg)
        except Exception as exc:
            msg = f"[web_profile] {company_id}: exception — {exc}"
            errors.append(msg)
            logger.error(msg)

    return raw_facts, errors


def _extract_web_fact(company_id: str, url: str, result: Any) -> dict[str, Any]:
    """Extract a standardised web fact dict from an AgentTaskResult."""
    title = None
    description = None
    ai_signals: list[str] = []
    tech_stack: list[str] = []

    for fact in result.extracted_facts:
        ft = fact.fact_type
        val = fact.value
        if ft == "website_title":
            title = str(val) if val else None
        elif ft == "website_description":
            description = str(val) if val else None
        elif ft == "ai_signal":
            if val:
                ai_signals.append(str(val))
        elif ft == "tech_stack_item":
            if val:
                tech_stack.append(str(val))

    # Enrich from raw_sources metadata when extracted_facts are sparse
    for raw_source in result.raw_sources:
        meta = getattr(raw_source, "metadata", {}) or {}
        raw_content = getattr(raw_source, "raw_content", {}) or {}
        if not title and raw_content.get("title"):
            title = str(raw_content["title"])
        if not description and raw_content.get("meta_description"):
            description = str(raw_content["meta_description"])
        meta_facts: list[dict[str, Any]] = meta.get("facts") or []
        for f in meta_facts:
            ftype = f.get("type", "")
            fval = f.get("value", "")
            if ftype == "ai_signal" and fval and fval not in ai_signals:
                ai_signals.append(str(fval))
            elif ftype == "tech_stack_item" and fval and fval not in tech_stack:
                tech_stack.append(str(fval))

    return {
        "company_id": company_id,
        "url": url,
        "title": title,
        "description": description,
        "ai_signals": ai_signals,
        "tech_stack": tech_stack,
    }
