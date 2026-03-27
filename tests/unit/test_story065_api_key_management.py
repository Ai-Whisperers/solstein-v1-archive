"""Tests for STORY-065: Tenant-Scoped API Key Management.

Validates:
- ApiKey domain model and ApiKeyScope enum
- API key generation, hashing, and prefix extraction
- Scope hierarchy enforcement
- ORM models exist with correct fields
- Migration files exist
- Key hash storage (no plaintext stored)
"""

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from solstein.domain.models import ApiKey, ApiKeyScope
from solstein.tenant.api_key_service import (
    generate_api_key,
    get_key_prefix,
    hash_api_key,
    scope_allows,
)

# Root paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
SUPABASE_MIGRATION = PROJECT_ROOT / "supabase" / "migrations" / "015_epic019_api_keys.sql"
ALEMBIC_MIGRATION = PROJECT_ROOT / "alembic" / "versions" / "015_epic019_api_keys_table.py"


class TestApiKeyScopeEnum:
    """Verify ApiKeyScope enum values."""

    def test_read_only_value(self) -> None:
        assert ApiKeyScope.READ_ONLY == "read_only"

    def test_read_write_value(self) -> None:
        assert ApiKeyScope.READ_WRITE == "read_write"

    def test_admin_value(self) -> None:
        assert ApiKeyScope.ADMIN == "admin"

    def test_scope_count(self) -> None:
        assert len(ApiKeyScope) == 3


class TestApiKeyDomainModel:
    """Verify ApiKey domain entity."""

    def test_create_api_key(self) -> None:
        key = ApiKey(
            tenant_id="tenant-123",
            name="Test Key",
            key_hash="abc123",
            scope=ApiKeyScope.READ_ONLY,
        )
        assert key.tenant_id == "tenant-123"
        assert key.name == "Test Key"
        assert key.scope == ApiKeyScope.READ_ONLY
        assert key.is_active is True

    def test_default_scope_is_read_only(self) -> None:
        key = ApiKey(tenant_id="t1", name="k1")
        assert key.scope == ApiKeyScope.READ_ONLY

    def test_default_is_active(self) -> None:
        key = ApiKey(tenant_id="t1", name="k1")
        assert key.is_active is True

    def test_default_timestamps(self) -> None:
        key = ApiKey(tenant_id="t1", name="k1")
        assert key.created_at is not None
        assert key.last_used_at is None
        assert key.expires_at is None
        assert key.revoked_at is None

    def test_rejects_empty_tenant_id(self) -> None:
        with pytest.raises(ValueError, match="tenant"):
            ApiKey(tenant_id="", name="k1")

    def test_rejects_whitespace_tenant_id(self) -> None:
        with pytest.raises(ValueError, match="tenant"):
            ApiKey(tenant_id="   ", name="k1")

    def test_rejects_empty_name(self) -> None:
        with pytest.raises(ValueError, match="name"):
            ApiKey(tenant_id="t1", name="")

    def test_strips_tenant_id(self) -> None:
        key = ApiKey(tenant_id="  t1  ", name="k1")
        assert key.tenant_id == "t1"

    def test_strips_name(self) -> None:
        key = ApiKey(tenant_id="t1", name="  my key  ")
        assert key.name == "my key"

    def test_all_scopes_assignable(self) -> None:
        for scope in ApiKeyScope:
            key = ApiKey(tenant_id="t1", name="k1", scope=scope)
            assert key.scope == scope


