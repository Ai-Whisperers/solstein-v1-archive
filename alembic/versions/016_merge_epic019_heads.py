"""Merge EPIC-019 migration heads (013, 014, 015) into single head.

Revision ID: 016
Revises: 013, 014, 015
Create Date: 2026-03-27 09:00:00.000000
"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "016"
down_revision: tuple[str, ...] = ("013", "014", "015")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Merge heads - no schema changes."""
    pass


def downgrade() -> None:
    """Merge heads - no schema changes."""
    pass
