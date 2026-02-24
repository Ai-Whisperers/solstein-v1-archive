"""Add refresh metadata, conflict resolution, and confidence calibration tables.

Revision ID: E2a
Revises: 003
Create Date: 2026-02-24

This migration adds three new tables for Wave 2 data freshness features:
1. refresh_metadata - tracks scheduling and status for each data source
2. data_source_conflicts - records contradictions between sources for resolution
3. confidence_calibration - tracks prediction accuracy for confidence tuning
"""

from alembic import op
import sqlalchemy as sa


revision = "E2a"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. refresh_metadata table
    op.create_table(
        "refresh_metadata",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_name", sa.String(length=100), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("last_refresh_time", sa.DateTime(), nullable=True),
        sa.Column("last_refresh_status", sa.String(length=50), nullable=True),
        sa.Column("last_refresh_job_id", sa.String(length=255), nullable=True),
        sa.Column("next_scheduled_time", sa.DateTime(), nullable=True),
        sa.Column("refresh_interval_seconds", sa.Integer(), nullable=False, server_default="86400"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_name", name="uq_refresh_metadata_source_name"),
    )
    op.create_index(
        "ix_refresh_metadata_source_name",
        "refresh_metadata",
        ["source_name"],
        unique=True,
    )
    op.create_index(
        "ix_refresh_metadata_next_scheduled",
        "refresh_metadata",
        ["next_scheduled_time"],
        unique=False,
    )

    # 2. data_source_conflicts table
    op.create_table(
        "data_source_conflicts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("company_id", sa.String(length=255), nullable=False),
        sa.Column("metric_key", sa.String(length=100), nullable=False),
        sa.Column("period", sa.String(length=50), nullable=True),
        # Source 1 (higher confidence)
        sa.Column("source1_name", sa.String(length=100), nullable=False),
        sa.Column("source1_value", sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column("source1_confidence", sa.Numeric(precision=3, scale=2), nullable=False),
        sa.Column("source1_url", sa.String(length=1000), nullable=True),
        # Source 2 (lower confidence)
        sa.Column("source2_name", sa.String(length=100), nullable=False),
        sa.Column("source2_value", sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column("source2_confidence", sa.Numeric(precision=3, scale=2), nullable=False),
        sa.Column("source2_url", sa.String(length=1000), nullable=True),
        # Resolution
        sa.Column("contradiction_detected", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("resolution_strategy", sa.String(length=50), nullable=True),
        sa.Column("chosen_value", sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column("chosen_source", sa.String(length=100), nullable=True),
        sa.Column("flagged_for_review", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("analyst_notes", sa.Text(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("resolved_by", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["company_id"], ["companies.company_id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_data_source_conflicts_company_metric",
        "data_source_conflicts",
        ["company_id", "metric_key"],
        unique=False,
    )
    op.create_index(
        "ix_data_source_conflicts_flagged",
        "data_source_conflicts",
        ["flagged_for_review"],
        unique=False,
    )

    # 3. confidence_calibration table
    op.create_table(
        "confidence_calibration",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_name", sa.String(length=100), nullable=False),
        sa.Column("metric_key", sa.String(length=100), nullable=False),
        sa.Column("company_id", sa.String(length=255), nullable=True),
        # Prediction
        sa.Column("predicted_value", sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column("confidence_original", sa.Numeric(precision=3, scale=2), nullable=False),
        # Actual (observed later)
        sa.Column("actual_value", sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column("actual_source", sa.String(length=100), nullable=True),
        sa.Column("actual_observed_at", sa.DateTime(), nullable=True),
        # Derived
        sa.Column("is_correct", sa.Boolean(), nullable=True),
        sa.Column("accuracy_tolerance_pct", sa.Float(), nullable=False, server_default="10.0"),
        # Calibration
        sa.Column("calibration_factor", sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column("confidence_adjusted", sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_confidence_calibration_source_metric",
        "confidence_calibration",
        ["source_name", "metric_key"],
        unique=False,
    )
    op.create_index(
        "ix_confidence_calibration_is_correct",
        "confidence_calibration",
        ["is_correct"],
        unique=False,
    )
    op.create_index(
        "ix_confidence_calibration_company",
        "confidence_calibration",
        ["company_id"],
        unique=False,
    )


def downgrade() -> None:
    # Drop confidence_calibration
    op.drop_index("ix_confidence_calibration_company", table_name="confidence_calibration")
    op.drop_index("ix_confidence_calibration_is_correct", table_name="confidence_calibration")
    op.drop_index("ix_confidence_calibration_source_metric", table_name="confidence_calibration")
    op.drop_table("confidence_calibration")

    # Drop data_source_conflicts
    op.drop_index("ix_data_source_conflicts_flagged", table_name="data_source_conflicts")
    op.drop_index("ix_data_source_conflicts_company_metric", table_name="data_source_conflicts")
    op.drop_table("data_source_conflicts")

    # Drop refresh_metadata
    op.drop_index("ix_refresh_metadata_next_scheduled", table_name="refresh_metadata")
    op.drop_index("ix_refresh_metadata_source_name", table_name="refresh_metadata")
    op.drop_table("refresh_metadata")
