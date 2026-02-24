import hashlib
import json
import time
from datetime import UTC, datetime
from pathlib import Path

from solstein.analytics.scoring import GrowthScorer
from solstein.config import Settings
from solstein.domain.models import Company, MarketAnalysis
from solstein.exporters.excel import ExcelExporter
from solstein.extractors.markdown_extractor import BatchExtractor
from solstein.infrastructure.database import db_manager
from solstein.infrastructure.research_dual_write import persist_research_run

from .contracts import StageName, build_config_hash, build_stage_artifact
from .discovery import DiscoveryCandidate, discover_companies
from .evidence import evaluate_market_evidence
from .gather import build_company_profile
from .hashing import sha256_canonical_json
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
    db_dual_write: bool = False,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)

    stages: list[dict[str, object]] = []
    artifact_hashes: dict[str, str] = {}
    stage_report: dict[str, object] = {
        "market": market,
        "seed_company": seed_company,
        "stages": stages,
        "artifact_hashes": artifact_hashes,
    }

    stage_config = {
        "market": market,
        "seed_company": seed_company,
        "max_companies": max_companies,
        "extra_keywords": sorted(extra_keywords or []),
        "strict_provenance": strict_provenance,
        "min_readiness_score": min_readiness_score,
        "max_contradictions": max_contradictions,
        "min_total_sources": min_total_sources,
        "db_dual_write": db_dual_write,
    }
    config_hash = build_config_hash(stage_config)
    artifact_schema_version = "1.0.0"
    model_version = "research.v1"
    prompt_version = "research.pipeline.v1"

    def _start_stage_timer() -> tuple[str, float]:
        return datetime.now(UTC).isoformat(), time.monotonic()

    def _append_stage_artifact(
        *,
        stage: StageName,
        stage_start: tuple[str, float],
        gate_decision: str,
        payload: dict[str, object] | None = None,
        status: str | None = None,
        description: str | None = None,
        error_class: str | None = None,
    ) -> None:
        stage_start_iso, stage_start_monotonic = stage_start
        stage_end_iso = datetime.now(UTC).isoformat()
        duration_ms = int((time.monotonic() - stage_start_monotonic) * 1000)
        stage_payload = dict(payload or {})
        stage_payload.update(
            {
                "stage_start": stage_start_iso,
                "stage_end": stage_end_iso,
                "duration_ms": duration_ms,
                "retry_count": 0,
                "gate_decision": gate_decision,
                "error_class": error_class if gate_decision == "failed" else None,
            }
        )
        stages.append(
            build_stage_artifact(
                stage=stage,
                artifact_schema_version=artifact_schema_version,
                model_version=model_version,
                prompt_version=prompt_version,
                config_hash=config_hash,
                description=description,
                status=status,
                payload=stage_payload,
            )
        )

    volatile_keys = {
        "analysis_date",
        "duration_ms",
        "last_updated",
        "stage_end",
        "stage_start",
    }

    def _strip_volatile_fields(value: object) -> object:
        if isinstance(value, dict):
            out: dict[str, object] = {}
            for k, v in value.items():
                if k in volatile_keys:
                    continue
                out[k] = _strip_volatile_fields(v)
            return out
        if isinstance(value, list):
            return [_strip_volatile_fields(item) for item in value]
        return value

    discovery_stage_start = _start_stage_timer()

    candidates: list[DiscoveryCandidate] = discover_companies(
        seed_company=seed_company,
        market=market,
        max_companies=max_companies,
        extra_keywords=extra_keywords,
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
    artifact_hashes["discovery_candidates"] = sha256_canonical_json(discovery_payload)
    (output_dir / "discovery_candidates.json").write_text(
        json.dumps(discovery_payload, indent=2),
        encoding="utf-8",
    )
    _append_stage_artifact(
        stage="discovery",
        stage_start=discovery_stage_start,
        gate_decision="passed",
        description="Discover related companies from market catalog and expansion rules.",
        payload={"candidate_count": len(candidates)},
    )

    gather_stage_start = _start_stage_timer()
    companies: list[Company] = [
        build_company_profile(candidate) for candidate in candidates
    ]

    extracted_payload = [company.model_dump(mode="json") for company in companies]
    artifact_hashes["extracted"] = sha256_canonical_json(
        _strip_volatile_fields(extracted_payload)
    )
    extracted_path = output_dir / "extracted.json"
    extracted_path.write_text(
        json.dumps(extracted_payload, indent=2),
        encoding="utf-8",
    )

    unique_sources = set()
    for company in companies:
        for source in company.source_links:
            unique_sources.add(canonicalize_url(source))
    total_sources = len(unique_sources)
    avg_sources_per_company = total_sources / len(companies) if companies else 0.0

    _append_stage_artifact(
        stage="gather",
        stage_start=gather_stage_start,
        gate_decision="passed",
        description="Enrich each discovered company with factual metrics and source links.",
        payload={
            "profile_count": len(companies),
            "total_unique_sources": total_sources,
            "avg_unique_sources_per_company": round(avg_sources_per_company, 2),
        },
    )

    source_volume_gate_stage_start = _start_stage_timer()
    if min_total_sources is not None and total_sources < min_total_sources:
        _append_stage_artifact(
            stage="source_volume_gate",
            stage_start=source_volume_gate_stage_start,
            gate_decision="failed",
            status="failed",
            error_class="SourceVolumeGateError",
            payload={
                "required_min_total_sources": min_total_sources,
                "observed_total_sources": total_sources,
                "message": "Insufficient source volume for requested evidence depth.",
            },
        )
        (output_dir / "stage_report.json").write_text(
            json.dumps(stage_report, indent=2),
            encoding="utf-8",
        )
        raise RuntimeError(
            f"Source volume gate failed: observed {total_sources}, required {min_total_sources}"
        )

    provenance_stage_start = _start_stage_timer()
    validator = BatchExtractor()
    violations = validator.validate_profiles_provenance(companies)
    artifact_hashes["provenance_report"] = sha256_canonical_json(violations)
    artifact_hashes["provenance"] = artifact_hashes["provenance_report"]
    (output_dir / "provenance_report.json").write_text(
        json.dumps(violations, indent=2),
        encoding="utf-8",
    )
    has_provenance_violations = len(violations) > 0

    _append_stage_artifact(
        stage="provenance_validation",
        stage_start=provenance_stage_start,
        gate_decision="failed" if has_provenance_violations else "passed",
        description="Validate required metrics have source links or explicit justifications.",
        status="failed" if has_provenance_violations else "passed",
        error_class="ProvenanceValidationError" if has_provenance_violations else None,
        payload={"violating_profiles": len(violations)},
    )

    if strict_provenance and has_provenance_violations:
        raise RuntimeError(
            f"Provenance validation failed for {len(violations)} companies"
        )

    contradiction_stage_start = _start_stage_timer()
    contradiction_report = detect_market_contradictions(companies)
    artifact_hashes["contradictions_report"] = sha256_canonical_json(
        contradiction_report
    )
    artifact_hashes["contradictions"] = artifact_hashes["contradictions_report"]
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

    total_contradictions = sum(
        len(items) for items in contradiction_report.values() if isinstance(items, list)
    )
    _append_stage_artifact(
        stage="contradiction_detection",
        stage_start=contradiction_stage_start,
        gate_decision="not_applicable",
        description="Detect conflicting observations for the same metric across sources.",
        payload={
            "contradicted_profiles": len(contradiction_report),
            "total_contradictions": total_contradictions,
        },
    )

    evidence_stage_start = _start_stage_timer()
    evidence_report = evaluate_market_evidence(companies)
    artifact_hashes["evidence_readiness"] = sha256_canonical_json(evidence_report)
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

    _append_stage_artifact(
        stage="evidence_readiness",
        stage_start=evidence_stage_start,
        gate_decision="not_applicable",
        description="Score explainability and source-backed readiness for decision support.",
        payload={
            "average_readiness_score": evidence_report["average_readiness_score"],
            "investment_ready_count": evidence_report["investment_ready_count"],
            "decision_support_ready_count": evidence_report[
                "decision_support_ready_count"
            ],
            "needs_more_evidence_count": evidence_report["needs_more_evidence_count"],
        },
    )

    scoring_stage_start = _start_stage_timer()
    scorer = GrowthScorer()
    scored = [scorer.calculate_scores(company) for company in companies]
    scored_payload = [company.model_dump(mode="json") for company in scored]
    artifact_hashes["scored"] = sha256_canonical_json(
        _strip_volatile_fields(scored_payload)
    )
    (output_dir / "scored.json").write_text(
        json.dumps(scored_payload, indent=2),
        encoding="utf-8",
    )
    _append_stage_artifact(
        stage="scoring",
        stage_start=scoring_stage_start,
        gate_decision="passed",
        description="Compute growth and competitiveness scores for each company profile.",
        payload={"scored_profiles": len(scored)},
    )

    analysis_stage_start = _start_stage_timer()
    analysis = MarketAnalysis(market_name=market, companies=scored)
    market_analysis_payload = analysis.model_dump(mode="json")
    artifact_hashes["market_analysis"] = sha256_canonical_json(
        _strip_volatile_fields(market_analysis_payload)
    )
    (output_dir / "market_analysis.json").write_text(
        json.dumps(market_analysis_payload, indent=2),
        encoding="utf-8",
    )
    _append_stage_artifact(
        stage="analysis",
        stage_start=analysis_stage_start,
        gate_decision="passed",
        description="Assemble market-level analytical view from scored company profiles.",
        payload={"analyzed_profiles": len(scored)},
    )

    export_stage_start = _start_stage_timer()
    ExcelExporter().create_dashboard(scored, output_dir / "dashboard.xlsx")

    _append_stage_artifact(
        stage="export",
        stage_start=export_stage_start,
        gate_decision="passed",
        description="Export final scored profiles and dashboard artifacts.",
        status="completed",
    )
    run_summary = {
        "market": market,
        "seed_company": seed_company,
        "discovered": len(candidates),
        "profiles": len(companies),
        "provenance_failures": len(violations),
        "contradicted_companies": len(contradiction_report),
        "total_contradictions": total_contradictions,
        "average_readiness_score": evidence_report["average_readiness_score"],
        "investment_ready_count": evidence_report["investment_ready_count"],
        "decision_support_ready_count": evidence_report["decision_support_ready_count"],
        "total_unique_sources": total_sources,
        "avg_unique_sources_per_company": round(avg_sources_per_company, 2),
        "output_dir": str(output_dir),
    }
    artifact_hashes["run_summary"] = sha256_canonical_json(run_summary)
    stable_stages = [
        {
            k: v
            for k, v in stage.items()
            if k not in {"stage_start", "stage_end", "duration_ms"}
        }
        for stage in stages
    ]
    stage_report_base = {
        "market": market,
        "seed_company": seed_company,
        "stages": stable_stages,
    }
    artifact_hashes["stage_report"] = sha256_canonical_json(stage_report_base)

    persist_stage_start = _start_stage_timer()
    if db_dual_write:
        settings = Settings.load()
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
                    "pipeline": "research.v1",
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
                    "extracted": extracted_payload,
                    "provenance": violations,
                    "contradictions": contradiction_report,
                    "evidence_readiness": evidence_report,
                    "scored": scored_payload,
                    "market_analysis": market_analysis_payload,
                    "stage_report": stage_report,
                    "run_summary": run_summary,
                },
            )
            _append_stage_artifact(
                stage="persist",
                stage_start=persist_stage_start,
                gate_decision="passed",
                status="completed",
                description="Persist run summary and stage artifacts into relational storage.",
                payload={"run_id": stable_run_id},
            )
        finally:
            session.close()
            db_manager.close_sync()
    else:
        _append_stage_artifact(
            stage="persist",
            stage_start=persist_stage_start,
            gate_decision="skipped",
            status="skipped",
            description="Persist stage skipped because db_dual_write is disabled.",
        )

    stable_stages = [
        {
            k: v
            for k, v in stage.items()
            if k not in {"stage_start", "stage_end", "duration_ms"}
        }
        for stage in stages
    ]
    stage_report_base = {
        "market": market,
        "seed_company": seed_company,
        "stages": stable_stages,
    }
    artifact_hashes["stage_report"] = sha256_canonical_json(stage_report_base)
    (output_dir / "stage_report.json").write_text(
        json.dumps(stage_report, indent=2),
        encoding="utf-8",
    )

    return run_summary
