"""Add database constraints and validation to all tables.

Revision ID: 010
Revises: 009
Create Date: 2026-02-27 21:45:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade: add CHECK constraints, NOT NULL constraints, and DEFAULT values."""

    # ===== scoring_records table =====
    # Add NOT NULL constraints
    op.alter_column("scoring_records", "score", nullable=False)
    op.alter_column("scoring_records", "company_id", nullable=False)
    op.alter_column("scoring_records", "created_at", nullable=False)

    # Add CHECK constraint for score range
    op.create_check_constraint("ck_scoring_records_score_range", "scoring_records", "score >= 0 AND score <= 100")

    # Add DEFAULT for created_at
    op.alter_column("scoring_records", "created_at", server_default=sa.text("CURRENT_TIMESTAMP"))

    # ===== signal_records table =====
    # Add NOT NULL constraints
    op.alter_column("signal_records", "signal_type", nullable=False)
    op.alter_column("signal_records", "value", nullable=False)
    op.alter_column("signal_records", "company_id", nullable=False)
    op.alter_column("signal_records", "created_at", nullable=False)

    # Add DEFAULT for created_at
    op.alter_column("signal_records", "created_at", server_default=sa.text("CURRENT_TIMESTAMP"))

    # ===== market_snapshots table =====
    # Add NOT NULL constraints
    op.alter_column("market_snapshots", "snapshot_date", nullable=False)
    op.alter_column("market_snapshots", "market_data", nullable=False)
    op.alter_column("market_snapshots", "created_at", nullable=False)

    # Add DEFAULT for created_at
    op.alter_column("market_snapshots", "created_at", server_default=sa.text("CURRENT_TIMESTAMP"))

    # ===== research_runs table =====
    # Add NOT NULL constraints
    op.alter_column("research_runs", "company_id", nullable=False)
    op.alter_column("research_runs", "status", nullable=False)
    op.alter_column("research_runs", "created_at", nullable=False)

    # Add DEFAULT values
    op.alter_column("research_runs", "created_at", server_default=sa.text("CURRENT_TIMESTAMP"))
    op.alter_column("research_runs", "status", server_default=sa.text("'pending'"))

    # ===== research_stages table =====
    # Add NOT NULL constraints
    op.alter_column("research_stages", "research_run_id", nullable=False)
    op.alter_column("research_stages", "stage_name", nullable=False)
    op.alter_column("research_stages", "status", nullable=False)

    # Add DEFAULT for status
    op.alter_column("research_stages", "status", server_default=sa.text("'pending'"))

    # ===== research_artifacts table =====
    # Add NOT NULL constraints
    op.alter_column("research_artifacts", "research_run_id", nullable=False)
    op.alter_column("research_artifacts", "artifact_type", nullable=False)
    op.alter_column("research_artifacts", "content", nullable=False)

    # ===== source_documents table =====
    # Add NOT NULL constraints
    op.alter_column("source_documents", "research_run_id", nullable=False)
    op.alter_column("source_documents", "source_url", nullable=False)
    op.alter_column("source_documents", "title", nullable=False)

    # ===== metric_observations table =====
    # Add NOT NULL constraints
    op.alter_column("metric_observations", "research_run_id", nullable=False)
    op.alter_column("metric_observations", "metric_name", nullable=False)
    op.alter_column("metric_observations", "value", nullable=False)

    # ===== evidence_readiness table =====
    # Add NOT NULL constraints
    op.alter_column("evidence_readiness", "research_run_id", nullable=False)
    op.alter_column("evidence_readiness", "evidence_type", nullable=False)
    op.alter_column("evidence_readiness", "readiness_score", nullable=False)

    # Add CHECK constraint for readiness_score range
    op.create_check_constraint(
        "ck_evidence_readiness_score_range", "evidence_readiness", "readiness_score >= 0 AND readiness_score <= 100"
    )

    # ===== research_contradictions table =====
    # Add NOT NULL constraints
    op.alter_column("research_contradictions", "research_run_id", nullable=False)
    op.alter_column("research_contradictions", "contradiction_type", nullable=False)
    op.alter_column("research_contradictions", "severity", nullable=False)

    # ===== enrichment_audit_trail table =====
    # Add NOT NULL constraints
    op.alter_column("enrichment_audit_trail", "company_id", nullable=False)
    op.alter_column("enrichment_audit_trail", "job_id", nullable=False)
    op.alter_column("enrichment_audit_trail", "status", nullable=False)
    op.alter_column("enrichment_audit_trail", "created_at", nullable=False)

    # Add DEFAULT for created_at
    op.alter_column("enrichment_audit_trail", "created_at", server_default=sa.text("CURRENT_TIMESTAMP"))

    # ===== enrichment_cache table =====
    # Add NOT NULL constraints
    op.alter_column("enrichment_cache", "company_id", nullable=False)
    op.alter_column("enrichment_cache", "cache_key", nullable=False)
    op.alter_column("enrichment_cache", "cache_value", nullable=False)
    op.alter_column("enrichment_cache", "created_at", nullable=False)

    # Add DEFAULT for created_at
    op.alter_column("enrichment_cache", "created_at", server_default=sa.text("CURRENT_TIMESTAMP"))


