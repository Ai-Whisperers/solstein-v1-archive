"""Initial schema with scoring records, signals, and market snapshots.

Revision ID: 001
Revises:
Create Date: 2026-02-20 22:30:00.000000

"""

import sqlalchemy as sa
from alembic import op

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scoring_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.String(length=255), nullable=False),
        sa.Column("company_name", sa.String(length=500), nullable=False),
        sa.Column("growth_score", sa.Float(), nullable=False),
        sa.Column("financial_health_score", sa.Float(), nullable=False),
        sa.Column("competitive_position_score", sa.Float(), nullable=False),
        sa.Column("overall_score", sa.Float(), nullable=False),
        sa.Column("classification", sa.String(length=50), nullable=False),
        sa.Column("scored_at", sa.DateTime(), nullable=False),
        sa.Column("data_sources_used", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_company_scored_at",
        "scoring_records",
        ["company_id", "scored_at"],
        unique=False,
    )
    op.create_index(
        "ix_overall_score", "scoring_records", ["overall_score"], unique=False
    )
    op.create_index(
        "ix_classification", "scoring_records", ["classification"], unique=False
    )
    op.create_index(
        "ix_scoring_records_company_id", "scoring_records", ["company_id"], unique=False
    )

    op.create_table(
        "signal_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("scoring_record_id", sa.Integer(), nullable=False),
        sa.Column("signal_name", sa.String(length=255), nullable=False),
        sa.Column("signal_category", sa.String(length=50), nullable=False),
        sa.Column("signal_value", sa.Float(), nullable=True),
        sa.Column("signal_text", sa.String(length=2000), nullable=True),
        sa.Column("source_agent", sa.String(length=100), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("extracted_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["scoring_record_id"],
            ["scoring_records.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_signal_name_category",
        "signal_records",
        ["signal_name", "signal_category"],
        unique=False,
    )
    op.create_index(
        "ix_signal_records_scoring_record_id",
        "signal_records",
        ["scoring_record_id"],
        unique=False,
    )

    op.create_table(
        "market_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("snapshot_date", sa.DateTime(), nullable=False),
        sa.Column("total_companies_scored", sa.Integer(), nullable=False),
        sa.Column("average_growth_score", sa.Float(), nullable=False),
        sa.Column("average_financial_score", sa.Float(), nullable=False),
        sa.Column("average_competitive_score", sa.Float(), nullable=False),
        sa.Column("phoenix_count", sa.Integer(), nullable=False),
        sa.Column("salt_count", sa.Integer(), nullable=False),
        sa.Column("lead_count", sa.Integer(), nullable=False),
        sa.Column("market_metadata", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_snapshot_date", "market_snapshots", ["snapshot_date"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_snapshot_date", table_name="market_snapshots")
    op.drop_table("market_snapshots")
    op.drop_index("ix_signal_records_scoring_record_id", table_name="signal_records")
    op.drop_index("ix_signal_name_category", table_name="signal_records")
    op.drop_table("signal_records")
    op.drop_index("ix_scoring_records_company_id", table_name="scoring_records")
    op.drop_index("ix_classification", table_name="scoring_records")
    op.drop_index("ix_overall_score", table_name="scoring_records")
    op.drop_index("ix_company_scored_at", table_name="scoring_records")
    op.drop_table("scoring_records")
