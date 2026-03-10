"""Research pipeline for market intelligence.

EPIC-020: Refactored from 505-line monolithic function to Pipeline Stage pattern.
Uses composition of stage classes for better testability and maintainability.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

from loguru import logger

from solstein.analytics.scoring import GrowthScorer
from solstein.config import Settings
from solstein.data.report_release_gate import ReportReleaseGate
from solstein.domain.models import Company, MarketAnalysis
from solstein.exporters.excel import ExcelExporter
from solstein.extractors.markdown_extractor import BatchExtractor
from solstein.infrastructure.database import db_manager
from solstein.infrastructure.research_dual_write import persist_research_run

from .contracts import StageName, build_config_hash, build_stage_artifact
from .discovery import DiscoveryCandidate, discover_companies
from .evidence import evaluate_market_evidence
from .gather import enrich_company
from .hashing import sha256_canonical_json
from .pipeline_stages import (
    AnalysisStage,
    ContradictionDetectionStage,
    DiscoveryStage,
    EvidenceReadinessStage,
    ExportStage,
    GatherStage,
    PerCompanySourceGate,
    PipelineContext,
    ProvenanceValidationStage,
    ScoringStage,
    SourceVolumeGate,
)
from .reconcile import detect_market_contradictions
from .sources import canonicalize_url


def _normalize_pipeline_options(options: dict[str, object]) -> dict[str, object]:
    normalized = {
        "max_companies": options.get("max_companies", 25),
        "extra_keywords": options.get("extra_keywords", []),
        "strict_provenance": options.get("strict_provenance", True),
        "min_readiness_score": options.get("min_readiness_score"),
        "max_contradictions": options.get("max_contradictions"),
        "min_total_sources": options.get("min_total_sources"),
        "min_sources_per_company": options.get("min_sources_per_company"),
        "db_dual_write": options.get("db_dual_write", False),
    }
    return normalized


def _run_quality_gate(context: PipelineContext, strict_provenance: bool) -> None:
    if not strict_provenance:
        return

    gate = ReportReleaseGate(min_confidence=0.6, allow_synthetic=False)
    gate_result = gate.evaluate(context.companies)
    gate_payload = gate_result.to_dict()
    resolved_override_ids: list[str] = []
    for reason in gate_result.reasons:
        if reason.code != "adjudication_override":
            continue
        details = cast("dict[str, Any]", reason.details or {})
        resolved_any = details.get("resolved_overrides", [])
        resolved = resolved_any if isinstance(resolved_any, list) else []
        for item in resolved:
            if not isinstance(item, dict):
                continue
            item_map = cast("dict[str, Any]", item)
            decision_id = item_map.get("decision_id")
            if isinstance(decision_id, str) and decision_id:
                resolved_override_ids.append(decision_id)

    context.artifact_hashes["quality_gate_report"] = sha256_canonical_json(gate_payload)
    (context.output_dir / "quality_gate_report.json").write_text(
        json.dumps(gate_payload, indent=2),
        encoding="utf-8",
    )

    gate_artifact: dict[str, object] = {
        "stage": "quality_gate",
        "config_hash": context.config_hash,
        "description": "Verify release quality gate before scoring stage.",
        "status": "passed" if gate_result.passed else "failed",
        "passed": gate_result.passed,
        "reason_count": len(gate_result.reasons),
        "reason_codes": sorted({reason.code for reason in gate_result.reasons}),
        "resolved_override_decision_ids": sorted(set(resolved_override_ids)),
    }
    context.stages.append(gate_artifact)

    if not gate_result.passed:
        reason_codes = ", ".join(sorted({reason.code for reason in gate_result.reasons}))
        raise RuntimeError(f"Quality gate failed before scoring: {reason_codes}")


def _execute_pipeline_stages(
    context: PipelineContext,
    options: dict[str, object],
) -> None:
    min_sources_per_company = cast("int | None", options["min_sources_per_company"])
    min_total_sources = cast("int | None", options["min_total_sources"])
    strict_provenance = cast(bool, options["strict_provenance"])
    max_contradictions = cast("int | None", options["max_contradictions"])
    min_readiness_score = cast("float | None", options["min_readiness_score"])
    db_dual_write = cast(bool, options["db_dual_write"])

    stages = [
        DiscoveryStage(),
        GatherStage(),
        PerCompanySourceGate(min_sources_per_company),
        SourceVolumeGate(min_total_sources),
        ProvenanceValidationStage(strict_provenance),
        ContradictionDetectionStage(max_contradictions),
        EvidenceReadinessStage(min_readiness_score),
        ScoringStage(),
        AnalysisStage(),
        ExportStage(db_dual_write),
    ]

    for stage in stages:
        result = stage.execute(context)
        artifact = stage.build_artifact(context, result)
        context.stages.append(artifact)
        if stage.name == "evidence_readiness":
            _run_quality_gate(context, strict_provenance)


def _persist_stage_report(
    *,
    context: PipelineContext,
    market: str,
    seed_company: str,
    output_dir: Path,
) -> None:
    stable_stages = [
        {k: v for k, v in stage.items() if k not in {"stage_start", "stage_end", "duration_ms"}}
        for stage in context.stages
    ]
    stage_report_base = {
        "market": market,
        "seed_company": seed_company,
        "stages": stable_stages,
    }
    context.artifact_hashes["stage_report"] = sha256_canonical_json(stage_report_base)
    (output_dir / "stage_report.json").write_text(
        json.dumps(stage_report_base, indent=2),
        encoding="utf-8",
    )


def run_market_intelligence(
    seed_company: str,
    market: str,
    output_dir: Path,
    options: dict[str, object] | None = None,
    **legacy_kwargs: object,
) -> dict[str, object]:
    merged_options = dict(options or {})
    merged_options.update(legacy_kwargs)
    normalized = _normalize_pipeline_options(merged_options)

    output_dir.mkdir(parents=True, exist_ok=True)

    from solstein.adapters.registry import build_default_registry

    settings = Settings.load()
    registry = build_default_registry(settings)
    batch_id = uuid.uuid4().hex[:12]
    logger.info(
        "Pipeline run batch_id={}, registry has {} discovery + {} enrichment sources",
        batch_id,
        len(registry.discovery_sources),
        len(registry.enrichment_sources),
    )

    stage_config = {
        "market": market,
        "seed_company": seed_company,
        "max_companies": normalized["max_companies"],
        "extra_keywords": sorted(cast("list[str]", normalized["extra_keywords"])),
        "strict_provenance": normalized["strict_provenance"],
        "min_readiness_score": normalized["min_readiness_score"],
        "max_contradictions": normalized["max_contradictions"],
        "min_total_sources": normalized["min_total_sources"],
        "min_sources_per_company": normalized["min_sources_per_company"],
        "db_dual_write": normalized["db_dual_write"],
    }
    context = PipelineContext(
        batch_id=batch_id,
        output_dir=output_dir,
        registry=registry,
        config=stage_config,
        config_hash=build_config_hash(stage_config),
    )

    _execute_pipeline_stages(context, normalized)

    run_summary = {
        "market": market,
        "seed_company": seed_company,
        "discovered": len(context.companies),
        "profiles": len(context.companies),
        "scored": len(context.scored_companies),
        "output_dir": str(output_dir),
    }
    context.artifact_hashes["run_summary"] = sha256_canonical_json(run_summary)
    _persist_stage_report(context=context, market=market, seed_company=seed_company, output_dir=output_dir)
    return run_summary
