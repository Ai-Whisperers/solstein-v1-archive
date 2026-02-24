from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from loguru import logger

from solstein.data.loaders import CompetitorDataLoader

if TYPE_CHECKING:
    from solstein.adapters.registry import SourceRegistry


@dataclass
class DiscoveryCandidate:
    company_id: str
    name: str
    market: str
    ticker: str | None
    industry: str
    region: str
    tags: list[str]
    seed_relevance: float
    discovery_reason: str
    source_links: list[str]


def _slugify(name: str) -> str:
    out = []
    for ch in name.lower():
        if ch.isalnum():
            out.append(ch)
        elif out and out[-1] != "-":
            out.append("-")
    slug = "".join(out).strip("-")
    return slug or "unknown-company"


def _catalog_for_market(market: str) -> list[dict[str, object]]:
    m = market.lower()
    if "dutch" in m or "netherlands" in m or "energy" in m:
        return [
            {
                "name": "Eneve",
                "ticker": None,
                "industry": "Energy Software",
                "region": "NL",
                "tags": ["energy", "software", "billing"],
                "sources": [
                    "https://eneve.com/",
                    "https://www.linkedin.com/company/eneve/",
                ],
            },
            {
                "name": "Octopus Energy Group / Kraken Technologies",
                "ticker": None,
                "industry": "Energy Software",
                "region": "UK/EU",
                "tags": ["energy", "platform", "kraken"],
                "sources": ["https://octopus.energy/", "https://kraken.tech/"],
            },
            {
                "name": "Volue ASA",
                "ticker": "VOLUE.OL",
                "industry": "Energy Software",
                "region": "Nordics/EU",
                "tags": ["energy", "trading", "optimization"],
                "sources": [
                    "https://www.volue.com/",
                    "https://finance.yahoo.com/quote/VOLUE.OL/",
                ],
            },
            {
                "name": "CGI Inc.",
                "ticker": "GIB",
                "industry": "IT Services",
                "region": "Global/EU",
                "tags": ["consulting", "utilities", "software"],
                "sources": [
                    "https://www.cgi.com/",
                    "https://finance.yahoo.com/quote/GIB/",
                ],
            },
            {
                "name": "Accenture",
                "ticker": "ACN",
                "industry": "IT Services",
                "region": "Global/EU",
                "tags": ["consulting", "utilities", "cloud"],
                "sources": [
                    "https://www.accenture.com/",
                    "https://finance.yahoo.com/quote/ACN/",
                ],
            },
            {
                "name": "Capgemini",
                "ticker": "CAP.PA",
                "industry": "IT Services",
                "region": "EU",
                "tags": ["consulting", "energy", "transformation"],
                "sources": [
                    "https://www.capgemini.com/",
                    "https://finance.yahoo.com/quote/CAP.PA/",
                ],
            },
            {
                "name": "Sopra Steria",
                "ticker": "SOP.PA",
                "industry": "IT Services",
                "region": "EU",
                "tags": ["utilities", "software", "platform"],
                "sources": [
                    "https://www.soprasteria.com/",
                    "https://finance.yahoo.com/quote/SOP.PA/",
                ],
            },
            {
                "name": "Asseco Poland",
                "ticker": "ACP.WA",
                "industry": "Enterprise Software",
                "region": "EU",
                "tags": ["utilities", "enterprise", "software"],
                "sources": [
                    "https://asseco.com/",
                    "https://finance.yahoo.com/quote/ACP.WA/",
                ],
            },
            {
                "name": "Hitachi Energy",
                "ticker": None,
                "industry": "Energy Technology",
                "region": "EU/Global",
                "tags": ["grid", "energy", "infrastructure"],
                "sources": [
                    "https://www.hitachienergy.com/",
                    "https://www.hitachi.com/",
                ],
            },
            {
                "name": "Siemens Energy",
                "ticker": "ENR.DE",
                "industry": "Energy Technology",
                "region": "EU",
                "tags": ["energy", "grid", "infrastructure"],
                "sources": [
                    "https://www.siemens-energy.com/",
                    "https://finance.yahoo.com/quote/ENR.DE/",
                ],
            },
            {
                "name": "Schneider Electric",
                "ticker": "SU.PA",
                "industry": "Energy Management",
                "region": "EU",
                "tags": ["energy", "management", "software"],
                "sources": [
                    "https://www.se.com/",
                    "https://finance.yahoo.com/quote/SU.PA/",
                ],
            },
            {
                "name": "ABB",
                "ticker": "ABB",
                "industry": "Industrial Technology",
                "region": "EU/Global",
                "tags": ["grid", "automation", "energy"],
                "sources": [
                    "https://global.abb/",
                    "https://finance.yahoo.com/quote/ABB/",
                ],
            },
            {
                "name": "Itron",
                "ticker": "ITRI",
                "industry": "Energy Technology",
                "region": "US/EU",
                "tags": ["metering", "grid", "software"],
                "sources": [
                    "https://www.itron.com/",
                    "https://finance.yahoo.com/quote/ITRI/",
                ],
            },
            {
                "name": "Landis+Gyr",
                "ticker": "LAND.SW",
                "industry": "Energy Technology",
                "region": "EU/Global",
                "tags": ["metering", "grid", "analytics"],
                "sources": [
                    "https://www.landisgyr.com/",
                    "https://finance.yahoo.com/quote/LAND.SW/",
                ],
            },
            {
                "name": "Fluence Energy",
                "ticker": "FLNC",
                "industry": "Energy Software",
                "region": "Global",
                "tags": ["storage", "energy", "software"],
                "sources": [
                    "https://fluenceenergy.com/",
                    "https://finance.yahoo.com/quote/FLNC/",
                ],
            },
            {
                "name": "AutoGrid",
                "ticker": None,
                "industry": "Energy AI Software",
                "region": "Global",
                "tags": ["ai", "energy", "flexibility"],
                "sources": ["https://www.autogrid.com/"],
            },
            {
                "name": "Uplight",
                "ticker": None,
                "industry": "Energy Software",
                "region": "US/EU",
                "tags": ["energy", "customer", "engagement"],
                "sources": ["https://www.uplight.com/"],
            },
            {
                "name": "Kaluza",
                "ticker": None,
                "industry": "Energy Software",
                "region": "UK/EU",
                "tags": ["energy", "platform", "decarbonization"],
                "sources": ["https://kaluza.com/"],
            },
            {
                "name": "GridX",
                "ticker": None,
                "industry": "Energy Software",
                "region": "EU",
                "tags": ["grid", "flexibility", "platform"],
                "sources": ["https://www.gridx.ai/"],
            },
            {
                "name": "Limejump",
                "ticker": None,
                "industry": "Energy Software",
                "region": "UK/EU",
                "tags": ["energy", "trading", "aggregation"],
                "sources": ["https://www.limejump.com/"],
            },
        ]

    return [
        {
            "name": "ueno bank S.A.",
            "ticker": None,
            "industry": "Digital Banking",
            "region": "LATAM",
            "tags": ["bank", "digital", "payments"],
            "sources": [
                "https://www.ueno.com.py/en/",
                "https://www.linkedin.com/company/ueno-paraguay/",
            ],
        },
        {
            "name": "Nu Holdings",
            "ticker": "NU",
            "industry": "Digital Banking",
            "region": "LATAM",
            "tags": ["bank", "fintech", "digital"],
            "sources": [
                "https://www.nubank.com.br/",
                "https://finance.yahoo.com/quote/NU/",
            ],
        },
        {
            "name": "PagSeguro Digital",
            "ticker": "PAGS",
            "industry": "Payments",
            "region": "LATAM",
            "tags": ["payments", "merchant", "fintech"],
            "sources": [
                "https://investors.pagseguro.com/",
                "https://finance.yahoo.com/quote/PAGS/",
            ],
        },
        {
            "name": "StoneCo",
            "ticker": "STNE",
            "industry": "Fintech",
            "region": "LATAM",
            "tags": ["payments", "sme", "fintech"],
            "sources": [
                "https://investors.stone.co/",
                "https://finance.yahoo.com/quote/STNE/",
            ],
        },
        {
            "name": "Itaú Unibanco",
            "ticker": "ITUB",
            "industry": "Banking",
            "region": "LATAM",
            "tags": ["bank", "retail", "enterprise"],
            "sources": [
                "https://www.itau.com.br/",
                "https://finance.yahoo.com/quote/ITUB/",
            ],
        },
        {
            "name": "Banco Bradesco",
            "ticker": "BBD",
            "industry": "Banking",
            "region": "LATAM",
            "tags": ["bank", "retail", "enterprise"],
            "sources": [
                "https://banco.bradesco/html/classic/index.shtm",
                "https://finance.yahoo.com/quote/BBD/",
            ],
        },
        {
            "name": "Bancolombia",
            "ticker": "CIB",
            "industry": "Banking",
            "region": "LATAM",
            "tags": ["bank", "retail", "enterprise"],
            "sources": [
                "https://www.grupobancolombia.com/",
                "https://finance.yahoo.com/quote/CIB/",
            ],
        },
        {
            "name": "Grupo Aval",
            "ticker": "AVAL",
            "industry": "Banking",
            "region": "LATAM",
            "tags": ["bank", "holding", "financial"],
            "sources": [
                "https://www.grupoaval.com/",
                "https://finance.yahoo.com/quote/AVAL/",
            ],
        },
        {
            "name": "Banco de Chile",
            "ticker": "BCH",
            "industry": "Banking",
            "region": "LATAM",
            "tags": ["bank", "retail", "financial"],
            "sources": [
                "https://portales.bancochile.cl/",
                "https://finance.yahoo.com/quote/BCH/",
            ],
        },
        {
            "name": "Banco Santander Chile",
            "ticker": "BSAC",
            "industry": "Banking",
            "region": "LATAM",
            "tags": ["bank", "retail", "digital"],
            "sources": [
                "https://banco.santander.cl/",
                "https://finance.yahoo.com/quote/BSAC/",
            ],
        },
        {
            "name": "Grupo Financiero Galicia",
            "ticker": "GGAL",
            "industry": "Banking",
            "region": "LATAM",
            "tags": ["bank", "retail", "financial"],
            "sources": [
                "https://www.gfgsa.com/",
                "https://finance.yahoo.com/quote/GGAL/",
            ],
        },
        {
            "name": "BBVA Argentina",
            "ticker": "BBAR",
            "industry": "Banking",
            "region": "LATAM",
            "tags": ["bank", "retail", "digital"],
            "sources": [
                "https://www.bbva.com.ar/",
                "https://finance.yahoo.com/quote/BBAR/",
            ],
        },
        {
            "name": "Grupo Supervielle",
            "ticker": "SUPV",
            "industry": "Banking",
            "region": "LATAM",
            "tags": ["bank", "retail", "financial"],
            "sources": [
                "https://www.supervielle.com.ar/",
                "https://finance.yahoo.com/quote/SUPV/",
            ],
        },
        {
            "name": "Credicorp",
            "ticker": "BAP",
            "industry": "Banking",
            "region": "LATAM",
            "tags": ["bank", "holding", "financial"],
            "sources": [
                "https://www.credicorpnet.com/",
                "https://finance.yahoo.com/quote/BAP/",
            ],
        },
        {
            "name": "Intercorp Financial Services",
            "ticker": "IFS",
            "industry": "Banking",
            "region": "LATAM",
            "tags": ["bank", "retail", "financial"],
            "sources": [
                "https://www.ifhperu.com/",
                "https://finance.yahoo.com/quote/IFS/",
            ],
        },
        {
            "name": "XP Inc.",
            "ticker": "XP",
            "industry": "Wealth & Brokerage",
            "region": "LATAM",
            "tags": ["brokerage", "investment", "fintech"],
            "sources": [
                "https://investors.xpinc.com/",
                "https://finance.yahoo.com/quote/XP/",
            ],
        },
        {
            "name": "MercadoLibre Fintech",
            "ticker": "MELI",
            "industry": "Payments",
            "region": "LATAM",
            "tags": ["payments", "wallet", "fintech"],
            "sources": [
                "https://investor.mercadolibre.com/",
                "https://finance.yahoo.com/quote/MELI/",
            ],
        },
        {
            "name": "Banorte",
            "ticker": "GFNORTEO.MX",
            "industry": "Banking",
            "region": "LATAM",
            "tags": ["bank", "retail", "enterprise"],
            "sources": [
                "https://www.banorte.com/",
                "https://finance.yahoo.com/quote/GFNORTEO.MX/",
            ],
        },
        {
            "name": "BBAJIO",
            "ticker": "BBAJIOO.MX",
            "industry": "Banking",
            "region": "LATAM",
            "tags": ["bank", "commercial", "financial"],
            "sources": [
                "https://www.bb.com.mx/",
                "https://finance.yahoo.com/quote/BBAJIOO.MX/",
            ],
        },
        {
            "name": "Gentera",
            "ticker": "GENTERA.MX",
            "industry": "Financial Services",
            "region": "LATAM",
            "tags": ["microfinance", "lending", "financial"],
            "sources": [
                "https://gentera.com.mx/",
                "https://finance.yahoo.com/quote/GENTERA.MX/",
            ],
        },
    ]