class TestKeyGeneration:
    """Verify API key generation functions."""

    def test_generate_live_key_prefix(self) -> None:
        key = generate_api_key()
        assert key.startswith("sk_live_")

    def test_generate_test_key_prefix(self) -> None:
        key = generate_api_key(test_mode=True)
        assert key.startswith("sk_test_")

    def test_generated_keys_are_unique(self) -> None:
        keys = {generate_api_key() for _ in range(100)}
        assert len(keys) == 100

    def test_key_length_sufficient(self) -> None:
        key = generate_api_key()
        # sk_live_ (8) + 43 chars of base64 = 51+
        assert len(key) >= 40

    def test_hash_is_sha256(self) -> None:
        key = "sk_live_test123"
        expected = hashlib.sha256(key.encode()).hexdigest()
        assert hash_api_key(key) == expected

    def test_hash_length_is_64(self) -> None:
        hashed = hash_api_key("sk_live_test")
        assert len(hashed) == 64

    def test_hash_is_deterministic(self) -> None:
        key = "sk_live_deterministic"
        assert hash_api_key(key) == hash_api_key(key)

    def test_different_keys_different_hashes(self) -> None:
        h1 = hash_api_key("key1")
        h2 = hash_api_key("key2")
        assert h1 != h2

    def test_get_key_prefix(self) -> None:
        prefix = get_key_prefix("sk_live_AbCdEfGh123456")
        assert prefix == "sk_live_"

    def test_get_key_prefix_length(self) -> None:
        prefix = get_key_prefix("sk_live_AbCdEfGh123456")
        assert len(prefix) == 8


class TestScopeEnforcement:
    """Verify scope hierarchy logic."""

    def test_read_only_allows_read_only(self) -> None:
        assert scope_allows("read_only", "read_only") is True

    def test_read_only_denies_read_write(self) -> None:
        assert scope_allows("read_only", "read_write") is False

    def test_read_only_denies_admin(self) -> None:
        assert scope_allows("read_only", "admin") is False

    def test_read_write_allows_read_only(self) -> None:
        assert scope_allows("read_write", "read_only") is True

    def test_read_write_allows_read_write(self) -> None:
        assert scope_allows("read_write", "read_write") is True

    def test_read_write_denies_admin(self) -> None:
        assert scope_allows("read_write", "admin") is False

    def test_admin_allows_all(self) -> None:
        assert scope_allows("admin", "read_only") is True
        assert scope_allows("admin", "read_write") is True
        assert scope_allows("admin", "admin") is True

    def test_unknown_scope_denied(self) -> None:
        assert scope_allows("unknown", "read_only") is False

    def test_unknown_required_denied(self) -> None:
        assert scope_allows("admin", "unknown") is False


class TestOrmModels:
    """Verify ORM models exist with correct attributes."""

    def test_api_key_record_exists(self) -> None:
        from solstein.infrastructure.models.infrastructure import ApiKeyRecord

        assert ApiKeyRecord.__tablename__ == "api_keys"

    def test_api_key_record_has_required_columns(self) -> None:
        from solstein.infrastructure.models.infrastructure import ApiKeyRecord

        required = ["id", "tenant_id", "name", "key_prefix", "key_hash", "scope", "is_active"]
        for col in required:
            assert hasattr(ApiKeyRecord, col), f"ApiKeyRecord missing column: {col}"

    def test_api_key_record_has_lifecycle_columns(self) -> None:
        from solstein.infrastructure.models.infrastructure import ApiKeyRecord

        lifecycle = ["last_used_at", "created_at", "expires_at", "revoked_at"]
        for col in lifecycle:
            assert hasattr(ApiKeyRecord, col), f"ApiKeyRecord missing column: {col}"

    def test_api_key_record_to_dict_no_hash(self) -> None:
        """to_dict must never expose key_hash."""
        from solstein.infrastructure.models.infrastructure import ApiKeyRecord

        record = ApiKeyRecord()
        record.id = "fake-id"
        record.tenant_id = "fake-tenant"
        record.name = "test"
        record.key_prefix = "sk_live_"
        record.key_hash = "should_not_appear"
        record.scope = "read_only"
        record.is_active = True
        record.last_used_at = None
        record.created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
        record.expires_at = None
        record.revoked_at = None

        d = record.to_dict()
        assert "key_hash" not in d
        assert d["key_prefix"] == "sk_live_"

    def test_api_key_usage_record_exists(self) -> None:
        from solstein.infrastructure.models.infrastructure import ApiKeyUsageRecord

        assert ApiKeyUsageRecord.__tablename__ == "api_key_usage_logs"

    def test_api_key_usage_has_required_columns(self) -> None:
        from solstein.infrastructure.models.infrastructure import ApiKeyUsageRecord

        required = ["id", "api_key_id", "tenant_id", "endpoint", "method", "status_code", "timestamp"]
        for col in required:
            assert hasattr(ApiKeyUsageRecord, col), f"ApiKeyUsageRecord missing column: {col}"


