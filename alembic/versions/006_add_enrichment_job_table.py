"""Add enrichment job table for tracking enrichment operations.

Revision ID: 006
Revises: 005
Create Date: 2026-02-27 10:05:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enrichment_jobs table
    op.create_table(
        "enrichment_jobs",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("job_id", sa.String(length=255), nullable=False),
        sa.Column("company_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("enrichment_type", sa.String(length=100), nullable=True),
        sa.Column("data_sources", sa.JSON(), nullable=True),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_id", name="uq_enrichment_job_id"),
    )
    op.create_index("ix_enrichment_jobs_job_id", "enrichment_jobs", ["job_id"], unique=True)
    op.create_index("ix_enrichment_jobs_company_id", "enrichment_jobs", ["company_id"])
    op.create_index("ix_enrichment_jobs_status", "enrichment_jobs", ["status"])
    op.create_index("ix_enrichment_jobs_created_at", "enrichment_jobs", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_enrichment_jobs_created_at", table_name="enrichment_jobs")
    op.drop_index("ix_enrichment_jobs_status", table_name="enrichment_jobs")
    op.drop_index("ix_enrichment_jobs_company_id", table_name="enrichment_jobs")
    op.drop_index("ix_enrichment_jobs_job_id", table_name="enrichment_jobs")
    op.drop_table("enrichment_jobs")
