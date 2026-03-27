"""Pipeline context for research pipeline stages.

This module provides the PipelineContext dataclass that holds shared state
across all pipeline stages during a research run.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from solstein.domain.models import Company, MarketAnalysis

if TYPE_CHECKING:
    from solstein.adapters.registry import SourceRegistry
    from solstein.research.discovery import DiscoveryCandidate


@dataclass
class PipelineConfig:
    """Configuration for the research pipeline."""

    seed_company: str
    market: str
    output_dir: Path
    max_companies: int = 25
    extra_keywords: list[str] | None = None
    strict_provenance: bool = True
    min_readiness_score: float | None = None
    max_contradictions: int | None = None
    min_total_sources: int | None = None
    min_sources_per_company: int | None = None
    db_dual_write: bool = False


@dataclass
class PipelineContext:
    """Shared context for all pipeline stages.

    This class holds the state that is passed between pipeline stages,
    including discovered candidates, enriched companies, and various reports.
    """

    # Configuration
    config: PipelineConfig
    registry: SourceRegistry
    batch_id: str

    # Stage tracking
    stages: list[dict[str, Any]] = field(default_factory=list)
    artifact_hashes: dict[str, str] = field(default_factory=dict)

    # Data
    candidates: list[DiscoveryCandidate] = field(default_factory=list)
    companies: list[Company] = field(default_factory=list)
    scored_companies: list[Company] = field(default_factory=list)
    analysis: MarketAnalysis | None = None

    # Reports
    violations: list[dict[str, Any]] = field(default_factory=list)
    contradiction_report: dict[str, Any] = field(default_factory=dict)
    evidence_report: dict[str, Any] = field(default_factory=dict)

    # Metadata
    total_sources: int = 0
    avg_sources_per_company: float = 0.0
    total_contradictions: int = 0

    # Version info
    artifact_schema_version: str = "1.0.0"
    model_version: str = "research.v2"
    prompt_version: str = "research.pipeline.v2"
    config_hash: str = ""

    @property
    def run_summary(self) -> dict[str, Any]:
        """Generate the run summary from current state."""
        return {
            "market": self.config.market,
            "seed_company": self.config.seed_company,
            "discovered": len(self.candidates),
            "profiles": len(self.companies),
            "provenance_failures": len(self.violations),
            "contradicted_companies": len(self.contradiction_report),
            "total_contradictions": self.total_contradictions,
            "average_readiness_score": self.evidence_report.get("average_readiness_score", 0.0),
            "investment_ready_count": self.evidence_report.get("investment_ready_count", 0),
            "decision_support_ready_count": self.evidence_report.get("decision_support_ready_count", 0),
            "total_unique_sources": self.total_sources,
            "avg_unique_sources_per_company": round(self.avg_sources_per_company, 2),
            "output_dir": str(self.config.output_dir),
        }

    def get_stage_report(self) -> dict[str, Any]:
        """Generate the stage report."""
        volatile_keys = {"analysis_date", "duration_ms", "last_updated", "stage_end", "stage_start"}

        def strip_volatile(value: Any) -> Any:
            if isinstance(value, dict):
                return {k: strip_volatile(v) for k, v in value.items() if k not in volatile_keys}
            if isinstance(value, list):
                return [strip_volatile(item) for item in value]
            return value

        stable_stages = [strip_volatile(stage) for stage in self.stages]
        return {
            "market": self.config.market,
            "seed_company": self.config.seed_company,
            "stages": stable_stages,
        }
