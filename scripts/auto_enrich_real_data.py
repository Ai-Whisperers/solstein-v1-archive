import json
import os
import re
from pathlib import Path
from typing import Any

from solstein.data.company_research import CompanyResearcher
from solstein.data.connectors.lookup_service import IdentifierLookupService
from solstein.data.enrichment_config import ConnectorConfig, UnifiedCompanyLoaderConfig
from solstein.data.enrichment_service import EnrichmentService
from solstein.data.metric_contract import normalize_percent, normalize_revenue_to_millions
from solstein.data.web_search_client import search_company_info
from solstein.domain.models import AIMaturity, Company, FinancialMetric


def _ai_maturity_from_score(score: Any) -> AIMaturity:
    if not isinstance(score, (int, float)):
        return AIMaturity.NONE
    if score >= 9:
        return AIMaturity.VERY_STRONG
    if score >= 7:
        return AIMaturity.STRONG
    if score >= 5:
        return AIMaturity.MODERATE
    if score >= 3:
        return AIMaturity.LOW
    return AIMaturity.NONE


def _ai_maturity_score_from_level(level: AIMaturity) -> float:
    mapping = {
        AIMaturity.NONE: 1.5,
        AIMaturity.LOW: 3.5,
        AIMaturity.MODERATE: 5.5,
        AIMaturity.STRONG: 7.5,
        AIMaturity.VERY_STRONG: 9.0,
    }
    return mapping.get(level, 1.5)


def _set_metric(
    company: Company,
    metric_name: str,
    value: Any,
    confidence: float,
    source: str,
    unit: str,
    lineage: dict[str, dict[str, Any]],
) -> None:
    if value is None:
        return

    current_conf = company.confidence_scores.get(metric_name)
    current_value = getattr(company, metric_name, None)
    should_update = current_value is None
    if isinstance(current_conf, (int, float)) and confidence > float(current_conf):
        should_update = True
    if current_conf is None:
        should_update = True

    if not should_update:
        return

    setattr(company, metric_name, value)
    if metric_name == "funding":
        company.financials.funding_raised = value
    elif metric_name == "valuation":
        company.financials.valuation = value
    else:
        setattr(company.financials, metric_name, value)

    company.confidence_scores[metric_name] = confidence
    lineage[metric_name] = {
        "value": value,
        "source": source,
        "confidence": confidence,
        "unit": unit,
    }


def _extract_numeric_from_snippets(text: str, metric: str) -> float | int | None:
    haystack = text.lower()
    if metric == "employees":
        match = re.search(r"(\d{1,3}(?:,\d{3}){1,3}|\d{2,7})\s+(?:employees|staff|workforce)", haystack)
        if match:
            return int(match.group(1).replace(",", ""))
        return None

    patterns = {
        "revenue": r"(?:revenue|sales)\D{0,15}(\$|€|£)?\s*(\d+(?:\.\d+)?)\s*(billion|million|bn|m)",
        "funding": r"(?:raised|funding)\D{0,15}(\$|€|£)?\s*(\d+(?:\.\d+)?)\s*(billion|million|bn|m)",
        "valuation": r"(?:valued at|valuation|market cap)\D{0,20}(\$|€|£)?\s*(\d+(?:\.\d+)?)\s*(billion|million|bn|m)",
        "growth_rate": r"(\d+(?:\.\d+)?)\s*%\s*(?:yoy|year[-\s]over[-\s]year|growth)",
        "profit_margin": r"(\d+(?:\.\d+)?)\s*%\s*(?:profit margin|margin)",
    }
    pattern = patterns.get(metric)
    if not pattern:
        return None
    match = re.search(pattern, haystack)
    if not match:
        return None

    if metric in {"growth_rate", "profit_margin"}:
        return float(match.group(1))

    value = float(match.group(2))
    scale = match.group(3)
    if scale in {"billion", "bn"}:
        return value * 1000.0
    if scale in {"million", "m"}:
        return value
    return value


