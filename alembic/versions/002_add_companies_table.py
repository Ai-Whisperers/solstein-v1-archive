"""Add companies table for comprehensive company data.

Revision ID: 002
Revises: 001
Create Date: 2026-02-21 01:45:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=500), nullable=False),
        sa.Column("industry", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("website", sa.String(length=500), nullable=True),
        sa.Column("headquarters", sa.String(length=100), nullable=True),
        sa.Column("founded_year", sa.Integer(), nullable=True),
        sa.Column("tier", sa.String(length=50), nullable=True),
        sa.Column("threat_level", sa.String(length=50), nullable=True),
        sa.Column("classification", sa.String(length=50), nullable=True),
        sa.Column("ai_maturity", sa.String(length=50), nullable=True),
        sa.Column("saas_maturity", sa.Integer(), nullable=True),
        sa.Column("ai_score", sa.Integer(), nullable=True),
        sa.Column("ai_signal_level", sa.String(length=50), nullable=True),
        sa.Column("ai_key_capabilities", sa.Text(), nullable=True),
        sa.Column("ai_in_production", sa.String(length=10), nullable=True),
        sa.Column("revenue_eur_m", sa.Float(), nullable=True),
        sa.Column("revenue_confidence", sa.String(length=50), nullable=True),
        sa.Column("growth_rate_pct", sa.Float(), nullable=True),
        sa.Column("growth_confidence", sa.String(length=50), nullable=True),
        sa.Column("profit_margin_pct", sa.Float(), nullable=True),
        sa.Column("ebitda_margin_pct", sa.Float(), nullable=True),
        sa.Column("recurring_revenue_pct", sa.Float(), nullable=True),
        sa.Column("revenue_per_employee_eur_k", sa.Float(), nullable=True),
        sa.Column("revenue_timeline", sa.JSON(), nullable=True),
        sa.Column("revenue_cagr_3yr", sa.Float(), nullable=True),
        sa.Column("revenue_cagr_5yr", sa.Float(), nullable=True),
        sa.Column("funding_rounds", sa.JSON(), nullable=True),
        sa.Column("total_funding_raised_eur", sa.Float(), nullable=True),
        sa.Column("latest_valuation_eur", sa.Float(), nullable=True),
        sa.Column("lead_investors", sa.JSON(), nullable=True),
        sa.Column("funding_war_chest", sa.Text(), nullable=True),
        sa.Column("employee_count", sa.Integer(), nullable=True),
        sa.Column("employee_cagr_3yr", sa.Float(), nullable=True),
        sa.Column("open_positions", sa.Integer(), nullable=True),
        sa.Column("profitability_raw_metrics", sa.JSON(), nullable=True),
        sa.Column("data_availability", sa.Text(), nullable=True),
        sa.Column("data_source", sa.String(length=255), nullable=True),
        sa.Column("growth_score", sa.Float(), nullable=True),
        sa.Column("financial_health_score", sa.Float(), nullable=True),
        sa.Column("competitive_position_score", sa.Float(), nullable=True),
        sa.Column("composite_score", sa.Float(), nullable=True),
        sa.Column("scoring_breakdown", sa.JSON(), nullable=True),
        sa.Column("last_updated", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("company_id"),
    )
    op.create_index("ix_company_name", "companies", ["name"], unique=False)
    op.create_index("ix_company_tier", "companies", ["tier"], unique=False)
    op.create_index(
        "ix_company_classification", "companies", ["classification"], unique=False
    )
    op.create_index("ix_company_ai_score", "companies", ["ai_score"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_company_ai_score", table_name="companies")
    op.drop_index("ix_company_classification", table_name="companies")
    op.drop_index("ix_company_tier", table_name="companies")
    op.drop_index("ix_company_name", table_name="companies")
    op.drop_table("companies")
