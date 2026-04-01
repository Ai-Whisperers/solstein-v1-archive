"""STORY-113: Add export status tracking fields to export_jobs table.

Adds user_id, file_size_bytes, and expires_at columns to support:
- User-scoped export queries
- File size reporting in status responses
- Automatic expiry of download links after 7 days

Also adds an index on expires_at for efficient expired-job queries.

Revision ID: 019
Revises: 018
Create Date: 2026-03-27 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "019"
down_revision: str | Sequence[str] | None = "018"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add user_id, file_size_bytes, expires_at to export_jobs."""
    op.add_column(
        "export_jobs",
        sa.Column("user_id", sa.String(255), nullable=True),
    )
    op.add_column(
        "export_jobs",
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "export_jobs",
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Indexes for query performance
    op.create_index(
        "ix_export_jobs_user_id",
        "export_jobs",
        ["user_id"],
    )
    op.create_index(
        "ix_export_jobs_expires_at",
        "export_jobs",
        ["expires_at"],
    )


def downgrade() -> None:
    """Remove STORY-113 columns from export_jobs."""
    op.drop_index("ix_export_jobs_expires_at", table_name="export_jobs")
    op.drop_index("ix_export_jobs_user_id", table_name="export_jobs")
    op.drop_column("export_jobs", "expires_at")
    op.drop_column("export_jobs", "file_size_bytes")
    op.drop_column("export_jobs", "user_id")
