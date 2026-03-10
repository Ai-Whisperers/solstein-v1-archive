from __future__ import annotations

import json
from pathlib import Path
from typing import cast

import pytest

from solstein.data.report_release_gate import GateReason, ReportGateResult
from solstein.domain.models import Company
from solstein.research import pipeline as research_pipeline
from solstein.research.pipeline import run_market_intelligence


def test_run_market_intelligence_quality_gate_blocks_before_scoring(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _fake_enrich(candidate, registry, batch_id) -> Company:
        return Company(
            id=candidate.company_id,
            name=candidate.name,
            industry=candidate.industry,
            source_links=candidate.source_links,
            metric_sources={
                "revenue": [],
                "growth_rate": candidate.source_links,
                "employees": candidate.source_links,
                "profit_margin": candidate.source_links,
                "funding": candidate.source_links,
                "valuation": candidate.source_links,
            },
        )

    monkeypatch.setattr(research_pipeline, "enrich_company", _fake_enrich)

    with pytest.raises(RuntimeError, match="Quality gate failed before scoring"):
        run_market_intelligence(
            seed_company="ueno",
            market="LATAM Financial Services",
            output_dir=tmp_path,
            max_companies=5,
            extra_keywords=["bank", "fintech"],
            strict_provenance=True,
        )

    assert (tmp_path / "quality_gate_report.json").exists()


def test_run_market_intelligence_quality_gate_passes_with_valid_batch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _always_pass(self, companies, **kwargs):
        return ReportGateResult(passed=True, reasons=[])

    monkeypatch.setattr("solstein.data.report_release_gate.ReportReleaseGate.evaluate", _always_pass)

    summary = run_market_intelligence(
        seed_company="ueno",
        market="LATAM Financial Services",
        output_dir=tmp_path,
        max_companies=5,
        extra_keywords=["bank", "fintech"],
        strict_provenance=True,
    )

    assert summary["profiles"] == 5
    assert (tmp_path / "quality_gate_report.json").exists()


def test_run_market_intelligence_quality_gate_blocks_synthetic_batch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _synthetic_fail(self, companies, **kwargs):
        reason = GateReason(
            code="synthetic_data",
            message="Synthetic or mixed data detected",
            details={"company": "Synthetic Co", "data_source_type": "synthetic"},
        )
        return ReportGateResult(passed=False, reasons=[reason])

    monkeypatch.setattr("solstein.data.report_release_gate.ReportReleaseGate.evaluate", _synthetic_fail)

    with pytest.raises(RuntimeError, match="synthetic_data"):
        run_market_intelligence(
            seed_company="ueno",
            market="LATAM Financial Services",
            output_dir=tmp_path,
            max_companies=5,
            extra_keywords=["bank", "fintech"],
            strict_provenance=True,
        )

    assert (tmp_path / "quality_gate_report.json").exists()


def test_run_market_intelligence_quality_gate_artifact_includes_override_decisions(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _override_only(self, companies, **kwargs):
        reason = GateReason(
            code="adjudication_override",
            message="resolved by reviewer",
            details={
                "resolved_overrides": [
                    {"metric": "revenue", "decision_id": "dec-1001"},
                    {"metric": "funding", "decision_id": "dec-1002"},
                ]
            },
        )
        return ReportGateResult(passed=True, reasons=[reason])

    monkeypatch.setattr("solstein.data.report_release_gate.ReportReleaseGate.evaluate", _override_only)

    run_market_intelligence(
        seed_company="ueno",
        market="LATAM Financial Services",
        output_dir=tmp_path,
        max_companies=5,
        extra_keywords=["bank", "fintech"],
        strict_provenance=True,
    )

    stage_report = cast(
        "dict[str, object]",
        json.loads((tmp_path / "stage_report.json").read_text(encoding="utf-8")),
    )
    stages = cast("list[dict[str, object]]", stage_report.get("stages", []))
    quality_stage = next(stage for stage in stages if stage.get("stage") == "quality_gate")
    assert quality_stage["resolved_override_decision_ids"] == ["dec-1001", "dec-1002"]
