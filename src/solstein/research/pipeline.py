import hashlib
import json
import uuid
from pathlib import Path

from loguru import logger

from solstein.analytics.scoring import GrowthScorer
from solstein.config import Settings
from solstein.domain.models import Company, MarketAnalysis
from solstein.exporters.excel import ExcelExporter
from solstein.extractors.markdown_extractor import BatchExtractor
from solstein.infrastructure.database import db_manager
from solstein.infrastructure.research_dual_write import persist_research_run

from .discovery import DiscoveryCandidate, discover_companies
from .evidence import evaluate_market_evidence
from .gather import build_company_profile, enrich_company
from .reconcile import detect_market_contradictions
from .sources import canonicalize_url


def run_market_intelligence(
    seed_company: str,
    market: str,
    output_dir: Path,
    max_companies: int = 25,
    extra_keywords: list[str] | None = None,
    strict_provenance: bool = True,
    min_readiness_score: float | None = None,
    max_contradictions: int | None = None,
    min_total_sources: int | None = None,
    min_sources_per_company: int | None = None,
    db_dual_write: bool = False,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build adapter registry from settings (lazy import to avoid circular dependency)
    from solstein.adapters.registry import build_default_registry

    settings = Settings.load()
    registry = build_default_registry(settings)
    batch_id = uuid.uuid4().hex[:12]
    logger.info("Pipeline run batch_id={}, registry has {} discovery + {} enrichment sources",
                batch_id, len(registry.discovery_sources), len(registry.enrichment_sources))

    stages: list[dict[str, object]] = []
    stage_report: dict[str, object] = {
        "market": market,
        "seed_company": seed_company,
        "stages": stages,
    }

    candidates: list[DiscoveryCandidate] = discover_companies(
        seed_company=seed_company,
        market=market,
        max_companies=max_companies,
        extra_keywords=extra_keywords,
        registry=registry,
    )

    discovery_payload = [
        {
            "company_id": c.company_id,
            "name": c.name,
            "market": c.market,
            "ticker": c.ticker,
            "industry": c.industry,
            "region": c.region,
            "tags": c.tags,
            "seed_relevance": c.seed_relevance,
            "discovery_reason": c.discovery_reason,
            "source_links": c.source_links,
        }
        for c in candidates
    ]
    (output_dir / "discovery_candidates.json").write_text(
        json.dumps(discovery_payload, indent=2),
        encoding="utf-8",
    )
    stages.append(
        {
            "stage": "discovery",
            "description": "Discover related companies from market catalog and expansion rules.",
            "candidate_count": len(candidates),
        }
    )

    companies: list[Company] = [
        enrich_company(candidate, registry, batch_id) for candidate in candidates
    ]

    extracted_path = output_dir / "extracted.json"
    extracted_path.write_text(
        json.dumps(
            [company.model_dump(mode="json") for company in companies], indent=2
        ),
        encoding="utf-8",
    )

    unique_sources = set()
    for company in companies:
        for source in company.source_links:
            unique_sources.add(canonicalize_url(source))
    total_sources = len(unique_sources)
    avg_sources_per_company = total_sources / len(companies) if companies else 0.0

    # Per-company source quality breakdown
    quality_counts = {"well-sourced": 0, "partial": 0, "stub": 0, "unknown": 0}
    per_company_sources = []
    for company in companies:
        tier = company.data_quality_tier
        quality_counts[tier] = quality_counts.get(tier, 0) + 1
        per_company_sources.append({
            "company_id": company.id,
            "name": company.name,
            "enrichment_source_count": company.enrichment_source_count,
            "data_quality_tier": tier,
        })

    stages.append(
        {
            "stage": "gather",
            "description": "Enrich each discovered company with factual metrics and source links.",
            "profile_count": len(companies),
            "total_unique_sources": total_sources,
            "avg_unique_sources_per_company": round(avg_sources_per_company, 2),
            "data_quality_breakdown": quality_counts,
            "per_company_sources": per_company_sources,
        }
    )

    # Per-company source volume gate
    if min_sources_per_company is not None:
        under_threshold = [
            c for c in companies if c.enrichment_source_count < min_sources_per_company
        ]
        if under_threshold:
            stages.append(
                {
                    "stage": "per_company_source_gate",
                    "status": "filtered",
                    "required_min_sources_per_company": min_sources_per_company,
                    "companies_below_threshold": len(under_threshold),
                    "filtered_companies": [
                        {"company_id": c.id, "name": c.name, "sources": c.enrichment_source_count}
                        for c in under_threshold
                    ],
                }
            )
            companies = [c for c in companies if c.enrichment_source_count >= min_sources_per_company]
            logger.info(
                "Per-company source gate: filtered {} companies below {} sources, {} remain",
                len(under_threshold), min_sources_per_company, len(companies),
            )
            if not companies:
                (output_dir / "stage_report.json").write_text(
                    json.dumps(stage_report, indent=2), encoding="utf-8",
                )
                raise RuntimeError(
                    f"Per-company source gate removed all companies (threshold={min_sources_per_company})"
                )

    if min_total_sources is not None and total_sources < min_total_sources:
        stages.append(
            {
                "stage": "source_volume_gate",
                "status": "failed",
                "required_min_total_sources": min_total_sources,
                "observed_total_sources": total_sources,
                "message": "Insufficient source volume for requested evidence depth.",
            }
        )
        (output_dir / "stage_report.json").write_text(
            json.dumps(stage_report, indent=2),
            encoding="utf-8",
        )
        raise RuntimeError(
            f"Source volume gate failed: observed {total_sources}, required {min_total_sources}"
        )

    validator = BatchExtractor()
    violations = validator.validate_profiles_provenance(companies)
    (output_dir / "provenance_report.json").write_text(
        json.dumps(violations, indent=2),
        encoding="utf-8",
    )
    if strict_provenance and violations:
        raise RuntimeError(
            f"Provenance validation failed for {len(violations)} companies"
        )

    stages.append(
        {
            "stage": "provenance_validation",
            "description": "Validate required metrics have source links or explicit justifications.",
            "violating_profiles": len(violations),
            "status": "failed" if violations else "passed",
        }
    )

    contradiction_report = detect_market_contradictions(companies)
    (output_dir / "contradictions_report.json").write_text(
        json.dumps(contradiction_report, indent=2),
        encoding="utf-8",
    )

    if max_contradictions is not None:
        total_contradictions = sum(
            len(items)
            for items in contradiction_report.values()
            if isinstance(items, list)
        )
        if total_contradictions > max_contradictions:
            raise RuntimeError(
                f"Detected {total_contradictions} contradictions, above threshold {max_contradictions}"
            )

    stages.append(
        {
            "stage": "contradiction_detection",
            "description": "Detect conflicting observations for the same metric across sources.",
            "contradicted_profiles": len(contradiction_report),
            "total_contradictions": sum(
                len(items)
                for items in contradiction_report.values()
                if isinstance(items, list)
            ),
        }
    )

    evidence_report = evaluate_market_evidence(companies)
    (output_dir / "evidence_readiness.json").write_text(
        json.dumps(evidence_report, indent=2),
        encoding="utf-8",
    )

    if min_readiness_score is not None:
        avg_readiness_raw = evidence_report.get("average_readiness_score", 0.0)
        if isinstance(avg_readiness_raw, float):
            avg_readiness = avg_readiness_raw
        elif isinstance(avg_readiness_raw, int):
            avg_readiness = avg_readiness_raw * 1.0
        else:
            avg_readiness = 0.0
        if avg_readiness < min_readiness_score:
            raise RuntimeError(
                f"Average readiness score {avg_readiness:.2f} is below required threshold {min_readiness_score:.2f}"
            )

    stages.append(
        {
            "stage": "evidence_readiness",
            "description": "Score explainability and source-backed readiness for decision support.",
            "average_readiness_score": evidence_report["average_readiness_score"],
            "investment_ready_count": evidence_report["investment_ready_count"],
            "decision_support_ready_count": evidence_report[
                "decision_support_ready_count"
            ],
            "needs_more_evidence_count": evidence_report["needs_more_evidence_count"],
        }
    )

    scorer = GrowthScorer()
    scored = [scorer.calculate_scores(company) for company in companies]
    (output_dir / "scored.json").write_text(
        json.dumps([company.model_dump(mode="json") for company in scored], indent=2),
        encoding="utf-8",
    )

    analysis = MarketAnalysis(market_name=market, companies=scored)
    (output_dir / "market_analysis.json").write_text(
        json.dumps(analysis.model_dump(mode="json"), indent=2),
        encoding="utf-8",
    )

    ExcelExporter().create_dashboard(scored, output_dir / "dashboard.xlsx")

    stages.append(
        {
            "stage": "export",
            "description": "Export final scored profiles and dashboard artifacts.",
            "status": "completed",
        }
    )
    (output_dir / "stage_report.json").write_text(
        json.dumps(stage_report, indent=2),
        encoding="utf-8",
    )

    run_summary = {
        "market": market,
        "seed_company": seed_company,
        "discovered": len(candidates),
        "profiles": len(companies),
        "provenance_failures": len(violations),
        "contradicted_companies": len(contradiction_report),
        "total_contradictions": sum(
            len(items)
            for items in contradiction_report.values()
            if isinstance(items, list)
        ),
        "average_readiness_score": evidence_report["average_readiness_score"],
        "investment_ready_count": evidence_report["investment_ready_count"],
        "decision_support_ready_count": evidence_report["decision_support_ready_count"],
        "total_unique_sources": total_sources,
        "avg_unique_sources_per_company": round(avg_sources_per_company, 2),
        "output_dir": str(output_dir),
    }

    if db_dual_write:
        db_manager.settings = settings
        db_manager.init_sync()
        session = db_manager.get_sync_session()
        try:
            from solstein.infrastructure.database import Base

            if db_manager._sync_engine is None:
                raise RuntimeError("Synchronous database engine not initialized")
            Base.metadata.create_all(bind=db_manager._sync_engine)

            extra_keywords_norm = sorted(extra_keywords or [])
            run_id_seed = json.dumps(
                {
                    "market": market,
                    "seed_company": seed_company,
                    "max_companies": max_companies,
                    "extra_keywords": extra_keywords_norm,
                    "strict_provenance": strict_provenance,
                    "min_readiness_score": min_readiness_score,
                    "max_contradictions": max_contradictions,
                    "min_total_sources": min_total_sources,
                    "pipeline": "research.v2",
                },
                sort_keys=True,
            ).encode("utf-8")
            stable_run_id = hashlib.sha256(run_id_seed).hexdigest()

            persist_research_run(
                session=session,
                run_id=stable_run_id,
                market=market,
                seed_company=seed_company,
                strict_provenance=strict_provenance,
                min_readiness_score=min_readiness_score,
                max_contradictions=max_contradictions,
                min_total_sources=min_total_sources,
                stage_report=stage_report,
                artifacts={
                    "discovery_candidates": discovery_payload,
                    "extracted": [
                        company.model_dump(mode="json") for company in companies
                    ],
                    "provenance": violations,
                    "contradictions": contradiction_report,
                    "evidence_readiness": evidence_report,
                    "scored": [company.model_dump(mode="json") for company in scored],
                    "market_analysis": analysis.model_dump(mode="json"),
                    "stage_report": stage_report,
                    "run_summary": run_summary,
                },
            )
        finally:
            session.close()
            db_manager.close_sync()

    return run_summary
