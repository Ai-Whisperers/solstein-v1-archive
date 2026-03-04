"""Add research tables for research runs, stages, and artifacts.

Revision ID: 005
Revises: E2a
Create Date: 2026-02-27 10:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "005"
down_revision = "E2a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create research_runs table
    op.create_table(
        "research_runs",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("run_id", sa.String(length=255), nullable=False),
        sa.Column("market", sa.String(length=255), nullable=False),
        sa.Column("seed_company", sa.String(length=500), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default=sa.text("'completed'")),
        sa.Column("strict_provenance", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("min_readiness_score", sa.Float(), nullable=True),
        sa.Column("max_contradictions", sa.Integer(), nullable=True),
        sa.Column("min_total_sources", sa.Integer(), nullable=True),
        sa.Column("summary", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("run_id", name="uq_research_run_id"),
    )
    op.create_index("ix_research_runs_run_id", "research_runs", ["run_id"], unique=True)
    op.create_index("ix_research_runs_market", "research_runs", ["market"])
    op.create_index("ix_research_runs_status", "research_runs", ["status"])

    # Create research_stages table
    op.create_table(
        "research_stages",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("run_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("stage_name", sa.String(length=100), nullable=False),
        sa.Column("stage_order", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("metrics", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["run_id"], ["research_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("run_id", "stage_name", name="uq_research_stage_run_name"),
    )
    op.create_index("ix_research_stages_run_id", "research_stages", ["run_id"])
    op.create_index("ix_research_stages_stage_name", "research_stages", ["stage_name"])
    op.create_index("ix_research_stage_run_order", "research_stages", ["run_id", "stage_order"])

    # Create research_artifacts table
    op.create_table(
        "research_artifacts",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("run_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("artifact_name", sa.String(length=255), nullable=False),
        sa.Column("artifact_path", sa.String(length=1000), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["run_id"], ["research_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("run_id", "artifact_name", name="uq_research_artifact_run_name"),
    )
    op.create_index("ix_research_artifacts_run_id", "research_artifacts", ["run_id"])
    op.create_index("ix_research_artifacts_artifact_name", "research_artifacts", ["artifact_name"])


def downgrade() -> None:
    op.drop_index("ix_research_artifacts_artifact_name", table_name="research_artifacts")
    op.drop_index("ix_research_artifacts_run_id", table_name="research_artifacts")
    op.drop_table("research_artifacts")
    op.drop_index("ix_research_stage_run_order", table_name="research_stages")
    op.drop_index("ix_research_stages_stage_name", table_name="research_stages")
    op.drop_index("ix_research_stages_run_id", table_name="research_stages")
    op.drop_table("research_stages")
    op.drop_index("ix_research_runs_status", table_name="research_runs")
    op.drop_index("ix_research_runs_market", table_name="research_runs")
    op.drop_index("ix_research_runs_run_id", table_name="research_runs")
    op.drop_table("research_runs")