def _score_candidate(
    candidate: DiscoveryCandidate,
    seed_company: str,
    market: str,
    extra_keywords: list[str] | None = None,
) -> DiscoveryCandidate:
    """Apply relevance scoring to a candidate based on seed/market/keywords."""
    keywords = [k.lower() for k in (extra_keywords or [])]
    seed_tokens = [tok for tok in seed_company.lower().replace("/", " ").split() if tok]
    tags = [t.lower() for t in candidate.tags]

    score = candidate.seed_relevance  # preserve any pre-existing score
    reasons: list[str] = []

    if any(tok in candidate.name.lower() for tok in seed_tokens):
        score += 3.0
        reasons.append("name similarity with seed")

    overlap = len(set(tags) & set(keywords))
    if overlap:
        score += float(overlap)
        reasons.append("keyword tag overlap")

    if "latam" in market.lower() and "latam" in candidate.region.lower():
        score += 1.0
        reasons.append("market region match")

    if any(k in tags for k in ["energy", "bank", "fintech", "payments", "software"]):
        score += 0.5

    candidate.seed_relevance = score
    if reasons:
        candidate.discovery_reason = ", ".join(reasons)
    return candidate


def _deduplicate_candidates(
    candidates: list[DiscoveryCandidate],
) -> list[DiscoveryCandidate]:
    """Deduplicate candidates by company_id, keeping highest relevance."""
    best: dict[str, DiscoveryCandidate] = {}
    for c in candidates:
        existing = best.get(c.company_id)
        if existing is None or c.seed_relevance > existing.seed_relevance:
            best[c.company_id] = c
    return list(best.values())


