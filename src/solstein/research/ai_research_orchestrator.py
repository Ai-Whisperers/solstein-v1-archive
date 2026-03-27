"""
AI-powered autonomous research orchestration.

This module performs company research by combining an LLM planning/extraction
stage with web search and deterministic validation.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger

from .research_agents import (
    ContentExtractorAgent,
    DataValidatorAgent,
    ResearchPlannerAgent,
    WebSearchAgent,
)
from .research_types import (
    ExtractedData,
    ResearchPlan,
    ResearchReport,
    SearchResult,
    ValidationResult,
)
from .research_memory import (
    ResearchMemoryStore as _ResearchMemoryStore,
    is_report_stale as _is_report_stale,
    normalize_url as _normalize_url,
    score_completeness as _score_completeness,
)

# Orchestrator constants (module-level to reduce class body size)
_TARGET_FIELDS = [
    "website", "description", "industry", "headquarters", "founded_year",
    "employees", "revenue", "revenue_currency", "valuation", "funding_raised", "funding_rounds",
]

_ADAPTIVE_QUERY_BY_FIELD: dict[str, list[str]] = {
    "website": ["{company} official website", "{company} contact us"],
    "description": ["{company} company overview", "{company} about us"],
    "industry": ["{company} business model", "{company} services"],
    "headquarters": ["{company} headquarters location", "{company} address"],
    "founded_year": ["{company} founded year", "{company} company history"],
    "employees": ["{company} employee count", "{company} headcount"],
    "revenue": ["{company} annual report pdf", "{company} revenue 2025"],
    "revenue_currency": ["{company} revenue currency", "{company} annual report"],
    "valuation": ["{company} valuation", "{company} market cap"],
    "funding_raised": ["{company} funding rounds", "{company} raised capital"],
    "funding_rounds": ["{company} series funding", "{company} investors"],
}

_VOLATILE_FIELDS = frozenset({"employees", "revenue", "revenue_currency",
                              "valuation", "funding_raised", "funding_rounds"})


def _flatten_report_to_fields(report_dict: dict[str, Any]) -> dict[str, Any]:
    """Flatten a report's nested sections into target field values."""
    basic = report_dict.get("basic_info", {}) if isinstance(report_dict.get("basic_info"), dict) else {}
    financials = report_dict.get("financials", {}) if isinstance(report_dict.get("financials"), dict) else {}
    funding = report_dict.get("funding", {}) if isinstance(report_dict.get("funding"), dict) else {}
    return {
        "website": basic.get("website"),
        "description": basic.get("description"),
        "industry": basic.get("industry"),
        "headquarters": basic.get("headquarters"),
        "founded_year": basic.get("founded_year"),
        "employees": basic.get("employees"),
        "revenue": financials.get("revenue"),
        "revenue_currency": financials.get("revenue_currency"),
        "valuation": financials.get("valuation"),
        "funding_raised": funding.get("total_raised"),
        "funding_rounds": funding.get("rounds"),
    }


def _synthesize_validated_data(validated_data: list[dict[str, Any]]) -> dict[str, Any]:
    """Merge data from multiple sources, preferring higher-confidence values."""
    field_values: dict[str, list[dict[str, Any]]] = {}

    for item in validated_data:
        extraction = item["extraction"]
        confidence = item["confidence"]
        for f_name, value in extraction.data.items():
            if value is None:
                continue
            field_values.setdefault(f_name, []).append(
                {"value": value, "confidence": confidence, "source": extraction.source_url}
            )

    final_data: dict[str, Any] = {"_confidence": 0.0}
    total_confidence = 0.0
    field_count = 0

    for f_name, values in field_values.items():
        values.sort(key=lambda item: item["confidence"], reverse=True)
        best = values[0]
        final_data[f_name] = best["value"]
        total_confidence += best["confidence"]
        field_count += 1

    if field_count > 0:
        final_data["_confidence"] = total_confidence / field_count

    return final_data


def _missing_fields(final_data: dict[str, Any]) -> list[str]:
    """Return TARGET_FIELDS that are empty or missing in the data."""
    return [f for f in _TARGET_FIELDS if final_data.get(f) in (None, "", [], {})]


def _build_adaptive_queries(
    company_name: str, missing_fields: list[str], max_queries: int = 6,
) -> list[dict[str, str]]:
    """Build targeted search queries for missing fields."""
    seen: set[str] = set()
    queries: list[dict[str, str]] = []
    for field_name in missing_fields:
        templates = _ADAPTIVE_QUERY_BY_FIELD.get(field_name, [])
        for template in templates:
            query = template.format(company=company_name)
            if query in seen:
                continue
            seen.add(query)
            intent = "financials" if field_name in {"revenue", "revenue_currency", "valuation"} else "funding"
            if field_name in {"website", "description", "industry", "headquarters", "founded_year", "employees"}:
                intent = "website"
            queries.append({"query": query, "intent": intent})
            if len(queries) >= max_queries:
                return queries
    return queries