def downgrade() -> None:
    """Downgrade: remove CHECK constraints, NOT NULL constraints, and DEFAULT values."""

    # ===== enrichment_cache table =====
    op.alter_column("enrichment_cache", "created_at", server_default=None)
    op.alter_column("enrichment_cache", "created_at", nullable=True)
    op.alter_column("enrichment_cache", "cache_value", nullable=True)
    op.alter_column("enrichment_cache", "cache_key", nullable=True)
    op.alter_column("enrichment_cache", "company_id", nullable=True)

    # ===== enrichment_audit_trail table =====
    op.alter_column("enrichment_audit_trail", "created_at", server_default=None)
    op.alter_column("enrichment_audit_trail", "created_at", nullable=True)
    op.alter_column("enrichment_audit_trail", "status", nullable=True)
    op.alter_column("enrichment_audit_trail", "job_id", nullable=True)
    op.alter_column("enrichment_audit_trail", "company_id", nullable=True)

    # ===== research_contradictions table =====
    op.alter_column("research_contradictions", "severity", nullable=True)
    op.alter_column("research_contradictions", "contradiction_type", nullable=True)
    op.alter_column("research_contradictions", "research_run_id", nullable=True)

    # ===== evidence_readiness table =====
    op.drop_constraint("ck_evidence_readiness_score_range", "evidence_readiness", type_="check")
    op.alter_column("evidence_readiness", "readiness_score", nullable=True)
    op.alter_column("evidence_readiness", "evidence_type", nullable=True)
    op.alter_column("evidence_readiness", "research_run_id", nullable=True)

    # ===== metric_observations table =====
    op.alter_column("metric_observations", "value", nullable=True)
    op.alter_column("metric_observations", "metric_name", nullable=True)
    op.alter_column("metric_observations", "research_run_id", nullable=True)

    # ===== source_documents table =====
    op.alter_column("source_documents", "title", nullable=True)
    op.alter_column("source_documents", "source_url", nullable=True)
    op.alter_column("source_documents", "research_run_id", nullable=True)

    # ===== research_artifacts table =====
    op.alter_column("research_artifacts", "content", nullable=True)
    op.alter_column("research_artifacts", "artifact_type", nullable=True)
    op.alter_column("research_artifacts", "research_run_id", nullable=True)

    # ===== research_stages table =====
    op.alter_column("research_stages", "status", server_default=None)
    op.alter_column("research_stages", "status", nullable=True)
    op.alter_column("research_stages", "stage_name", nullable=True)
    op.alter_column("research_stages", "research_run_id", nullable=True)

    # ===== research_runs table =====
    op.alter_column("research_runs", "status", server_default=None)
    op.alter_column("research_runs", "created_at", server_default=None)
    op.alter_column("research_runs", "created_at", nullable=True)
    op.alter_column("research_runs", "status", nullable=True)
    op.alter_column("research_runs", "company_id", nullable=True)

    # ===== market_snapshots table =====
    op.alter_column("market_snapshots", "created_at", server_default=None)
    op.alter_column("market_snapshots", "created_at", nullable=True)
    op.alter_column("market_snapshots", "market_data", nullable=True)
    op.alter_column("market_snapshots", "snapshot_date", nullable=True)

    # ===== signal_records table =====
    op.alter_column("signal_records", "created_at", server_default=None)
    op.alter_column("signal_records", "created_at", nullable=True)
    op.alter_column("signal_records", "company_id", nullable=True)
    op.alter_column("signal_records", "value", nullable=True)
    op.alter_column("signal_records", "signal_type", nullable=True)

    # ===== scoring_records table =====
    op.drop_constraint("ck_scoring_records_score_range", "scoring_records", type_="check")
    op.alter_column("scoring_records", "created_at", server_default=None)
    op.alter_column("scoring_records", "created_at", nullable=True)
    op.alter_column("scoring_records", "company_id", nullable=True)
    op.alter_column("scoring_records", "score", nullable=True)