def discover_companies(
    seed_company: str,
    market: str,
    max_companies: int = 25,
    extra_keywords: list[str] | None = None,
    registry: SourceRegistry | None = None,
) -> list[DiscoveryCandidate]:
    if registry is not None:
        return _discover_via_registry(
            seed_company, market, max_companies, extra_keywords, registry
        )
    return _discover_legacy(seed_company, market, max_companies, extra_keywords)


def _discover_via_registry(
    seed_company: str,
    market: str,
    max_companies: int,
    extra_keywords: list[str] | None,
    registry: SourceRegistry,
) -> list[DiscoveryCandidate]:
    """New path: iterate all DiscoverySource adapters from the registry."""
    all_candidates: list[DiscoveryCandidate] = []
    for source in registry.discovery_sources:
        try:
            candidates = source.discover(
                market=market,
                seed_company=seed_company,
                max_results=max_companies * 2,  # over-fetch to allow dedup
                extra_keywords=extra_keywords,
            )
            logger.info(
                "Discovery source '{}' returned {} candidates",
                source.source_name,
                len(candidates),
            )
            all_candidates.extend(candidates)
        except Exception as exc:
            logger.warning(
                "Discovery source '{}' failed: {}",
                source.source_name,
                exc,
            )

    deduped = _deduplicate_candidates(all_candidates)

    # Apply relevance scoring
    for candidate in deduped:
        _score_candidate(candidate, seed_company, market, extra_keywords)

    deduped.sort(key=lambda c: (c.seed_relevance, c.name), reverse=True)
    return deduped[:max_companies]


