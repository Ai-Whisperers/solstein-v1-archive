"""Research pipeline stages for market intelligence.

EPIC-020: Refactored from monolithic run_market_intelligence function.
Uses Pipeline Stage pattern to break down 505-line function into manageable stages.
"""

from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from loguru import logger

from solstein.analytics.scoring import GrowthScorer
from solstein.domain.models import Company, MarketAnalysis
from solstein.exporters.excel import ExcelExporter
from solstein.extractors.markdown_extractor import BatchExtractor

from .contracts import StageName, build_stage_artifact
from .discovery import DiscoveryCandidate, discover_companies
from .evidence import evaluate_market_evidence
from .gather import enrich_company
from .hashing import sha256_canonical_json
from .reconcile import detect_market_contradictions
from .sources import canonicalize_url


@dataclass
class PipelineContext:
    """Context object passed through pipeline stages."""

    batch_id: str
    output_dir: Path
    registry: Any
    config: dict[str, Any]
    config_hash: str
    artifact_hashes: dict[str, str] = field(default_factory=dict)
    stages: list[dict] = field(default_factory=list)
    companies: list[Company] = field(default_factory=list)
    scored_companies: list[Company] = field(default_factory=list)
    analysis: MarketAnalysis | None = None


@dataclass
class StageResult:
    """Result from a pipeline stage."""

    gate_decision: str
    description: str
    status: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    error_class: str | None = None


class PipelineStage(ABC):
    """Abstract base class for pipeline stages."""

    def __init__(self, name: StageName):
        self.name = name
        self._start_time: float = 0.0
        self._start_iso: str = ""

    def _start_timer(self) -> None:
        """Start stage timer."""
        self._start_iso = datetime.now(timezone.utc).isoformat()
        self._start_time = time.monotonic()

    def _get_duration_ms(self) -> int:
        """Get elapsed duration in milliseconds."""
        return int((time.monotonic() - self._start_time) * 1000)

    def execute(self, context: PipelineContext, **kwargs) -> StageResult:
        """Execute the stage and return result."""
        self._start_timer()
        logger.info(f"Starting stage: {self.name}")

        try:
            result = self._run(context)
            logger.info(f"Completed stage: {self.name} ({self._get_duration_ms()}ms)")
            return result
        except Exception as e:
            logger.error(f"Stage {self.name} failed: {e}")
            raise

    async def execute_async(self, context: PipelineContext) -> StageResult:
        """Execute the stage asynchronously."""
        self._start_timer()
        logger.info(f"Starting async stage: {self.name}")

        try:
            result = await self._run_async(context)
            logger.info(f"Completed async stage: {self.name} ({self._get_duration_ms()}ms)")
            return result
        except Exception as e:
            logger.error(f"Async stage {self.name} failed: {e}")
            raise

    @abstractmethod
    def _run(self, context: PipelineContext) -> StageResult:
        """Implement stage logic."""
        pass

    async def _run_async(self, context: PipelineContext) -> StageResult:
        """Implement async stage logic. Default delegates to sync version."""
        import asyncio

        return await asyncio.to_thread(self._run, context)

    def build_artifact(
        self,
        context: PipelineContext,
        result: StageResult,
        artifact_schema_version: str = "1.0.0",
        model_version: str = "research.v2",
        prompt_version: str = "research.pipeline.v2",
    ) -> dict[str, Any]:
        """Build stage artifact for reporting."""
        return build_stage_artifact(
            stage=self.name,
            artifact_schema_version=artifact_schema_version,
            model_version=model_version,
            prompt_version=prompt_version,
            config_hash=context.config_hash,
            description=result.description,
            status=result.status,
            payload=result.payload,
        )


