import sqlalchemy as sa
from alembic import op

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    _ = op.create_table(
        "gathering_batches",
        sa.Column("batch_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("company_id", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default=sa.text("'in_progress'"),
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.company_id"]),
        sa.PrimaryKeyConstraint("batch_id"),
    )
    op.create_index(
        "ix_gathering_batches_company_created_at",
        "gathering_batches",
        ["company_id", "created_at"],
        unique=False,
    )

    _ = op.create_table(
        "facts",
        sa.Column("fact_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("company_id", sa.String(length=255), nullable=False),
        sa.Column("batch_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("fact_type", sa.String(length=100), nullable=False),
        sa.Column("value", sa.Numeric(precision=20, scale=4), nullable=True),
        sa.Column("value_str", sa.String(length=500), nullable=True),
        sa.Column("value_date", sa.Date(), nullable=True),
        sa.Column(
            "confidence",
            sa.Numeric(precision=3, scale=2),
            nullable=False,
            server_default=sa.text("0.5"),
        ),
        sa.Column(
            "extracted_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.company_id"]),
        sa.ForeignKeyConstraint(["batch_id"], ["gathering_batches.batch_id"]),
        sa.PrimaryKeyConstraint("fact_id"),
    )
    op.create_index(
        "ix_facts_company_fact_type",
        "facts",
        ["company_id", "fact_type"],
        unique=False,
    )
    op.create_index(
        "ix_facts_fact_type",
        "facts",
        ["fact_type"],
        unique=False,
    )

    _ = op.create_table(
        "fact_sources",
        sa.Column("source_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("fact_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("source_type", sa.String(length=100), nullable=False),
        sa.Column("source_url", sa.String(length=1000), nullable=True),
        sa.Column(
            "extraction_timestamp",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("raw_content", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["fact_id"], ["facts.fact_id"]),
        sa.PrimaryKeyConstraint("source_id"),
    )


def downgrade() -> None:
    op.drop_index("ix_facts_fact_type", table_name="facts")
    op.drop_index("ix_facts_company_fact_type", table_name="facts")
    op.drop_table("fact_sources")
    op.drop_table("facts")
    op.drop_index("ix_gathering_batches_company_created_at", table_name="gathering_batches")
    op.drop_table("gathering_batches")
