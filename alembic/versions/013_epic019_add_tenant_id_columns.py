"""EPIC-019 STORY-063: Add tenant_id columns to all business data tables.

Adds tenant_id to: scoring_records, market_snapshots, audit_trails,
enrichment_audit_trail, enrichment_cache, enrichment_jobs, research_runs.

Backfills existing rows with a default tenant.

Revision ID: 013
Revises: 012
Create Date: 2026-03-27 03:30:00.000000
"""

import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "013"
down_revision: str | Sequence[str] | None = "012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Default tenant UUID for backfilling existing data
DEFAULT_TENANT_ID = "00000000-0000-0000-0000-000000000000"
DEFAULT_TENANT_NAME = "default"


def upgrade() -> None:
    """Add tenant_id to all business data tables and backfill default tenant."""

    # 1. Ensure the tenants table has a default tenant row for backfilling
    tenants_table = sa.table(
        "tenants",
        sa.column("id", sa.Uuid),
        sa.column("name", sa.String),
        sa.column("api_key_hash", sa.String),
        sa.column("is_active", sa.Boolean),
        sa.column("plan", sa.String),
        sa.column("rate_limit_per_min", sa.Integer),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )

    # Insert default tenant (ignore if exists via conflict handling)
    op.execute(
        tenants_table.insert()
        .values(
            id=uuid.UUID(DEFAULT_TENANT_ID),
            name=DEFAULT_TENANT_NAME,
            api_key_hash="0" * 64,  # Placeholder hash, not a real key
            is_active=True,
            plan="enterprise",
            rate_limit_per_min=9999,
            created_at=sa.func.now(),
            updated_at=sa.func.now(),
        )
        .prefix_with("OR IGNORE")  # SQLite
    )

    # 2. Add tenant_id columns to tables that don't have them yet
    # (companies already has tenant_id from prior work)

    tables_needing_tenant_id = [
        "scoring_records",
        "market_snapshots",
        "audit_trails",
        "enrichment_audit_trail",
        "enrichment_cache",
        "enrichment_jobs",
        "research_runs",
    ]

    for table_name in tables_needing_tenant_id:
        op.add_column(
            table_name,
            sa.Column("tenant_id", sa.String(255), nullable=True),
        )

    # 3. Backfill existing rows with default tenant
    for table_name in tables_needing_tenant_id:
        op.execute(
            sa.text(f"UPDATE {table_name} SET tenant_id = :tid WHERE tenant_id IS NULL")
            .bindparams(tid=DEFAULT_TENANT_ID)
        )

    # Also backfill companies table if any rows have NULL tenant_id
    op.execute(
        sa.text("UPDATE companies SET tenant_id = :tid WHERE tenant_id IS NULL")
        .bindparams(tid=DEFAULT_TENANT_ID)
    )

    # 4. Add indexes for tenant_id on new columns
    index_specs = [
        ("ix_scoring_tenant", "scoring_records"),
        ("ix_market_snapshot_tenant", "market_snapshots"),
        ("ix_audit_trail_tenant", "audit_trails"),
        ("ix_enrichment_audit_tenant", "enrichment_audit_trail"),
        ("ix_enrichment_cache_tenant", "enrichment_cache"),
        ("ix_enrichment_job_tenant", "enrichment_jobs"),
        ("ix_research_run_tenant", "research_runs"),
    ]

    for index_name, table_name in index_specs:
        op.create_index(index_name, table_name, ["tenant_id"])


def downgrade() -> None:
    """Remove tenant_id columns from business data tables."""

    index_specs = [
        ("ix_scoring_tenant", "scoring_records"),
        ("ix_market_snapshot_tenant", "market_snapshots"),
        ("ix_audit_trail_tenant", "audit_trails"),
        ("ix_enrichment_audit_tenant", "enrichment_audit_trail"),
        ("ix_enrichment_cache_tenant", "enrichment_cache"),
        ("ix_enrichment_job_tenant", "enrichment_jobs"),
        ("ix_research_run_tenant", "research_runs"),
    ]

    for index_name, table_name in index_specs:
        op.drop_index(index_name, table_name=table_name)

    tables_needing_tenant_id = [
        "scoring_records",
        "market_snapshots",
        "audit_trails",
        "enrichment_audit_trail",
        "enrichment_cache",
        "enrichment_jobs",
        "research_runs",
    ]

    for table_name in tables_needing_tenant_id:
        op.drop_column(table_name, "tenant_id")

    # Remove default tenant
    op.execute(
        sa.text("DELETE FROM tenants WHERE id = :tid")
        .bindparams(tid=DEFAULT_TENANT_ID)
    )