def _apply_free_source_research(company: Company) -> tuple[Company, list[str], dict[str, dict[str, Any]]]:
    free_sources: list[str] = []
    lineage_updates: dict[str, dict[str, Any]] = {}

    ticker = company.ticker
    if ticker:
        try:
            researcher = CompanyResearcher()
            profile = researcher.research(ticker)
            free_sources.append("yahoo_finance")

            if profile.financials is not None:
                revenue_norm = normalize_revenue_to_millions(profile.financials.revenue)
                _set_metric(
                    company,
                    "revenue",
                    revenue_norm.value,
                    confidence=0.78,
                    source="yahoo_finance",
                    unit="millions",
                    lineage=lineage_updates,
                )

                growth_norm = normalize_percent(profile.financials.revenue_growth_yoy)
                _set_metric(
                    company,
                    "growth_rate",
                    growth_norm.value,
                    confidence=0.72,
                    source="yahoo_finance",
                    unit="percent",
                    lineage=lineage_updates,
                )

                margin_norm = normalize_percent(profile.financials.profit_margin)
                _set_metric(
                    company,
                    "profit_margin",
                    margin_norm.value,
                    confidence=0.74,
                    source="yahoo_finance",
                    unit="percent",
                    lineage=lineage_updates,
                )

            _set_metric(
                company,
                "employees",
                profile.employees,
                confidence=0.7,
                source="yahoo_finance",
                unit="count",
                lineage=lineage_updates,
            )

            valuation_norm = normalize_revenue_to_millions(profile.market_cap)
            _set_metric(
                company,
                "valuation",
                valuation_norm.value,
                confidence=0.76,
                source="yahoo_finance",
                unit="millions",
                lineage=lineage_updates,
            )
        except Exception:
            pass

    snippet_blob = ""
    for query_type in ["general", "funding", "product", "technology"]:
        results = search_company_info(company.name, query_type=query_type)
        if results:
            free_sources.append(f"web_search:{query_type}")
            snippet_blob += " " + " ".join(item.get("snippet", "") for item in results)

    if snippet_blob:
        revenue_val = _extract_numeric_from_snippets(snippet_blob, "revenue")
        _set_metric(
            company,
            "revenue",
            revenue_val,
            confidence=0.58,
            source="web_search",
            unit="millions",
            lineage=lineage_updates,
        )

        employees_val = _extract_numeric_from_snippets(snippet_blob, "employees")
        _set_metric(
            company,
            "employees",
            employees_val,
            confidence=0.55,
            source="web_search",
            unit="count",
            lineage=lineage_updates,
        )

        growth_val = _extract_numeric_from_snippets(snippet_blob, "growth_rate")
        _set_metric(
            company,
            "growth_rate",
            growth_val,
            confidence=0.5,
            source="web_search",
            unit="percent",
            lineage=lineage_updates,
        )

        margin_val = _extract_numeric_from_snippets(snippet_blob, "profit_margin")
        _set_metric(
            company,
            "profit_margin",
            margin_val,
            confidence=0.5,
            source="web_search",
            unit="percent",
            lineage=lineage_updates,
        )

        funding_val = _extract_numeric_from_snippets(snippet_blob, "funding")
        _set_metric(
            company,
            "funding",
            funding_val,
            confidence=0.52,
            source="web_search",
            unit="millions",
            lineage=lineage_updates,
        )

        valuation_val = _extract_numeric_from_snippets(snippet_blob, "valuation")
        _set_metric(
            company,
            "valuation",
            valuation_val,
            confidence=0.54,
            source="web_search",
            unit="millions",
            lineage=lineage_updates,
        )

    dedup_sources = sorted(set(free_sources))
    return company, dedup_sources, lineage_updates


