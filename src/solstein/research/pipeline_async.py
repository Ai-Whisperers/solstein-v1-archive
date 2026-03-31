"""Async research pipeline for market intelligence.

EPIC-023 Story 5: Converted from synchronous to async pipeline for better performance.

NOTE (STORY-256): The backward-compatible alias ``run_market_intelligence``
was removed in this module.  The canonical synchronous entry-point lives in
``solstein.research.pipeline.run_market_intelligence``.  If you need the
async variant, import ``run_market_intelligence_async`` explicitly.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path

from loguru import logger

from solstein.config import Settings

from .contracts import build_config_hash
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


async def run_market_intelligence_async(
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
    max_concurrent: int = 5,
) -> dict[str, object]:
    """Execute async market intelligence research pipeline.

    EPIC-023: Converted to async for improved performance through concurrent execution.

    Args:
        max_concurrent: Maximum number of concurrent operations per stage
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build adapter registry from settings
    from solstein.adapters.registry import build_default_registry

    settings = Settings.load()
    registry = build_default_registry(settings)
    batch_id = uuid.uuid4().hex[:12]
    logger.info(
        "Async pipeline run batch_id={}, registry has {} discovery + {} enrichment sources",
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

    # Execute pipeline with async stages
    for stage in stages:
        result = await stage.execute_async(context)
        artifact = stage.build_artifact(context, result)
        context.stages.append(artifact)

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


# STORY-256: Backward-compatibility alias removed.
# The canonical synchronous ``run_market_intelligence`` lives in
# ``solstein.research.pipeline``.  Import the async variant explicitly
# as ``run_market_intelligence_async`` when needed.
#
# Deletion trigger: this comment block can be removed once all callers
# have been audited (target: EPIC-067 completion).
