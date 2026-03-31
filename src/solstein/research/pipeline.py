"""Research pipeline for market intelligence.

.. note:: CANONICAL RUNTIME — STORY-255 (2026-03-31)

   This sequential pipeline is the **canonical production runtime**.
   All new feature work, bug fixes, and optimizations target this path.
   The LangGraph graph runtime (``research/graph/``) is frozen and
   receives only security patches. See ``docs/architecture/decisions.md``.

EPIC-020: Refactored from 505-line monolithic function to Pipeline Stage pattern.
Uses composition of stage classes for better testability and maintainability.
"""

from __future__ import annotations

import json
import uuid
from collections import Counter
from pathlib import Path
from typing import Any, cast

from loguru import logger

from solstein.config import Settings
from solstein.data.report_release_gate import ReportReleaseGate

from .checkpoints import can_resume_from_checkpoint, load_latest_checkpoint, write_checkpoint
from .contracts import PipelineRunState, RunState, StageName, build_config_hash
from .gather import enrich_company as _compat_enrich_company
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
    PipelineStage,
    ProvenanceValidationStage,
    ScoringStage,
    SourceVolumeGate,
)

enrich_company = _compat_enrich_company
_RESEARCH_COUNTERS: Counter[str] = Counter()


def track_research_run_state_transition(from_state: str, to_state: str) -> None:
    _RESEARCH_COUNTERS[f"run_state_transition:{from_state}->{to_state}"] += 1


def track_research_checkpoint_write(state: str) -> None:
    _RESEARCH_COUNTERS[f"checkpoint_write:{state}"] += 1


def track_research_quality_gate_reason(reason_code: str) -> None:
    _RESEARCH_COUNTERS[f"quality_gate_reason:{reason_code}"] += 1


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
    for reason in gate_result.reasons:
        track_research_quality_gate_reason(reason.code)
    resolved_override_ids: list[str] = []
    for reason in gate_result.reasons:
        if reason.code != "adjudication_override":
            continue
        details = cast("dict[str, Any]", reason.details or {})
        resolved_any = details.get("resolved_overrides", [])
        resolved_items = cast("list[dict[str, Any]]", resolved_any if isinstance(resolved_any, list) else [])
        for item_map in resolved_items:
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
    stages_list = _stage_artifacts(context)
    stages_list.append(gate_artifact)

    if not gate_result.passed:
        reason_codes = ", ".join(sorted({reason.code for reason in gate_result.reasons}))
        raise RuntimeError(f"Quality gate failed before scoring: {reason_codes}")