def _build_company(
    raw: dict[str, Any],
    lookup: IdentifierLookupService,
    resolved: dict[str, Any] | None = None,
) -> Company:
    name = raw.get("company_name") or raw.get("name") or "Unknown"
    headquarters = raw.get("country") or raw.get("headquarters")
    resolved = resolved or lookup.resolve_identifiers(name, headquarters=headquarters)
    ticker = raw.get("ticker") or resolved.get("ticker")
    company_number = raw.get("company_number") or resolved.get("company_number")
    isin = raw.get("isin") or resolved.get("isin")

    financials = FinancialMetric(
        revenue=raw.get("revenue"),
        growth_rate=raw.get("growth_rate"),
        employees=raw.get("employees"),
        profit_margin=raw.get("profit_margin"),
        funding_raised=raw.get("funding_raised"),
        valuation=raw.get("valuation"),
    )

    return Company(
        id=raw.get("id") or name.lower().replace(" ", "-")[:50],
        name=name,
        company_name=raw.get("company_name"),
        industry=raw.get("industry") or "Unknown",
        description=raw.get("description"),
        website=raw.get("website"),
        headquarters=headquarters,
        founded_year=raw.get("founded_year"),
        ticker=ticker,
        company_number=company_number,
        isin=isin,
        ai_maturity=_ai_maturity_from_score(raw.get("ai_maturity_score")),
        financials=financials,
        data_source_type=raw.get("data_source_type", "real"),
        signal_confidences=raw.get("signal_confidences", {}),
        confidence_scores=raw.get("confidence_scores", {}),
        geographic_presence=raw.get("geographic_presence", []),
        data_source="real_data",
    )


