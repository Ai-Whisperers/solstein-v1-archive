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
from typing import Any

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
    """Execute market intelligence research pipeline.

    EPIC-020: Refactored from 505-line monolithic function to Pipeline Stage pattern.
    Each stage is now a separate class for better testability and maintainability.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build adapter registry from settings
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

    # Build configuration
    stage_config = {
        "market": market,
        "seed_company": seed_company,
        "max_companies": max_companies,
        "extra_keywords": sorted(extra_keywords or []),
        "strict_provenance": strict_provenance,
        "min_readiness_score": min_readiness_score,
        "max_contradictions": max_contradictions,
        "min_total_sources": min_total_sources,
        "min_sources_per_company": min_sources_per_company,
        "db_dual_write": db_dual_write,
    }
    config_hash = build_config_hash(stage_config)

    # Create pipeline context
    context = PipelineContext(
        batch_id=batch_id,
        output_dir=output_dir,
        registry=registry,
        config=stage_config,
        config_hash=config_hash,
    )

    # Define pipeline stages
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

    # Execute pipeline
    for stage in stages:
        result = stage.execute(context)
        artifact = stage.build_artifact(context, result)
        context.stages.append(artifact)

        if strict_provenance and stage.name == "evidence_readiness":
            gate = ReportReleaseGate(min_confidence=0.6, allow_synthetic=False)
            gate_result = gate.evaluate(context.companies)
            gate_payload = gate_result.to_dict()

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
            }
            context.stages.append(gate_artifact)

            if not gate_result.passed:
                reason_codes = ", ".join(sorted({reason.code for reason in gate_result.reasons}))
                raise RuntimeError(f"Quality gate failed before scoring: {reason_codes}")

    # Build run summary
    run_summary = {
        "market": market,
        "seed_company": seed_company,
        "discovered": len(context.companies),
        "profiles": len(context.companies),
        "scored": len(context.scored_companies),
        "output_dir": str(output_dir),
    }

    # Persist stage report
    context.artifact_hashes["run_summary"] = sha256_canonical_json(run_summary)
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

    return run_summary
