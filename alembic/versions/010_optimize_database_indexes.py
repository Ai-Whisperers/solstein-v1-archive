"""Optimize database indexes for common queries.

Revision ID: 010
Revises: 009
Create Date: 2026-02-27 22:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade: add indexes to optimize common queries."""

    # scoring_records table indexes
    op.create_index("ix_scoring_records_company_id", "scoring_records", ["company_id"])
    op.create_index("ix_scoring_records_created_at", "scoring_records", ["created_at"])
    op.create_index("ix_scoring_records_company_id_created_at", "scoring_records", ["company_id", "created_at"])

    # signal_records table indexes
    op.create_index("ix_signal_records_company_id", "signal_records", ["company_id"])
    op.create_index("ix_signal_records_signal_type", "signal_records", ["signal_type"])
    op.create_index("ix_signal_records_created_at", "signal_records", ["created_at"])
    op.create_index("ix_signal_records_company_id_signal_type", "signal_records", ["company_id", "signal_type"])

    # market_snapshots table indexes
    op.create_index("ix_market_snapshots_snapshot_date", "market_snapshots", ["snapshot_date"])
    op.create_index("ix_market_snapshots_created_at", "market_snapshots", ["created_at"])

    # research_runs table indexes
    op.create_index("ix_research_runs_company_id", "research_runs", ["company_id"])
    op.create_index("ix_research_runs_status", "research_runs", ["status"])
    op.create_index("ix_research_runs_created_at", "research_runs", ["created_at"])
    op.create_index("ix_research_runs_company_id_status", "research_runs", ["company_id", "status"])

    # research_stages table indexes
    op.create_index("ix_research_stages_research_run_id", "research_stages", ["research_run_id"])
    op.create_index("ix_research_stages_stage_name", "research_stages", ["stage_name"])
    op.create_index("ix_research_stages_status", "research_stages", ["status"])

    # research_artifacts table indexes
    op.create_index("ix_research_artifacts_research_run_id", "research_artifacts", ["research_run_id"])
    op.create_index("ix_research_artifacts_artifact_type", "research_artifacts", ["artifact_type"])

    # source_documents table indexes
    op.create_index("ix_source_documents_research_run_id", "source_documents", ["research_run_id"])
    op.create_index("ix_source_documents_source_url", "source_documents", ["source_url"])

    # metric_observations table indexes
    op.create_index("ix_metric_observations_research_run_id", "metric_observations", ["research_run_id"])
    op.create_index("ix_metric_observations_metric_name", "metric_observations", ["metric_name"])

    # evidence_readiness table indexes
    op.create_index("ix_evidence_readiness_research_run_id", "evidence_readiness", ["research_run_id"])
    op.create_index("ix_evidence_readiness_evidence_type", "evidence_readiness", ["evidence_type"])

    # research_contradictions table indexes
    op.create_index("ix_research_contradictions_research_run_id", "research_contradictions", ["research_run_id"])
    op.create_index("ix_research_contradictions_contradiction_type", "research_contradictions", ["contradiction_type"])

    # enrichment_audit_trail table indexes
    op.create_index("ix_enrichment_audit_trail_company_id", "enrichment_audit_trail", ["company_id"])
    op.create_index("ix_enrichment_audit_trail_job_id", "enrichment_audit_trail", ["job_id"])
    op.create_index("ix_enrichment_audit_trail_status", "enrichment_audit_trail", ["status"])
    op.create_index("ix_enrichment_audit_trail_created_at", "enrichment_audit_trail", ["created_at"])

    # enrichment_cache table indexes
    op.create_index("ix_enrichment_cache_company_id", "enrichment_cache", ["company_id"])
    op.create_index("ix_enrichment_cache_cache_key", "enrichment_cache", ["cache_key"])
    op.create_index("ix_enrichment_cache_company_id_cache_key", "enrichment_cache", ["company_id", "cache_key"])


def downgrade() -> None:
    """Downgrade: remove all added indexes."""

    # enrichment_cache table indexes
    op.drop_index("ix_enrichment_cache_company_id_cache_key", table_name="enrichment_cache")
    op.drop_index("ix_enrichment_cache_cache_key", table_name="enrichment_cache")
    op.drop_index("ix_enrichment_cache_company_id", table_name="enrichment_cache")

    # enrichment_audit_trail table indexes
    op.drop_index("ix_enrichment_audit_trail_created_at", table_name="enrichment_audit_trail")
    op.drop_index("ix_enrichment_audit_trail_status", table_name="enrichment_audit_trail")
    op.drop_index("ix_enrichment_audit_trail_job_id", table_name="enrichment_audit_trail")
    op.drop_index("ix_enrichment_audit_trail_company_id", table_name="enrichment_audit_trail")

    # research_contradictions table indexes
    op.drop_index("ix_research_contradictions_contradiction_type", table_name="research_contradictions")
    op.drop_index("ix_research_contradictions_research_run_id", table_name="research_contradictions")

    # evidence_readiness table indexes
    op.drop_index("ix_evidence_readiness_evidence_type", table_name="evidence_readiness")
    op.drop_index("ix_evidence_readiness_research_run_id", table_name="evidence_readiness")

    # metric_observations table indexes
    op.drop_index("ix_metric_observations_metric_name", table_name="metric_observations")
    op.drop_index("ix_metric_observations_research_run_id", table_name="metric_observations")

    # source_documents table indexes
    op.drop_index("ix_source_documents_source_url", table_name="source_documents")
    op.drop_index("ix_source_documents_research_run_id", table_name="source_documents")

    # research_artifacts table indexes
    op.drop_index("ix_research_artifacts_artifact_type", table_name="research_artifacts")
    op.drop_index("ix_research_artifacts_research_run_id", table_name="research_artifacts")

    # research_stages table indexes
    op.drop_index("ix_research_stages_status", table_name="research_stages")
    op.drop_index("ix_research_stages_stage_name", table_name="research_stages")
    op.drop_index("ix_research_stages_research_run_id", table_name="research_stages")

    # research_runs table indexes
    op.drop_index("ix_research_runs_company_id_status", table_name="research_runs")
    op.drop_index("ix_research_runs_created_at", table_name="research_runs")
    op.drop_index("ix_research_runs_status", table_name="research_runs")
    op.drop_index("ix_research_runs_company_id", table_name="research_runs")

    # market_snapshots table indexes
    op.drop_index("ix_market_snapshots_created_at", table_name="market_snapshots")
    op.drop_index("ix_market_snapshots_snapshot_date", table_name="market_snapshots")

    # signal_records table indexes
    op.drop_index("ix_signal_records_company_id_signal_type", table_name="signal_records")
    op.drop_index("ix_signal_records_created_at", table_name="signal_records")
    op.drop_index("ix_signal_records_signal_type", table_name="signal_records")
    op.drop_index("ix_signal_records_company_id", table_name="signal_records")

    # scoring_records table indexes
    op.drop_index("ix_scoring_records_company_id_created_at", table_name="scoring_records")
    op.drop_index("ix_scoring_records_created_at", table_name="scoring_records")
    op.drop_index("ix_scoring_records_company_id", table_name="scoring_records")