def _merge_back(
    raw: dict[str, Any],
    company: Company,
    sources: list[str],
    errors: list[str],
    free_sources: list[str],
    free_lineage: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    raw["company_name"] = raw.get("company_name") or company.name
    raw["ticker"] = company.ticker
    raw["company_number"] = company.company_number
    raw["isin"] = company.isin
    raw["country"] = raw.get("country") or company.headquarters
    raw["headquarters"] = raw.get("headquarters") or company.headquarters

    raw["revenue"] = company.revenue
    raw["growth_rate"] = company.growth_rate
    raw["employees"] = company.employees
    raw["profit_margin"] = company.profit_margin
    raw["funding_raised"] = company.funding
    raw["valuation"] = company.valuation
    raw["ai_maturity_score"] = raw.get("ai_maturity_score") or _ai_maturity_score_from_level(company.ai_maturity)

    raw["enrichment_sources"] = sources
    raw["free_research_sources"] = free_sources
    raw["enrichment_errors"] = errors
    raw["identifier_confidence"] = company.confidence_scores.get("identifier_confidence")
    confidence_scores = company.confidence_scores or {}

    def lineage_for(metric_key: str, default_unit: str) -> dict[str, Any]:
        if metric_key in free_lineage:
            line = dict(free_lineage[metric_key])
            line.setdefault("unit", default_unit)
            return line
        return {
            "value": getattr(company, metric_key if metric_key != "funding_raised" else "funding"),
            "source": (sources[0] if sources else (free_sources[0] if free_sources else "unknown")),
            "confidence": confidence_scores.get(metric_key if metric_key != "funding_raised" else "funding"),
            "unit": default_unit,
        }

    raw["metric_lineage"] = {
        "revenue": lineage_for("revenue", "millions"),
        "employees": lineage_for("employees", "count"),
        "growth_rate": lineage_for("growth_rate", "percent"),
        "profit_margin": lineage_for("profit_margin", "percent"),
        "funding_raised": lineage_for("funding_raised", "millions"),
        "valuation": lineage_for("valuation", "millions"),
    }
    raw["source_priority"] = [
        "sec_edgar",
        "companies_house",
        "yahoo_finance",
        "web_search",
        "news_signals",
    ]
    return raw


def _build_research_queue(companies: list[dict[str, Any]]) -> dict[str, Any]:
    required_fields = [
        "company_name",
        "industry",
        "headquarters",
        "website",
        "revenue",
        "employees",
        "growth_rate",
        "profit_margin",
        "funding_raised",
        "valuation",
        "ai_maturity_score",
    ]
    queue = []
    missing_counts: dict[str, int] = dict.fromkeys(required_fields, 0)

    recommendations = {
        "company_number": "Use Companies House/OpenCorporates lookup",
        "ticker": "Use OpenFIGI + exchange mapping",
        "revenue": "Use SEC filings or premium private-company connector",
        "employees": "Use annual reports/official filings",
        "growth_rate": "Derive from multi-period revenue after revenue is sourced",
        "profit_margin": "Use financial statements",
        "funding_raised": "Use Crunchbase/PitchBook/Orbis",
        "valuation": "Use PitchBook/CapIQ/transactions",
        "ai_maturity_score": "Use AI signal extractor with source evidence",
    }

    for comp in companies:
        missing = []
        for field in required_fields:
            value = comp.get(field)
            if value is None or value == "" or value == []:
                missing.append(field)
                missing_counts[field] += 1

        ticker_value = comp.get("ticker")
        company_number_value = comp.get("company_number")
        has_ticker = isinstance(ticker_value, str) and ticker_value.strip() != ""
        has_company_number = isinstance(company_number_value, str) and company_number_value.strip() != ""
        if not has_ticker and not has_company_number:
            missing.append("identifier")
            missing_counts["identifier"] = missing_counts.get("identifier", 0) + 1

        if missing:
            critical_missing = [
                f for f in missing if f in {"revenue", "employees", "growth_rate", "profit_margin", "identifier"}
            ]
            priority_score = len(critical_missing) * 3 + (len(missing) - len(critical_missing))
            queue.append(
                {
                    "company": comp.get("company_name") or comp.get("name"),
                    "missing_fields": missing,
                    "confidence": comp.get("confidence"),
                    "sources": comp.get("data_sources") or comp.get("metadata", {}).get("sources"),
                    "priority_score": priority_score,
                    "research_actions": [recommendations.get(field, "Manual analyst research") for field in missing],
                }
            )

    queue.sort(key=lambda item: int(item.get("priority_score", 0)), reverse=True)

    return {
        "total_companies": len(companies),
        "queued_companies": len(queue),
        "missing_counts": missing_counts,
        "queue": queue,
    }


def main() -> None:
    input_path = Path("data/input/competitor_data_real.json")
    if not input_path.exists():
        raise SystemExit("Missing data/input/competitor_data_real.json")

    raw_data = json.loads(input_path.read_text())
    companies = raw_data.get("competitors", [])

    lookup = IdentifierLookupService()
    sec_key = os.getenv("SEC_EDGAR_API_KEY")
    ch_key = os.getenv("COMPANIES_HOUSE_API_KEY")
    news_key = os.getenv("NEWS_API_KEY")
    config = UnifiedCompanyLoaderConfig(
        enrichment_enabled=True,
        sec_edgar_config=ConnectorConfig(enabled=True, api_key=sec_key),
        companies_house_config=ConnectorConfig(enabled=bool(ch_key), api_key=ch_key),
        news_signals_config=ConnectorConfig(enabled=bool(news_key), api_key=news_key),
    )
    enrichment = EnrichmentService(config=config)

    enriched_companies = []
    for comp in companies:
        resolved = lookup.resolve_identifiers(
            comp.get("company_name") or comp.get("name") or "Unknown",
            headquarters=comp.get("country") or comp.get("headquarters"),
        )
        company = _build_company(comp, lookup, resolved=resolved)
        company.confidence_scores["identifier_confidence"] = float(resolved.get("overall_confidence", 0.0))
        company, free_sources, free_lineage = _apply_free_source_research(company)
        enriched, sources, errors = enrichment.enrich_company(company)
        enriched_companies.append(
            _merge_back(
                comp,
                enriched,
                sources,
                errors,
                free_sources,
                free_lineage,
            )
        )

    raw_data["competitors"] = enriched_companies

    output_path = Path("data/input/competitor_data_real_enriched.json")
    output_path.write_text(json.dumps(raw_data, indent=2))

    queue = _build_research_queue(enriched_companies)
    queue_path = Path("data/output/research_queue.json")
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    queue_path.write_text(json.dumps(queue, indent=2))

    print(f"✅ Saved enriched data to {output_path}")
    print(f"Queue updated: {queue_path}")
    print(f"Queued companies: {queue['queued_companies']} / {queue['total_companies']}")


if __name__ == "__main__":
    main()