class DiscoveryStage(PipelineStage):
    """Stage 1: Discover companies from market catalog."""

    def __init__(self):
        super().__init__("discovery")

    def _run(self, context: PipelineContext) -> StageResult:
        candidates: list[DiscoveryCandidate] = discover_companies(
            seed_company=context.config["seed_company"],
            market=context.config["market"],
            max_companies=context.config["max_companies"],
            extra_keywords=context.config.get("extra_keywords"),
            registry=context.registry,
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

        context.artifact_hashes["discovery_candidates"] = sha256_canonical_json(discovery_payload)
        (context.output_dir / "discovery_candidates.json").write_text(
            json.dumps(discovery_payload, indent=2),
            encoding="utf-8",
        )

        return StageResult(
            gate_decision="passed",
            description="Discover related companies from market catalog and expansion rules.",
            payload={"candidate_count": len(candidates)},
        )


class GatherStage(PipelineStage):
    """Stage 2: Enrich discovered companies with data."""

    def __init__(self):
        super().__init__("gather")

    def _run(self, context: PipelineContext) -> StageResult:
        # Get candidates from discovery stage (would need to pass them through context)
        # For now, re-discover (this could be optimized)
        candidates: list[DiscoveryCandidate] = discover_companies(
            seed_company=context.config["seed_company"],
            market=context.config["market"],
            max_companies=context.config["max_companies"],
            extra_keywords=context.config.get("extra_keywords"),
            registry=context.registry,
        )

        companies: list[Company] = [
            enrich_company(candidate, context.registry, context.batch_id) for candidate in candidates
        ]
        context.companies = companies

        extracted_payload = [company.model_dump(mode="json") for company in companies]
        context.artifact_hashes["extracted"] = sha256_canonical_json(extracted_payload)
        (context.output_dir / "extracted.json").write_text(
            json.dumps(extracted_payload, indent=2),
            encoding="utf-8",
        )

        unique_sources = set()
        for company in companies:
            for source in company.source_links:
                unique_sources.add(canonicalize_url(source))

        total_sources = len(unique_sources)
        avg_sources_per_company = total_sources / len(companies) if companies else 0.0

        quality_counts = {"well-sourced": 0, "partial": 0, "stub": 0, "unknown": 0}
        per_company_sources = []

        for company in companies:
            tier = company.data_quality_tier
            quality_counts[tier] = quality_counts.get(tier, 0) + 1
            per_company_sources.append(
                {
                    "company_id": company.id,
                    "name": company.name,
                    "enrichment_source_count": company.enrichment_source_count,
                    "data_quality_tier": tier,
                }
            )

        return StageResult(
            gate_decision="passed",
            description="Enrich each discovered company with factual metrics and source links.",
            payload={
                "profile_count": len(companies),
                "total_unique_sources": total_sources,
                "avg_unique_sources_per_company": round(avg_sources_per_company, 2),
                "data_quality_breakdown": quality_counts,
                "per_company_sources": per_company_sources,
            },
        )


class PerCompanySourceGate(PipelineStage):
    """Gate: Filter companies below per-company source threshold."""

    def __init__(self, min_sources: int | None):
        super().__init__("per_company_source_gate")
        self.min_sources = min_sources

    def _run(self, context: PipelineContext) -> StageResult:
        if self.min_sources is None:
            return StageResult(
                gate_decision="not_applicable",
                description="Per-company source gate disabled.",
            )

        under_threshold = [c for c in context.companies if c.enrichment_source_count < self.min_sources]

        if under_threshold:
            context.companies = [c for c in context.companies if c.enrichment_source_count >= self.min_sources]
            logger.info(
                "Per-company source gate: filtered {} companies below {} sources, {} remain",
                len(under_threshold),
                self.min_sources,
                len(context.companies),
            )

            if not context.companies:
                raise RuntimeError(f"Per-company source gate removed all companies (threshold={self.min_sources})")

            return StageResult(
                gate_decision="filtered",
                description="Filter companies below per-company source threshold.",
                status="filtered",
                payload={
                    "required_min_sources_per_company": self.min_sources,
                    "companies_below_threshold": len(under_threshold),
                    "filtered_companies": [
                        {"company_id": c.id, "name": c.name, "sources": c.enrichment_source_count}
                        for c in under_threshold
                    ],
                },
            )

        return StageResult(
            gate_decision="passed",
            description="All companies meet per-company source threshold.",
        )


class SourceVolumeGate(PipelineStage):
    """Gate: Check total source volume meets requirements."""

    def __init__(self, min_total_sources: int | None):
        super().__init__("source_volume_gate")
        self.min_total_sources = min_total_sources

    def _run(self, context: PipelineContext) -> StageResult:
        if self.min_total_sources is None:
            return StageResult(
                gate_decision="not_applicable",
                description="Source volume gate disabled.",
            )

        unique_sources = set()
        for company in context.companies:
            for source in company.source_links:
                unique_sources.add(canonicalize_url(source))

        total_sources = len(unique_sources)

        if total_sources < self.min_total_sources:
            raise RuntimeError(
                f"Source volume gate failed: observed {total_sources}, required {self.min_total_sources}"
            )

        return StageResult(
            gate_decision="passed",
            description="Total source volume meets requirements.",
            payload={"total_sources": total_sources},
        )


class ProvenanceValidationStage(PipelineStage):
    """Stage: Validate required metrics have source links."""

    def __init__(self, strict: bool = True):
        super().__init__("provenance_validation")
        self.strict = strict

    def _run(self, context: PipelineContext) -> StageResult:
        validator = BatchExtractor()
        violations = validator.validate_profiles_provenance(context.companies)

        context.artifact_hashes["provenance_report"] = sha256_canonical_json(violations)
        (context.output_dir / "provenance_report.json").write_text(
            json.dumps(violations, indent=2),
            encoding="utf-8",
        )

        has_violations = len(violations) > 0

        if self.strict and has_violations:
            raise RuntimeError(f"Provenance validation failed for {len(violations)} companies")

        return StageResult(
            gate_decision="failed" if has_violations else "passed",
            description="Validate required metrics have source links or explicit justifications.",
            status="failed" if has_violations else "passed",
            error_class="ProvenanceValidationError" if has_violations else None,
            payload={"violating_profiles": len(violations)},
        )


class ContradictionDetectionStage(PipelineStage):
    """Stage: Detect conflicting observations across sources."""

    def __init__(self, max_contradictions: int | None = None):
        super().__init__("contradiction_detection")
        self.max_contradictions = max_contradictions

    def _run(self, context: PipelineContext) -> StageResult:
        contradiction_report = detect_market_contradictions(context.companies)

        context.artifact_hashes["contradictions_report"] = sha256_canonical_json(contradiction_report)
        (context.output_dir / "contradictions_report.json").write_text(
            json.dumps(contradiction_report, indent=2),
            encoding="utf-8",
        )

        total_contradictions = sum(len(items) for items in contradiction_report.values() if isinstance(items, list))

        if self.max_contradictions is not None and total_contradictions > self.max_contradictions:
            raise RuntimeError(
                f"Detected {total_contradictions} contradictions, above threshold {self.max_contradictions}"
            )

        return StageResult(
            gate_decision="not_applicable",
            description="Detect conflicting observations for the same metric across sources.",
            payload={
                "contradicted_profiles": len(contradiction_report),
                "total_contradictions": total_contradictions,
            },
        )


class EvidenceReadinessStage(PipelineStage):
    """Stage: Score explainability and source-backed readiness."""

    def __init__(self, min_readiness_score: float | None = None):
        super().__init__("evidence_readiness")
        self.min_readiness_score = min_readiness_score

    def _run(self, context: PipelineContext) -> StageResult:
        evidence_report = evaluate_market_evidence(context.companies)

        context.artifact_hashes["evidence_readiness"] = sha256_canonical_json(evidence_report)
        (context.output_dir / "evidence_readiness.json").write_text(
            json.dumps(evidence_report, indent=2),
            encoding="utf-8",
        )

        if self.min_readiness_score is not None:
            avg_readiness = evidence_report.get("average_readiness_score", 0.0)
            if isinstance(avg_readiness, (int, float)) and avg_readiness < self.min_readiness_score:
                raise RuntimeError(
                    f"Average readiness score {avg_readiness:.2f} is below required threshold {self.min_readiness_score:.2f}"
                )

        return StageResult(
            gate_decision="not_applicable",
            description="Score explainability and source-backed readiness for decision support.",
            payload={
                "average_readiness_score": evidence_report.get("average_readiness_score"),
                "investment_ready_count": evidence_report.get("investment_ready_count"),
                "decision_support_ready_count": evidence_report.get("decision_support_ready_count"),
                "needs_more_evidence_count": evidence_report.get("needs_more_evidence_count"),
            },
        )


class ScoringStage(PipelineStage):
    """Stage: Compute growth and competitiveness scores."""

    def __init__(self):
        super().__init__("scoring")

    def _run(self, context: PipelineContext) -> StageResult:
        scorer = GrowthScorer()
        scored = [scorer.calculate_scores(company) for company in context.companies]
        context.scored_companies = scored

        scored_payload = [company.model_dump(mode="json") for company in scored]
        context.artifact_hashes["scored"] = sha256_canonical_json(scored_payload)
        (context.output_dir / "scored.json").write_text(
            json.dumps(scored_payload, indent=2),
            encoding="utf-8",
        )

        return StageResult(
            gate_decision="passed",
            description="Compute growth and competitiveness scores for each company profile.",
            payload={"scored_profiles": len(scored)},
        )


class AnalysisStage(PipelineStage):
    """Stage: Generate market analysis."""

    def __init__(self):
        super().__init__("analysis")

    def _run(self, context: PipelineContext) -> StageResult:
        analysis = MarketAnalysis(
            market_name=context.config["market"],
            companies=context.scored_companies,
        )
        context.analysis = analysis

        market_analysis_payload = analysis.model_dump(mode="json")
        context.artifact_hashes["market_analysis"] = sha256_canonical_json(market_analysis_payload)
        (context.output_dir / "market_analysis.json").write_text(
            json.dumps(market_analysis_payload, indent=2),
            encoding="utf-8",
        )

        return StageResult(
            gate_decision="passed",
            description="Aggregate market-level analysis across all scored companies.",
            payload={"market": context.config["market"], "company_count": len(context.scored_companies)},
        )


class ExportStage(PipelineStage):
    """Stage: Export results to Excel and persist to database."""

    def __init__(self, db_dual_write: bool = False):
        super().__init__("export")
        self.db_dual_write = db_dual_write

    def _run(self, context: PipelineContext) -> StageResult:
        # Export to Excel
        exporter = ExcelExporter()
        excel_path = context.output_dir / "market_analysis.xlsx"
        exporter.export_market_analysis(context.analysis, excel_path)

        # Persist to database if enabled
        if self.db_dual_write:
            from solstein.infrastructure.research_dual_write import persist_research_run

            persist_research_run(
                batch_id=context.batch_id,
                market=context.config["market"],
                companies=context.scored_companies,
                artifact_hashes=context.artifact_hashes,
            )

        return StageResult(
            gate_decision="passed",
            description="Export market analysis to Excel and persist to database.",
            payload={
                "excel_exported": True,
                "db_persisted": self.db_dual_write,
                "output_dir": str(context.output_dir),
            },
        )

    async def _run_async(self, context: PipelineContext) -> StageResult:
        """Async version with concurrent enrichment."""
        import asyncio

        # Get candidates from discovery stage
        candidates: list[DiscoveryCandidate] = discover_companies(
            seed_company=context.config["seed_company"],
            market=context.config["market"],
            max_companies=context.config["max_companies"],
            extra_keywords=context.config.get("extra_keywords"),
            registry=context.registry,
        )

        # Concurrent enrichment using asyncio.gather
        from .gather import enrich_company_async

        companies: list[Company] = await asyncio.gather(
            *[enrich_company_async(candidate, context.registry, context.batch_id) for candidate in candidates]
        )
        context.companies = companies

        extracted_payload = [company.model_dump(mode="json") for company in companies]
        context.artifact_hashes["extracted"] = sha256_canonical_json(extracted_payload)
        (context.output_dir / "extracted.json").write_text(
            json.dumps(extracted_payload, indent=2),
            encoding="utf-8",
        )

        unique_sources = set()
        for company in companies:
            for source in company.source_links:
                unique_sources.add(canonicalize_url(source))

        total_sources = len(unique_sources)
        avg_sources_per_company = total_sources / len(companies) if companies else 0.0

        quality_counts = {"well-sourced": 0, "partial": 0, "stub": 0, "unknown": 0}
        per_company_sources = []

        for company in companies:
            tier = company.data_quality_tier
            quality_counts[tier] = quality_counts.get(tier, 0) + 1
            per_company_sources.append(
                {
                    "company_id": company.id,
                    "name": company.name,
                    "enrichment_source_count": company.enrichment_source_count,
                    "data_quality_tier": tier,
                }
            )

        return StageResult(
            gate_decision="passed",
            description="Enrich each discovered company concurrently with asyncio.",
            payload={
                "profile_count": len(companies),
                "total_unique_sources": total_sources,
                "avg_unique_sources_per_company": round(avg_sources_per_company, 2),
                "data_quality_breakdown": quality_counts,
                "per_company_sources": per_company_sources,
                "concurrent": True,
            },
        )
