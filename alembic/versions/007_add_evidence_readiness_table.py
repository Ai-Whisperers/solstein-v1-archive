"""Add evidence readiness table for tracking evidence quality.

Revision ID: 007
Revises: 006
Create Date: 2026-02-27 10:10:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create evidence_readiness table
    op.create_table(
        "evidence_readiness",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("signal_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("readiness_score", sa.Float(), nullable=False),
        sa.Column("source_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("contradiction_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("confidence_level", sa.String(length=50), nullable=True),
        sa.Column("assessment_details", sa.JSON(), nullable=True),
        sa.Column("assessed_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["signal_id"], ["signal_records.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("signal_id", name="uq_evidence_readiness_signal_id"),
    )
    op.create_index("ix_evidence_readiness_signal_id", "evidence_readiness", ["signal_id"], unique=True)
    op.create_index("ix_evidence_readiness_readiness_score", "evidence_readiness", ["readiness_score"])
    op.create_index("ix_evidence_readiness_confidence", "evidence_readiness", ["confidence_level"])


def downgrade() -> None:
    op.drop_index("ix_evidence_readiness_confidence", table_name="evidence_readiness")
    op.drop_index("ix_evidence_readiness_readiness_score", table_name="evidence_readiness")
    op.drop_index("ix_evidence_readiness_signal_id", table_name="evidence_readiness")
    op.drop_table("evidence_readiness")
