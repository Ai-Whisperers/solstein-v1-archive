"""EPIC-025 Story 2: Strategic Index Implementation

Add indexes for optimal query performance per EPIC-025 requirements.

Revision ID: 012
Revises: 086d0b4872a0
Create Date: 2026-03-06 03:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "012"
down_revision: Union[str, Sequence[str], None] = "086d0b4872a0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade: Add strategic indexes for EPIC-025 performance optimization."""

    # ==========================================
    # 1. FULL-TEXT SEARCH INDEX (EPIC-025 Requirement)
    # ==========================================
    # For company name/description search
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_company_search 
        ON companies 
        USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));
        """
    )

    # ==========================================
    # 2. SIGNAL RECORDS INDEXES
    # ==========================================
    # Date range queries for signal analysis
    op.create_index("ix_signal_records_extracted_at", "signal_records", ["extracted_at"])

    # Composite index for filtering signals by record + date
    op.create_index(
        "ix_signal_records_scoring_id_extracted",
        "signal_records",
        ["scoring_record_id", "extracted_at"],
    )

    # ==========================================
    # 3. AUDIT TRAIL INDEXES
    # ==========================================
    # Date range queries for audit trail
    op.create_index(
        "ix_audit_trails_created_at",
        "audit_trails",
        ["created_at"],
    )

    # Composite index for company audit history
    op.create_index(
        "ix_audit_trails_company_created",
        "audit_trails",
        ["company_id", "created_at"],
    )

    # ==========================================
    # 4. ENRICHMENT AUDIT INDEXES
    # ==========================================
    # Status + timestamp for monitoring
    op.create_index(
        "ix_enrichment_audit_status_timestamp",
        "enrichment_audit_trail",
        ["status", "timestamp"],
    )

    # ==========================================
    # 5. CONTRADICTION RECORD INDEXES
    # ==========================================
    # Status tracking for open contradictions
    op.create_index(
        "ix_research_contradictions_status",
        "research_contradictions",
        ["status"],
    )

    # Date range for contradiction resolution tracking
    op.create_index(
        "ix_research_contradictions_created_at",
        "research_contradictions",
        ["created_at"],
    )

    # ==========================================
    # 6. CONTRADICTION TRANSITION INDEXES
    # ==========================================
    op.create_index(
        "ix_research_contradiction_transitions_changed_at",
        "research_contradiction_transitions",
        ["changed_at"],
    )

    # ==========================================
    # 7. OUTBOX RECORD INDEXES
    # ==========================================
    # For efficient outbox polling
    op.create_index(
        "ix_outbox_records_available_at",
        "outbox_records",
        ["available_at"],
    )

    # ==========================================
    # 8. COMPANY RECORD ADDITIONAL INDEXES
    # ==========================================
    # For revenue range queries (common filter)
    op.create_index(
        "ix_companies_revenue_range",
        "companies",
        ["revenue_eur_m"],
    )

    # For employee count filtering
    op.create_index(
        "ix_companies_employee_count",
        "companies",
        ["employee_count"],
    )

    # For founded year filtering (age analysis)
    op.create_index(
        "ix_companies_founded_year",
        "companies",
        ["founded_year"],
    )


def downgrade() -> None:
    """Downgrade: Remove strategic indexes."""

    # Company indexes
    op.drop_index("ix_companies_founded_year", table_name="companies")
    op.drop_index("ix_companies_employee_count", table_name="companies")
    op.drop_index("ix_companies_revenue_range", table_name="companies")

    # Outbox indexes
    op.drop_index("ix_outbox_records_available_at", table_name="outbox_records")

    # Contradiction transition indexes
    op.drop_index(
        "ix_research_contradiction_transitions_changed_at",
        table_name="research_contradiction_transitions",
    )

    # Contradiction indexes
    op.drop_index("ix_research_contradictions_created_at", table_name="research_contradictions")
    op.drop_index("ix_research_contradictions_status", table_name="research_contradictions")

    # Enrichment audit indexes
    op.drop_index(
        "ix_enrichment_audit_status_timestamp",
        table_name="enrichment_audit_trail",
    )

    # Audit trail indexes
    op.drop_index("ix_audit_trails_company_created", table_name="audit_trails")
    op.drop_index("ix_audit_trails_created_at", table_name="audit_trails")

    # Signal record indexes
    op.drop_index("ix_signal_records_scoring_id_extracted", table_name="signal_records")
    op.drop_index("ix_signal_records_extracted_at", table_name="signal_records")

    # Full-text search index
    op.execute("DROP INDEX IF EXISTS ix_company_search;")
