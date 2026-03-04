"""Add missing foreign key constraints to enrichment tables.

Revision ID: 009
Revises: 008
Create Date: 2026-02-27 20:30:00.000000

"""

from alembic import op

revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade: add foreign key constraints to enrichment tables."""
    # Add FK constraint to enrichment_audit_trail.company_id -> companies.company_id
    op.create_foreign_key(
        "fk_enrichment_audit_trail_companies_company_id",
        "enrichment_audit_trail",
        "companies",
        ["company_id"],
        ["company_id"],
        ondelete="CASCADE",
    )

    # Add FK constraint to enrichment_cache.company_id -> companies.company_id
    op.create_foreign_key(
        "fk_enrichment_cache_companies_company_id",
        "enrichment_cache",
        "companies",
        ["company_id"],
        ["company_id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade: remove foreign key constraints from enrichment tables."""
    op.drop_constraint(
        "fk_enrichment_cache_companies_company_id",
        "enrichment_cache",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_enrichment_audit_trail_companies_company_id",
        "enrichment_audit_trail",
        type_="foreignkey",
    )