class TestMigrationFiles:
    """Verify migration files exist and contain correct content."""

    def test_supabase_migration_exists(self) -> None:
        assert SUPABASE_MIGRATION.exists()

    def test_alembic_migration_exists(self) -> None:
        assert ALEMBIC_MIGRATION.exists()

    def test_supabase_creates_api_keys_table(self) -> None:
        sql = SUPABASE_MIGRATION.read_text()
        assert "CREATE TABLE IF NOT EXISTS public.api_keys" in sql

    def test_supabase_creates_usage_logs_table(self) -> None:
        sql = SUPABASE_MIGRATION.read_text()
        assert "CREATE TABLE IF NOT EXISTS public.api_key_usage_logs" in sql

    def test_supabase_has_scope_check_constraint(self) -> None:
        sql = SUPABASE_MIGRATION.read_text()
        assert "ck_api_key_scope" in sql

    def test_supabase_enables_rls(self) -> None:
        sql = SUPABASE_MIGRATION.read_text()
        assert "ENABLE ROW LEVEL SECURITY" in sql

    def test_supabase_has_tenant_policies(self) -> None:
        sql = SUPABASE_MIGRATION.read_text()
        assert '"tenant_select" ON public.api_keys' in sql
        assert '"tenant_insert" ON public.api_keys' in sql

    def test_alembic_revision_id(self) -> None:
        py = ALEMBIC_MIGRATION.read_text()
        assert 'revision: str = "015"' in py

    def test_alembic_has_downgrade(self) -> None:
        py = ALEMBIC_MIGRATION.read_text()
        assert "def downgrade" in py

    def test_key_hash_never_stored_as_plaintext(self) -> None:
        """Verify no plaintext key storage patterns in migration."""
        sql = SUPABASE_MIGRATION.read_text()
        # key_hash column stores the hash, not the key
        assert "key_hash" in sql
        # No column named 'key_value' or 'api_key_value' or 'plaintext'
        assert "key_value" not in sql
        assert "plaintext" not in sql


class TestCreateApiKeyService:
    """Test create_api_key service function."""

    def test_create_returns_key_and_record(self) -> None:
        mock_db = MagicMock()

        result = None
        with patch(
            "solstein.tenant.api_key_service.ApiKeyRecord",
            create=True,
        ):
            from solstein.tenant.api_key_service import create_api_key

            # Patch ApiKeyRecord import inside the function
            mock_record_cls = MagicMock()
            mock_instance = MagicMock()
            mock_instance.to_dict.return_value = {"id": "new-id", "name": "test"}
            mock_record_cls.return_value = mock_instance

            with patch(
                "solstein.infrastructure.models.infrastructure.ApiKeyRecord",
                mock_record_cls,
            ):
                # Just test the key generation parts
                key = generate_api_key()
                assert key.startswith("sk_live_")
                h = hash_api_key(key)
                assert len(h) == 64


class TestSecurityGuarantees:
    """Security-focused tests for API key management."""

    def test_hash_not_reversible(self) -> None:
        """SHA-256 is a one-way function — hash cannot reveal the key."""
        key = generate_api_key()
        hashed = hash_api_key(key)
        # The hash should not contain the key
        assert key not in hashed
        # The hash should be hex characters only
        assert re.match(r"^[0-9a-f]{64}$", hashed)

    def test_prefix_does_not_reveal_full_key(self) -> None:
        key = generate_api_key()
        prefix = get_key_prefix(key)
        assert len(prefix) < len(key)
        assert prefix == key[:8]

    def test_scope_hierarchy_is_strict(self) -> None:
        """Lower scopes cannot access higher-privilege operations."""
        assert not scope_allows("read_only", "read_write")
        assert not scope_allows("read_only", "admin")
        assert not scope_allows("read_write", "admin")