def _merge_report_with_previous(
    current: ResearchReport,
    previous: dict[str, Any],
) -> tuple[ResearchReport, int]:
    """Merge current report with previous data, carrying forward missing fields."""
    previous_fields = _flatten_report_to_fields(previous)
    previous_is_stale = _is_report_stale(previous, max_age_hours=24 * 30)
    merged_fields = _flatten_report_to_fields(
        {
            "basic_info": current.basic_info,
            "financials": current.financials,
            "funding": current.funding,
        }
    )

    carry_forward_count = 0
    for field_name in _TARGET_FIELDS:
        if merged_fields.get(field_name) in (None, "", [], {}):
            if previous_is_stale and field_name in _VOLATILE_FIELDS:
                continue
            previous_value = previous_fields.get(field_name)
            if previous_value not in (None, "", [], {}):
                merged_fields[field_name] = previous_value
                carry_forward_count += 1

    current.basic_info = {
        "website": merged_fields.get("website"),
        "description": merged_fields.get("description"),
        "industry": merged_fields.get("industry"),
        "headquarters": merged_fields.get("headquarters"),
        "founded_year": merged_fields.get("founded_year"),
        "employees": merged_fields.get("employees"),
    }
    current.financials = {
        "revenue": merged_fields.get("revenue"),
        "revenue_currency": merged_fields.get("revenue_currency") or "EUR",
        "valuation": merged_fields.get("valuation"),
    }
    current.funding = {
        "total_raised": merged_fields.get("funding_raised"),
        "rounds": merged_fields.get("funding_rounds") if merged_fields.get("funding_rounds") is not None else [],
    }

    previous_sources = previous.get("data_sources", []) if isinstance(previous.get("data_sources"), list) else []
    seen_urls: set[str] = set()
    merged_sources: list[dict[str, Any]] = []
    for source in current.data_sources + previous_sources:
        if not isinstance(source, dict):
            continue
        raw_url = source.get("url")
        if not isinstance(raw_url, str) or not raw_url:
            continue
        url = _normalize_url(raw_url)
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        merged_source = dict(source)
        merged_source["url"] = url
        merged_sources.append(merged_source)
    current.data_sources = merged_sources

    return current, carry_forward_count


