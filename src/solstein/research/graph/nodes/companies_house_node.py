"""LangGraph node: Companies House filing collection.

STORY-078: Implements the companies_house graph node using the real
CompaniesHouseAgent (UK Companies House REST API).

Input interface (fields read from ResearchState):
    - company_identifiers: list of company IDs / names to research
    - config: optional runtime config

Output interface (fields written to ResearchState):
    - raw_companies_house_facts: list of per-company filing fact dicts
    - data_collection_errors: list of error strings (appended, not overwritten)
    - completed_nodes: appends "companies_house"

Each fact dict schema:
    {
        company_id: str,
        registered_name: str | None,
        company_number: str | None,
        filing_date: str | None,       # ISO-8601 date
        directors: list[str],
        sic_codes: list[str],
        accounts_made_up_to: str | None,
        company_status: str | None,
    }
"""

from __future__ import annotations

import asyncio
from typing import Any

from loguru import logger

from ..state import ResearchState

# Maps fact_type → (field_name, converter).
# Using a dict dispatch eliminates deep elif chains in _extract_companies_house_fact.
_CH_FACT_MAP: dict[str, tuple[str, Any]] = {
    "registered_name": ("registered_name", lambda v: str(v) if v else None),
    "company_number": ("company_number", lambda v: str(v) if v else None),
    "filing_date": ("filing_date", lambda v: str(v) if v else None),
    "directors": ("directors", lambda v: v if isinstance(v, list) else []),
    "sic_codes": ("sic_codes", lambda v: v if isinstance(v, list) else []),
    "accounts_made_up_to": ("accounts_made_up_to", lambda v: str(v) if v else None),
    "company_status": ("company_status", lambda v: str(v) if v else None),
}


def companies_house_node(state: ResearchState, config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Companies House filing collection node.

    Reads: company_identifiers, config
    Writes: raw_companies_house_facts, data_collection_errors, completed_nodes

    Calls the real Companies House API via CompaniesHouseAgent. Only collects
    data for companies found in UK Companies House — non-UK companies will
    produce a coverage gap (logged as data_collection_errors, not pipeline errors).

    Args:
        state: Current ResearchState dict.
        config: LangGraph config dict.

    Returns:
        Partial state dict with raw_companies_house_facts, data_collection_errors,
        and completed_nodes.
    """
    company_identifiers: list[str] = state.get("company_identifiers") or []
    raw_facts: list[dict[str, Any]] = []
    errors: list[str] = []

    if not company_identifiers:
        logger.warning("[companies_house] No company_identifiers in state — skipping")
        return {
            "raw_companies_house_facts": raw_facts,
            "data_collection_errors": errors,
            "completed_nodes": ["companies_house"],
        }

    try:
        results = asyncio.run(_gather_all(company_identifiers))
        raw_facts, errors = results
    except RuntimeError as exc:
        logger.error("[companies_house] Cannot run async agent in current context: %s", exc)
        errors.append(f"[companies_house] event loop conflict: {exc}")

    return {
        "raw_companies_house_facts": raw_facts,
        "data_collection_errors": errors,
        "completed_nodes": ["companies_house"],
    }


async def _gather_all(
    company_identifiers: list[str],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Async helper: calls CompaniesHouseAgent for each company."""
    from solstein.agents.companies_house_agent import CompaniesHouseAgent

    agent = CompaniesHouseAgent()
    raw_facts: list[dict[str, Any]] = []
    errors: list[str] = []

    for company_id in company_identifiers:
        try:
            result = await agent.gather(company_id, {})
            if result.success:
                fact = _extract_companies_house_fact(company_id, result)
                raw_facts.append(fact)
                logger.debug("[companies_house] %s: collected filing data", company_id)
            else:
                msg = f"[companies_house] {company_id}: {result.error_message or 'unknown error'}"
                errors.append(msg)
                logger.warning(msg)
        except Exception as exc:
            msg = f"[companies_house] {company_id}: exception — {exc}"
            errors.append(msg)
            logger.error(msg)

    return raw_facts, errors


def _extract_companies_house_fact(company_id: str, result: Any) -> dict[str, Any]:
    """Extract a standardised fact dict from an AgentTaskResult.

    Uses _CH_FACT_MAP for O(1) dispatch to avoid deep elif nesting.
    """
    fields: dict[str, Any] = {
        "company_id": company_id,
        "registered_name": None,
        "company_number": None,
        "filing_date": None,
        "directors": [],
        "sic_codes": [],
        "accounts_made_up_to": None,
        "company_status": None,
    }

    for fact in result.extracted_facts:
        entry = _CH_FACT_MAP.get(fact.fact_type)
        if entry:
            field_name, converter = entry
            fields[field_name] = converter(fact.value)

    # Fall back to raw_sources metadata when extracted_facts are sparse
    for raw_source in result.raw_sources:
        meta = getattr(raw_source, "metadata", {}) or {}
        _enrich_ch_fields_from_meta(fields, meta)

    return fields


def _enrich_ch_fields_from_meta(fields: dict[str, Any], meta: dict[str, Any]) -> None:
    """Enrich Companies House fields from raw_source metadata in-place."""
    if not fields["registered_name"] and meta.get("company_name"):
        fields["registered_name"] = str(meta["company_name"])
    if not fields["company_number"] and meta.get("company_number"):
        fields["company_number"] = str(meta["company_number"])
    if not fields["company_status"] and meta.get("company_status"):
        fields["company_status"] = str(meta["company_status"])
    if not fields["directors"] and meta.get("officers"):
        fields["directors"] = [o.get("name", "") for o in meta.get("officers", [])][:10]
    if not fields["sic_codes"] and meta.get("sic_codes"):
        fields["sic_codes"] = meta["sic_codes"]
