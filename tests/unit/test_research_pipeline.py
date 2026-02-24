# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownParameterType=false
# pyright: reportMissingParameterType=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnusedCallResult=false

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from solstein.domain.models import Company
from solstein.infrastructure.database import Base as BaseImported  # type: ignore
from solstein.infrastructure.database_models import OutboxRecord, ResearchRunRecord
from solstein.infrastructure.outbox_worker import process_outbox_records
from solstein.research import pipeline as research_pipeline
from solstein.research.discovery import discover_companies
from solstein.research.evidence import evaluate_company_evidence
from solstein.research.gather import build_company_profile
from solstein.research.pipeline import run_market_intelligence
from solstein.research.reconcile import detect_company_contradictions


def test_discover_companies_returns_ranked_candidates() -> None:
    candidates = discover_companies(
        seed_company="ueno",
        market="LATAM Financial Services",
        max_companies=10,
        extra_keywords=["bank", "payments", "fintech"],
    )

    assert len(candidates) == 10
    assert candidates[0].seed_relevance >= candidates[-1].seed_relevance
    assert any(candidate.name.lower().find("ueno") >= 0 for candidate in candidates)


def test_build_company_profile_without_ticker_is_explainable() -> None:
    candidate = discover_companies(
        seed_company="Eneve",
        market="Dutch Energy Software",
        max_companies=5,
        extra_keywords=["energy", "software"],
    )[0]

    profile = build_company_profile(candidate)
    assert profile.source_links
    assert "revenue" in profile.metric_justifications
    assert profile.metric_justifications["revenue"]


def test_run_market_intelligence_writes_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _fake_profile(candidate) -> Company:
        return Company(
            id=candidate.company_id,
            name=candidate.name,
            industry=candidate.industry,
            source_links=candidate.source_links,
            metric_sources={
                "revenue": candidate.source_links,
                "growth_rate": candidate.source_links,
                "employees": candidate.source_links,
                "profit_margin": candidate.source_links,
                "funding": candidate.source_links,
                "valuation": candidate.source_links,
            },
        )

    monkeypatch.setattr(research_pipeline, "build_company_profile", _fake_profile)

    def _run() -> dict[str, object]:
        return run_market_intelligence(
            seed_company="ueno",
            market="LATAM Financial Services",
            output_dir=tmp_path,
            max_companies=5,
            extra_keywords=["bank", "fintech"],
            strict_provenance=False,
        )

    summary = _run()

    assert summary["discovered"] == 5
    for expected in [
        "discovery_candidates.json",
        "extracted.json",
        "stage_report.json",
        "provenance_report.json",
        "contradictions_report.json",
        "evidence_readiness.json",
        "scored.json",
        "market_analysis.json",
        "dashboard.xlsx",
    ]:
        assert (tmp_path / expected).exists()

    stage_report_a = cast(
        "dict[str, object]",
        json.loads((tmp_path / "stage_report.json").read_text(encoding="utf-8")),
    )
    artifact_hashes_a = cast("dict[str, str]", stage_report_a.get("artifact_hashes"))
    assert isinstance(artifact_hashes_a, dict)
    for key in [
        "discovery_candidates",
        "extracted",
        "provenance_report",
        "contradictions_report",
        "evidence_readiness",
        "scored",
        "market_analysis",
        "stage_report",
        "run_summary",
    ]:
        assert key in artifact_hashes_a
        assert isinstance(artifact_hashes_a[key], str)
        assert len(artifact_hashes_a[key]) == 64

    _run()

    stage_report_b = cast(
        "dict[str, object]",
        json.loads((tmp_path / "stage_report.json").read_text(encoding="utf-8")),
    )
    artifact_hashes_b = cast("dict[str, str]", stage_report_b.get("artifact_hashes"))
    assert artifact_hashes_b == artifact_hashes_a


def test_run_market_intelligence_source_volume_gate_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _fake_profile(candidate) -> Company:
        return Company(
            id=candidate.company_id,
            name=candidate.name,
            industry=candidate.industry,
            source_links=["https://example.com/source-a"],
            metric_sources={
                "revenue": ["https://example.com/source-a"],
                "growth_rate": ["https://example.com/source-a"],
                "employees": ["https://example.com/source-a"],
                "profit_margin": ["https://example.com/source-a"],
                "funding": ["https://example.com/source-a"],
                "valuation": ["https://example.com/source-a"],
            },
        )

    monkeypatch.setattr(research_pipeline, "build_company_profile", _fake_profile)

    with pytest.raises(RuntimeError, match="Source volume gate failed"):
        run_market_intelligence(
            seed_company="ueno",
            market="LATAM Financial Services",
            output_dir=tmp_path,
            max_companies=5,
            extra_keywords=["bank", "fintech"],
            strict_provenance=False,
            min_total_sources=20,
        )

    assert (tmp_path / "stage_report.json").exists()


