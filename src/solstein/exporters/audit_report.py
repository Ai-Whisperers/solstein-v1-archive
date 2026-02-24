"""Markdown audit report generator for pipeline runs.

Reads JSON artifacts produced by ``run_market_intelligence()`` and
optional adapter health records to generate a structured markdown
audit document.
"""

from __future__ import annotations

import json
from datetime import timezone, datetime
from pathlib import Path
from typing import Any

from loguru import logger

# All 10 signal types from src/solstein/research/signals.py
_ALL_SIGNAL_NAMES = frozenset(
    {
        "revenue_level",
        "growth_rate",
        "profitability",
        "company_size",
        "valuation",
        "innovation",
        "ai_maturity",
        "hiring_velocity",
        "market_sentiment",
        "funding",
    }
)


class PipelineAuditReportGenerator:
    """Generates a markdown pipeline audit report from run artifacts."""

    def generate(
        self,
        artifacts_dir: Path,
        output_dir: Path | None = None,
        adapter_health: list[dict[str, Any]] | None = None,
    ) -> Path:
        """Generate audit report from pipeline output artifacts.

        Parameters
        ----------
        artifacts_dir:
            Directory containing pipeline JSON artifacts.
        output_dir:
            Where to write the audit report. Defaults to artifacts_dir.
        adapter_health:
            Optional list of AdapterHealthRecord dicts for the adapter
            health table.

        Returns
        -------
        Path to the generated markdown file.
        """
        output_dir = output_dir or artifacts_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        stage_report = self._load_artifact(artifacts_dir, "stage_report.json")
        candidates = self._load_artifact(artifacts_dir, "discovery_candidates.json")
        companies = self._load_artifact(artifacts_dir, "extracted.json")
        scored = self._load_artifact(artifacts_dir, "scored.json")
        contradictions = self._load_artifact(artifacts_dir, "contradictions_report.json")
        evidence = self._load_artifact(artifacts_dir, "evidence_readiness.json")

        market = stage_report.get("market", "Unknown") if stage_report else "Unknown"
        seed = (
            stage_report.get("seed_company", "Unknown") if stage_report else "Unknown"
        )
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        sections: list[str] = []
        sections.append(f"# Pipeline Audit Report — {market}\n")
        sections.append(f"**Seed company:** {seed}")
        sections.append(f"**Date:** {timestamp}")
        sections.append(f"**Pipeline version:** research.v2\n")

        if stage_report and candidates:
            sections.append(self._render_discovery_section(stage_report, candidates))
        if stage_report and companies:
            sections.append(self._render_enrichment_section(stage_report, companies))
        if companies:
            sections.append(
                self._render_aggregation_section(companies, contradictions or {})
            )
            sections.append(self._render_signal_section(companies))
        if scored:
            sections.append(self._render_scoring_section(scored))
        if evidence:
            sections.append(self._render_evidence_summary(evidence))
        if adapter_health:
            sections.append(self._render_adapter_health_section(adapter_health))

        report_text = "\n".join(sections) + "\n"
        filename = f"PIPELINE_AUDIT_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}_{_slug(market)}.md"
        output_path = output_dir / filename
        output_path.write_text(report_text, encoding="utf-8")
        logger.info("Audit report written to {}", output_path)
        return output_path

    # ------------------------------------------------------------------
    # Artifact loader
    # ------------------------------------------------------------------

    def _load_artifact(self, artifacts_dir: Path, filename: str) -> Any:
        path = artifacts_dir / filename
        if not path.exists():
            logger.warning("Artifact not found: {}", path)
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    # ------------------------------------------------------------------
    # Section renderers
    # ------------------------------------------------------------------

    def _render_discovery_section(
        self,
        stage_report: dict,
        candidates: list[dict],
    ) -> str:
        discovery_stage = next(
            (s for s in stage_report.get("stages", []) if s.get("stage") == "discovery"),
            None,
        )
        candidate_count = (
            discovery_stage.get("candidate_count", len(candidates))
            if discovery_stage
            else len(candidates)
        )
        lines = [
            "## Discovery\n",
            f"- Candidates discovered: **{candidate_count}**",
            f"- Final candidate list: **{len(candidates)}** companies",
            "",
        ]
        return "\n".join(lines)

    def _render_enrichment_section(
        self,
        stage_report: dict,
        companies: list[dict],
    ) -> str:
        gather_stage = next(
            (s for s in stage_report.get("stages", []) if s.get("stage") == "gather"),
            None,
        )
        quality_breakdown = (
            gather_stage.get("data_quality_breakdown", {}) if gather_stage else {}
        )

        lines = [
            "## Enrichment\n",
            "| Company | Sources Succeeded | Data Quality Tier | Signal Completeness |",
            "|---------|-------------------|-------------------|---------------------|",
        ]

        for company in companies:
            name = company.get("name", "Unknown")
            source_count = company.get("enrichment_source_count", 0)
            tier = company.get("data_quality_tier", "unknown")
            signal_conf = company.get("signal_confidences", {})
            completeness = f"{len(signal_conf)}/{len(_ALL_SIGNAL_NAMES)}"
            lines.append(f"| {name} | {source_count} | {tier} | {completeness} |")

        if quality_breakdown:
            lines.append("")
            lines.append("**Quality breakdown:** " + ", ".join(
                f"{tier}: {count}" for tier, count in quality_breakdown.items() if count
            ))

        lines.append("")
        return "\n".join(lines)

    def _render_aggregation_section(
        self,
        companies: list[dict],
        contradictions: dict,
    ) -> str:
        lines = [
            "## Aggregation Quality\n",
            "| Company | Observations | Contradictions | Avg Confidence |",
            "|---------|-------------|----------------|----------------|",
        ]

        for company in companies:
            name = company.get("name", "Unknown")
            cid = company.get("id", "")
            observations = company.get("metric_observations", {})
            obs_count = sum(len(v) for v in observations.values() if isinstance(v, list))
            company_contradictions = contradictions.get(cid, [])
            contradiction_count = (
                len(company_contradictions)
                if isinstance(company_contradictions, list)
                else 0
            )
            signal_conf = company.get("signal_confidences", {})
            avg_conf = (
                f"{sum(signal_conf.values()) / len(signal_conf):.2f}"
                if signal_conf
                else "N/A"
            )
            lines.append(
                f"| {name} | {obs_count} | {contradiction_count} | {avg_conf} |"
            )

        lines.append("")
        return "\n".join(lines)

    def _render_signal_section(self, companies: list[dict]) -> str:
        lines = [
            "## Signal Extraction\n",
            "| Company | Signals Produced | Avg Confidence | Missing Signals |",
            "|---------|-----------------|----------------|-----------------|",
        ]

        for company in companies:
            name = company.get("name", "Unknown")
            signal_conf = company.get("signal_confidences", {})
            produced = len(signal_conf)
            avg_conf = (
                f"{sum(signal_conf.values()) / len(signal_conf):.2f}"
                if signal_conf
                else "N/A"
            )
            missing = sorted(_ALL_SIGNAL_NAMES - set(signal_conf.keys()))
            missing_str = ", ".join(missing) if missing else "none"
            lines.append(f"| {name} | {produced} | {avg_conf} | {missing_str} |")

        lines.append("")
        return "\n".join(lines)

    def _render_scoring_section(self, scored: list[dict]) -> str:
        lines = [
            "## Scoring\n",
            "| Company | Growth | Financial Health | Competitive | Composite | Tier |",
            "|---------|--------|-----------------|-------------|-----------|------|",
        ]

        for company in scored:
            name = company.get("name", "Unknown")
            growth = _fmt_score(company.get("growth_score"))
            fin = _fmt_score(company.get("financial_health_score"))
            comp = _fmt_score(company.get("competitive_position_score"))
            composite = _fmt_score(company.get("composite_score"))
            tier = company.get("data_quality_tier", "unknown")
            lines.append(f"| {name} | {growth} | {fin} | {comp} | {composite} | {tier} |")

        lines.append("")
        return "\n".join(lines)

    def _render_evidence_summary(self, evidence: dict) -> str:
        lines = [
            "## Evidence Readiness\n",
            f"- Average readiness score: **{evidence.get('average_readiness_score', 'N/A')}**",
            f"- Investment-ready companies: **{evidence.get('investment_ready_count', 0)}**",
            f"- Decision-support-ready: **{evidence.get('decision_support_ready_count', 0)}**",
            f"- Needs more evidence: **{evidence.get('needs_more_evidence_count', 0)}**",
            "",
        ]
        return "\n".join(lines)

    def _render_adapter_health_section(
        self,
        health_records: list[dict[str, Any]],
    ) -> str:
        lines = [
            "## Adapter Health\n",
            "| Adapter | Type | Status | Response Time (ms) | Items | Error |",
            "|---------|------|--------|--------------------|-------|-------|",
        ]

        for record in health_records:
            name = record.get("adapter_name", "unknown")
            atype = record.get("adapter_type", "unknown")
            status = record.get("status", "unknown")
            ms = record.get("response_time_ms", 0)
            items = record.get("data_item_count", 0)
            error = record.get("error_message", "") or ""
            if len(error) > 60:
                error = error[:57] + "..."
            lines.append(f"| {name} | {atype} | {status} | {ms:.0f} | {items} | {error} |")

        lines.append("")
        return "\n".join(lines)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _slug(text: str) -> str:
    """Convert text to a filesystem-safe slug."""
    return text.lower().replace(" ", "_").replace("/", "_")[:40]


def _fmt_score(value: Any) -> str:
    """Format a score value for the table."""
    if value is None:
        return "N/A"
    if isinstance(value, (int, float)):
        return f"{value:.2f}"
    return str(value)
