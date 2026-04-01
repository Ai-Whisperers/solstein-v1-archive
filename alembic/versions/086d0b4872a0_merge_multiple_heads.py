"""Merge multiple heads

Revision ID: 086d0b4872a0
Revises: 004, 011
Create Date: 2026-03-06 02:45:28.657622

"""
from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = '086d0b4872a0'
down_revision: str | Sequence[str] | None = ('004', '011')
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