def _discover_legacy(
    seed_company: str,
    market: str,
    max_companies: int,
    extra_keywords: list[str] | None,
) -> list[DiscoveryCandidate]:
    """Legacy path: hardcoded catalog + CompetitorDataLoader expansion."""
    keywords = [k.lower() for k in (extra_keywords or [])]
    seed_tokens = [tok for tok in seed_company.lower().replace("/", " ").split() if tok]
    catalog = _catalog_for_market(market)

    if (
        "dutch" in market.lower()
        or "netherlands" in market.lower()
        or "energy" in market.lower()
    ) and max_companies > len(catalog):
        try:
            loader = CompetitorDataLoader()
            existing = {str(item["name"]).lower() for item in catalog}
            source_primary = "https://github.com/ai-whisperers/solstein/blob/main/data/input/competitor_data.json"
            for company in loader.load_companies():
                if company.name.lower() in existing:
                    continue
                catalog.append(
                    {
                        "name": company.name,
                        "ticker": None,
                        "industry": company.industry,
                        "region": (
                            ", ".join(company.geographic_presence)
                            if company.geographic_presence
                            else "NL/EU"
                        ),
                        "tags": (
                            company.tech_stack[:3]
                            if company.tech_stack
                            else ["energy", "software"]
                        ),
                        "sources": [source_primary],
                    }
                )
                existing.add(company.name.lower())
        except Exception as exc:
            logger.warning(
                "CompetitorDataLoader enrichment failed; proceeding without expansion: {}",
                exc,
            )

    scored: list[DiscoveryCandidate] = []
    for item in catalog:
        name = str(item["name"])
        src_links: list[str] = []
        sources_obj = item.get("sources")
        if isinstance(sources_obj, list):
            src_links = [str(s) for s in sources_obj]
        raw_tags = item.get("tags", [])
        tags_list = raw_tags if isinstance(raw_tags, list) else []
        tags = [str(t).lower() for t in tags_list]
        score = 0.0
        reasons: list[str] = []

        if any(tok in name.lower() for tok in seed_tokens):
            score += 3.0
            reasons.append("name similarity with seed")

        overlap = len(set(tags) & set(keywords))
        if overlap:
            score += float(overlap)
            reasons.append("keyword tag overlap")

        if (
            "latam" in market.lower()
            and str(item.get("region", "")).lower().find("latam") >= 0
        ):
            score += 1.0
            reasons.append("market region match")

        if any(
            k in tags for k in ["energy", "bank", "fintech", "payments", "software"]
        ):
            score += 0.5

        candidate = DiscoveryCandidate(
            company_id=_slugify(name),
            name=name,
            market=market,
            ticker=str(item["ticker"]) if item.get("ticker") else None,
            industry=str(item.get("industry", "Unknown")),
            region=str(item.get("region", "Unknown")),
            tags=[str(t) for t in tags_list],
            seed_relevance=score,
            discovery_reason=", ".join(reasons) or "catalog inclusion",
            source_links=src_links,
        )
        scored.append(candidate)

    scored.sort(key=lambda c: (c.seed_relevance, c.name), reverse=True)
    return scored[:max_companies]
