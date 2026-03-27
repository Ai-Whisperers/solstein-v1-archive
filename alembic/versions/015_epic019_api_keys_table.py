"""EPIC-019 STORY-065: Create API key management tables.

Adds api_keys and api_key_usage_logs tables for tenant-scoped
programmatic access.

Revision ID: 015
Revises: 012
Create Date: 2026-03-27 19:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "015"
down_revision: Union[str, None] = "012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create api_keys and api_key_usage_logs tables."""
    # API keys table
    op.create_table(
        "api_keys",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("key_prefix", sa.String(16), nullable=False),
        sa.Column("key_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("scope", sa.String(50), nullable=False, server_default="read_only"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("last_used_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint(
            "scope IN ('read_only', 'read_write', 'admin')",
            name="ck_api_key_scope",
        ),
    )

    op.create_index("ix_api_keys_tenant_id", "api_keys", ["tenant_id"])
    op.create_index("ix_api_keys_key_hash", "api_keys", ["key_hash"])
    op.create_index("ix_api_keys_tenant_active", "api_keys", ["tenant_id", "is_active"])

    # API key usage logs table
    op.create_table(
        "api_key_usage_logs",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("api_key_id", sa.Uuid(as_uuid=True), sa.ForeignKey("api_keys.id"), nullable=False),
        sa.Column("tenant_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("endpoint", sa.String(500), nullable=False),
        sa.Column("method", sa.String(10), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_index("ix_api_key_usage_key_timestamp", "api_key_usage_logs", ["api_key_id", "timestamp"])
    op.create_index("ix_api_key_usage_tenant_timestamp", "api_key_usage_logs", ["tenant_id", "timestamp"])

    # Enable RLS
    op.execute("ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE public.api_key_usage_logs ENABLE ROW LEVEL SECURITY;")


def downgrade() -> None:
    """Drop api_key_usage_logs and api_keys tables."""
    op.execute("ALTER TABLE public.api_key_usage_logs DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE public.api_keys DISABLE ROW LEVEL SECURITY;")

    op.drop_index("ix_api_key_usage_tenant_timestamp", table_name="api_key_usage_logs")
    op.drop_index("ix_api_key_usage_key_timestamp", table_name="api_key_usage_logs")
    op.drop_table("api_key_usage_logs")

    op.drop_index("ix_api_keys_tenant_active", table_name="api_keys")
    op.drop_index("ix_api_keys_key_hash", table_name="api_keys")
    op.drop_index("ix_api_keys_tenant_id", table_name="api_keys")
    op.drop_table("api_keys")
