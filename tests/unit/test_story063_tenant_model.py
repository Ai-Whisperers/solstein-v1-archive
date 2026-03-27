"""STORY-063: Tests for tenant model and domain object scoping.

Validates:
- Tenant entity exists in domain layer
- Company requires tenant_id (cannot be empty/null)
- tenant_id is propagated through domain object graph
- Default tenant backfill constant is defined
- Database models have tenant_id columns
"""

import uuid
from pathlib import Path

import pytest

from solstein.domain.models import (
    DEFAULT_TENANT_ID,
    Company,
)
from solstein.infrastructure.models.company import (
    AuditTrailRecord,
    CompanyRecord,
    MarketSnapshot,
    ScoringRecord,
)
from solstein.infrastructure.models.enrichment import (
    EnrichmentAuditRecord,
    EnrichmentCacheRecord,
    EnrichmentJobRecord,
)
from solstein.infrastructure.models.infrastructure import TenantRecord
from solstein.infrastructure.models.research import ResearchRunRecord
from solstein.tenant.models import (
    Tenant,
    TenantConfig,
    TenantPlan,
    TenantStatus,
    TenantUser,
)

# --- Tenant Domain Entity Tests ---


class TestTenantEntity:
    """REQ-1: Tenant entity must exist with id, name, subscription tier, created_at, is_active."""

    def test_tenant_has_required_fields(self):
        """Tenant entity has id, name, plan (subscription tier), status, created_at."""
        tenant = Tenant(name="Test Firm")
        assert tenant.id is not None
        assert tenant.name == "Test Firm"
        assert tenant.plan == TenantPlan.STARTER
        assert tenant.status == TenantStatus.ACTIVE
        assert tenant.created_at is not None

    def test_tenant_plans_exist(self):
        """Subscription tiers are defined."""
        assert TenantPlan.STARTER == "starter"
        assert TenantPlan.PROFESSIONAL == "professional"
        assert TenantPlan.ENTERPRISE == "enterprise"

    def test_tenant_statuses_exist(self):
        """Tenant statuses cover active/inactive lifecycle."""
        assert TenantStatus.ACTIVE == "active"
        assert TenantStatus.SUSPENDED == "suspended"
        assert TenantStatus.PENDING == "pending"
        assert TenantStatus.CANCELLED == "cancelled"

    def test_tenant_is_extensible(self):
        """REQ-5: Tenant model supports per-tenant configuration."""
        tenant = Tenant(
            name="Enterprise Firm",
            plan=TenantPlan.ENTERPRISE,
            settings={"custom_scoring_weights": {"growth": 0.4}},
        )
        assert tenant.settings["custom_scoring_weights"]["growth"] == 0.4


class TestTenantConfig:
    """REQ-5: Extensible per-tenant configuration."""

    def test_tenant_config_has_limits(self):
        config = TenantConfig(tenant_id="test-123")
        assert config.limits.max_companies == 1000
        assert config.limits.max_api_calls_per_day == 10000

    def test_tenant_config_has_features(self):
        config = TenantConfig(tenant_id="test-123")
        assert config.features.ai_enrichment is True
        assert config.features.sso is False

    def test_tenant_config_supports_custom_fields(self):
        config = TenantConfig(
            tenant_id="test-123",
            custom_fields=[{"name": "deal_stage", "type": "string"}],
            scoring_weights={"growth": 0.5, "financial_health": 0.3},
        )
        assert len(config.custom_fields) == 1
        assert config.scoring_weights["growth"] == 0.5


class TestTenantUser:
    """Tenant user model validation."""

    def test_tenant_user_has_tenant_id(self):
        user = TenantUser(tenant_id="tid-123", email="user@firm.com")
        assert user.tenant_id == "tid-123"
        assert user.role == "member"


# --- Company Domain Entity Tests ---


class TestCompanyTenantScoping:
    """REQ-2/REQ-3: Company requires tenant_id, propagated through domain graph."""

    def test_company_has_tenant_id_field(self):
        """Company domain model includes tenant_id."""
        company = Company(
            id="COMP-TEST-001",
            name="Test Corp",
            tenant_id="tid-abc-123",
        )
        assert company.tenant_id == "tid-abc-123"

    def test_company_default_tenant_id(self):
        """Company uses default tenant when not explicitly provided (migration path)."""
        company = Company(id="COMP-TEST-002", name="Legacy Corp")
        assert company.tenant_id == DEFAULT_TENANT_ID

    def test_company_rejects_empty_tenant_id(self):
        """Constructing Company with empty tenant_id raises domain exception."""
        with pytest.raises(ValueError, match="tenant_id is required"):
            Company(id="COMP-TEST-003", name="Bad Corp", tenant_id="")

    def test_company_rejects_whitespace_tenant_id(self):
        """Constructing Company with whitespace-only tenant_id raises domain exception."""
        with pytest.raises(ValueError, match="tenant_id is required"):
            Company(id="COMP-TEST-004", name="Bad Corp", tenant_id="   ")

    def test_company_tenant_id_is_stripped(self):
        """tenant_id whitespace is stripped."""
        company = Company(
            id="COMP-TEST-005",
            name="Strip Corp",
            tenant_id="  tid-123  ",
        )
        assert company.tenant_id == "tid-123"


class TestDefaultTenantConstant:
    """REQ-4: Default tenant constant for migration backfill."""

    def test_default_tenant_id_is_valid_uuid(self):
        """DEFAULT_TENANT_ID is a valid UUID string."""
        parsed = uuid.UUID(DEFAULT_TENANT_ID)
        assert str(parsed) == DEFAULT_TENANT_ID

    def test_default_tenant_id_is_zero_uuid(self):
        """Default tenant uses the zero UUID for easy identification."""
        assert DEFAULT_TENANT_ID == "00000000-0000-0000-0000-000000000000"


# --- Database Model Tests ---


class TestDatabaseModelsTenantId:
    """REQ-2: All major database tables have tenant_id column."""

    def test_company_record_has_tenant_id(self):
        assert hasattr(CompanyRecord, "tenant_id")

    def test_scoring_record_has_tenant_id(self):
        assert hasattr(ScoringRecord, "tenant_id")

    def test_market_snapshot_has_tenant_id(self):
        assert hasattr(MarketSnapshot, "tenant_id")

    def test_audit_trail_has_tenant_id(self):
        assert hasattr(AuditTrailRecord, "tenant_id")

    def test_enrichment_audit_has_tenant_id(self):
        assert hasattr(EnrichmentAuditRecord, "tenant_id")

    def test_enrichment_cache_has_tenant_id(self):
        assert hasattr(EnrichmentCacheRecord, "tenant_id")

    def test_enrichment_job_has_tenant_id(self):
        assert hasattr(EnrichmentJobRecord, "tenant_id")

    def test_research_run_has_tenant_id(self):
        assert hasattr(ResearchRunRecord, "tenant_id")

    def test_tenant_record_exists(self):
        assert hasattr(TenantRecord, "id")
        assert hasattr(TenantRecord, "name")
        assert hasattr(TenantRecord, "is_active")
        assert hasattr(TenantRecord, "plan")
        assert hasattr(TenantRecord, "rate_limit_per_min")


# --- Migration Test ---


class TestMigrationFile:
    """REQ-4: Migration file exists for tenant_id columns."""

    def test_migration_file_exists(self):
        migration_path = Path(__file__).resolve().parents[2] / "alembic" / "versions"
        migration_files = list(migration_path.glob("013_epic019_*.py"))
        assert len(migration_files) == 1, f"Expected 1 migration file, found {len(migration_files)}"