def test_evidence_readiness_uses_sources_and_justifications() -> None:
    company = Company(
        id="c1",
        name="Company One",
        industry="Software",
        source_links=["https://example.com", "https://finance.yahoo.com/quote/ABC/"],
        metric_sources={
            "revenue": ["https://finance.yahoo.com/quote/ABC/"],
            "growth_rate": ["https://finance.yahoo.com/quote/ABC/"],
        },
        metric_justifications={
            "employees": "No audited source available in current feed.",
            "profit_margin": "No margin disclosure in source period.",
            "funding": "Private round data unavailable.",
            "valuation": "No direct valuation source for this period.",
        },
    )

    report = evaluate_company_evidence(company)
    assert report["source_count"] == 2
    explainability = report["metric_explainability"]
    assert isinstance(explainability, (int, float))
    assert float(explainability) >= 1.0
    assert report["unsupported_metrics"] == 0


def test_detect_company_contradictions_flags_divergence() -> None:
    company = Company(
        id="c2",
        name="Company Two",
        industry="Software",
        metric_observations={
            "revenue": [
                {"source": "https://a.example", "value": 100.0},
                {"source": "https://b.example", "value": 160.0},
            ]
        },
    )

    contradictions = detect_company_contradictions(company)
    assert contradictions
    assert contradictions[0]["metric"] == "revenue"


def test_run_market_intelligence_dual_write_sqlite(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "research_test.db"
    monkeypatch.setenv("SUPABASE__DB_URL", f"sqlite:///{db_path}")

    def _fake_profile(candidate) -> Company:
        return Company(
            id=candidate.company_id,
            name=candidate.name,
            industry=candidate.industry,
            source_links=[
                "https://example.com/source-a",
                "https://example.com/source-b",
            ],
            metric_sources={
                "revenue": ["https://example.com/source-a"],
                "growth_rate": ["https://example.com/source-a"],
                "employees": ["https://example.com/source-b"],
                "profit_margin": ["https://example.com/source-b"],
                "funding": ["https://example.com/source-a"],
                "valuation": ["https://example.com/source-a"],
            },
        )

    monkeypatch.setattr(research_pipeline, "build_company_profile", _fake_profile)

    run_market_intelligence(
        seed_company="ueno",
        market="LATAM Financial Services",
        output_dir=tmp_path / "out",
        max_companies=5,
        extra_keywords=["bank", "fintech"],
        strict_provenance=False,
        db_dual_write=True,
    )

    engine = create_engine(f"sqlite:///{db_path}")
    with Session(engine) as session:
        count = session.query(ResearchRunRecord).count()
        assert count >= 1
        outbox_record = session.query(OutboxRecord).one()
        assert outbox_record.status == "succeeded"
        assert outbox_record.attempt_count >= 1
        assert outbox_record.event_key.endswith(":research_run_persist")


def test_outbox_worker_replays_pending_records(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path = tmp_path / "research_outbox.db"
    monkeypatch.setenv("SUPABASE__DB_URL", f"sqlite:///{db_path}")

    def _fake_profile(candidate) -> Company:
        return Company(
            id=candidate.company_id,
            name=candidate.name,
            industry=candidate.industry,
            source_links=[
                "https://example.com/source-a",
                "https://example.com/source-b",
            ],
            metric_sources={
                "revenue": ["https://example.com/source-a"],
                "growth_rate": ["https://example.com/source-a"],
                "employees": ["https://example.com/source-b"],
                "profit_margin": ["https://example.com/source-b"],
                "funding": ["https://example.com/source-a"],
                "valuation": ["https://example.com/source-a"],
            },
        )

    monkeypatch.setattr(research_pipeline, "build_company_profile", _fake_profile)

    output_dir = tmp_path / "outbox"
    run_summary = run_market_intelligence(
        seed_company="ueno",
        market="LATAM Financial Services",
        output_dir=output_dir,
        max_companies=5,
        extra_keywords=["bank", "fintech"],
        strict_provenance=False,
        db_dual_write=False,
    )
    (output_dir / "run_summary.json").write_text(
        json.dumps(run_summary, indent=2), encoding="utf-8"
    )

    run_id = "test-run-outbox-001"
    event_key = f"{run_id}:research_run_persist"
    payload = {
        "run_id": run_id,
        "event_type": "research_run_persist",
        "market": run_summary["market"],
        "seed_company": run_summary["seed_company"],
        "strict_provenance": False,
        "min_readiness_score": None,
        "max_contradictions": None,
        "min_total_sources": None,
        "output_dir": str(output_dir),
    }

    engine = create_engine(f"sqlite:///{db_path}")
    BaseImported.metadata.create_all(bind=engine)  # type: ignore
    with Session(engine) as session:
        session.add(
            OutboxRecord(
                event_key=event_key,
                event_type="research_run_persist",
                status="pending",
                payload=payload,
                attempt_count=0,
                available_at=datetime.now(UTC),
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
                last_error=None,
            )
        )
        session.commit()

    processed = process_outbox_records(limit=5)
    assert processed == 1

    with Session(engine) as session:
        outbox_record = session.query(OutboxRecord).one()
        assert outbox_record.status == "succeeded"
        assert outbox_record.attempt_count == 1
        run_record = (
            session.query(ResearchRunRecord)
            .filter(ResearchRunRecord.run_id == run_id)
            .one()
        )
        assert run_record.summary is not None