def _execute_pipeline_stages(
    context: PipelineContext,
    options: dict[str, object],
    run_state: PipelineRunState,
) -> None:
    min_sources_per_company = cast("int | None", options["min_sources_per_company"])
    min_total_sources = cast("int | None", options["min_total_sources"])
    strict_provenance = cast(bool, options["strict_provenance"])
    max_contradictions = cast("int | None", options["max_contradictions"])
    min_readiness_score = cast("float | None", options["min_readiness_score"])
    db_dual_write = cast(bool, options["db_dual_write"])

    stages: list[PipelineStage] = [
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
        run_state.current_stage = cast(StageName, stage.name)
        stage_runner = cast(Any, stage)
        result = stage_runner.execute(context)
        artifact = stage_runner.build_artifact(context, result)
        stages_list = _stage_artifacts(context)
        stages_list.append(cast("dict[str, object]", artifact))
        _write_checkpoint(context, run_state)
        if stage.name == "evidence_readiness":
            _run_quality_gate(context, strict_provenance)
            _write_checkpoint(context, run_state)


def _write_checkpoint(context: PipelineContext, run_state: PipelineRunState) -> None:
    stages_list = _stage_artifacts(context)
    write_checkpoint(
        context.output_dir,
        run_id=run_state.run_id,
        state=run_state.state.value,
        current_stage=run_state.current_stage,
        reason=run_state.reason,
        stage_count=len(stages_list),
    )
    track_research_checkpoint_write(run_state.state.value)


def _persist_stage_report(
    *,
    context: PipelineContext,
    market: str,
    seed_company: str,
    output_dir: Path,
    run_state: PipelineRunState,
) -> None:
    stages_list = _stage_artifacts(context)
    stable_stages: list[dict[str, object]] = []
    for stage in stages_list:
        stage_map = stage
        stable_stages.append(
            {key: value for key, value in stage_map.items() if key not in {"stage_start", "stage_end", "duration_ms"}}
        )
    stage_report_base = {
        "market": market,
        "seed_company": seed_company,
        "run_state": run_state.model_dump(mode="json"),
        "stages": stable_stages,
    }
    context.artifact_hashes["stage_report"] = sha256_canonical_json(stage_report_base)
    (output_dir / "stage_report.json").write_text(
        json.dumps(stage_report_base, indent=2),
        encoding="utf-8",
    )


def _stage_artifacts(context: PipelineContext) -> list[dict[str, object]]:
    context_any = cast(Any, context)
    return cast("list[dict[str, object]]", context_any.stages)


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

    run_state = PipelineRunState(run_id=batch_id)
    track_research_run_state_transition(RunState.CREATED.value, RunState.RUNNING.value)
    run_state.transition_to(RunState.RUNNING)

    try:
        _execute_pipeline_stages(context, normalized, run_state)
        track_research_run_state_transition(RunState.RUNNING.value, RunState.COMPLETED.value)
        run_state.transition_to(RunState.COMPLETED)

        run_summary: dict[str, object] = {
            "market": market,
            "seed_company": seed_company,
            "discovered": len(context.companies),
            "profiles": len(context.companies),
            "scored": len(context.scored_companies),
            "output_dir": str(output_dir),
        }
        context.artifact_hashes["run_summary"] = sha256_canonical_json(run_summary)
        return run_summary
    except Exception as exc:
        logger.exception(
            "Market intelligence pipeline failed for market='{}', seed_company='{}', batch_id='{}'",
            market,
            seed_company,
            batch_id,
        )
        track_research_run_state_transition(RunState.RUNNING.value, RunState.FAILED.value)
        run_state.transition_to(RunState.FAILED, reason=str(exc))
        _write_checkpoint(context, run_state)
        raise
    finally:
        if run_state.state is RunState.COMPLETED:
            _write_checkpoint(context, run_state)
        _persist_stage_report(
            context=context,
            market=market,
            seed_company=seed_company,
            output_dir=output_dir,
            run_state=run_state,
        )


def resume_market_intelligence_run(output_dir: Path) -> dict[str, object]:
    checkpoint = load_latest_checkpoint(output_dir)
    if not can_resume_from_checkpoint(checkpoint):
        raise RuntimeError("No resumable checkpoint found")

    assert checkpoint is not None
    current_state = RunState(str(checkpoint.get("state", "failed")))
    run_state = PipelineRunState(
        run_id=str(checkpoint.get("run_id", "")),
        state=current_state,
        current_stage=cast("StageName | None", checkpoint.get("current_stage")),
        reason=cast("str | None", checkpoint.get("reason")),
    )

    track_research_run_state_transition(run_state.state.value, RunState.RUNNING.value)
    run_state.transition_to(RunState.RUNNING)
    write_checkpoint(
        output_dir,
        run_id=run_state.run_id,
        state=run_state.state.value,
        current_stage=run_state.current_stage,
        reason=run_state.reason,
        stage_count=int(checkpoint.get("stage_count", 0)),
    )
    track_research_checkpoint_write(run_state.state.value)
    return run_state.model_dump(mode="json")


def cancel_market_intelligence_run(output_dir: Path, reason: str) -> dict[str, object]:
    checkpoint = load_latest_checkpoint(output_dir)
    if checkpoint is None:
        raise RuntimeError("No checkpoint found to cancel")

    current_state = RunState(str(checkpoint.get("state", "failed")))
    run_state = PipelineRunState(
        run_id=str(checkpoint.get("run_id", "")),
        state=current_state,
        current_stage=cast("StageName | None", checkpoint.get("current_stage")),
        reason=cast("str | None", checkpoint.get("reason")),
    )

    track_research_run_state_transition(run_state.state.value, RunState.CANCELLED.value)
    run_state.transition_to(RunState.CANCELLED, reason=reason)
    write_checkpoint(
        output_dir,
        run_id=run_state.run_id,
        state=run_state.state.value,
        current_stage=run_state.current_stage,
        reason=run_state.reason,
        stage_count=int(checkpoint.get("stage_count", 0)),
    )
    track_research_checkpoint_write(run_state.state.value)
    return run_state.model_dump(mode="json")
