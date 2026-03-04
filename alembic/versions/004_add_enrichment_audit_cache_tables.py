"""Add enrichment audit trail and cache tables (Phase 11).

Revision ID: 004
Revises: E2a
Create Date: 2026-02-25 21:45:00.000000
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "004"
down_revision = "E2a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade: create enrichment audit trail and cache tables."""
    # Create enrichment_audit_trail table
    op.create_table(
        "enrichment_audit_trail",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.String(255), nullable=False),
        sa.Column("company_name", sa.String(500), nullable=True),
        sa.Column("operation", sa.String(50), nullable=False),
        sa.Column("source", sa.String(255), nullable=True),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("duration_ms", sa.Float(), nullable=True),
        sa.Column("fields_enriched", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("user_id", sa.String(255), nullable=True),
        sa.Column("client_id", sa.String(255), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for enrichment_audit_trail
    op.create_index("ix_enrichment_audit_trail_company_id", "enrichment_audit_trail", ["company_id"])
    op.create_index("ix_enrichment_audit_trail_operation", "enrichment_audit_trail", ["operation"])
    op.create_index("ix_enrichment_audit_trail_timestamp", "enrichment_audit_trail", ["timestamp"])
    op.create_index("ix_enrichment_audit_company_timestamp", "enrichment_audit_trail", ["company_id", "timestamp"])
    op.create_index("ix_enrichment_audit_operation_timestamp", "enrichment_audit_trail", ["operation", "timestamp"])

    # Create enrichment_cache table
    op.create_table(
        "enrichment_cache",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.String(255), nullable=False, unique=True),
        sa.Column("enriched_data", sa.JSON(), nullable=False),
        sa.Column("sources_used", sa.JSON(), nullable=True),
        sa.Column("fields_enriched", sa.JSON(), nullable=True),
        sa.Column("cached_at", sa.DateTime(), nullable=False),
        sa.Column("ttl_seconds", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("hits", sa.Integer(), nullable=False),
        sa.Column("last_accessed_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for enrichment_cache
    op.create_index("ix_enrichment_cache_company_id", "enrichment_cache", ["company_id"])
    op.create_index("ix_enrichment_cache_expires_at", "enrichment_cache", ["expires_at"])


def downgrade() -> None:
    """Downgrade: drop enrichment audit trail and cache tables."""
    op.drop_index("ix_enrichment_cache_expires_at", table_name="enrichment_cache")
    op.drop_index("ix_enrichment_cache_company_id", table_name="enrichment_cache")
    op.drop_table("enrichment_cache")

    op.drop_index("ix_enrichment_audit_operation_timestamp", table_name="enrichment_audit_trail")
    op.drop_index("ix_enrichment_audit_company_timestamp", table_name="enrichment_audit_trail")
    op.drop_index("ix_enrichment_audit_trail_timestamp", table_name="enrichment_audit_trail")
    op.drop_index("ix_enrichment_audit_trail_operation", table_name="enrichment_audit_trail")
    op.drop_index("ix_enrichment_audit_trail_company_id", table_name="enrichment_audit_trail")
    op.drop_table("enrichment_audit_trail")
