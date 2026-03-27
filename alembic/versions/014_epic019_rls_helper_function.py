"""EPIC-019 STORY-064: Create RLS helper function and enable RLS on all tables.

This Alembic migration creates the get_user_tenant_id() SQL function used by
Supabase RLS policies. It also ensures RLS is enabled on all tenant-scoped
tables in the PostgreSQL schema.

NOTE: The full RLS policies are defined in supabase/migrations/014_epic019_tenant_rls_policies.sql
since Supabase manages its own policy application. This migration handles the
helper function and ENABLE ROW LEVEL SECURITY statements on the Alembic side.

Depends on: STORY-063 migration 013 (adds tenant_id columns to all tables).

Revision ID: 014
Revises: 012
Create Date: 2026-03-27 18:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "014"
down_revision: Union[str, None] = "012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# All tenant-scoped tables that need RLS enabled
TENANT_SCOPED_TABLES = [
    "companies",
    "scoring_records",
    "signal_records",
    "market_snapshots",
    "audit_trails",
    "research_runs",
    "research_stages",
    "research_artifacts",
    "source_documents",
    "metric_observations",
    "evidence_readiness",
    "research_contradictions",
    "enrichment_audit_trail",
    "enrichment_cache",
    "enrichment_jobs",
    "outbox_records",
]


def upgrade() -> None:
    """Create RLS helper function and enable RLS on tenant-scoped tables."""
    # 1. Create the helper function that extracts tenant_id from JWT claims
    op.execute("""
        CREATE OR REPLACE FUNCTION public.get_user_tenant_id()
        RETURNS TEXT
        LANGUAGE sql
        STABLE
        SECURITY DEFINER
        AS $$
            SELECT COALESCE(
                (current_setting('request.jwt.claims', true)::json -> 'app_metadata' ->> 'tenant_id'),
                (current_setting('request.jwt.claims', true)::json -> 'user_metadata' ->> 'tenant_id')
            );
        $$;
    """)

    op.execute("""
        COMMENT ON FUNCTION public.get_user_tenant_id() IS
            'EPIC-019: Extracts tenant_id from JWT claims. Used by RLS policies for tenant isolation.';
    """)

    # 2. Enable RLS on all tenant-scoped tables (idempotent)
    for table in TENANT_SCOPED_TABLES:
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY;")


def downgrade() -> None:
    """Remove RLS helper function and disable RLS."""
    # Disable RLS on all tenant-scoped tables
    for table in reversed(TENANT_SCOPED_TABLES):
        op.execute(f"ALTER TABLE public.{table} DISABLE ROW LEVEL SECURITY;")

    # Drop the helper function
    op.execute("DROP FUNCTION IF EXISTS public.get_user_tenant_id();")