class AIResearchOrchestrator:
    """Orchestrates the multi-agent research workflow."""

    TARGET_FIELDS = _TARGET_FIELDS  # backward compat
    ADAPTIVE_QUERY_BY_FIELD = _ADAPTIVE_QUERY_BY_FIELD  # backward compat
    VOLATILE_FIELDS = _VOLATILE_FIELDS  # backward compat

    def __init__(self) -> None:
        self.planner = ResearchPlannerAgent()
        self.searcher = WebSearchAgent()
        self.extractor = ContentExtractorAgent()
        self.validator = DataValidatorAgent()
        self.repo_root = Path(__file__).resolve().parents[3]
        memory_path = self.repo_root / "data/research_results/research_memory.json"
        bootstrap_path = self.repo_root / "data/research_results/research_results.json"
        self._memory_store = _ResearchMemoryStore(memory_path, bootstrap_path)
        self._memory = self._memory_store.data

    def _merge_with_previous(self, company_name: str, current: ResearchReport) -> tuple[ResearchReport, int]:
        previous = self._memory_store.get_previous_report(company_name)
        if not previous:
            return current, 0
        return _merge_report_with_previous(current, previous)

    def _persist_report(self, report: ResearchReport) -> None:
        report_dict = {
            "company_name": report.company_name,
            "is_synthetic": report.is_synthetic,
            "confidence_score": report.confidence_score,
            "basic_info": report.basic_info,
            "financials": report.financials,
            "funding": report.funding,
            "data_sources": report.data_sources,
            "metadata": report.metadata,
            "errors": report.errors,
        }
        source_urls: set[str] = set()
        for source in report.data_sources:
            url = source.get("url") if isinstance(source, dict) else None
            if isinstance(url, str) and url:
                source_urls.add(url)
        self._memory_store.update_company(report.company_name, report_dict, source_urls)
        self._memory_store.save()

    async def _extract_and_validate(
        self, company_name: str, results: list[SearchResult],
    ) -> list[dict[str, Any]]:
        validated_data: list[dict[str, Any]] = []
        for result in results:
            extracted = await self.extractor.extract(result.url, company_name)
            if extracted.confidence <= 0.2:
                await asyncio.sleep(0.2)
                continue
            validation = await self.validator.validate(extracted)
            adjusted_confidence = max(0.0, min(1.0, extracted.confidence + validation.confidence_adjustment))
            if adjusted_confidence > 0.3:
                validated_data.append(
                    {
                        "extraction": extracted,
                        "validation": validation,
                        "confidence": adjusted_confidence,
                    }
                )
            await asyncio.sleep(0.2)
        return validated_data

    async def research_company(
        self, company_name: str, industry: str | None = None, max_sources: int = 8
    ) -> ResearchReport:
        """Perform full autonomous research on a company."""
        start_time = datetime.now()
        report = ResearchReport(company_name=company_name)
        previous_report = self._memory_store.get_previous_report(company_name)
        previous_urls = self._memory_store.get_known_urls(company_name)

        if previous_report:
            previous_flat = _flatten_report_to_fields(previous_report)
            completeness = _score_completeness(previous_flat, self.TARGET_FIELDS)
            report_is_stale = _is_report_stale(previous_report, max_age_hours=24 * 7)
            if completeness >= 0.65 and not report_is_stale:
                report = ResearchReport(
                    company_name=company_name,
                    is_synthetic=bool(previous_report.get("is_synthetic", False)),
                    confidence_score=float(previous_report.get("confidence_score", 0.0)),
                    basic_info=previous_report.get("basic_info", {}),
                    financials=previous_report.get("financials", {}),
                    funding=previous_report.get("funding", {}),
                    data_sources=previous_report.get("data_sources", []),
                    metadata={
                        **(previous_report.get("metadata", {}) if isinstance(previous_report.get("metadata"), dict) else {}),
                        "research_date": datetime.now().isoformat(),
                        "cache_reuse": True,
                        "previous_completeness": round(completeness, 3),
                        "previous_report_stale": report_is_stale,
                        "sources_reused": len(previous_urls),
                        "research_time_seconds": (datetime.now() - start_time).total_seconds(),
                    },
                    errors=list(previous_report.get("errors", [])) if isinstance(previous_report.get("errors"), list) else [],
                )
                self._persist_report(report)
                return report

        try:
            plan = await self.planner.create_plan(company_name, industry)

            all_search_results: list[SearchResult] = []
            for query_info in plan.queries[:6]:
                query = query_info.get("query", "")
                intent = query_info.get("intent", "general")
                if not query:
                    continue
                all_search_results.extend(await self.searcher.search(query, intent, max_results=5))
                await asyncio.sleep(0.3)

            unique_results: list[SearchResult] = []
            seen_urls: set[str] = set()
            known_urls = set(previous_urls)
            deferred_known: list[SearchResult] = []
            for result in all_search_results:
                normalized_url = _normalize_url(result.url) if result.url else ""
                if normalized_url and normalized_url not in seen_urls:
                    seen_urls.add(normalized_url)
                    normalized_result = SearchResult(
                        title=result.title,
                        url=normalized_url,
                        snippet=result.snippet,
                        source=result.source,
                        relevance_score=result.relevance_score,
                        intent_match=result.intent_match,
                    )
                    if normalized_url in known_urls:
                        deferred_known.append(normalized_result)
                    else:
                        unique_results.append(normalized_result)
                if len(unique_results) >= max_sources:
                    break

            if len(unique_results) < max_sources:
                for result in deferred_known:
                    unique_results.append(result)
                    if len(unique_results) >= max_sources:
                        break

            extracted_data_list: list[ExtractedData] = []
            for result in unique_results:
                extracted = await self.extractor.extract(result.url, company_name)
                if extracted.confidence > 0.2:
                    extracted_data_list.append(extracted)
                await asyncio.sleep(0.2)

            validated_data: list[dict[str, Any]] = []
            for extraction in extracted_data_list:
                validation = await self.validator.validate(extraction)
                adjusted_confidence = max(0.0, min(1.0, extraction.confidence + validation.confidence_adjustment))
                if adjusted_confidence > 0.3:
                    validated_data.append(
                        {
                            "extraction": extraction,
                            "validation": validation,
                            "confidence": adjusted_confidence,
                        }
                    )

            additional_pass_used = False
            additional_queries_executed = 0
            additional_sources_used = 0

            initial_synthesized = _synthesize_validated_data(validated_data)
            missing_before = _missing_fields(initial_synthesized)
            initial_completeness = _score_completeness(initial_synthesized, self.TARGET_FIELDS)

            if missing_before and initial_completeness < 0.8:
                adaptive_queries = _build_adaptive_queries(company_name, missing_before)
                adaptive_results: list[SearchResult] = []
                adaptive_seen = {r.url for r in unique_results}
                adaptive_known: list[SearchResult] = []

                for query_info in adaptive_queries:
                    query = query_info["query"]
                    intent = query_info["intent"]
                    additional_queries_executed += 1
                    results = await self.searcher.search(query, intent, max_results=5)
                    for result in results:
                        normalized_url = _normalize_url(result.url) if result.url else ""
                        if not normalized_url or normalized_url in adaptive_seen:
                            continue
                        adaptive_seen.add(normalized_url)
                        normalized_result = SearchResult(
                            title=result.title,
                            url=normalized_url,
                            snippet=result.snippet,
                            source=result.source,
                            relevance_score=result.relevance_score,
                            intent_match=result.intent_match,
                        )
                        if normalized_url in previous_urls:
                            adaptive_known.append(normalized_result)
                        else:
                            adaptive_results.append(normalized_result)
                        if len(adaptive_results) >= 6:
                            break
                    if len(adaptive_results) >= 6:
                        break
                    await asyncio.sleep(0.3)

                if len(adaptive_results) < 4:
                    for result in adaptive_known:
                        adaptive_results.append(result)
                        if len(adaptive_results) >= 6:
                            break

                if adaptive_results:
                    additional_validated = await self._extract_and_validate(company_name, adaptive_results)
                    if additional_validated:
                        validated_data.extend(additional_validated)
                        unique_results.extend(adaptive_results)
                        additional_sources_used = len(additional_validated)
                        additional_pass_used = True

            final_data = _synthesize_validated_data(validated_data)
            revisited_count = len([r for r in unique_results if r.url in previous_urls])
            missing_after = _missing_fields(final_data)
            report = ResearchReport(
                company_name=company_name,
                is_synthetic=False,
                confidence_score=final_data.get("_confidence", 0.0),
                basic_info={
                    "website": final_data.get("website"),
                    "description": final_data.get("description"),
                    "industry": final_data.get("industry"),
                    "headquarters": final_data.get("headquarters"),
                    "founded_year": final_data.get("founded_year"),
                    "employees": final_data.get("employees"),
                },
                financials={
                    "revenue": final_data.get("revenue"),
                    "revenue_currency": final_data.get("revenue_currency", "EUR"),
                    "valuation": final_data.get("valuation"),
                },
                funding={
                    "total_raised": final_data.get("funding_raised"),
                    "rounds": final_data.get("funding_rounds", []),
                },
                data_sources=[
                    {
                        "url": item["extraction"].source_url,
                        "type": item["extraction"].source_type,
                        "confidence": item["confidence"],
                    }
                    for item in validated_data
                ],
                metadata={
                    "research_date": datetime.now().isoformat(),
                    "queries_executed": len(plan.queries),
                    "sources_found": len(unique_results),
                    "sources_used": len(validated_data),
                    "known_sources_skipped": len(deferred_known) - revisited_count,
                    "known_sources_revisited": revisited_count,
                    "adaptive_pass_used": additional_pass_used,
                    "adaptive_queries_executed": additional_queries_executed,
                    "adaptive_sources_used": additional_sources_used,
                    "missing_fields_before_adaptive": missing_before,
                    "missing_fields_after_adaptive": missing_after,
                    "research_time_seconds": (datetime.now() - start_time).total_seconds(),
                },
            )

            report, carry_forward_count = self._merge_with_previous(company_name, report)
            report.metadata["fields_carried_forward"] = carry_forward_count
        except Exception as error:
            logger.error(f"Research failed for {company_name}: {error}")
            if previous_report:
                report = ResearchReport(
                    company_name=company_name,
                    is_synthetic=bool(previous_report.get("is_synthetic", False)),
                    confidence_score=float(previous_report.get("confidence_score", 0.0)),
                    basic_info=previous_report.get("basic_info", {}),
                    financials=previous_report.get("financials", {}),
                    funding=previous_report.get("funding", {}),
                    data_sources=previous_report.get("data_sources", []),
                    metadata={
                        **(previous_report.get("metadata", {}) if isinstance(previous_report.get("metadata"), dict) else {}),
                        "research_date": datetime.now().isoformat(),
                        "fallback_to_previous_on_error": True,
                        "error": str(error),
                    },
                    errors=list(previous_report.get("errors", [])) if isinstance(previous_report.get("errors"), list) else [],
                )
            report.errors.append(str(error))

        self._persist_report(report)
        return report


__all__ = [
    "AIResearchOrchestrator", "ResearchPlannerAgent", "WebSearchAgent",
    "ContentExtractorAgent", "DataValidatorAgent", "ResearchReport",
    "ResearchPlan", "SearchResult", "ExtractedData", "ValidationResult",
]
