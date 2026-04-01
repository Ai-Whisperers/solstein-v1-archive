"""EPIC-025 STORY-088: Add failed_tasks table for persistent Dead Letter Queue.

Replaces the in-memory DeadLetterQueue class (which evaporated on every worker
restart) with a durable PostgreSQL-backed table. Every task failure writes a row
here before the task terminates. Failed tasks survive worker crashes, pod evictions,
and deployments.

Table schema is chosen for:
- UUID primary key (avoids sequential scan on DLQ admin list endpoint)
- JSONB args/kwargs (structured, indexable, human-readable in psql)
- Nullable resolved_at/resolved_by (supports manual and automated re-queue)
- Composite index on (resolved_at IS NULL, created_at DESC) for the default
  admin query pattern (unresolved failures, newest first)

Revision ID: 018
Revises: 017
Create Date: 2026-03-27 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "018"
down_revision: str | Sequence[str] | None = "017"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the failed_tasks table with indexes."""
    op.create_table(
        "failed_tasks",
        sa.Column("task_id", sa.UUID(), nullable=False, primary_key=True),
        sa.Column("task_name", sa.String(255), nullable=False),
        sa.Column("queue_name", sa.String(255), nullable=False, server_default="default"),
        sa.Column("args", sa.JSON(), nullable=True),
        sa.Column("kwargs", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=False),
        sa.Column("traceback", sa.Text(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tenant_id", sa.String(255), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "last_attempted_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("resolved_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("resolved_by", sa.String(255), nullable=True),
    )

    # Primary access pattern: list unresolved failures newest-first
    op.create_index(
        "ix_failed_tasks_unresolved_created",
        "failed_tasks",
        [sa.text("(resolved_at IS NULL)"), sa.text("created_at DESC")],
    )

    # Filtering by task name (admin filtering)
    op.create_index(
        "ix_failed_tasks_task_name",
        "failed_tasks",
        ["task_name"],
    )

    # Filtering by queue name (admin filtering)
    op.create_index(
        "ix_failed_tasks_queue_name",
        "failed_tasks",
        ["queue_name"],
    )

    # Filtering by tenant (multi-tenant admin)
    op.create_index(
        "ix_failed_tasks_tenant_id",
        "failed_tasks",
        ["tenant_id"],
    )


def downgrade() -> None:
    """Drop the failed_tasks table and all indexes."""
    op.drop_index("ix_failed_tasks_tenant_id", table_name="failed_tasks")
    op.drop_index("ix_failed_tasks_queue_name", table_name="failed_tasks")
    op.drop_index("ix_failed_tasks_task_name", table_name="failed_tasks")
    op.drop_index("ix_failed_tasks_unresolved_created", table_name="failed_tasks")
    op.drop_table("failed_tasks")
