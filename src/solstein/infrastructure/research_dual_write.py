from datetime import UTC, datetime
from urllib.parse import urlparse
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from solstein.research.sources import canonicalize_url

from .database_models import (
    ContradictionRecord,
    EvidenceReadinessRecord,
    MetricObservationRecord,
    ResearchArtifactRecord,
    ResearchRunRecord,
    ResearchStageRecord,
    SourceDocumentRecord,
)


def persist_research_run(
    session: Session,
    run_id: str,
    market: str,
    seed_company: str,
    strict_provenance: bool,
    min_readiness_score: float | None,
    max_contradictions: int | None,
    min_total_sources: int | None,
    stage_report: dict[str, object],
    artifacts: dict[str, object],
) -> UUID:
    existing = session.execute(
        select(ResearchRunRecord).where(ResearchRunRecord.run_id == run_id)
    ).scalar_one_or_none()

    if existing is not None:
        session.query(ResearchStageRecord).filter(
            ResearchStageRecord.run_id == existing.id
        ).delete()
        session.query(ResearchArtifactRecord).filter(
            ResearchArtifactRecord.run_id == existing.id
        ).delete()
        session.query(SourceDocumentRecord).filter(
            SourceDocumentRecord.run_id == existing.id
        ).delete()
        session.query(MetricObservationRecord).filter(
            MetricObservationRecord.run_id == existing.id
        ).delete()
        session.query(EvidenceReadinessRecord).filter(
            EvidenceReadinessRecord.run_id == existing.id
        ).delete()
        session.query(ContradictionRecord).filter(
            ContradictionRecord.run_id == existing.id
        ).delete()
        session.delete(existing)
        session.flush()

    run = ResearchRunRecord(
        run_id=run_id,
        market=market,
        seed_company=seed_company,
        status="completed",
        strict_provenance=strict_provenance,
        min_readiness_score=min_readiness_score,
        max_contradictions=max_contradictions,
        min_total_sources=min_total_sources,
        summary=artifacts.get("run_summary"),
        created_at=datetime.now(UTC),
    )
    session.add(run)
    session.flush()

    run_pk = session.execute(
        select(ResearchRunRecord.id).where(ResearchRunRecord.run_id == run_id)
    ).scalar_one()

    stages: list[dict[str, object]] = []
    stages_obj = stage_report.get("stages")
    if isinstance(stages_obj, list):
        for stage in stages_obj:
            if isinstance(stage, dict):
                stages.append(stage)

    for idx, stage in enumerate(stages):
        stage_name = str(stage.get("stage", f"stage_{idx}"))
        status = stage.get("status")
        session.add(
            ResearchStageRecord(
                run_id=run.id,
                stage_name=stage_name,
                stage_order=idx,
                status=str(status) if status is not None else None,
                metrics=stage,
                created_at=datetime.now(UTC),
            )
        )

    for name, payload in artifacts.items():
        session.add(
            ResearchArtifactRecord(
                run_id=run.id,
                artifact_name=name,
                artifact_path=None,
                payload=payload,
                created_at=datetime.now(UTC),
            )
        )

    extracted = artifacts.get("extracted", [])
    if isinstance(extracted, list):
        for company in extracted:
            if not isinstance(company, dict):
                continue
            company_id = str(company.get("id", "unknown"))

            source_links = company.get("source_links", [])
            if isinstance(source_links, list):
                for source_url in source_links:
                    if not isinstance(source_url, str):
                        continue
                    canonical = canonicalize_url(source_url)
                    parsed = urlparse(canonical)
                    session.add(
                        SourceDocumentRecord(
                            run_id=run.id,
                            company_id=company_id,
                            source_url=canonical,
                            source_domain=(
                                parsed.netloc.lower() if parsed.netloc else None
                            ),
                            source_type="web",
                            observed_at=datetime.now(UTC),
                        )
                    )

            observations = company.get("metric_observations", {})
            if isinstance(observations, dict):
                for metric_key, rows in observations.items():
                    if not isinstance(rows, list):
                        continue
                    for row in rows:
                        if not isinstance(row, dict):
                            continue
                        raw_value = row.get("value")
                        metric_value: float | None
                        if isinstance(raw_value, (int, float)):
                            metric_value = float(raw_value)
                        else:
                            metric_value = None
                        session.add(
                            MetricObservationRecord(
                                run_id=run.id,
                                company_id=company_id,
                                metric_key=str(metric_key),
                                metric_value=metric_value,
                                metric_value_raw=raw_value,
                                source_url=(
                                    str(row.get("source"))
                                    if row.get("source") is not None
                                    else None
                                ),
                                created_at=datetime.now(UTC),
                            )
                        )

    readiness = artifacts.get("evidence_readiness", {})
    if isinstance(readiness, dict):
        company_reports = readiness.get("company_reports", [])
        if isinstance(company_reports, list):
            for report in company_reports:
                if not isinstance(report, dict):
                    continue
                session.add(
                    EvidenceReadinessRecord(
                        run_id=run.id,
                        company_id=str(report.get("company_id", "unknown")),
                        company_name=str(report.get("company_name", "unknown")),
                        readiness_score=float(
                            report.get("readiness_score", 0.0) or 0.0
                        ),
                        readiness_level=str(report.get("readiness_level", "unknown")),
                        source_count=int(report.get("source_count", 0) or 0),
                        source_domain_count=int(
                            report.get("source_domain_count", 0) or 0
                        ),
                        metric_source_coverage=float(
                            report.get("metric_source_coverage", 0.0) or 0.0
                        ),
                        metric_explainability=float(
                            report.get("metric_explainability", 0.0) or 0.0
                        ),
                        unsupported_metrics=int(
                            report.get("unsupported_metrics", 0) or 0
                        ),
                        created_at=datetime.now(UTC),
                    )
                )

    contradictions = artifacts.get("contradictions", {})
    if isinstance(contradictions, dict):
        for company_id, rows in contradictions.items():
            if not isinstance(rows, list):
                continue
            for row in rows:
                if not isinstance(row, dict):
                    continue
                session.add(
                    ContradictionRecord(
                        run_id=run.id,
                        company_id=str(company_id),
                        metric_key=str(row.get("metric", "unknown")),
                        contradiction_type=str(row.get("type", "unknown")),
                        details=row,
                        created_at=datetime.now(UTC),
                    )
                )

    session.commit()
    return run_pk
