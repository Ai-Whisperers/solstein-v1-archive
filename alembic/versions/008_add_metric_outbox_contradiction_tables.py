"""Add metric observations, outbox, and contradiction transition tables.

Revision ID: 008
Revises: 007
Create Date: 2026-02-27 10:15:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create metric_observations table
    op.create_table(
        "metric_observations",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("company_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("metric_name", sa.String(length=255), nullable=False),
        sa.Column("metric_value", sa.Float(), nullable=True),
        sa.Column("metric_unit", sa.String(length=100), nullable=True),
        sa.Column("observation_date", sa.Date(), nullable=False),
        sa.Column("source", sa.String(length=255), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_metric_observations_company_id", "metric_observations", ["company_id"])
    op.create_index("ix_metric_observations_metric_name", "metric_observations", ["metric_name"])
    op.create_index("ix_metric_observations_observation_date", "metric_observations", ["observation_date"])

    # Create outbox table
    op.create_table(
        "outbox",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("aggregate_id", sa.String(length=255), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("published", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_outbox_event_type", "outbox", ["event_type"])
    op.create_index("ix_outbox_aggregate_id", "outbox", ["aggregate_id"])
    op.create_index("ix_outbox_published", "outbox", ["published"])
    op.create_index("ix_outbox_created_at", "outbox", ["created_at"])

    # Create contradiction_transitions table
    op.create_table(
        "contradiction_transitions",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("contradiction_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("from_status", sa.String(length=50), nullable=True),
        sa.Column("to_status", sa.String(length=50), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("resolved_by", sa.String(length=255), nullable=True),
        sa.Column("resolution_details", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["contradiction_id"], ["data_source_conflicts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_contradiction_transitions_contradiction_id", "contradiction_transitions", ["contradiction_id"])
    op.create_index("ix_contradiction_transitions_to_status", "contradiction_transitions", ["to_status"])
    op.create_index("ix_contradiction_transitions_created_at", "contradiction_transitions", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_contradiction_transitions_created_at", table_name="contradiction_transitions")
    op.drop_index("ix_contradiction_transitions_to_status", table_name="contradiction_transitions")
    op.drop_index("ix_contradiction_transitions_contradiction_id", table_name="contradiction_transitions")
    op.drop_table("contradiction_transitions")
    op.drop_index("ix_outbox_created_at", table_name="outbox")
    op.drop_index("ix_outbox_published", table_name="outbox")
    op.drop_index("ix_outbox_aggregate_id", table_name="outbox")
    op.drop_index("ix_outbox_event_type", table_name="outbox")
    op.drop_table("outbox")
    op.drop_index("ix_metric_observations_observation_date", table_name="metric_observations")
    op.drop_index("ix_metric_observations_metric_name", table_name="metric_observations")
    op.drop_index("ix_metric_observations_company_id", table_name="metric_observations")
    op.drop_table("metric_observations")
